#!/usr/bin/env node
/**
 * Server-side copy fonts-packages/{old}/ → fonts-packages/{new}/
 * Additive. Skip dest objects with the same size. Do not delete source.
 *
 *   node scripts/oss-unify-20261007/copy-packs.js              # dry-run wave1
 *   node scripts/oss-unify-20261007/copy-packs.js --go
 *   node scripts/oss-unify-20261007/copy-packs.js --go --only=xwbright
 *   node scripts/oss-unify-20261007/copy-packs.js --go --wave=2
 */
const fs = require('fs');
const path = require('path');
const OSS = require('ali-oss');
const pLimit = require('p-limit');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const args = process.argv.slice(2);
const DO = args.includes('--go');
const OVERWRITE = args.includes('--overwrite-mismatch');
const WAVE = (args.find((a) => a.startsWith('--wave=')) || '--wave=1').slice(7);
const onlyArg = args.find((a) => a.startsWith('--only='));
const ONLY = onlyArg
  ? onlyArg
      .slice('--only='.length)
      .toLowerCase()
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
  : [];
const CONC = Number((args.find((a) => a.startsWith('--conc=')) || '--conc=12').slice(7)) || 12;
const MAP = path.join(__dirname, 'map.json');
const logArg = args.find((a) => a.startsWith('--log='));
const LOG = path.join(__dirname, logArg ? logArg.slice('--log='.length) : `copy-wave${WAVE}.jsonl`);

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

async function copyOne(c, rec, limit) {
  const srcPrefix = BASE + rec.old + '/';
  const dstPrefix = BASE + rec.new + '/';
  const src = await listObjects(c, srcPrefix);
  if (!src.length) {
    const row = { ok: false, skip: 'empty-src', id: rec.id, name: rec.name, old: rec.old, new: rec.new, n: 0 };
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
          if (have >= 0 && have !== o.size && !OVERWRITE) {
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
    id: rec.id,
    name: rec.name,
    old: rec.old,
    new: rec.new,
    src: src.length,
    copied,
    skipped,
    failed,
    errors,
    dry: !DO,
  };
  log(row);
  return row;
}

async function main() {
  const map = JSON.parse(fs.readFileSync(MAP, 'utf8'));
  const key = WAVE === '2' ? 'wave2_copies' : 'wave1_copies';
  let list = map[key] || [];
  if (ONLY.length) list = list.filter((x) => ONLY.includes(x.old) || ONLY.includes(x.new));
  const c = client();
  const limit = pLimit(CONC);
  console.log(
    JSON.stringify({
      wave: WAVE,
      do: DO,
      n: list.length,
      bucket: process.env.OSS_BUCKET,
      base: BASE,
      conc: CONC,
      only: ONLY.length ? ONLY : null,
      overwrite: OVERWRITE,
    })
  );
  let empty = 0;
  let fail = 0;
  let ok = 0;
  for (let i = 0; i < list.length; i++) {
    const rec = list[i];
    const t0 = Date.now();
    const row = await copyOne(c, rec, limit);
    const ms = Date.now() - t0;
    if (row.skip === 'empty-src') empty += 1;
    else if (!row.ok) fail += 1;
    else ok += 1;
    console.log(
      `${i + 1}/${list.length} ${row.old} -> ${row.new} src=${row.src || 0} copied=${row.copied || 0} skip=${row.skipped || 0} fail=${row.failed || 0} ${ms}ms ${row.skip || ''}`
    );
  }
  console.log(JSON.stringify({ done: true, ok, empty, fail, wave: WAVE, do: DO }));
  if (fail) process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
