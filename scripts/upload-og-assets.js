#!/usr/bin/env node
/**
 * Upload OG batch assets (webp + yong svg) to oss://wenfeng-fonts.
 *
 * Source: work/wpfonts-og-batch-20161118/{norm}/*.webp|yong*.svg
 * Target: fonts-packages/{norm}/og/{file}
 *
 *   node scripts/upload-og-assets.js                     # dry-run
 *   node scripts/upload-og-assets.js --apply             # upload
 *   node scripts/upload-og-assets.js --apply --only 975yt,symcb
 */
const fs = require('fs-extra');
const path = require('path');
const OSS = require('ali-oss');
const { glob } = require('glob');
const pLimit = require('p-limit');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const APPLY = process.argv.includes('--apply');
const ONLY = (() => {
  const i = process.argv.indexOf('--only');
  return i >= 0 ? new Set(process.argv[i + 1].split(',')) : null;
})();
const SRC = process.argv.includes('--src')
  ? path.resolve(process.argv[process.argv.indexOf('--src') + 1])
  : '/Users/feibisi-studio/office/modiqi/work/wpfonts-og-batch-20261118';
const PREFIX = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  return {
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.png': 'image/png',
  }[ext] || 'application/octet-stream';
}

async function main() {
  const missing = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET', 'OSS_BUCKET', 'OSS_REGION']
    .filter((k) => !process.env[k]);
  if (missing.length) {
    console.error('missing env', missing.join(','));
    process.exit(2);
  }
  const files = (await glob(path.join(SRC, '*', '*.{webp,svg}'), { nodir: true, nocase: true }))
    .filter((f) => {
      const norm = path.basename(path.dirname(f));
      return !ONLY || ONLY.has(norm);
    });
  console.log(`src=${SRC} files=${files.length} apply=${APPLY} bucket=${process.env.OSS_BUCKET}`);
  if (!files.length) {
    console.error('no files');
    process.exit(1);
  }
  if (!APPLY) {
    files.slice(0, 8).forEach((f) => {
      const norm = path.basename(path.dirname(f));
      const rel = path.relative(SRC, f).split(path.sep).join('/');
      console.log(`[dry] ${rel} -> ${PREFIX}${norm}/og/${path.basename(f)}`);
    });
    console.log(`dry-run ${files.length} files; pass --apply to upload`);
    return;
  }
  const client = new OSS({
    accessKeyId: process.env.OSS_ACCESS_KEY_ID,
    accessKeySecret: process.env.OSS_ACCESS_KEY_SECRET,
    bucket: process.env.OSS_BUCKET,
    region: process.env.OSS_REGION,
    endpoint: process.env.OSS_ENDPOINT,
  });
  const limit = pLimit(8);
  let ok = 0;
  let fail = 0;
  await Promise.all(files.map((localPath) => limit(async () => {
    const norm = path.basename(path.dirname(localPath));
    const remote = `${PREFIX}${norm}/og/${path.basename(localPath)}`;
    try {
      await client.put(remote, localPath, {
        headers: {
          'Cache-Control': 'public, max-age=86400',
          'Content-Type': contentType(localPath),
        },
      });
      ok += 1;
      if (ok % 100 === 0) console.log(`uploaded ${ok}/${files.length}`);
    } catch (e) {
      fail += 1;
      console.error('FAIL', remote, e.message);
    }
  })));
  console.log(`done ok=${ok} fail=${fail}`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
