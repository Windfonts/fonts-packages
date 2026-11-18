#!/usr/bin/env node
/**
 * factory-agent — fonts-packages 流水线的 Web 化执行端。
 *
 * 职责：
 *   1. scan：扫描 fonts//fonts-subset//dist//metadata + CDN HEAD，生成家族六阶段状态快照
 *   2. report：把快照 POST 到 vault /api/factory/agent/report
 *   3. poll：轮询 /api/factory/agent/jobs 认领任务 → 本地执行 → 回传进度/结果
 *
 * 用法：
 *   node scripts/factory-agent.js scan [--print]     # 只扫描，--print 输出 JSON 不上传
 *   node scripts/factory-agent.js report [--print]   # 扫描并上报（默认行为同 scan+post）
 *   node scripts/factory-agent.js poll               # 守护：定时上报 + 轮询任务

 *
 * env（.env 或环境变量）：
 *   FACTORY_VAULT_URL       默认 https://vault.windfonts.com
 *   FACTORY_AGENT_TOKEN     必需（与 vault .env.production 一致），缺省只允许 --print
 *   FACTORY_AGENT_NAME      默认 os.hostname()
 *   FACTORY_POLL_INTERVAL   任务轮询秒数，默认 20
 *   FACTORY_REPORT_INTERVAL 状态上报秒数，默认 600
 *   FACTORY_CDN_BASE        默认 https://cn.windfonts.com（uploaded HEAD 检查）
 */

const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');
require('dotenv').config();

const ROOT = path.resolve(__dirname, '..');
const FONTS_DIR = path.join(ROOT, 'fonts');
const SUBSET_DIR = path.join(ROOT, 'fonts-subset');
const DIST_DIR = path.join(ROOT, 'dist');
const META_DIR = path.join(ROOT, 'metadata');
const PARK_DIR = path.join(ROOT, '_factory_park');
const LOCK_FILE = path.join(os.tmpdir(), `factory-agent-${os.hostname()}.lock`);

const VAULT_URL = (process.env.FACTORY_VAULT_URL || 'https://vault.windfonts.com').replace(/\/+$/, '');
const AGENT_TOKEN = process.env.FACTORY_AGENT_TOKEN || '';
const AGENT_NAME = (process.env.FACTORY_AGENT_NAME || os.hostname()).slice(0, 120);
const POLL_INTERVAL = Math.max(5, parseInt(process.env.FACTORY_POLL_INTERVAL || '20', 10)) * 1000;
const REPORT_INTERVAL = Math.max(30, parseInt(process.env.FACTORY_REPORT_INTERVAL || '600', 10)) * 1000;
const CDN_BASE = (process.env.FACTORY_CDN_BASE || 'https://cn.windfonts.com').replace(/\/+$/, '');
const FONT_EXT = /\.(ttf|otf|woff2?)$/i;
const VERSIONS = ['full', 'en', 'zh', 'zh-common'];

const log = (...a) => console.error(`[factory-agent ${new Date().toISOString()}]`, ...a);
const die = (msg, code = 1) => { console.error(msg); process.exit(code); };

// ---------- 小工具 ----------

async function readJsonSafe(p) {
  try { return JSON.parse(await fsp.readFile(p, 'utf8')); } catch { return null; }
}

async function listDirSafe(p) {
  try { return await fsp.readdir(p, { withFileTypes: true }); } catch { return []; }
}

function isFontFile(name) { return FONT_EXT.test(name); }

/** fonts/ 下家族目录 → { dirName, lower }（lower 即 OSS/normalized 目录名） */
async function scanFamilies() {
  const entries = await listDirSafe(FONTS_DIR);
  const families = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const dirName = e.name;
    const weights = {};
    const files = await fsp.readdir(path.join(FONTS_DIR, dirName)).catch(() => []);
    for (const f of files) {
      if (!isFontFile(f)) continue;
      const weight = f.replace(FONT_EXT, '');
      weights[weight] = { source: true, versions: {} };
    }
    if (Object.keys(weights).length === 0) continue;
    families.push({ dirName, norm: dirName.toLowerCase(), weights });
  }
  return families;
}

