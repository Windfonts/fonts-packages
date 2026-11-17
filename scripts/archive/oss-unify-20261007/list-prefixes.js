#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const OSS = require('ali-oss');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const OUT = path.join(__dirname, 'oss-prefixes.json');

async function main() {
  const c = new OSS({
    accessKeyId: process.env.OSS_ACCESS_KEY_ID,
    accessKeySecret: process.env.OSS_ACCESS_KEY_SECRET,
    bucket: process.env.OSS_BUCKET,
    region: process.env.OSS_REGION,
    endpoint: process.env.OSS_ENDPOINT || undefined,
  });
  const prefs = [];
  let marker;
  do {
    const r = await c.list({ prefix: BASE, delimiter: '/', marker, 'max-keys': 1000 });
    for (const p of r.prefixes || []) prefs.push(p.slice(BASE.length).replace(/\/$/, ''));
    marker = r.nextMarker;
  } while (marker);
  const lower = prefs.map((p) => p.toLowerCase());
  const mixed = prefs.filter((p) => p !== p.toLowerCase());
  fs.writeFileSync(
    OUT,
    JSON.stringify(
      { n: prefs.length, mixed: mixed.length, prefixes: prefs.sort((a, b) => a.localeCompare(b)) },
      null,
      2
    ) + '\n'
  );
  console.log(JSON.stringify({ n: prefs.length, mixed: mixed.length, sample: prefs.slice(0, 8) }));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
