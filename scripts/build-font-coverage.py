#!/usr/bin/env python3
"""Build compact per-font Unicode coverage index from local font files + CDN result.css fallback.

Output: metadata/font-coverage.json
  { generated, count, fonts: { <normalized-lower>: { family, name, en, license, foundry, chars, ranges } } }
  ranges = "start-end|start-end" hex codepoints (inclusive), sorted, merged.

Usage:
  python3 scripts/build-font-coverage.py
  python3 scripts/build-font-coverage.py --catalog /path/to/fonts.json --out metadata/font-coverage.json
"""
import argparse
import concurrent.futures
import datetime
import json
import os
import re
import sys
import urllib.request
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONTS_DIR = os.path.join(ROOT, "fonts")
DEFAULT_OUT = os.path.join(ROOT, "metadata", "font-coverage.json")
DEFAULT_CATALOG_URL = os.environ.get(
    "CATALOG_EXPORT_URL",
    "https://vault.windfonts.com/api/catalog/export?view=fonts",
)
DEFAULT_CDN_BASE = os.environ.get(
    "COVERAGE_CDN_BASE",
    "https://cn.windfonts.com/fonts-packages",
)
FALLBACK_MAPPING = os.path.join(ROOT, "metadata", "font-mapping.json")
LFS_MAGIC = b"version https://git-lfs.github.com/spec/v1"


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


def is_lfs_pointer(path):
    try:
        if os.path.getsize(path) > 1024:
            return False
        with open(path, "rb") as fh:
            head = fh.read(len(LFS_MAGIC))
        return head == LFS_MAGIC
    except OSError:
        return False


def font_cps(path):
    if is_lfs_pointer(path):
        return None
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


def bdf_cps(path):
    if is_lfs_pointer(path):
        return None
    cps = set()
    try:
        with open(path, "r", encoding="latin-1", errors="ignore") as fh:
            for line in fh:
                if line.startswith("ENCODING "):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            cp = int(parts[1])
                            if 0 <= cp <= 0x10FFFF:
                                cps.add(cp)
                        except ValueError:
                            pass
    except Exception as e:
        print(f"  ! {path}: {e}", file=sys.stderr)
        return None
    return cps if cps else None


def parse_css_unicode_ranges(css):
    cps = set()
    for m in re.finditer(r"unicode-range\s*:\s*([^;}]+)", css, re.I):
        val = m.group(1).strip()
        if val.upper() == "U+0-10FFFF":
            continue
        for part in val.split(","):
            pm = re.match(r"U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?$", part.strip(), re.I)
            if not pm:
                continue
            start = int(pm.group(1), 16)
            end = int(pm.group(2), 16) if pm.group(2) else start
            if end >= start and (end - start) <= 200000:
                cps.update(range(start, end + 1))
    return cps


def fetch_url_text(url, timeout=15):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={"User-Agent": "fonts-packages/build-font-coverage"})
    with opener.open(req, timeout=timeout) as resp:
        if resp.status != 200:
            return None
        return resp.read().decode("utf-8", errors="replace")


def fetch_json_url(url, timeout=20):
    text = fetch_url_text(url, timeout=timeout)
    return json.loads(text)


