#!/usr/bin/env python3
"""Precompute single-WOFF2 shop-window preview packs (preview-shop).

Builds 1 merged `0.woff2` + canonical `result.css` per (normalized-lower, weight).
Source resolution order:
  1. Local font file in `fonts/{norm}/` (skipping Git LFS pointers)
  2. CDN `source/index.json` or catalog archive URL (cached locally, never OSS SDK read)
  3. CDN `{norm}/{weight}/{subset}/result.css` covering woff2 shards -> subset & merge into 1 `0.woff2`

Usage:
  python3 scripts/build-preview-pack.py --norms zjgljt,xwwkb,albbpht --force
  python3 scripts/build-preview-pack.py --all-catalog --workers 10 --force
"""
from __future__ import annotations

import argparse
import concurrent.futures
import io
import json
import os
import re
import ssl
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from fontTools.merge import Merger
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
PACKS_FILE = ROOT / "config" / "preview-packs.json"
DEFAULT_CATALOG = Path.home() / "Projects" / "fonts-front" / "data" / "fonts.json"
DEFAULT_SRC_CACHE = Path("/tmp/wf-preview-src-cache")
CDN = "https://cn.windfonts.com/fonts-packages"
UA = "linuxjoy-preview-pack/2"
LFS_MAGIC = b"version https://git-lfs.github.com/spec/v1"
FONT_EXTS = (".ttf", ".otf", ".ttc", ".woff2", ".woff")
SUBSETS_TRY = ("full", "zh", "zh-common", "en")

FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
URL_RE = re.compile(r"url\(\s*['\"]?([^)\"']+)['\"]?\s*\)", re.I)
RANGE_RE = re.compile(r"unicode-range\s*:\s*([^;}]+)", re.I)

WEIGHT_MAP = {
    "thin": "100",
    "extralight": "200",
    "extra-light": "200",
    "ultralight": "200",
    "ultra-light": "200",
    "w200": "200",
    "light": "300",
    "lightitalic": "300",
    "w300": "300",
    "demilight": "350",
    "book": "400",
    "regular": "400",
    "normal": "400",
    "roman": "400",
    "italic": "400",
    "oblique": "400",
    "w400": "400",
    "medium": "500",
    "mediumitalic": "500",
    "w500": "500",
    "demi": "600",
    "demibold": "600",
    "semibold": "600",
    "semi-bold": "600",
    "w600": "600",
    "bold": "700",
    "w700": "700",
    "extrabold": "800",
    "extra-bold": "800",
    "ultrabold": "800",
    "ultra": "800",
    "w800": "800",
    "heavy": "900",
    "black": "900",
    "ultrablack": "900",
    "w900": "900",
}

_OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()),
)


def load_packs() -> dict:
    return json.loads(PACKS_FILE.read_text(encoding="utf-8"))["packs"]


