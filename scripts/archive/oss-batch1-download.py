#!/usr/bin/env python3
"""Download / stage OSS batch1 fonts into fonts/{Norm}/{Weight}.{ttf|otf}.

Usage:
  python3 scripts/oss-batch1-download.py [--wave chilltype] [Norm ...]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "scripts" / "oss-batch1-map.json"
FONTS = ROOT / "fonts"
DL = Path("/Users/feibisi-studio/Projects/_fonts_park/oss-batch1-dl")
STAGING = Path("/Users/feibisi-studio/Projects/_fonts_park/oss-batch1-staging")

WEIGHT_PATTERNS = [
    (r"(?i)extralight|ultralight", "ExtraLight"),
    (r"(?i)demilight|semilight", "DemiLight"),
    (r"(?i)semibold|demibold", "SemiBold"),
    (r"(?i)extrabold|ultrabold", "ExtraBold"),
    (r"(?i)(?<![a-z])thin(?![a-z])", "Thin"),
    (r"(?i)(?<![a-z])light(?![a-z])", "Light"),
    (r"(?i)(?<![a-z])medium(?![a-z])", "Medium"),
    (r"(?i)(?<![a-z])bold(?![a-z])", "Bold"),
    (r"(?i)(?<![a-z])black(?![a-z])", "Black"),
    (r"(?i)(?<![a-z])heavy(?![a-z])", "Heavy"),
    (r"(?i)(?<![a-z])ultra(?![a-z])", "Ultra"),
    (r"(?i)(?<![a-z])demi(?![a-z])", "Demi"),
    (r"(?i)(?<![a-z])normal(?![a-z])", "Normal"),
    (r"(?i)(?<![a-z])regular(?![a-z])|(?<![a-z])reg(?![a-z])", "Regular"),
]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kw)


def gh_json(path: str):
    r = subprocess.run(
        ["gh", "api", path], capture_output=True, text=True, timeout=120
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:300] or r.stdout[:300])
    return json.loads(r.stdout)


def guess_weight(name: str) -> str | None:
    # Underscore is \w; camelCase FooRegular needs split; ExtraLight must stay glued.
    base = Path(name).stem
    compact = re.sub(r"[_\-\s]+", "", base)
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base)
    spaced = re.sub(r"[_\-\s]+", " ", spaced)
    for text in (compact, spaced, base):
        for pat, w in WEIGHT_PATTERNS:
            if re.search(pat, text):
                return w
    return None


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  skip exists {dest.name}")
        return
    print(f"  GET {dest.name} ...")
    run(["curl", "-fsSL", "--retry", "3", "-L", "-o", str(dest), url])


def raw_url(repo: str, path: str) -> str:
    from urllib.parse import quote
    # Encode path segments but keep slashes
    enc = "/".join(quote(seg, safe="") for seg in path.split("/"))
    return f"https://raw.githubusercontent.com/{repo}/HEAD/{enc}"


def pick_assets(fam: dict, assets: list[dict]) -> list[dict]:
    prefer = [p.lower() for p in fam.get("assetPrefer") or []]
    avoid = [p.lower() for p in fam.get("assetAvoid") or []]
    scored = []
    for a in assets:
        name = a["name"]
        low = name.lower()
        if avoid and any(x in low for x in avoid):
            continue
        if not re.search(r"\.(zip|ttf|otf|ttc|7z)$", low):
            continue
        score = 0
        for i, p in enumerate(prefer):
            if p in low:
                score += 100 - i
        if low.endswith((".ttf", ".otf")):
            score += 10
        if "lite" in low or "demo" in low or "variable" in low:
            score -= 5
        scored.append((score, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored]


def _is_junk_font_path(path: str) -> bool:
    low = path.lower().replace("\\", "/")
    base = Path(low).name
    if not low.endswith((".ttf", ".otf")):
        return True
    if "__macosx" in low or base.startswith("._") or base.startswith("."):
        return True
    if "/." in low:
        return True
    return False


def _is_width_variant(name: str) -> bool:
    low = name.lower()
    return bool(
        re.search(
            r"(condensed|compact|compressed|extended|expanded|wide|narrow|soft|vf\b|variable|_con[a-z]|conregular|conbold|conmedium|consemibold)",
            low,
        )
    )


def extract_fonts(archive: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    found: list[Path] = []
    if archive.suffix.lower() in {".ttf", ".otf", ".ttc"}:
        dest = out_dir / archive.name
        if not dest.exists():
            shutil.copy2(archive, dest)
        return [dest]
    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                if info.is_dir() or _is_junk_font_path(info.filename):
                    continue
                base = Path(info.filename).name
                dest = out_dir / base
                if not dest.exists() or dest.stat().st_size < info.file_size:
                    with zf.open(info) as src, open(dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                found.append(dest)
        return found
    raise RuntimeError(f"unsupported archive {archive}")


def _file_score(path: Path) -> int:
    """Higher is better when colliding on same weight."""
    score = 0
    name = path.name
    if path.suffix.lower() == ".ttf":
        score += 5
    if not _is_width_variant(name):
        score += 20
    # prefer OtF in Std/otf folders already flattened; prefer shorter names
    score -= len(name) // 20
    return score


def select_weights(files: list[Path], fam: dict) -> dict[str, Path]:
    weight_map = fam.get("weightMap") or {}
    prefer = fam.get("weightPrefer") or [
        "Regular",
        "Normal",
        "Medium",
        "Bold",
        "Light",
        "SemiBold",
        "ExtraLight",
    ]
    max_w = int(fam.get("maxWeights") or 3)
    # drop width variants unless that removes everything
    primary = [f for f in files if not _is_width_variant(f.name)]
    pool = primary if primary else files
    by_w: dict[str, Path] = {}
    for f in pool:
        if f.name in weight_map:
            w = weight_map[f.name]
        else:
            w = guess_weight(f.name)
        if not w:
            if len(pool) == 1:
                w = "Regular"
            else:
                continue
        prev = by_w.get(w)
        if prev is None or _file_score(f) > _file_score(prev):
            by_w[w] = f
    # Normal → Regular alias if Regular missing
    if "Regular" not in by_w and "Normal" in by_w:
        by_w["Regular"] = by_w.pop("Normal")
    ordered: dict[str, Path] = {}
    for w in prefer:
        if w in by_w:
            ordered[w] = by_w.pop(w)
            if len(ordered) >= max_w:
                return ordered
    for w, p in list(by_w.items()):
        if len(ordered) >= max_w:
            break
        ordered[w] = p
    if not ordered and files:
        ordered["Regular"] = files[0]
    return ordered


def stage_family(fam: dict) -> dict:
    if fam.get("skip"):
        return {"status": "skip", "reason": fam.get("skipReason"), "norm": fam["norm"]}
    norm = fam["norm"]
    dest_dir = FONTS / norm
    if dest_dir.exists() and any(dest_dir.glob("*.[to]tf")):
        weights = {p.stem: p for p in dest_dir.glob("*.[to]tf")}
        return {"status": "staged", "norm": norm, "weights": list(weights), "family": fam["family"]}

    DL.mkdir(parents=True, exist_ok=True)
    extract_root = STAGING / norm
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True)

    files: list[Path] = []
    source = fam.get("source") or "release"

    if source == "raw":
        for path in fam.get("rawPaths") or []:
            url = raw_url(fam["repo"], path)
            local = DL / norm / Path(path).name
            download(url, local)
            files.append(local)
    else:
        # release assets
        try:
            data = gh_json(f"repos/{fam['repo']}/releases/latest")
            assets = [
                {"name": a["name"], "url": a["browser_download_url"], "size": a.get("size", 0)}
                for a in data.get("assets") or []
            ]
        except Exception:
            assets = []
            rels = gh_json(f"repos/{fam['repo']}/releases?per_page=5")
            if rels:
                a0 = rels[0]
                assets = [
                    {"name": a["name"], "url": a["browser_download_url"], "size": a.get("size", 0)}
                    for a in a0.get("assets") or []
                ]
        picked = pick_assets(fam, assets)
        if not picked:
            return {"status": "fail", "norm": norm, "reason": "no downloadable assets"}
        # take top 1 archive or all direct font files
        archives = [a for a in picked if a["name"].lower().endswith((".zip", ".7z"))]
        directs = [a for a in picked if a["name"].lower().endswith((".ttf", ".otf", ".ttc"))]
        to_get = archives[:1] if archives else directs[: max(int(fam.get("maxWeights") or 3), 1)]
        for a in to_get:
            local = DL / norm / a["name"]
            download(a["url"], local)
            files.extend(extract_fonts(local, extract_root))

    if not files:
        return {"status": "fail", "norm": norm, "reason": "no font files after extract"}

    selected = select_weights(files, fam)
    if not selected:
        return {"status": "fail", "norm": norm, "reason": "could not map weights"}

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    for w, src in selected.items():
        ext = src.suffix.lower()
        target = dest_dir / f"{w}{ext}"
        shutil.copy2(src, target)
        print(f"  staged {norm}/{w}{ext} from {src.name}")

    # cleanup extract
    shutil.rmtree(extract_root, ignore_errors=True)
    return {
        "status": "staged",
        "norm": norm,
        "weights": list(selected.keys()),
        "family": fam["family"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave")
    ap.add_argument("norms", nargs="*")
    args = ap.parse_args()
    data = json.loads(MAP.read_text())
    fams = data["families"]
    if args.wave:
        fams = [f for f in fams if f.get("wave") == args.wave]
    if args.norms:
        want = set(args.norms)
        fams = [f for f in fams if f["norm"] in want]
    results = []
    for fam in fams:
        print(f"== {fam['norm']} {fam.get('name')} ==")
        try:
            r = stage_family(fam)
        except Exception as e:
            r = {"status": "fail", "norm": fam["norm"], "reason": str(e)}
        print("  ->", r)
        results.append(r)
    out = ROOT / "logs" / "oss-batch1-download.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
