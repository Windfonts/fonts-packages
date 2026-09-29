#!/usr/bin/env node
/**
 * Upload only staging/preview-shop-oss/{Norm}/{Weight}/preview-shop/*
 * to oss://wenfeng-fonts/fonts-packages/{Norm}/{Weight}/preview-shop/
 *
 * Does not touch metadata or full/zh packages.
 *   node scripts/upload-preview-shop.js           # dry-run
 *   node scripts/upload-preview-shop.js --apply
 */
const fs = require('fs-extra');
const path = require('path');
const OSS = require('ali-oss');
const { glob } = require('glob');
const pLimit = require('p-limit');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const APPLY = process.argv.includes('--apply');
const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'staging', 'preview-shop-oss');
const PREFIX = process.env.OSS_BASE_PATH || 'fonts-packages/';

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  return {
    '.woff2': 'font/woff2',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
  }[ext] || 'application/octet-stream';
}

async function main() {
  const missing = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET', 'OSS_BUCKET', 'OSS_REGION']
    .filter((k) => !process.env[k]);
  if (missing.length) {
    console.error('missing env', missing.join(','));
    process.exit(2);
  }
  const files = (await glob(path.join(SRC, '**', '*'), { nodir: true }))
    .filter((f) => ['.woff2', '.css'].includes(path.extname(f).toLowerCase()))
    .filter((f) => !path.basename(f).startsWith('_'));
  console.log(`src=${SRC} files=${files.length} apply=${APPLY} bucket=${process.env.OSS_BUCKET} prefix=${PREFIX}`);
  if (!files.length) {
    console.error('no files');
    process.exit(1);
  }
  if (!APPLY) {
    files.slice(0, 8).forEach((f) => {
      const rel = path.relative(SRC, f).split(path.sep).join('/');
      console.log(`[dry] ${rel} -> ${PREFIX}${rel}`);
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
    const rel = path.relative(SRC, localPath).split(path.sep).join('/');
    const remote = PREFIX.replace(/\/?$/, '/') + rel;
    try {
      await client.put(remote, localPath, {
        headers: {
          'Cache-Control': 'public, max-age=86400',
          'Content-Type': contentType(localPath),
        },
      });
      ok += 1;
      if (ok % 25 === 0) console.log(`uploaded ${ok}/${files.length}`);
    } catch (e) {
      fail += 1;
      console.error('FAIL', remote, e.message);
    }
  })));
  console.log(`done ok=${ok} fail=${fail}`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