def fetch(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with _OPENER.open(req, timeout=timeout) as r:
        return r.read()


def weight_to_css(weight: str) -> str:
    s = str(weight or "").strip()
    if re.fullmatch(r"\d{2,4}", s):
        return s
    k = re.sub(r"[\s_-]+", "", s.lower())
    return WEIGHT_MAP.get(k, "400")


def weight_to_style(weight: str) -> str:
    low = str(weight or "").lower()
    if "italic" in low:
        return "italic"
    if "oblique" in low:
        return "oblique"
    return "normal"


def pick_primary_weight(weights: list) -> str:
    ws = [str(w) for w in (weights or []) if w]
    if not ws:
        return "Regular"
    for cand in ("Regular", "Normal", "Medium", "Book"):
        for w in ws:
            if w.lower() == cand.lower():
                return w
    return ws[0]


def is_real_font_file(path: Path) -> bool:
    try:
        if not path.is_file() or path.suffix.lower() not in FONT_EXTS:
            return False
        sz = path.stat().st_size
        if sz <= 1024:
            with path.open("rb") as fh:
                if fh.read(len(LFS_MAGIC)) == LFS_MAGIC:
                    return False
        return sz > 1000
    except OSError:
        return False


def pick_best_font_file(files: list[Path], weight: str) -> Path | None:
    if not files:
        return None
    if len(files) == 1:
        return files[0]
    w_key = re.sub(r"[\s_-]+", "", weight.lower())

    def score(p: Path) -> tuple[int, int, str]:
        stem_key = re.sub(r"[\s_-]+", "", p.stem.lower())
        ext_pri = {".ttf": 0, ".otf": 1, ".ttc": 2, ".woff2": 3, ".woff": 4}.get(p.suffix.lower(), 5)
        if stem_key == w_key:
            return (0, ext_pri, p.name)
        if stem_key.endswith(w_key) and w_key:
            return (1, ext_pri, p.name)
        if w_key and w_key in stem_key:
            return (2, ext_pri, p.name)
        if w_key in ("regular", "normal"):
            bad = ("bold", "italic", "oblique", "light", "heavy", "black", "thin", "medium", "semi", "extra", "demi", "_b", "_d", "_p", "variable")
            if not any(b in p.stem.lower() for b in bad):
                return (3, ext_pri, p.name)
        return (4, ext_pri, p.name)

    return sorted(files, key=score)[0]


def find_local_font(fonts_dir: Path, norm: str, weight: str) -> Path | None:
    d = fonts_dir / norm
    if not d.is_dir():
        return None
    real = [p for p in d.rglob("*") if is_real_font_file(p)]
    return pick_best_font_file(real, weight)


def fetch_cdn_source(norm: str, weight: str, entry: dict | None, cache_dir: Path) -> Path | None:
    cdir = cache_dir / norm
    if cdir.is_dir():
        cached = [p for p in cdir.iterdir() if is_real_font_file(p)]
        hit = pick_best_font_file(cached, weight)
        if hit:
            return hit

    candidates: list[tuple[str, str]] = []
    # 1. source/index.json on CDN
    try:
        meta = json.loads(fetch(f"{CDN}/{norm}/source/index.json", timeout=12).decode("utf-8", "replace"))
        for item in meta.get("items") or []:
            fname = str(item.get("file") or "")
            if not fname or ".." in fname or "/" in fname:
                continue
            if Path(fname).suffix.lower() not in FONT_EXTS:
                continue
            u = item.get("url") or f"{CDN}/{norm}/source/{fname}"
            if str(u).startswith("https://cn.windfonts.com/"):
                candidates.append((fname, str(u)))
    except Exception:
        pass

    # 2. catalog files archive href
    if not candidates and entry:
        for fitem in entry.get("files") or []:
            if fitem.get("kind") != "archive":
                continue
            href = str(fitem.get("href") or "")
            fname = str(fitem.get("file") or Path(href).name)
            if href.startswith("https://cn.windfonts.com/") and Path(fname).suffix.lower() in FONT_EXTS:
                candidates.append((fname, href))

    if not candidates:
        return None

    fake_paths = [Path(fn) for fn, _ in candidates]
    best = pick_best_font_file(fake_paths, weight)
    if not best:
        return None
    url = dict(candidates)[best.name]
    try:
        raw = fetch(url, timeout=35)
    except Exception:
        cut = url.rfind("/") + 1
        lower_url = url[:cut].lower() + url[cut:]
        if lower_url == url:
            return None
        try:
            raw = fetch(lower_url, timeout=35)
        except Exception:
            return None
    if len(raw) <= 1024 and raw.startswith(LFS_MAGIC):
        return None
    cdir.mkdir(parents=True, exist_ok=True)
    dest = cdir / best.name
    dest.write_bytes(raw)
    return dest if is_real_font_file(dest) else None


def codepoints(text: str) -> list[int]:
    return sorted({ord(ch) for ch in text if ord(ch) >= 0x20})


def range_covers(spec: str, cps: list[int]) -> bool:
    for part in spec.split(","):
        tok = part.strip().upper().replace("U+", "").replace(" ", "")
        if not tok:
            continue
        if "-" in tok:
            a, b = tok.split("-", 1)
            lo, hi = int(a, 16), int(b, 16)
        else:
            lo = hi = int(tok, 16)
        for cp in cps:
            if lo <= cp <= hi:
                return True
    return False


def covering_urls(css: str, cps: list[int]) -> list[str]:
    out = []
    for body in FACE_RE.findall(css):
        src_m = URL_RE.search(body)
        if not src_m:
            continue
        src = src_m.group(1).strip()
        rng_m = RANGE_RE.search(body)
        if rng_m and not range_covers(rng_m.group(1), cps):
            continue
        out.append(src)
    return out


def cmap_to_range(cps: list[int]) -> str:
    if not cps:
        return "U+20"
    cps = sorted(cps)
    parts = []
    start = prev = cps[0]
    for cp in cps[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        parts.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
        start = prev = cp
    parts.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
    return ", ".join(parts)


def open_ttfont(src: Path | io.BytesIO) -> TTFont:
    if isinstance(src, Path) and src.suffix.lower() == ".ttc":
        return TTFont(src, fontNumber=0)
    return TTFont(src)


def sanitize_cff_strings(font: TTFont) -> None:
    if "CFF " not in font:
        return
    cff = font["CFF "].cff
    cff.fontNames = [
        n.encode("ascii", "ignore").decode("ascii") or "WFPreview" for n in cff.fontNames
    ]
    for td in cff.topDictIndex:
        for attr in ("version", "Notice", "Copyright", "FullName", "FamilyName", "Weight"):
            val = getattr(td, attr, None)
            if isinstance(val, str):
                cleaned = val.encode("ascii", "ignore").decode("ascii")
                setattr(td, attr, cleaned)


def subset_single_font(src: Path, cps: list[int], dest: Path) -> tuple[int, list[int]]:
    for attempt in (0, 1):
        font = open_ttfont(src)
        try:
            opt = Options()
            opt.flavor = "woff2"
            opt.notdef_outline = True
            opt.recommended_glyphs = True
            if attempt == 0:
                opt.layout_features = ["*"]
            else:
                if "gasp" in font:
                    del font["gasp"]
                opt.layout_features = []
                opt.hinting = False
                opt.drop_tables += ["DSIG", "GPOS", "GSUB", "GDEF", "kern", "vmtx", "vhea", "VORG", "gasp"]
            sub = Subsetter(options=opt)
            sub.populate(unicodes=cps)
            sub.subset(font)
            sanitize_cff_strings(font)
            font.flavor = "woff2"
            dest.parent.mkdir(parents=True, exist_ok=True)
            font.save(dest)
            kept = sorted((font.getBestCmap() or {}).keys())
            return dest.stat().st_size, kept
        except Exception:
            if attempt == 1:
                raise
        finally:
            font.close()
    raise RuntimeError("subset failed")


def merge_same_family_cff(part_paths: list[str]) -> TTFont:
    """Merge desubroutinized CFF subset shards originating from the same font."""
    base = TTFont(part_paths[0])
    cff = base["CFF "].cff
    top = cff.topDictIndex[0]
    is_cid = hasattr(top, "ROS")
    cs = top.CharStrings
    hmtx = base["hmtx"].metrics
    glyph_order = list(base.getGlyphOrder())
    existing = set(glyph_order)
    base_cmap = {}
    for t in base["cmap"].tables:
        if t.isUnicode():
            base_cmap.update(t.cmap)

    for idx, p in enumerate(part_paths[1:], start=1):
        other = TTFont(p)
        try:
            otop = other["CFF "].cff.topDictIndex[0]
            ocs = otop.CharStrings
            ohmtx = other["hmtx"].metrics
            ocmap = other.getBestCmap() or {}
            for cp, og in ocmap.items():
                if cp in base_cmap:
                    continue
                new_g = og if og not in existing else f"{og}_s{idx}"
                while new_g in existing:
                    new_g = f"{new_g}_x"
                existing.add(new_g)
                glyph_order.append(new_g)
                if is_cid:
                    charstring = ocs[og]
                    charstring.decompile()
                    cs.charStringsIndex.append(charstring)
                    gid = len(cs.charStringsIndex) - 1
                    cs.charStrings[new_g] = gid
                    if hasattr(top, "FDSelect") and hasattr(otop, "FDSelect"):
                        top.FDSelect.gidArray.append(otop.FDSelect[other.getGlyphID(og)])
                else:
                    charstring = ocs[og]
                    charstring.decompile()
                    cs.charStringsIndex.append(charstring)
                    cs.charStrings[new_g] = len(cs.charStringsIndex) - 1
                hmtx[new_g] = ohmtx.get(og, (500, 0))
                base_cmap[cp] = new_g
        finally:
            other.close()

    base.setGlyphOrder(glyph_order)
    top.charset = glyph_order
    base["maxp"].numGlyphs = len(glyph_order)
    for t in base["cmap"].tables:
        if t.isUnicode():
            t.cmap = dict(base_cmap)
    sanitize_cff_strings(base)
    return base


def build_from_cdn_shards(norm: str, weight: str, cps: list[int], dest: Path) -> tuple[int, list[int], int]:
    css = None
    css_base = None
    last_err = None
    weights_try = [weight]
    if weight == "Regular":
        weights_try.append("Normal")
    elif weight == "Normal":
        weights_try.append("Regular")

    for w_cand in weights_try:
        for subset in SUBSETS_TRY:
            url = f"{CDN}/{norm}/{w_cand}/{subset}/result.css"
            try:
                cand = fetch(url, timeout=20).decode("utf-8", "replace")
                css, css_base = cand, url.rsplit("/", 1)[0] + "/"
                break
            except Exception as e:
                last_err = f"{w_cand}/{subset}: {e}"
        if css:
            break
    if not css or not css_base:
        raise RuntimeError(last_err or "no cdn result.css")

    rels = covering_urls(css, cps)
    if not rels:
        raise RuntimeError("no covering shards")

    target_set = set(cps)
    urls = [rel if rel.startswith("http") else css_base + rel.lstrip("./") for rel in rels]

    def _get(u: str) -> bytes | None:
        try:
            return fetch(u, timeout=25)
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(urls))) as ex:
        raws = list(ex.map(_get, urls))

    with tempfile.TemporaryDirectory(prefix=f"wf-merge-{norm}-") as td:
        td_path = Path(td)
        parts: list[str] = []
        seen_cps: set[int] = set()
        is_cff = False
        for i, raw in enumerate(raws):
            if not raw:
                continue
            f = TTFont(io.BytesIO(raw))
            try:
                cmap = set((f.getBestCmap() or {}).keys())
                want = sorted((cmap & target_set) - seen_cps)
                if not want:
                    continue
                if "CFF " in f:
                    is_cff = True
                opt = Options()
                opt.flavor = None
                opt.notdef_outline = True
                opt.recommended_glyphs = True
                opt.desubroutinize = True
                if len(urls) > 1:
                    opt.layout_features = []
                    opt.drop_tables += ["DSIG", "GPOS", "GSUB", "GDEF", "kern", "vmtx", "vhea", "VORG"]
                else:
                    opt.layout_features = ["*"]
                if "gasp" in f:
                    del f["gasp"]
                sub = Subsetter(options=opt)
                sub.populate(unicodes=want)
                sub.subset(f)
                sanitize_cff_strings(f)
                ext = ".otf" if "CFF " in f else ".ttf"
                p = td_path / f"part_{i}{ext}"
                f.save(p)
                seen_cps.update(want)
                parts.append(str(p))
            finally:
                f.close()

        if not parts:
            raise RuntimeError("empty after shard subset")

        if len(parts) == 1:
            merged = TTFont(parts[0])
        elif is_cff:
            merged = merge_same_family_cff(parts)
        else:
            merged = Merger().merge(parts)

        try:
            merged.flavor = "woff2"
            dest.parent.mkdir(parents=True, exist_ok=True)
            merged.save(dest)
            kept = sorted((merged.getBestCmap() or {}).keys())
        finally:
            merged.close()
        return dest.stat().st_size, kept, len(parts)


