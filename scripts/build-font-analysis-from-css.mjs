#!/usr/bin/env node
/**
 * 从 CDN 预计算 CSS 的 unicode-range 重建 metadata/font-analysis.json。
 * 不依赖本地 TTF；覆盖「有包无 analysis」的缺口。
 *
 * 用法（在 fonts-packages 根目录）：
 *   node scripts/build-font-analysis-from-css.mjs
 *   OSS_UPLOAD_DIRS=./metadata node scripts/upload.js
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const FRONT = join(ROOT, '..', 'fonts-front');
const OUT = join(ROOT, 'metadata', 'font-analysis.json');
const CDN = process.env.WF_CDN_ORIGIN || 'https://cn.windfonts.com';
const CONCURRENCY = Number(process.env.WF_ANALYSIS_CONCURRENCY || 10);
const WEIGHT_CANDIDATES = ['Regular', 'Normal', 'Medium', 'Book', 'Text', 'Light', 'Bold'];
const SUBSET = 'full';

const fonts = JSON.parse(readFileSync(join(FRONT, 'data', 'fonts.json'), 'utf8'));

function parseRanges(css) {
  const cps = new Set();
  const re = /unicode-range\s*:\s*([^;}{]+)/gi;
  let m;
  while ((m = re.exec(css))) {
    for (const part of m[1].split(',')) {
      const t = part.trim();
      const hit = /^U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?$/i.exec(t);
      if (!hit) continue;
      const a = parseInt(hit[1], 16);
      const b = hit[2] ? parseInt(hit[2], 16) : a;
      if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) continue;
      const end = Math.min(b, a + 50000); // 防异常超大区间
      for (let c = a; c <= end; c++) cps.add(c);
    }
  }
  return cps;
}

function bucketRanges(cps) {
  const buckets = {
    'CJK Unified Ideographs': 0,
    'CJK Compatibility': 0,
    Latin: 0,
    'CJK Symbols': 0,
    Other: 0,
  };
  for (const cp of cps) {
    if (cp >= 0x4e00 && cp <= 0x9fff) buckets['CJK Unified Ideographs']++;
    else if (cp >= 0xf900 && cp <= 0xfaff) buckets['CJK Compatibility']++;
    else if ((cp >= 0x0000 && cp <= 0x024f) || (cp >= 0x1e00 && cp <= 0x1eff)) buckets.Latin++;
    else if (cp >= 0x3000 && cp <= 0x303f) buckets['CJK Symbols']++;
    else buckets.Other++;
  }
  for (const k of Object.keys(buckets)) {
    if (!buckets[k]) delete buckets[k];
  }
  return buckets;
}

function sampleChars(cps, limit = 400) {
  const cjk = [...cps].filter((c) => c >= 0x4e00 && c <= 0x9fff).sort((a, b) => a - b);
  const pick = cjk.length ? cjk : [...cps].sort((a, b) => a - b);
  let out = '';
  for (const cp of pick) {
    if (out.length >= limit) break;
    try {
      out += String.fromCodePoint(cp);
    } catch {
      /* ignore */
    }
  }
  return out;
}

async function fetchCss(normalized, weight) {
  const url = `${CDN}/fonts-packages/${encodeURIComponent(normalized)}/${encodeURIComponent(weight)}/${SUBSET}/result.css`;
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) return null;
  const css = await res.text();
  if (!/unicode-range/i.test(css)) return null;
  return { weight, css, bytes: Buffer.byteLength(css, 'utf8') };
}

async function analyzeOne(font) {
  const normalized = String(font.normalized || '').trim();
  if (!normalized) return null;
  const weights = Array.isArray(font.weights) && font.weights.length
    ? [...new Set([...font.weights, ...WEIGHT_CANDIDATES])]
    : WEIGHT_CANDIDATES;
  for (const w of weights) {
    try {
      const hit = await fetchCss(normalized, w);
      if (!hit) continue;
      const cps = parseRanges(hit.css);
      if (!cps.size) continue;
      return {
        name: normalized,
        children: [
          {
            name: hit.weight,
            char_count: cps.size,
            glyph_count: cps.size,
            unicode_ranges: bucketRanges(cps),
            characters: sampleChars(cps),
            subfamily_name: hit.weight,
            full_name: String(font.name || normalized),
            source: 'css-unicode-range',
            css_bytes: hit.bytes,
            subset: SUBSET,
          },
        ],
      };
    } catch {
      /* try next weight */
    }
  }
  return null;
}

async function mapPool(items, limit, fn) {
  const out = new Array(items.length);
  let i = 0;
  async function worker() {
    while (i < items.length) {
      const idx = i++;
      out[idx] = await fn(items[idx], idx);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, () => worker()));
  return out;
}

const unique = [];
const seen = new Set();
for (const f of fonts) {
  const n = String(f.normalized || '').trim();
  if (!n || seen.has(n)) continue;
  seen.add(n);
  unique.push(f);
}

console.error('fonts', unique.length, 'concurrency', CONCURRENCY);
const rows = await mapPool(unique, CONCURRENCY, async (font, idx) => {
  const row = await analyzeOne(font);
  if ((idx + 1) % 25 === 0 || idx === unique.length - 1) {
    console.error(`… ${idx + 1}/${unique.length}`);
  }
  return row;
});

const fontsOut = rows.filter(Boolean);
const summary = {
  total_fonts: fontsOut.length,
  total_font_families: fontsOut.length,
  total_standalone_fonts: 0,
  total_weights: fontsOut.reduce((n, f) => n + (f.children?.length || 0), 0),
  generated_at: new Date().toISOString(),
  source: 'css-unicode-range',
  subset: SUBSET,
  catalog_normalized: unique.length,
  coverage_ratio: unique.length ? Number((fontsOut.length / unique.length).toFixed(4)) : 0,
};

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, JSON.stringify({ summary, fonts: fontsOut }, null, 2) + '\n');
console.error('wrote', OUT, 'hit', fontsOut.length, '/', unique.length, 'ratio', summary.coverage_ratio);
