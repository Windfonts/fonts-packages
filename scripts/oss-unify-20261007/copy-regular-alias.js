#!/usr/bin/env node
/**
 * Copy one weight folder to Regular under the same prefix.
 * Additive. Skip dest objects with the same size. Do not delete source.
 *
 *   node scripts/oss-unify-20261007/copy-regular-alias.js
 *   node scripts/oss-unify-20261007/copy-regular-alias.js --go
 */
const fs = require('fs');
const path = require('path');
const OSS = require('ali-oss');
const pLimit = require('p-limit');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const args = process.argv.slice(2);
const DO = args.includes('--go');
const CONC = Number((args.find((a) => a.startsWith('--conc=')) || '--conc=12').slice(7)) || 12;
const LOG = path.join(__dirname, 'copy-regular-alias.jsonl');

const JOBS = [
  { dir: 'mkcjp', from: 'mikachan', to: 'Regular' },
  { dir: 'kisjp', from: 'Kaisotai-Next-UP-B', to: 'Regular' },
  { dir: 'knkkjp', from: 'Normal', to: 'Regular' },
  { dir: 'smsnjp', from: 'Donokun-01', to: 'Regular' },
  { dir: 'mystp3l', from: 'CN-W7', to: 'Regular' },
  { dir: 'myhtp3l', from: 'CN-W7', to: 'Regular' },
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

async function listObjects(c, prefix) {
  const out = [];
  let marker;
  do {
    const r = await c.list({ prefix, marker, 'max-keys': 1000 });
    for (const o of r.objects || []) {
      if (o.name && !o.name.endsWith('/')) out.push({ name: o.name, size: o.size || 0 });
    }
    marker = r.nextMarker;
  } while (marker);
  return out;
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

function log(row) {
  fs.appendFileSync(LOG, JSON.stringify(row) + '\n');
}

async function copyJob(c, job, limit) {
  const srcPrefix = BASE + job.dir + '/' + job.from + '/';
  const dstPrefix = BASE + job.dir + '/' + job.to + '/';
  const src = await listObjects(c, srcPrefix);
  if (!src.length) {
    const row = { ok: false, skip: 'empty-src', ...job, n: 0 };
    log(row);
    return row;
  }
  let copied = 0;
  let skipped = 0;
  let failed = 0;
  const errors = [];
  await Promise.all(
    src.map((o) =>
      limit(async () => {
        const dstKey = dstPrefix + o.name.slice(srcPrefix.length);
        try {
          const have = await destSize(c, dstKey);
          if (have === o.size) {
            skipped += 1;
            return;
          }
          if (have >= 0 && have !== o.size) {
            failed += 1;
            if (errors.length < 8) errors.push(dstKey + ' :: dest-exists-size-mismatch ' + have + '!=' + o.size);
            return;
          }
          if (!DO) {
            copied += 1;
            return;
          }
          await c.copy(dstKey, o.name);
          copied += 1;
        } catch (e) {
          failed += 1;
          if (errors.length < 8) errors.push(dstKey + ' :: ' + (e.message || e));
        }
      })
    )
  );
  const row = {
    ok: failed === 0,
    ...job,
    n: src.length,
    copied,
    skipped,
    failed,
    errors,
    go: DO,
  };
  log(row);
  return row;
}

(async () => {
  fs.writeFileSync(LOG, '');
  const c = client();
  const limit = pLimit(CONC);
  const rows = [];
  for (const job of JOBS) {
    process.stderr.write((DO ? 'GO ' : 'DRY ') + job.dir + ' ' + job.from + ' -> ' + job.to + '\n');
    const row = await copyJob(c, job, limit);
    rows.push(row);
    process.stderr.write(JSON.stringify({ dir: row.dir, n: row.n, copied: row.copied, skipped: row.skipped, failed: row.failed, ok: row.ok }) + '\n');
  }
  const summary = {
    go: DO,
    ok: rows.filter((r) => r.ok).length,
    fail: rows.filter((r) => !r.ok).length,
    copied: rows.reduce((s, r) => s + (r.copied || 0), 0),
    skipped: rows.reduce((s, r) => s + (r.skipped || 0), 0),
    failed: rows.reduce((s, r) => s + (r.failed || 0), 0),
  };
  console.log(JSON.stringify(summary));
  if (summary.fail) process.exit(1);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
