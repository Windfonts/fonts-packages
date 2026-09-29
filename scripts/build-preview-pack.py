#!/usr/bin/env python3
"""Precompute named shop-window font packs from CDN unicode-range shards.

Not anonymous /api/css?text=. Pack id is an enum (shop/card/yong).
Source TTF on this Mac is often a Git LFS pointer, so we pull covering
woff2 from cn.windfonts.com, subset with fontTools, write one CSS + tiny woff2s.

Usage:
  python3 scripts/build-preview-pack.py --pack shop --norm Albbpht --weight Regular
  python3 scripts/build-preview-pack.py --pack shop --from-catalog --limit 12
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
PACKS_FILE = ROOT / "config" / "preview-packs.json"
CDN = "https://cn.windfonts.com/fonts-packages"
UA = "linuxjoy-preview-pack/1"
CTX = ssl.create_default_context()
SUBSETS_TRY = ("full", "zh", "zh-common")
FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
URL_RE = re.compile(r"url\(\s*['\"]?([^)\"']+)['\"]?\s*\)", re.I)
RANGE_RE = re.compile(r"unicode-range\s*:\s*([^;}]+)", re.I)


def load_packs() -> dict:
    return json.loads(PACKS_FILE.read_text())["packs"]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return r.read()


def codepoints(text: str) -> list[int]:
    return sorted({ord(ch) for ch in text})


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


def subset_woff2(src: Path, text: str, dest: Path) -> tuple[int, list[int]]:
    font = TTFont(src)
    opt = Options()
    opt.flavor = "woff2"
    opt.layout_features = ["*"]
    opt.notdef_outline = True
    opt.recommended_glyphs = True
    sub = Subsetter(options=opt)
    sub.populate(text=text)
    sub.subset(font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    font.save(dest)
    cmap = font.getBestCmap() or {}
    return dest.stat().st_size, sorted(cmap)


def write_css(out_dir: Path, files: list[tuple[str, list[int]]]) -> None:
    blocks = []
    for name, cps in files:
        blocks.append(
            "@font-face{\n"
            "  font-family:'wf-preview';\n"
            "  font-style:normal;\n"
            "  font-weight:400;\n"
            "  font-display:swap;\n"
            f"  src:url('./{name}') format('woff2');\n"
            f"  unicode-range:{cmap_to_range(cps)};\n"
            "}\n"
        )
    (out_dir / "result.css").write_text("".join(blocks), encoding="utf-8")


def build_one(norm: str, weight: str, pack: dict, dest_root: Path) -> dict:
    cps = codepoints(pack["text"])
    def css_cps(src: str) -> set[int]:
        out: set[int] = set()
        for m in RANGE_RE.finditer(src):
            for part in m.group(1).split(","):
                tok = part.strip().upper().replace("U+", "").replace(" ", "")
                if not tok:
                    continue
                if "-" in tok:
                    a, b = tok.split("-", 1)
                    lo, hi = int(a, 16), int(b, 16)
                    if hi - lo > 8000:
                        out.add(-1)
                        continue
                    out.update(range(lo, hi + 1))
                else:
                    out.add(int(tok, 16))
        return out

    def missing_needed(src: str) -> list[int]:
        have = css_cps(src)
        if -1 in have:
            return []
        return [c for c in cps if c >= 128 and c not in have]

    css = None
    css_base = None
    last_err = None
    for subset in SUBSETS_TRY:
        url = f"{CDN}/{norm}/{weight}/{subset}/result.css"
        try:
            cand = fetch(url).decode("utf-8", "replace")
            cand_base = url.rsplit("/", 1)[0] + "/"
        except urllib.error.HTTPError as e:
            last_err = f"{subset} {e.code}"
            continue
        except Exception as e:
            last_err = f"{subset} {e}"
            continue
        css, css_base = cand, cand_base
        if not missing_needed(cand):
            break
    if not css:
        return {"ok": False, "norm": norm, "weight": weight, "error": last_err or "no css"}

    rels = covering_urls(css, cps)
    if not rels:
        return {"ok": False, "norm": norm, "weight": weight, "error": "no covering face"}

    out_dir = dest_root / norm / weight / pack["path"]
    out_dir.mkdir(parents=True, exist_ok=True)
    kept: list[tuple[str, list[int]]] = []
    total = 0
    for i, rel in enumerate(rels):
        file_url = rel if rel.startswith("http") else css_base + rel.lstrip("./")
        try:
            raw = fetch(file_url)
        except Exception as e:
            print(f"  skip {file_url}: {e}", file=sys.stderr)
            continue
        tmp = out_dir / f"_src-{i}.woff2"
        tmp.write_bytes(raw)
        name = f"{i}.woff2"
        try:
            size, kept_cps = subset_woff2(tmp, pack["text"], out_dir / name)
        except Exception as e:
            print(f"  subset fail {norm}/{weight} {rel}: {e}", file=sys.stderr)
            tmp.unlink(missing_ok=True)
            continue
        tmp.unlink(missing_ok=True)
        if size < 400 or not kept_cps:
            (out_dir / name).unlink(missing_ok=True)
            continue
        kept.append((name, kept_cps))
        total += size
    if not kept:
        return {"ok": False, "norm": norm, "weight": weight, "error": "empty after subset"}
    write_css(out_dir, kept)
    meta = {
        "ok": True,
        "norm": norm,
        "weight": weight,
        "pack": pack["id"],
        "files": len(kept),
        "bytes": total,
        "css": str(out_dir / "result.css"),
    }
    (out_dir / "pack.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def pick_weight(ws: list) -> str:
    if not ws:
        return "Regular"
    for cand in ("Regular", "Medium", "Normal", "Book"):
        if cand in ws:
            return cand
    return str(ws[0])


def all_from_catalog(catalog: Path) -> list[tuple[str, str]]:
    fonts = json.loads(catalog.read_text())
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    extras = [
        ("Albbpht", "Medium"),
        ("Albbpht", "Bold"),
        ("Albbpht", "Heavy"),
        ("Albbpht", "Black"),
        ("Systcn", "Heavy"),
        ("Hckht", "Medium"),
        ("Dyh", "Oblique"),
        ("Ddjbt", "Normal"),
        ("Xwwk", "Regular"),
        ("Zkxwt", "Regular"),
        ("Ibmps", "Regular"),
    ]
    for f in fonts:
        if not isinstance(f, dict):
            continue
        norm = f.get("normalized")
        if not norm:
            continue
        w = pick_weight(f.get("weights") or [])
        key = (str(norm), str(w))
        if key not in seen:
            seen.add(key)
            out.append(key)
    for key in extras:
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def featured_from_catalog(catalog: Path, n: int) -> list[tuple[str, str]]:
    fonts = json.loads(catalog.read_text())
    keys = ["阿里巴巴普惠体", "得意黑", "思源黑体", "站酷", "思源宋体", "霞鹜文楷", "LXGW", "寒蝉", "钟齐"]
    extra = [("Xwwk", "Regular"), ("Zkxwt", "Regular"), ("Hckht", "Medium"), ("Ibmps", "Regular")]
    out: list[tuple[str, str]] = []
    seen = set()
    for key in keys:
        hit = next((f for f in fonts if key in (f.get("name") or "")), None)
        if not hit:
            continue
        norm = hit.get("normalized")
        ws = hit.get("weights") or ["Regular"]
        w = "Regular" if "Regular" in ws else ws[-1]
        if norm and (norm, w) not in seen:
            seen.add((norm, w))
            out.append((norm, w))
        if len(out) >= n:
            break
    for norm, w in extra:
        if (norm, w) not in seen:
            seen.add((norm, w))
            out.append((norm, w))
    return out[: max(n, len(out))]


def import_lab_packs(lab_root: Path, dest: Path, pack: dict) -> int:
    """Copy earlier lab layout preview-shop/{Norm}/{Weight}/ into packages layout."""
    src_root = lab_root / pack["path"]
    if not src_root.is_dir():
        return 0
    n = 0
    for css in src_root.glob("*/*/result.css"):
        weight_dir = css.parent
        norm = weight_dir.parent.name
        weight = weight_dir.name
        target = dest / norm / weight / pack["path"]
        target.mkdir(parents=True, exist_ok=True)
        for f in weight_dir.iterdir():
            if f.is_file() and not f.name.startswith("_"):
                (target / f.name).write_bytes(f.read_bytes())
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="shop")
    ap.add_argument("--norm")
    ap.add_argument("--weight", default="Regular")
    ap.add_argument("--from-catalog", action="store_true")
    ap.add_argument("--all-catalog", action="store_true")
    ap.add_argument("--catalog", default=str(Path.home() / "Projects/fonts-front-v4-lab/data/fonts.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dest", default=str(ROOT / "staging" / "preview-shop-oss"))
    ap.add_argument("--import-lab", default=str(Path.home() / "Projects/fonts-front-v4-lab/assets/fonts"))
    ap.add_argument("--skip-existing", action="store_true", default=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    packs = load_packs()
    pack = packs[args.pack]
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    imported = import_lab_packs(Path(args.import_lab), dest, pack)
    if imported:
        print(f"imported lab packs {imported}")
    jobs: list[tuple[str, str]]
    if args.all_catalog:
        jobs = all_from_catalog(Path(args.catalog))
    elif args.from_catalog:
        jobs = featured_from_catalog(Path(args.catalog), args.limit or 12)
    elif args.norm:
        jobs = [(args.norm, args.weight)]
    else:
        print("need --norm, --from-catalog, or --all-catalog", file=sys.stderr)
        return 2
    if args.limit and args.all_catalog:
        jobs = jobs[: args.limit]
    skip = args.skip_existing and not args.force

    def run(job: tuple[str, str]) -> dict:
        norm, weight = job
        existing = dest / norm / weight / pack["path"] / "result.css"
        if skip and existing.is_file() and existing.stat().st_size > 40:
            return {"ok": True, "norm": norm, "weight": weight, "skipped": True}
        return build_one(norm, weight, pack, dest)

    ok = 0
    fail = 0
    skipped = 0
    if args.jobs <= 1 or len(jobs) == 1:
        results = [run(j) for j in jobs]
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = []
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
            futs = [ex.submit(run, j) for j in jobs]
            for fut in as_completed(futs):
                results.append(fut.result())
    for meta in results:
        if meta.get("skipped"):
            skipped += 1
            print(f"SKIP {meta['norm']}/{meta['weight']}")
            continue
        status = "OK" if meta.get("ok") else "FAIL"
        print(f"{status} {meta.get('norm')}/{meta.get('weight')} {meta}")
        if meta.get("ok"):
            ok += 1
        else:
            fail += 1
    print(f"done ok={ok} skip={skipped} fail={fail} dest={dest}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
