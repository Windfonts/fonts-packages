#!/usr/bin/env node
/**
 * Download 6 bitmap BDF from Guangzhou, convert to TTF, cn-font-split Regular/full, upload.
 * Additive. Does not delete BDF/source/license at prefix root.
 *
 *   node scripts/oss-unify-20261007/ingest-bdf6.js           # download+convert only
 *   node scripts/oss-unify-20261007/ingest-bdf6.js --upload
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const OSS = require('ali-oss');
const pLimit = require('p-limit');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const ROOT = path.join(__dirname, '../..');
const WORK = path.join(ROOT, '_work_bdf6');
const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const DO_UPLOAD = process.argv.includes('--upload');
const CONC = Number((process.argv.find((a) => a.startsWith('--conc=')) || '--conc=8').slice(7)) || 8;
const LOG = path.join(__dirname, 'ingest-bdf6.jsonl');

const JOBS = [
  { prefix: 'bestten', bdf: 'BestTen-CRT-10px.bdf', family: 'BestTen', weight: 'Regular' },
  { prefix: 'lana-pixel', bdf: 'LanaPixel-11px.bdf', family: 'LanaPixel', weight: 'Regular' },
  { prefix: 'taipei-pixel', bdf: 'Taipei16.bdf', family: 'TaipeiPixel', weight: 'Regular' },
  { prefix: 'taipei-pixel', bdf: 'Taipei24.bdf', family: 'TaipeiPixel', weight: 'Taipei24' },
  { prefix: 'fonsung', bdf: 'Fonsung-16px.bdf', family: 'Fonsung', weight: 'Regular' },
  { prefix: 'lyusung', bdf: 'Lyusung-210618-24px.bdf', family: 'Lyusung', weight: 'Regular' },
  { prefix: 'chusung', bdf: 'Chusung-210529-16px.bdf', family: 'Chusung', weight: 'Regular' },
];

function client() {
  return new OSS({
    accessKeyId: process.env.OSS_ACCESS_KEY_ID,
    accessKeySecret: process.env.OSS_ACCESS_KEY_SECRET,
    bucket: process.env.OSS_BUCKET,
    region: process.env.OSS_REGION,
    endpoint: process.env.OSS_ENDPOINT || undefined,
  });
}

function log(row) {
  fs.appendFileSync(LOG, JSON.stringify(row) + '\n');
}

function run(cmd, args, opts) {
  const r = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
  if (r.status !== 0) throw new Error(cmd + ' ' + args.join(' ') + ' exit ' + r.status);
}

async function downloadBdf(c, job) {
  const key = BASE + job.prefix + '/' + job.bdf;
  const dest = path.join(WORK, 'bdf', job.prefix, job.bdf);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (fs.existsSync(dest) && fs.statSync(dest).size > 1000) {
    log({ step: 'download-skip', key, dest, size: fs.statSync(dest).size });
    return dest;
  }
  const result = await c.get(key, dest);
  log({ step: 'download', key, dest, status: result.res && result.res.status, size: fs.statSync(dest).size });
  return dest;
}

function toTtf(job, bdfPath) {
  const ttfDir = path.join(WORK, 'fonts', job.prefix, job.weight);
  fs.mkdirSync(ttfDir, { recursive: true });
  const ttf = path.join(ttfDir, job.prefix + '-' + job.weight + '-full.ttf');
  if (fs.existsSync(ttf) && fs.statSync(ttf).size > 1000) {
    log({ step: 'ttf-skip', ttf, size: fs.statSync(ttf).size });
    return ttf;
  }
  run('python3', [path.join(ROOT, 'scripts/bdf-to-ttf.py'), bdfPath, ttf, job.family, job.family + ' ' + job.weight], {
    cwd: WORK,
  });
  log({ step: 'ttf', ttf, size: fs.statSync(ttf).size });
  return ttf;
}

function splitAll() {
  run('node', [path.join(ROOT, 'scripts/convert.js')], { cwd: WORK });
}

async function destSize(c, name) {
  try {
    const h = await c.head(name);
    const n = Number(h.res && h.res.headers && h.res.headers['content-length']);
    return Number.isFinite(n) ? n : -1;
  } catch (e) {
    if (e && (e.status === 404 || e.code === 'NoSuchKey')) return -1;
    throw e;
  }
}

async function uploadJob(c, job, limit) {
  const localDir = path.join(WORK, 'dist', job.prefix, job.weight, 'full');
  if (!fs.existsSync(localDir)) throw new Error('missing dist ' + localDir);
  const files = fs.readdirSync(localDir).filter((f) => !f.startsWith('.') && !f.endsWith('.html'));
  let copied = 0;
  let skipped = 0;
  let failed = 0;
  const errors = [];
  await Promise.all(
    files.map((f) =>
      limit(async () => {
        const local = path.join(localDir, f);
        const key = BASE + job.prefix + '/' + job.weight + '/full/' + f;
        const size = fs.statSync(local).size;
        try {
          const have = await destSize(c, key);
          if (have === size) {
            skipped += 1;
            return;
          }
          await c.put(key, local);
          copied += 1;
        } catch (e) {
          failed += 1;
          if (errors.length < 8) errors.push(key + ' :: ' + (e.message || e));
        }
      })
    )
  );
  const row = { step: 'upload', ...job, n: files.length, copied, skipped, failed, errors };
  log(row);
  return row;
}

async function copyAlias(c, srcPrefix, dstPrefix, limit) {
  const src = [];
  let marker;
  do {
    const r = await c.list({ prefix: srcPrefix, marker, 'max-keys': 1000 });
    for (const o of r.objects || []) {
      if (o.name && !o.name.endsWith('/')) src.push({ name: o.name, size: o.size || 0 });
    }
    marker = r.nextMarker;
  } while (marker);
  let copied = 0;
  let skipped = 0;
  await Promise.all(
    src.map((o) =>
      limit(async () => {
        const dstKey = dstPrefix + o.name.slice(srcPrefix.length);
        const have = await destSize(c, dstKey);
        if (have === o.size) {
          skipped += 1;
          return;
        }
        await c.copy(dstKey, o.name);
        copied += 1;
      })
    )
  );
  const row = { step: 'alias', srcPrefix, dstPrefix, n: src.length, copied, skipped };
  log(row);
  return row;
}

(async () => {
  fs.mkdirSync(path.join(WORK, 'fonts'), { recursive: true });
  fs.mkdirSync(path.join(WORK, 'bdf'), { recursive: true });
  fs.writeFileSync(LOG, '');
  const c = client();
  for (const job of JOBS) {
    process.stderr.write('GET ' + job.prefix + ' ' + job.bdf + '\n');
    const bdf = await downloadBdf(c, job);
    toTtf(job, bdf);
  }
  process.stderr.write('SPLIT\n');
  splitAll();
  if (!DO_UPLOAD) {
    console.log(JSON.stringify({ upload: false, work: WORK }));
    return;
  }
  const limit = pLimit(CONC);
  const rows = [];
  for (const job of JOBS) {
    process.stderr.write('PUT ' + job.prefix + '/' + job.weight + '\n');
    rows.push(await uploadJob(c, job, limit));
  }
  rows.push(
    await copyAlias(
      c,
      BASE + 'bestten/Regular/',
      BASE + 'bestten/BestTen_CRT_10px/',
      limit
    )
  );
  const fail = rows.filter((r) => r.failed).length;
  console.log(JSON.stringify({ upload: true, fail, rows: rows.map((r) => ({ prefix: r.prefix || r.srcPrefix, n: r.n, copied: r.copied, skipped: r.skipped, failed: r.failed })) }));
  if (fail) process.exit(1);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
