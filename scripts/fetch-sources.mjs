#!/usr/bin/env node
// 从 CDN 拉取字体源文件到 fonts/{norm}/（source/ 目录）。
// 铁律：禁止用 OSS AK/SK 直接读桶（零公网出网，集群记忆 #9290/#11584）。
// 只走 https://cn.windfonts.com —— CyberCDN 边缘缓存 + origin shield 回源。
// 用法:
//   node scripts/fetch-sources.mjs <norm> [norm...]
//   node scripts/fetch-sources.mjs --file /tmp/norms.txt
const https = require('https');
const fs = require('fs');
const path = require('path');

const CDN = 'https://cn.windfonts.com';
const ROOT = path.join(__dirname, '..', 'fonts');
const CONC = 6;

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { timeout: 60000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return resolve(get(res.headers.location));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} ${url}`));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('timeout', function () { this.destroy(new Error('timeout')); })
      .on('error', reject);
  });
}

async function fetchOne(norm) {
  const dir = path.join(ROOT, norm);
  fs.mkdirSync(dir, { recursive: true });
  const idxBuf = await get(`${CDN}/fonts-packages/${norm}/source/index.json`);
  const meta = JSON.parse(idxBuf.toString());
  let n = 0;
  for (const item of meta.items || []) {
    const fname = item.file;
    if (!fname || fname.includes('..') || fname.includes('/')) continue;
    const dest = path.join(dir, fname);
    if (fs.existsSync(dest) && fs.statSync(dest).size > 0) continue;
    const buf = await get(`${CDN}/fonts-packages/${norm}/source/${fname}`);
    fs.writeFileSync(dest, buf);
    n++;
  }
  return n;
}

(async () => {
  let norms = process.argv.slice(2).filter((a) => !a.startsWith('--'));
  const fileArg = process.argv.indexOf('--file');
  if (fileArg >= 0 && process.argv[fileArg + 1]) {
    norms = fs.readFileSync(process.argv[fileArg + 1], 'utf8')
      .split(/\s+/).map((s) => s.trim().toLowerCase()).filter(Boolean);
  }
  if (!norms.length) {
    console.error('用法: node scripts/fetch-sources.mjs <norm>... | --file list.txt');
    process.exit(1);
  }
  let idx = 0, ok = 0, fail = 0;
  async function worker() {
    while (idx < norms.length) {
      const n = norms[idx++];
      try { await fetchOne(n); ok++; }
      catch (e) { fail++; console.error('FAIL', n, e.message.slice(0, 100)); }
      if ((ok + fail) % 25 === 0) console.error(`progress ${ok + fail}/${norms.length} ok=${ok} fail=${fail}`);
    }
  }
  await Promise.all(Array.from({ length: CONC }, worker));
  console.error(`DONE ok=${ok} fail=${fail}`);
})();
