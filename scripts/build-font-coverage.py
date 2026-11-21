#!/usr/bin/env python3
"""Build compact per-font Unicode coverage index from local font files.

Output: metadata/font-coverage.json
  { generated, count, fonts: { <normalized-lower>: { family, name, en, license, foundry, chars, ranges } } }
  ranges = "start-end|start-end" hex codepoints (inclusive), sorted, merged.

Usage:
  python3 scripts/build-font-coverage.py
  python3 scripts/build-font-coverage.py --catalog /path/to/fonts.json --out metadata/font-coverage.json
"""
import argparse
import datetime
import json
import os
import sys
import urllib.request
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONTS_DIR = os.path.join(ROOT, "fonts")
DEFAULT_OUT = os.path.join(ROOT, "metadata", "font-coverage.json")
DEFAULT_CATALOG_URL = os.environ.get(
    "CATALOG_EXPORT_URL",
    "https://api.windfonts.com/api/catalog/export?view=fonts",
)
FALLBACK_MAPPING = os.path.join(ROOT, "metadata", "font-mapping.json")


def cps_to_ranges(cps):
    cps = sorted(cps)
    ranges = []
    if not cps:
        return ""
    start = prev = cps[0]
    for cp in cps[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        ranges.append((start, prev))
        start = prev = cp
    ranges.append((start, prev))
    return "|".join(f"{a:X}-{b:X}" if a != b else f"{a:X}" for a, b in ranges)


def font_cps(path):
    cps = set()
    try:
        with TTFont(path, lazy=True, fontNumber=0) as f:
            for table in f["cmap"].tables:
                if table.isUnicode():
                    cps.update(table.cmap.keys())
    except Exception as e:
        print(f"  ! {path}: {e}", file=sys.stderr)
        return None
    return cps


def fetch_json_url(url, timeout=20):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={"User-Agent": "fonts-packages/build-font-coverage"})
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_catalog_payload(payload):
    by_norm = {}
    items = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else None
    if items is None and isinstance(payload, dict) and isinstance(payload.get("fonts"), list):
        items = payload["fonts"]
    if items is None and isinstance(payload, list):
        items = payload

    if items is not None:
        for f in items:
            if not isinstance(f, dict):
                continue
            n = (f.get("normalized") or "").strip().lower()
            if n:
                by_norm[n] = {
                    "family": f.get("family") or f"wenfeng-{n}",
                    "name": f.get("name") or n,
                    "en": f.get("en") or "",
                    "license": f.get("license") or "",
                    "foundry": f.get("foundry") or "",
                }
    elif isinstance(payload, dict):
        for k, v in payload.items():
            if not isinstance(v, dict):
                continue
            n = (v.get("normalized_name") or k or "").strip().lower()
            if n:
                by_norm[n] = {
                    "family": f"wenfeng-{n}",
                    "name": v.get("chinese_name") or v.get("original_name") or n,
                    "en": v.get("english_name") or "",
                    "license": v.get("license") or v.get("license_type") or "",
                    "foundry": v.get("foundry") or v.get("designer") or "",
                }
    return by_norm


def load_catalog(catalog_arg):
    by_norm = {}
    # Load local mapping as baseline fallback first so unpublished local fonts still get metadata
    if os.path.isfile(FALLBACK_MAPPING):
        try:
            with open(FALLBACK_MAPPING, "r", encoding="utf-8") as fh:
                by_norm.update(normalize_catalog_payload(json.load(fh)))
        except Exception as e:
            print(f"  ! fallback mapping load warning ({FALLBACK_MAPPING}): {e}", file=sys.stderr)

    source = catalog_arg or DEFAULT_CATALOG_URL
    try:
        if source.startswith(("http://", "https://")):
            payload = fetch_json_url(source)
            api_norm = normalize_catalog_payload(payload)
            by_norm.update(api_norm)
            print(f"Loaded {len(api_norm)} published entries from {source}")
        else:
            with open(source, "r", encoding="utf-8") as fh:
                file_norm = normalize_catalog_payload(json.load(fh))
            by_norm.update(file_norm)
            print(f"Loaded {len(file_norm)} entries from {source}")
    except Exception as e:
        if catalog_arg:
            raise
        print(f"  ! remote catalog fetch failed ({source}: {e}), using local fallback ({len(by_norm)} entries)", file=sys.stderr)

    return by_norm


def main():
    parser = argparse.ArgumentParser(description="Build compact per-font Unicode coverage index.")
    parser.add_argument(
        "--catalog",
        default=None,
        help=f"Catalog JSON path or URL (default: {DEFAULT_CATALOG_URL}, with local fallback)",
    )
    parser.add_argument("--fonts-dir", default=DEFAULT_FONTS_DIR, help="Directory containing font family folders")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output JSON path")
    args = parser.parse_args()

    by_norm = load_catalog(args.catalog)

    fonts = {}
    skipped = []
    for d in sorted(os.listdir(args.fonts_dir)):
        if d.startswith("_") or d.startswith("."):
            continue
        dpath = os.path.join(args.fonts_dir, d)
        if not os.path.isdir(dpath):
            continue
        norm = d.lower()
        files = [
            os.path.join(dpath, x)
            for x in os.listdir(dpath)
            if x.lower().endswith((".ttf", ".otf", ".ttc")) and os.path.isfile(os.path.join(dpath, x))
        ]
        if not files:
            skipped.append((norm, "no font files"))
            continue
        union = set()
        ok = True
        for fp in sorted(files):
            cps = font_cps(fp)
            if cps is None:
                ok = False
                break
            union |= cps
        if not ok:
            skipped.append((norm, "parse failed"))
            continue
        meta = by_norm.get(norm, {})
        fonts[norm] = {
            "family": meta.get("family") or f"wenfeng-{norm}",
            "name": meta.get("name") or norm,
            "en": meta.get("en") or "",
            "license": meta.get("license") or "",
            "foundry": meta.get("foundry") or "",
            "chars": len(union),
            "ranges": cps_to_ranges(union),
        }

    out = {
        "generated": datetime.date.today().isoformat(),
        "count": len(fonts),
        "fonts": fonts,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(args.out)
    print(f"fonts={len(fonts)} skipped={len(skipped)} size={size/1024:.0f}KB out={args.out}")
    for s in skipped[:20]:
        print("  skip:", s)


if __name__ == "__main__":
    main()