def write_css(out_dir: Path, family: str, weight: str, cps: list[int]) -> Path:
    css_weight = weight_to_css(weight)
    css_style = weight_to_style(weight)
    content = (
        "@font-face {\n"
        f'  font-family: "{family}";\n'
        f"  font-style: {css_style};\n"
        f"  font-weight: {css_weight};\n"
        "  font-display: swap;\n"
        '  src: url("./0.woff2") format("woff2");\n'
        f"  unicode-range: {cmap_to_range(cps)};\n"
        "}\n"
    )
    css_path = out_dir / "result.css"
    css_path.write_text(content, encoding="utf-8")
    return css_path


def verify_woff2(path: Path) -> list[int]:
    if path.read_bytes()[:4] != b"wOF2":
        raise ValueError("missing wOF2 magic header")
    with TTFont(path) as f:
        if f.flavor != "woff2":
            raise ValueError(f"unexpected flavor {f.flavor}")
        return sorted((f.getBestCmap() or {}).keys())


def build_one(job: dict) -> dict:
    norm: str = job["norm"].lower()
    weight: str = job["weight"]
    family: str = job["family"]
    pack_id: str = job["pack_id"]
    pack_path: str = job["pack_path"]
    text: str = job["text"]
    dest_root = Path(job["dest"])
    fonts_dir = Path(job["fonts_dir"])
    src_cache = Path(job["src_cache"])
    entry = job.get("entry")
    force: bool = job.get("force", False)

    out_dir = dest_root / norm / weight / pack_path
    woff2_path = out_dir / "0.woff2"
    css_path = out_dir / "result.css"
    pack_json = out_dir / "pack.json"

    if not force and woff2_path.is_file() and css_path.is_file() and pack_json.is_file():
        try:
            prev = json.loads(pack_json.read_text(encoding="utf-8"))
            if prev.get("schema") == 2 and prev.get("files") == 1 and woff2_path.stat().st_size > 200:
                return {"ok": True, "norm": norm, "weight": weight, "skipped": True, "bytes": woff2_path.stat().st_size}
        except Exception:
            pass

    cps = codepoints(text)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Remove any legacy multi-shard woff2 files before writing
    for old in out_dir.glob("*.woff2"):
        old.unlink(missing_ok=True)

    source_kind = None
    shards_merged = 1
    errors: list[str] = []
    size = 0
    kept_cps: list[int] = []

    # Tier 1: Local source font
    local_src = find_local_font(fonts_dir, norm, weight)
    if local_src is not None:
        try:
            size, kept_cps = subset_single_font(local_src, cps, woff2_path)
            if kept_cps:
                source_kind = f"local:{local_src.name}"
        except Exception as e:
            errors.append(f"local({local_src.name}): {e}")
            woff2_path.unlink(missing_ok=True)

    # Tier 2: CDN source archive
    if not source_kind:
        cdn_src = fetch_cdn_source(norm, weight, entry, src_cache)
        if cdn_src is not None:
            try:
                size, kept_cps = subset_single_font(cdn_src, cps, woff2_path)
                if kept_cps:
                    source_kind = f"cdn-source:{cdn_src.name}"
            except Exception as e:
                errors.append(f"cdn-source({cdn_src.name}): {e}")
                woff2_path.unlink(missing_ok=True)

    # Tier 3: CDN result.css shards -> subset & merge
    if not source_kind:
        try:
            size, kept_cps, shards_merged = build_from_cdn_shards(norm, weight, cps, woff2_path)
            if kept_cps:
                source_kind = f"cdn-shards:{shards_merged}"
        except Exception as e:
            errors.append(f"cdn-shards: {e}")
            woff2_path.unlink(missing_ok=True)

    if not source_kind or not kept_cps or not woff2_path.is_file():
        return {"ok": False, "norm": norm, "weight": weight, "error": "; ".join(errors) or "no glyphs"}

    try:
        verified_cps = verify_woff2(woff2_path)
    except Exception as e:
        woff2_path.unlink(missing_ok=True)
        return {"ok": False, "norm": norm, "weight": weight, "error": f"verify failed: {e}"}

    write_css(out_dir, family, weight, verified_cps)
    meta = {
        "ok": True,
        "schema": 2,
        "norm": norm,
        "weight": weight,
        "family": family,
        "pack": pack_id,
        "files": 1,
        "bytes": woff2_path.stat().st_size,
        "glyphs": len(verified_cps),
        "requestedCps": len(cps),
        "source": source_kind,
        "shardsMerged": shards_merged,
        "css": str(css_path),
    }
    pack_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def load_catalog(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def build_jobs(args, pack: dict) -> list[dict]:
    catalog = load_catalog(Path(args.catalog)) if Path(args.catalog).is_file() else []
    by_norm = {str(f.get("normalized", "")).lower(): f for f in catalog if f.get("normalized")}
    base_text = pack["text"]

    def make_job(norm: str, weight: str | None = None, entry: dict | None = None) -> dict:
        n = norm.lower()
        ent = entry or by_norm.get(n)
        w = weight or (pick_primary_weight(ent.get("weights") or []) if ent else "Regular")
        fam = (ent.get("family") if ent else None) or f"wenfeng-{n}"
        extra = ""
        if ent:
            extra = f"{ent.get('name') or ''} {ent.get('en') or ''}"
        if args.extra_text:
            extra += " " + args.extra_text
        return {
            "norm": n,
            "weight": w,
            "family": fam,
            "pack_id": pack["id"],
            "pack_path": pack["path"],
            "text": base_text + extra,
            "dest": str(Path(args.dest)),
            "fonts_dir": str(Path(args.fonts_dir)),
            "src_cache": str(Path(args.src_cache)),
            "entry": ent,
            "force": args.force,
        }

    jobs: list[dict] = []
    if args.norms:
        for raw in args.norms.split(","):
            n = raw.strip().lower()
            if n:
                jobs.append(make_job(n, args.weight if args.weight else None))
    elif args.norm:
        jobs.append(make_job(args.norm, args.weight if args.weight else None))
    elif args.all_catalog:
        seen: set[tuple[str, str]] = set()
        for ent in catalog:
            n = str(ent.get("normalized") or "").strip().lower()
            if not n:
                continue
            w = pick_primary_weight(ent.get("weights") or [])
            if (n, w) in seen:
                continue
            seen.add((n, w))
            jobs.append(make_job(n, w, ent))
        if args.limit:
            jobs = jobs[: args.limit]
    else:
        raise SystemExit("need --norm, --norms, or --all-catalog")
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser(description="Build single-WOFF2 preview-shop font packs")
    ap.add_argument("--pack", default="shop")
    ap.add_argument("--norm", help="Single font normalized slug")
    ap.add_argument("--norms", help="Comma-separated normalized slugs")
    ap.add_argument("--weight", default="", help="Override weight folder name")
    ap.add_argument("--extra-text", default="")
    ap.add_argument("--all-catalog", action="store_true")
    ap.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dest", default=str(ROOT / "staging" / "preview-shop-oss"))
    ap.add_argument("--fonts-dir", default=str(ROOT / "fonts"))
    ap.add_argument("--src-cache", default=str(DEFAULT_SRC_CACHE))
    ap.add_argument("--workers", "--jobs", dest="workers", type=int, default=min(10, os.cpu_count() or 8))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--report", help="Optional JSON report path")
    args = ap.parse_args()

    packs = load_packs()
    if args.pack not in packs:
        print(f"unknown pack: {args.pack}", file=sys.stderr)
        return 2
    pack = packs[args.pack]
    Path(args.dest).mkdir(parents=True, exist_ok=True)
    jobs = build_jobs(args, pack)

    results: list[dict] = []
    if args.workers <= 1 or len(jobs) == 1:
        for idx, j in enumerate(jobs, 1):
            r = build_one(j)
            results.append(r)
            if not r.get("ok") or len(jobs) <= 20 or idx % 50 == 0:
                print(f"[{idx}/{len(jobs)}] {'OK' if r.get('ok') else 'FAIL'} {r['norm']}/{r['weight']} "
                      f"bytes={r.get('bytes', 0)} glyphs={r.get('glyphs', 0)} src={r.get('source', r.get('error'))}")
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(build_one, j) for j in jobs]
            for idx, fut in enumerate(concurrent.futures.as_completed(futs), 1):
                r = fut.result()
                results.append(r)
                if not r.get("ok") or len(jobs) <= 20 or idx % 50 == 0:
                    print(f"[{idx}/{len(jobs)}] {'OK' if r.get('ok') else 'FAIL'} {r['norm']}/{r['weight']} "
                          f"bytes={r.get('bytes', 0)} glyphs={r.get('glyphs', 0)} src={r.get('source', r.get('error'))}",
                          flush=True)

    ok_list = [r for r in results if r.get("ok") and not r.get("skipped")]
    skip_list = [r for r in results if r.get("skipped")]
    fail_list = [r for r in results if not r.get("ok")]
    total_bytes = sum(r.get("bytes", 0) for r in results if r.get("ok"))
    built_total = len(ok_list) + len(skip_list)
    avg_bytes = round(total_bytes / built_total, 1) if built_total else 0

    src_breakdown: dict[str, int] = {}
    for r in ok_list:
        tag = str(r.get("source") or "unknown").split(":", 1)[0]
        src_breakdown[tag] = src_breakdown.get(tag, 0) + 1

    summary = {
        "total": len(jobs),
        "built": len(ok_list),
        "skipped": len(skip_list),
        "failed": len(fail_list),
        "totalBytes": total_bytes,
        "avgBytes": avg_bytes,
        "sourceBreakdown": src_breakdown,
        "failures": [{"norm": r["norm"], "weight": r["weight"], "error": r.get("error")} for r in fail_list],
        "results": sorted(results, key=lambda x: (x["norm"], x["weight"])),
    }
    if args.report:
        Path(args.report).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"DONE total={summary['total']} built={summary['built']} skipped={summary['skipped']} "
        f"failed={summary['failed']} total_bytes={total_bytes} avg_bytes={avg_bytes} sources={src_breakdown}"
    )
    if fail_list:
        for f in fail_list[:20]:
            print(f"  FAIL {f['norm']}/{f['weight']}: {f.get('error')}", file=sys.stderr)
    return 0 if not fail_list else 1


if __name__ == "__main__":
    raise SystemExit(main())