def extract_oss_dir_from_files(files):
    if not isinstance(files, list):
        return None
    for item in files:
        if not isinstance(item, dict):
            continue
        href = item.get("href") or ""
        m = re.search(r"/fonts-packages/([^/]+)/", href)
        if m:
            return m.group(1).lower()
    return None


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
                aliases = []
                for a in f.get("aliases") or []:
                    if isinstance(a, str):
                        al = a.strip().lower()
                        if al and al != n and " " not in al and al not in aliases:
                            aliases.append(al)
                weights = [
                    w.strip()
                    for w in (f.get("weights") or [])
                    if isinstance(w, str) and w.strip()
                ]
                by_norm[n] = {
                    "family": f.get("family") or f"wenfeng-{n}",
                    "name": f.get("name") or n,
                    "en": f.get("en") or "",
                    "license": f.get("license") or "",
                    "foundry": f.get("foundry") or "",
                    "aliases": aliases,
                    "weights": weights,
                    "oss_dir": extract_oss_dir_from_files(f.get("files")),
                }
    elif isinstance(payload, dict):
        for k, v in payload.items():
            if not isinstance(v, dict):
                continue
            n = (v.get("normalized_name") or k or "").strip().lower()
            if n:
                weights = list((v.get("weights") or {}).keys()) if isinstance(v.get("weights"), dict) else []
                by_norm[n] = {
                    "family": f"wenfeng-{n}",
                    "name": v.get("chinese_name") or v.get("original_name") or n,
                    "en": v.get("english_name") or "",
                    "license": v.get("license") or v.get("license_type") or "",
                    "foundry": v.get("foundry") or v.get("designer") or "",
                    "aliases": [],
                    "weights": weights,
                    "oss_dir": None,
                }
    return by_norm


def load_catalog(catalog_arg):
    by_norm = {}
    published_norms = set()
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
            published_norms = set(api_norm.keys())
            print(f"Loaded {len(api_norm)} published entries from {source}")
        else:
            with open(source, "r", encoding="utf-8") as fh:
                file_norm = normalize_catalog_payload(json.load(fh))
            by_norm.update(file_norm)
            published_norms = set(file_norm.keys())
            print(f"Loaded {len(file_norm)} entries from {source}")
    except Exception as e:
        if catalog_arg:
            raise
        print(f"  ! remote catalog fetch failed ({source}: {e}), using local fallback ({len(by_norm)} entries)", file=sys.stderr)

    return by_norm, published_norms


def fetch_cdn_coverage(norm, meta, cdn_base):
    dirs = []
    for d in [meta.get("oss_dir"), norm] + list(meta.get("aliases") or []):
        if d and d not in dirs:
            dirs.append(d)
    weights = list(meta.get("weights") or [])
    if not weights:
        weights = ["Regular"]
    weights = sorted(weights, key=lambda w: (0 if w.lower() == "regular" else 1, w))

    union = set()
    for d in dirs:
        found_for_dir = False
        for w in weights:
            for sub in ("full", "zh", "zh-common", "en", "standard"):
                url = f"{cdn_base.rstrip('/')}/{d}/{w}/{sub}/result.css"
                try:
                    css = fetch_url_text(url, timeout=12)
                except Exception:
                    css = None
                if not css:
                    continue
                cps = parse_css_unicode_ranges(css)
                if cps:
                    union |= cps
                    found_for_dir = True
                    break
        if found_for_dir:
            break
    return norm, union


def build_entry(norm, meta, union):
    return {
        "family": meta.get("family") or f"wenfeng-{norm}",
        "name": meta.get("name") or norm,
        "en": meta.get("en") or "",
        "license": meta.get("license") or "",
        "foundry": meta.get("foundry") or "",
        "chars": len(union),
        "ranges": cps_to_ranges(union),
    }


