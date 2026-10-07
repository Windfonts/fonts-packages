#!/usr/bin/env node
/**
 * List Guangzhou pack layout for the 14 broken faces.
 * Additive read. Does not copy or delete.
 */
const fs = require('fs');
const path = require('path');
const OSS = require('ali-oss');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const OUT = path.join(__dirname, 'probe-14.json');

const PREFIXES = [
  'mkcjp',
  'mikachan',
  'kisjp',
  'kaiso',
  'kaiseiopti',
  'knkkjp',
  'kinkaku',
  'smsnjp',
  'samasan',
  'zhfy',
  'taigihuninn',
  'hcgh',
  'clg',
  'mystp3l',
  'dreamhanserif',
  'myhtp3l',
  'dreamhansans',
  'bestten',
  'lana-pixel',
  'lanapixel',
  'taipei-pixel',
  'taipeipixel',
  'fonsung',
  'lyusung',
  'chusung',
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

function summarize(prefix, objects) {
  const p = BASE + prefix + '/';
  const weights = {};
  const css = [];
  const other = [];
  for (const o of objects) {
    const rel = o.name.slice(p.length);
    const parts = rel.split('/');
    if (parts.length >= 3 && parts[2] === 'result.css') {
      const w = parts[0];
      const ver = parts[1];
      if (!weights[w]) weights[w] = { n: 0, bytes: 0, css: {} };
      weights[w].n += 1;
      weights[w].bytes += o.size;
      weights[w].css[ver] = o.size;
      css.push({ w, ver, size: o.size });
    } else if (parts.length >= 2 && parts[1] !== 'result.css') {
      const w = parts[0];
      if (!weights[w]) weights[w] = { n: 0, bytes: 0, css: {} };
      weights[w].n += 1;
      weights[w].bytes += o.size;
    } else {
      other.push({ rel, size: o.size });
    }
  }
  return {
    prefix,
    n: objects.length,
    bytes: objects.reduce((s, o) => s + o.size, 0),
    weights,
    css,
    other: other.slice(0, 40),
    other_n: other.length,
  };
}

async function versionsOf(c, key) {
  try {
    if (typeof c.getBucketVersions !== 'function' && typeof c.listObjectVersions !== 'function') {
      const r = await c.request({
        method: 'GET',
        query: { prefix: key, versions: '', 'max-keys': 50 },
        xmlResponse: true,
      });
      return { ok: true, rawType: typeof r, sample: JSON.stringify(r).slice(0, 500) };
    }
  } catch (e) {
    return { ok: false, err: e.message || String(e) };
  }
  try {
    const r = await c.getBucketVersions({ prefix: key, 'max-keys': 20 });
    return { ok: true, via: 'getBucketVersions', n: (r.objects || r.versions || []).length, objects: r };
  } catch (e) {
    return { ok: false, err: e.message || String(e) };
  }
}

(async () => {
  const c = client();
  const rows = [];
  for (const prefix of PREFIXES) {
    const objects = await listObjects(c, BASE + prefix + '/');
    rows.push(summarize(prefix, objects));
    process.stderr.write(prefix + ' n=' + objects.length + '\n');
  }
  const verKeys = [
    BASE + 'kaiso/Regular/full/result.css',
    BASE + 'kaiso/Medium/full/result.css',
    BASE + 'kaiso/Bold/full/result.css',
    BASE + 'kisjp/Regular/full/result.css',
    BASE + 'kisjp/Kaisotai-Next-UP-B/full/result.css',
  ];
  const versions = {};
  for (const k of verKeys) {
    versions[k] = await versionsOf(c, k);
  }
  const out = { rows, versions, at: new Date().toISOString() };
  fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
  console.log('wrote', OUT);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