/** fonts-subset/{Norm}/{Weight}/{ver}.ttf 存在性 */
async function scanSubsets(families) {
  const byLower = new Map(families.map((f) => [f.norm, f]));
  const entries = await listDirSafe(SUBSET_DIR);
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const fam = byLower.get(e.name.toLowerCase());
    if (!fam) continue;
    for (const w of await listDirSafe(path.join(SUBSET_DIR, e.name))) {
      if (!w.isDirectory()) continue;
      const weight = w.name;
      if (!fam.weights[weight]) fam.weights[weight] = { source: false, versions: {} };
      const wstate = fam.weights[weight];
      for (const v of await listDirSafe(path.join(SUBSET_DIR, e.name, w.name))) {
        if (!v.isFile() || !FONT_EXT.test(v.name)) continue;
        // 文件名形如 {Weight}-{ver}.ttf，version 取 weight 前缀之后的部分
        const stem = v.name.replace(FONT_EXT, '');
        const prefix = `${weight}-`;
        const ver = stem.startsWith(prefix) ? stem.slice(prefix.length) : stem;
        if (VERSIONS.includes(ver)) {
          wstate.versions[ver] = wstate.versions[ver] || { subset: false, converted: false, uploaded: false };
          wstate.versions[ver].subset = true;
        }
      }
    }
  }
  return families;
}

/** dist/{Norm}/{Weight}/{ver}/result.css 存在性 */
async function scanConverted(families) {
  const byLower = new Map(families.map((f) => [f.norm, f]));
  const entries = await listDirSafe(DIST_DIR);
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const fam = byLower.get(e.name.toLowerCase());
    if (!fam) continue;
    for (const w of await listDirSafe(path.join(DIST_DIR, e.name))) {
      if (!w.isDirectory()) continue;
      const weight = w.name;
      if (!fam.weights[weight]) fam.weights[weight] = { source: false, versions: {} };
      const wstate = fam.weights[weight];
      for (const v of await listDirSafe(path.join(DIST_DIR, e.name, w.name))) {
        if (!v.isDirectory()) continue;
        const ver = v.name;
        const hasCss = await fsp
          .access(path.join(DIST_DIR, e.name, w.name, ver, 'result.css'))
          .then(() => true)
          .catch(() => false);
        if (hasCss) {
          wstate.versions[ver] = wstate.versions[ver] || { subset: false, converted: false, uploaded: false };
          wstate.versions[ver].converted = true;
        }
      }
    }
  }
  return families;
}

/**
 * subset 证据修正：convert.js 成功后会删除整个 fonts-subset/，
 * 因此 subset 文件只在 subset→convert 之间存在。
 * 已 converted/uploaded 的版本必然已经走过子集化（或被有意跳过），
 * 统一标记 subset=true，避免状态台把已完成家族误报为「待子集」。
 */
function settleSubsetEvidence(families) {
  for (const fam of families) {
    for (const w of Object.values(fam.weights)) {
      for (const v of Object.values(w.versions || {})) {
        if (v.converted || v.uploaded) v.subset = true;
      }
    }
  }
  return families;
}

/**
 * CDN HEAD 检查 uploaded。
 * 对每个家族×字重检查 VERSIONS ∪ 本地已发现版本 的 result.css——
 * uploaded 的真源是 CDN 本身，不依赖本地 dist 是否还在
 * （dist 是可再生产物，清理后不应让已发布家族显示未上传）。
 */
async function headOk(url, timeoutMs = 8000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { method: 'HEAD', signal: ctrl.signal, redirect: 'follow' });
    return res.status === 200;
  } catch {
    return false;
  } finally {
    clearTimeout(t);
  }
}

async function scanUploaded(families, { onlyNorms } = {}) {
  const want = onlyNorms ? new Set(onlyNorms.map((n) => n.toLowerCase())) : null;
  const tasks = [];
  for (const fam of families) {
    if (want && !want.has(fam.norm)) continue;
    for (const [weight, wstate] of Object.entries(fam.weights)) {
      const vers = new Set([...VERSIONS, ...Object.keys(wstate.versions || {})]);
      for (const ver of vers) {
        const url = `${CDN_BASE}/fonts-packages/${fam.norm}/${weight}/${ver}/result.css`;
        tasks.push({ fam, weight, ver, url });
      }
    }
  }
  const CONCURRENCY = 12;
  let idx = 0, done = 0;
  async function worker() {
    while (idx < tasks.length) {
      const t = tasks[idx++];
      const ok = await headOk(t.url);
      if (ok) {
        const wstate = t.fam.weights[t.weight];
        wstate.versions[t.ver] = wstate.versions[t.ver] || { subset: false, converted: false, uploaded: false };
        wstate.versions[t.ver].uploaded = true;
      }
      if (++done % 100 === 0) log(`  HEAD ${done}/${tasks.length}`);
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));
  return families;
}