def main():
    parser = argparse.ArgumentParser(description="Build compact per-font Unicode coverage index.")
    parser.add_argument(
        "--catalog",
        default=None,
        help=f"Catalog JSON path or URL (default: {DEFAULT_CATALOG_URL}, with local fallback)",
    )
    parser.add_argument("--fonts-dir", default=DEFAULT_FONTS_DIR, help="Directory containing font family folders")
    parser.add_argument("--cdn-base", default=DEFAULT_CDN_BASE, help="CDN base URL for result.css fallback")
    parser.add_argument("--no-cdn", action="store_true", help="Disable CDN result.css fallback for missing fonts")
    parser.add_argument("--workers", type=int, default=16, help="Parallel workers for CDN result.css fallback")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output JSON path")
    args = parser.parse_args()

    by_norm, published_norms = load_catalog(args.catalog)

    # Map non-canonical alias directory names -> canonical published slug
    alias_to_canonical = {}
    for canon in sorted(published_norms):
        meta = by_norm.get(canon, {})
        for al in meta.get("aliases") or []:
            if al not in published_norms and al not in alias_to_canonical:
                alias_to_canonical[al] = canon
        oss_dir = meta.get("oss_dir")
        if oss_dir and oss_dir != canon and oss_dir not in published_norms and oss_dir not in alias_to_canonical:
            alias_to_canonical[oss_dir] = canon

    local_cps = {}
    skipped = []
    if os.path.isdir(args.fonts_dir):
        for d in sorted(os.listdir(args.fonts_dir)):
            if d.startswith("_") or d.startswith("."):
                continue
            dpath = os.path.join(args.fonts_dir, d)
            if not os.path.isdir(dpath):
                continue
            norm = d.lower()
            ttf_files = [
                os.path.join(dpath, x)
                for x in os.listdir(dpath)
                if x.lower().endswith((".ttf", ".otf", ".ttc")) and os.path.isfile(os.path.join(dpath, x))
            ]
            bdf_files = [
                os.path.join(dpath, x)
                for x in os.listdir(dpath)
                if x.lower().endswith(".bdf") and os.path.isfile(os.path.join(dpath, x))
            ]
            union = set()
            for fp in sorted(ttf_files):
                cps = font_cps(fp)
                if cps:
                    union |= cps
            if not union and bdf_files:
                for fp in sorted(bdf_files):
                    cps = bdf_cps(fp)
                    if cps:
                        union |= cps
            if not union:
                skipped.append((norm, "no readable font files"))
                continue
            local_cps[norm] = union

    fonts = {}
    alias_resolved = 0
    local_direct = 0

    # 1. Emit direct local entries (skipping stale alias directories that map to a published canonical slug)
    for norm, union in sorted(local_cps.items()):
        if norm in alias_to_canonical:
            continue
        fonts[norm] = build_entry(norm, by_norm.get(norm, {}), union)
        local_direct += 1

    # 2. Resolve alias directories into canonical published slugs if not already covered directly
    for norm, union in sorted(local_cps.items()):
        canon = alias_to_canonical.get(norm)
        if not canon:
            continue
        if canon not in fonts:
            fonts[canon] = build_entry(canon, by_norm.get(canon, {}), union)
            alias_resolved += 1

    # 3. CDN result.css fallback for remaining published fonts missing locally
    cdn_resolved = 0
    still_missing = []
    if published_norms:
        missing_pub = sorted(published_norms - set(fonts.keys()))
        if missing_pub and not args.no_cdn:
            print(f"Probing CDN result.css for {len(missing_pub)} missing published fonts...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
                futs = [
                    ex.submit(fetch_cdn_coverage, norm, by_norm.get(norm, {}), args.cdn_base)
                    for norm in missing_pub
                ]
                for fut in concurrent.futures.as_completed(futs):
                    norm, union = fut.result()
                    if union:
                        fonts[norm] = build_entry(norm, by_norm.get(norm, {}), union)
                        cdn_resolved += 1
                    else:
                        still_missing.append(norm)
        else:
            still_missing = missing_pub

    fonts_sorted = {k: fonts[k] for k in sorted(fonts.keys())}
    out = {
        "generated": datetime.date.today().isoformat(),
        "count": len(fonts_sorted),
        "fonts": fonts_sorted,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(args.out)
    pub_covered = len(published_norms & set(fonts_sorted.keys()))
    print(
        f"fonts={len(fonts_sorted)} published={pub_covered}/{len(published_norms)} "
        f"(local={local_direct} alias={alias_resolved} cdn_css={cdn_resolved}) "
        f"missing_published={len(still_missing)} local_skipped={len(skipped)} "
        f"size={size/1024:.0f}KB out={args.out}"
    )
    if still_missing:
        print("  missing published:", sorted(still_missing))
    for s in skipped[:20]:
        print("  local skip:", s)


if __name__ == "__main__":
    main()
