#!/usr/bin/env node
/**
 * Normalize fonts-packages/{Norm}/ to lowercase-only keys.
 *
 * - Merge mixed-case trees into {norm.lower()}/
 * - When both exist, keep the larger object; fill missing from other casings
 * - Delete non-lowercase prefixes after merge
 *
 * Usage:
 *   node scripts/normalize-pack-case.js              # dry-run report
 *   node scripts/normalize-pack-case.js --only=hcszt # dry-run one pack
 *   node scripts/normalize-pack-case.js --go         # execute all
 *   node scripts/normalize-pack-case.js --go --only=hcszt
 */

const fs = require('fs-extra');
const path = require('path');
const OSS = require('ali-oss');
const pLimit = require('p-limit');
require('dotenv').config();

const BASE = (process.env.OSS_BASE_PATH || 'fonts-packages/').replace(/\/?$/, '/');
const args = process.argv.slice(2);
const DO = args.includes('--go');
const MERGE_ONLY = args.includes('--merge-only'); // skip deletes (bucket ACL may deny delete)
const onlyArg = args.find((a) => a.startsWith('--only='));
const ONLY = onlyArg ? onlyArg.slice('--only='.length).toLowerCase() : '';

function client() {
  return new OSS({
    accessKeyId: process.env.OSS_ACCESS_KEY_ID,
    accessKeySecret: process.env.OSS_ACCESS_KEY_SECRET,
    bucket: process.env.OSS_BUCKET,
    region: process.env.OSS_REGION,
    endpoint: process.env.OSS_ENDPOINT,
  });
}

async function listPrefixes(c) {
  const prefs = [];
  let marker;
  do {
    const r = await c.list({ prefix: BASE, delimiter: '/', marker, 'max-keys': 1000 });
    for (const p of r.prefixes || []) prefs.push(p);
    marker = r.nextMarker;
  } while (marker);
  return prefs
    .map((p) => p.slice(BASE.length).replace(/\/$/, ''))
    .filter(Boolean);
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

async function headSize(c, name) {
  try {
    const h = await c.head(name);
    const n = Number(h.res && h.res.headers && h.res.headers['content-length']);
    return Number.isFinite(n) ? n : -1;
  } catch (e) {
    if (e && (e.status === 404 || e.code === 'NoSuchKey')) return -1;
    throw e;
  }
}

async function mergeGroup(c, lower, casings, limit) {
  const targetPrefix = BASE + lower + '/';
  const sources = casings.filter((x) => x !== lower);
  const stats = {
    lower,
    casings,
    copied: 0,
    skipped: 0,
    replaced: 0,
    deleted: 0,
    sourceObjects: 0,
    errors: [],
  };

  if (!sources.length) {
    stats.note = 'already-lowercase-only';
    return stats;
  }

  for (const src of sources) {
    const srcPrefix = BASE + src + '/';
    const objs = await listObjects(c, srcPrefix);
    stats.sourceObjects += objs.length;

    await Promise.all(
      objs.map((o) =>
        limit(async () => {
          const rel = o.name.slice(srcPrefix.length);
          const dest = targetPrefix + rel;
          try {
            const destSize = await headSize(c, dest);
            if (destSize < 0) {
              if (DO) await c.copy(dest, o.name);
              stats.copied += 1;
            } else if (o.size > destSize) {
              if (DO) await c.copy(dest, o.name);
              stats.replaced += 1;
            } else {
              stats.skipped += 1;
            }
          } catch (e) {
            stats.errors.push({ from: o.name, to: dest, err: String(e.message || e) });
          }
        })
      )
    );
  }

  // Delete mixed-case trees only after merge (optional; fonts-packages AK may lack delete)
  if (!MERGE_ONLY) {
    for (const src of sources) {
      const srcPrefix = BASE + src + '/';
      const objs = await listObjects(c, srcPrefix);
      await Promise.all(
        objs.map((o) =>
          limit(async () => {
            try {
              if (DO) await c.delete(o.name);
              stats.deleted += 1;
            } catch (e) {
              stats.errors.push({ delete: o.name, err: String(e.message || e) });
            }
          })
        )
      );
    }
  } else {
    stats.note = (stats.note ? stats.note + ';' : '') + 'merge-only-no-delete';
  }

  return stats;
}

async function main() {
  const c = client();
  const names = await listPrefixes(c);
  const by = {};
  for (const n of names) {
    const k = n.toLowerCase();
    (by[k] = by[k] || []).push(n);
  }

  let keys = Object.keys(by).sort();
  if (ONLY) keys = keys.filter((k) => k === ONLY);
  if (!keys.length) {
    console.error('no matching pack', ONLY || '(all)');
    process.exit(1);
  }

  const duals = keys.filter((k) => by[k].length > 1);
  const rename = keys.filter((k) => by[k].some((x) => x !== k));
  console.log(
    JSON.stringify(
      {
        mode: DO ? 'GO' : 'DRY-RUN',
        base: BASE,
        bucket: process.env.OSS_BUCKET,
        packs: keys.length,
        duals: duals.length,
        needMerge: rename.length,
        only: ONLY || null,
      },
      null,
      2
    )
  );

  const limit = pLimit(12);
  const report = [];
  let i = 0;
  for (const lower of rename) {
    i += 1;
    process.stderr.write(`[${i}/${rename.length}] ${lower} <- ${by[lower].join(',')}\n`);
    const st = await mergeGroup(c, lower, by[lower], limit);
    report.push(st);
    if (st.errors.length) {
      console.error('errors', lower, st.errors.slice(0, 3));
    }
  }

  const outDir = path.join(__dirname, '..', 'ossutil_output');
  await fs.ensureDir(outDir);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outPath = path.join(outDir, `normalize-pack-case-${DO ? 'go' : 'dry'}-${stamp}.json`);
  await fs.writeJson(
    outPath,
    {
      mode: DO ? 'GO' : 'DRY-RUN',
      generated: new Date().toISOString(),
      duals,
      summary: {
        packs: report.length,
        copied: report.reduce((a, r) => a + r.copied, 0),
        replaced: report.reduce((a, r) => a + r.replaced, 0),
        skipped: report.reduce((a, r) => a + r.skipped, 0),
        deleted: report.reduce((a, r) => a + r.deleted, 0),
        errors: report.reduce((a, r) => a + r.errors.length, 0),
      },
      report,
    },
    { spaces: 2 }
  );
  console.log('wrote', outPath);
  console.log(
    'summary',
    JSON.stringify(
      {
        packs: report.length,
        copied: report.reduce((a, r) => a + r.copied, 0),
        replaced: report.reduce((a, r) => a + r.replaced, 0),
        skipped: report.reduce((a, r) => a + r.skipped, 0),
        deleted: report.reduce((a, r) => a + r.deleted, 0),
        errors: report.reduce((a, r) => a + r.errors.length, 0),
      },
      null,
      2
    )
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