/** 上报给 vault 的元数据白名单（与 vault factory.service FONT_META_* 对齐） */
const META_KEYS = [
  'chinese_name', 'english_name', 'designer', 'foundry', 'release_year',
  'category', 'font_category', 'style', 'copyright', 'license', 'license_type',
  'version', 'description', 'tags', 'font_tags', 'languages', 'use_cases',
];

function pickMeta(m) {
  const out = {};
  for (const k of META_KEYS) {
    const v = m[k];
    if (v === null || v === undefined) continue;
    if (Array.isArray(v)) {
      if (v.length) out[k] = v.slice(0, 50).map((x) => String(x).slice(0, 60));
      continue;
    }
    const str = String(v).trim();
    if (!str || str === 'null' || str === '{}') continue;
    out[k] = str.slice(0, 2000);
  }
  return Object.keys(out).length ? out : undefined;
}

/** metadata/font-mapping.json → analyzed + displayName + meta */
async function applyMapping(families) {
  const mapping = await readJsonSafe(path.join(META_DIR, 'font-mapping.json'));
  if (!mapping || typeof mapping !== 'object') return families;
  const byNorm = new Map(families.map((f) => [f.norm, f]));
  // mapping 顶层 key 是目录名（可能大小写混写），统一小写比对
  const lowerMap = new Map();
  for (const [k, v] of Object.entries(mapping)) lowerMap.set(String(k).toLowerCase(), v);
  for (const fam of families) {
    const m = lowerMap.get(fam.norm) || lowerMap.get(fam.dirName.toLowerCase());
    if (m) {
      fam.analyzed = true;
      fam.name =
        (m.chinese_name && m.chinese_name !== 'null' ? m.chinese_name : null) ||
        (m.english_name && m.english_name !== 'null' ? m.english_name : null) ||
        (m.original_name && String(m.original_name) !== 'null' ? m.original_name : null) ||
        fam.norm;
      fam.meta = pickMeta(m);
    } else {
      fam.name = fam.norm;
    }
  }
  return families;
}

/** 完整扫描 → 上报 payload */
async function scan({ skipHead = false, onlyNorms } = {}) {
  let families = await scanFamilies();
  families = await scanSubsets(families);
  families = await scanConverted(families);
  if (!skipHead) await scanUploaded(families, { onlyNorms });
  settleSubsetEvidence(families);
  await applyMapping(families);

  return {
    agent: AGENT_NAME,
    generatedAt: new Date().toISOString(),
    families: families.map((f) => ({
      norm: f.norm,
      name: f.name || f.norm,
      analyzed: !!f.analyzed,
      ...(f.meta ? { meta: f.meta } : {}),
      weights: f.weights,
    })),
  };
}

// ---------- vault API ----------

async function api(pathname, { method = 'GET', body, timeoutMs = 30000 } = {}) {
  if (!AGENT_TOKEN) throw new Error('FACTORY_AGENT_TOKEN 未配置');
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${VAULT_URL}${pathname}`, {
      method,
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${AGENT_TOKEN}`,
        'x-factory-agent': AGENT_NAME,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: ctrl.signal,
    });
    const json = await res.json().catch(() => null);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${json?.message || res.statusText}`);
    return json;
  } finally {
    clearTimeout(t);
  }
}

async function report(payload) {
  if (!AGENT_TOKEN) {
    log('FACTORY_AGENT_TOKEN 未配置，仅打印不上传（--print 模式）');
    return { dry: true };
  }
  const res = await api('/api/factory/agent/report', { method: 'POST', body: payload });
  log(`上报完成: ${res?.data?.upserted ?? '?'} 个家族`);
  return res?.data;
}

// ---------- park（家族级工作区隔离） ----------

/** 把 fonts/ fonts-subset/ dist/ 下不在 keepNorms 的家族目录挪进 _factory_park/，返回 restore() */
async function parkOthers(keepNorms) {
  const keep = new Set((keepNorms || []).map((n) => String(n).toLowerCase()));
  const parked = [];
  async function parkTree(root) {
    for (const e of await listDirSafe(root)) {
      if (!e.isDirectory()) continue;
      if (keep.has(e.name.toLowerCase())) continue;
      const dest = path.join(PARK_DIR, path.relative(ROOT, root), e.name);
      await fsp.mkdir(path.dirname(dest), { recursive: true });
      await fsp.rename(path.join(root, e.name), dest);
      parked.push({ src: path.join(root, e.name), dest });
    }
  }
  await fsp.mkdir(PARK_DIR, { recursive: true });
  await parkTree(FONTS_DIR);
  await parkTree(SUBSET_DIR);
  await parkTree(DIST_DIR);
  if (parked.length) log(`park: 隔离 ${parked.length} 个非目标目录`);
  return async () => {
    for (const { src, dest } of parked) {
      await fsp.mkdir(path.dirname(src), { recursive: true });
      // 目标位若已有同名（理论上不该有），先让位
      if (await fsp.access(src).then(() => true).catch(() => false)) {
        const alt = `${src}.agent-conflict-${Date.now()}`;
        await fsp.rename(src, alt);
        await fsp.rename(dest, src);
        await fsp.rename(alt, `${src}.conflict-kept`);
      } else {
        await fsp.rename(dest, src);
      }
    }
    if (parked.length) log(`unpark: 还原 ${parked.length} 个目录`);
    // 清掉空的 park 骨架
    await fsp.rm(PARK_DIR, { recursive: true, force: true }).catch(() => {});
  };
}

// ---------- 任务执行 ----------

function runCmd(cmd, args, { env = {}, timeoutMs = 0, onTail } = {}) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, {
      cwd: ROOT,
      env: { ...process.env, ...env },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '', stderr = '';
    const tail = [];
    const push = (chunk, isErr) => {
      const s = chunk.toString();
      if (isErr) stderr += s; else stdout += s;
      for (const line of s.split('\n')) {
        if (line.trim()) {
          tail.push(line.slice(0, 300));
          if (tail.length > 60) tail.shift();
        }
      }
      if (onTail) onTail(tail.slice(-30).join('\n'));
    };
    child.stdout.on('data', (d) => push(d, false));
    child.stderr.on('data', (d) => push(d, true));
    const timer = timeoutMs ? setTimeout(() => child.kill('SIGKILL'), timeoutMs) : null;
    child.on('close', (code) => {
      if (timer) clearTimeout(timer);
      resolve({ code: code ?? -1, stdout, stderr, tail: tail.slice(-40).join('\n') });
    });
    child.on('error', (err) => {
      if (timer) clearTimeout(timer);
      resolve({ code: -1, stdout, stderr: stderr + String(err), tail: tail.join('\n') });
    });
  });
}

/** norm → 实际目录名（大小写不敏感解析） */
async function resolveDirName(base, norm) {
  const entries = await listDirSafe(base);
  const lower = norm.toLowerCase();
  const hit = entries.find((e) => e.isDirectory() && e.name.toLowerCase() === lower);
  return hit ? hit.name : null;
}

async function execJob(job, onProgress) {
  const params = (() => { try { return JSON.parse(job.paramsJson || '{}'); } catch { return {}; } })();
  const type = job.type;
  const families = Array.isArray(params.families) ? params.families.map((f) => String(f).toLowerCase()) : [];
  const results = { type, params, steps: [] };
  let liveTail = '';
  const onTail = (t) => { liveTail = t; };

  const progress = async (stage, extra = {}) => {
    results.steps.push({ stage, at: new Date().toISOString(), ...extra });
    await onProgress(stage, liveTail || undefined);
  };

  // verify：不跑流水线，agent 直接核对 dist↔CDN
  if (type === 'verify') {
    await progress('扫描 dist 版本');
    const fams = await scanFamilies();
    await scanSubsets(fams);
    await scanConverted(fams);
    const targets = families.length ? fams.filter((f) => families.includes(f.norm)) : fams;
    await progress(`HEAD 检查 ${targets.length} 家族`);
    await scanUploaded(targets, {});
    settleSubsetEvidence(targets);
    await applyMapping(targets);
    const missing = [];
    let checked = 0;
    for (const f of targets) {
      for (const [w, ws] of Object.entries(f.weights)) {
        for (const [v, vs] of Object.entries(ws.versions || {})) {
          if (!vs.converted) continue;
          checked++;
          if (!vs.uploaded) missing.push(`${f.norm}/${w}/${v}`);
        }
      }
    }
    results.verify = { checked, missing };
    await report({
      agent: AGENT_NAME,
      generatedAt: new Date().toISOString(),
      families: targets.map((f) => ({
        norm: f.norm, name: f.name || f.norm, analyzed: !!f.analyzed,
        ...(f.meta ? { meta: f.meta } : {}), weights: f.weights,
      })),
    }).catch(() => {});
    return { ok: true, result: results };
  }

  // inspect：单字体 name 表 + AI normalize 试跑
  if (type === 'inspect') {
    const fam = String(params.families?.[0] || params.family || '').toLowerCase();
    const weight = String(params.weight || '');
    if (!fam || !weight) return { ok: false, error: 'inspect 需要 params.families[0] + params.weight' };
    const dirName = await resolveDirName(FONTS_DIR, fam);
    if (!dirName) return { ok: false, error: `fonts/ 下找不到家族 ${fam}` };
    const file = (await fsp.readdir(path.join(FONTS_DIR, dirName)))
      .find((f) => isFontFile(f) && f.replace(FONT_EXT, '') === weight);
    if (!file) return { ok: false, error: `找不到字重文件 ${weight}.*` };
    const rel = path.join('fonts', dirName, file);
    await progress(`inspect ${rel}`);
    const r = await runCmd('python3', ['python-scripts/analyze-fonts.py', 'inspect', rel], { timeoutMs: 120000 });
    results.inspect = { exitCode: r.code, tail: r.tail };
    return { ok: r.code === 0, error: r.code === 0 ? undefined : `exit ${r.code}: ${r.tail.slice(-500)}`, result: results };
  }

  // analyze / subset / convert / upload：park 非目标家族后跑整脚本
  const keep = families; // 空 = 全量，不 park
  const park = keep.length ? await parkOthers(keep) : async () => {};
  try {
    if (type === 'analyze') {
      const env = {};
      if (params.subsetOnly) env.SUBSET_ONLY = params.subsetOnly;
      await progress(`analyze${keep.length ? ` (${keep.length} 家族)` : ' 全量'}`);
      const r = await runCmd('python3', ['python-scripts/analyze-fonts.py'], { env, onTail });
      results.analyze = { exitCode: r.code, tail: r.tail };
      return finishWithReport(r, results, { ok: r.code === 0 });
    }
    if (type === 'subset') {
      const env = {};
      if (params.subsetOnly) env.SUBSET_ONLY = params.subsetOnly;
      await progress(`subset${keep.length ? ` (${keep.length} 家族)` : ' 全量'}`);
      const r = await runCmd('python3', ['python-scripts/create-font-subsets.py'], { env, onTail });
      results.subset = { exitCode: r.code, tail: r.tail };
      return finishWithReport(r, results, { ok: r.code === 0 });
    }
    if (type === 'convert') {
      await progress(`convert${keep.length ? ` (${keep.length} 家族)` : ' 全量'}`);
      const r = await runCmd('node', ['scripts/convert.js'], { onTail });
      results.convert = { exitCode: r.code, tail: r.tail };
      return finishWithReport(r, results, { ok: r.code === 0 });
    }
    if (type === 'upload') {
      // 安全默认：除非显式 dryRun:false，否则强制 dry-run
      const dryRun = params.dryRun !== false;
      const env = { OSS_DRY_RUN: dryRun ? 'true' : 'false' };
      await progress(`upload ${dryRun ? 'DRY-RUN' : 'REAL'}${keep.length ? ` (${keep.length} 家族)` : ' 全量'}`);
      const r = await runCmd('node', ['scripts/upload.js'], { env, onTail });
      results.upload = { exitCode: r.code, dryRun, tail: r.tail };
      return finishWithReport(r, results, { ok: r.code === 0 });
    }
    return { ok: false, error: `未知任务类型 ${type}` };
  } finally {
    await park();
  }

  async function finishWithReport(r, res, { ok }) {
    // 任务后自动刷新状态快照（best-effort，不阻塞结果）
    try {
      const snap = await scan({ skipHead: type === 'analyze' || type === 'subset' });
      await report(snap);
      res.snapshotFamilies = snap.families.length;
    } catch (e) {
      res.snapshotError = String(e).slice(0, 300);
    }
    return {
      ok,
      error: ok ? undefined : `exit ${r.code}: ${(r.stderr || r.stdout || '').slice(-800)}`,
      result: res,
    };
  }
}

// ---------- poll 守护 ----------

async function tick(onEvent) {
  // 1) 领任务
  const claim = await api('/api/factory/agent/jobs?claim=1');
  const job = claim?.data?.job;
  if (job) {
    log(`认领任务 ${job.id} type=${job.type}`);
    const started = Date.now();
    let lastBeat = 0;
    const onProgress = async (stage, logTail) => {
      const now = Date.now();
      if (now - lastBeat < 5000 && !logTail) return; // 节流
      lastBeat = now;
      try {
        await api(`/api/factory/agent/jobs/${job.id}`, {
          method: 'POST',
          body: { action: 'progress', stage, logTail },
        });
      } catch (e) {
        log(`progress 回传失败: ${e.message}`);
      }
    };
    // 运行期间心跳
    const hb = setInterval(() => {
      api(`/api/factory/agent/jobs/${job.id}`, {
        method: 'POST',
        body: { action: 'heartbeat' },
      }).catch(() => {});
    }, 15000);

    let outcome;
    try {
      outcome = await execJob(job, async (stage, logTail) => {
        await onProgress(stage, logTail);
      });
    } catch (e) {
      outcome = { ok: false, error: String(e) };
    } finally {
      clearInterval(hb);
    }

    // 结果里补 run 尾部日志（execJob 的 result 里没有统一 tail，取 steps 最后一条）
    try {
      await api(`/api/factory/agent/jobs/${job.id}`, {
        method: 'POST',
        body: {
          action: 'result',
          ok: outcome.ok,
          error: outcome.error,
          result: { ...outcome.result, durationMs: Date.now() - started },
        },
      });
    } catch (e) {
      log(`result 回传失败: ${e.message}（任务可能被标记超时）`);
    }
    log(`任务 ${job.id} ${outcome.ok ? '完成' : '失败'} 用时 ${((Date.now() - started) / 1000).toFixed(0)}s`);
    onEvent?.('job-done', job.id);
    return 'job';
  }
  return 'idle';
}

async function main() {
  const cmd = process.argv[2] || 'report';
  const printOnly = process.argv.includes('--print');

  // 全局互斥：同一台机器同时只跑一个 agent 实例
  try {
    const fd = fs.openSync(LOCK_FILE, 'wx');
    fs.writeSync(fd, JSON.stringify({ pid: process.pid, at: Date.now() }));
    fs.closeSync(fd);
    process.on('exit', () => { try { fs.unlinkSync(LOCK_FILE); } catch {} });
    process.on('SIGINT', () => process.exit(0));
    process.on('SIGTERM', () => process.exit(0));
  } catch {
    // 锁存在：超过 6h 视为僵尸锁，接管
    try {
      const st = fs.statSync(LOCK_FILE);
      if (Date.now() - st.mtimeMs > 6 * 3600 * 1000) {
        fs.unlinkSync(LOCK_FILE);
        log('清理僵尸锁后继续');
      } else {
        die(`另一 factory-agent 实例在运行（锁: ${LOCK_FILE}）`);
      }
    } catch {
      die(`另一 factory-agent 实例在运行（锁: ${LOCK_FILE}）`);
    }
  }

  if (cmd === 'scan' || cmd === 'report') {
    log('开始扫描…');
    const payload = await scan();
    log(`扫描完成: ${payload.families.length} 家族`);
    if (printOnly) {
      console.log(JSON.stringify(payload, null, 2));
    } else {
      await report(payload);
    }
    return;
  }

  if (cmd === 'poll') {
    const once = process.argv.includes('--once');
    log(`poll 启动: vault=${VAULT_URL} agent=${AGENT_NAME} poll=${POLL_INTERVAL / 1000}s report=${REPORT_INTERVAL / 1000}s`);
    let lastReport = 0;
    // 启动先报一次
    try {
      const payload = await scan();
      await report(payload);
      lastReport = Date.now();
      log(`初始上报: ${payload.families.length} 家族`);
    } catch (e) {
      log(`初始上报失败: ${e.message}（10 分钟后重试）`);
      lastReport = Date.now() - REPORT_INTERVAL + 600000;
    }
    if (once) {
      try { await tick(); } catch (e) { log(`tick 错误: ${e.message}`); }
      return;
    }
    // eslint-disable-next-line no-constant-condition
    while (true) {
      try {
        const r = await tick();
        if (r === 'idle' && Date.now() - lastReport > REPORT_INTERVAL) {
          const payload = await scan();
          await report(payload);
          lastReport = Date.now();
          log(`周期上报: ${payload.families.length} 家族`);
        }
      } catch (e) {
        log(`tick 错误: ${e.message}`);
      }
      await new Promise((r) => setTimeout(r, POLL_INTERVAL));
    }
  }

  die(`未知命令: ${cmd}（scan|report|poll）`);
}

main().catch((e) => die(`fatal: ${e.stack || e}`, 1));
