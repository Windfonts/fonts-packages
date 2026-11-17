#!/usr/bin/env python3
"""Stage batch3 ready families plus the known CC0 汇文明朝 into fonts/{Norm}/.

Reads the batch3 scout JSON. Does not upload.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
DL = Path("/Users/feibisi-studio/Projects/_fonts_park/oss-batch3-dl")
DOCS = Path("/Users/feibisi-studio/Projects/fonts-front/docs")
PREFER = ["Regular", "Medium", "Bold", "Light"]
SUFFIX = {
    "EL": "ExtraLight",
    "SB": "SemiBold",
    "EB": "ExtraBold",
    "H": "Heavy",
    "B": "Bold",
    "L": "Light",
    "M": "Medium",
    "R": "Regular",
    "N": "Normal",
    "TH": "Thin",
}
WORD = [
    ("extralight", "ExtraLight"),
    ("semibold", "SemiBold"),
    ("extrabold", "ExtraBold"),
    ("regular", "Regular"),
    ("medium", "Medium"),
    ("light", "Light"),
    ("bold", "Bold"),
    ("heavy", "Heavy"),
    ("black", "Black"),
    ("thin", "Thin"),
]


def weight_of(name: str) -> str | None:
    low = name.lower()
    if "italic" in low or low.endswith("-it.otf") or "-it." in low:
        return None
    if any(x in low for x in ("condensed", "compact", "compressed", "extended", "variable", ".ttc", "woff")):
        return None
    for token, w in WORD:
        if token in low:
            return w
    stem = Path(name).stem
    suf = stem.rsplit("-", 1)[-1]
    # GenSenRounded2TW-R -> R, not Rounded
    if suf in SUFFIX:
        return SUFFIX[suf]
    return None


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  have {dest.name}", flush=True)
        return
    print(f"  GET {dest.name}", flush=True)
    subprocess.run(["curl", "-fsSL", "--retry", "3", "-L", "-o", str(dest), url], check=True)


def extract_fonts(archive: Path, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    found: list[Path] = []
    suf = archive.suffix.lower()
    if suf in {".ttf", ".otf"}:
        dest = out / archive.name
        if archive.resolve() != dest.resolve():
            shutil.copy2(archive, dest)
        return [dest]
    if suf == ".zip":
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = Path(info.filename).name
                if name.startswith("._") or "__MACOSX" in info.filename:
                    continue
                if not name.lower().endswith((".ttf", ".otf")):
                    continue
                dest = out / name
                with zf.open(info) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                found.append(dest)
        return found
    if suf == ".7z":
        subprocess.run(["bsdtar", "-xf", str(archive), "-C", str(out)], check=True)
        return [p for p in out.rglob("*") if p.suffix.lower() in {".ttf", ".otf"} and not p.name.startswith("._")]
    raise RuntimeError(f"unsupported {archive}")


def select(files: list[Path]) -> dict[str, Path]:
    by: dict[str, Path] = {}
    for f in files:
        w = weight_of(f.name)
        if not w:
            continue
        prev = by.get(w)
        if prev is None or len(f.name) < len(prev.name):
            by[w] = f
    if "Regular" not in by and "Normal" in by:
        by["Regular"] = by.pop("Normal")
    if not by and len(files) == 1:
        by["Regular"] = files[0]
    ordered: dict[str, Path] = {}
    for w in PREFER:
        if w in by:
            ordered[w] = by[w]
    if not ordered and by:
        w, p = next(iter(by.items()))
        ordered[w] = p
    return ordered


def load_items() -> list[dict]:
    items = []
    for name in ("huiwen", "justfont", "mplus-zen", "supplements"):
        data = json.loads((DOCS / f"_oss-ingest-batch3-{name}.json").read_text())
        for item in data["items"]:
            if item.get("status") != "ready":
                continue
            if name == "supplements" and item.get("name") not in ("源起明体", "源起黑体"):
                continue
            items.append(item)
    # CC0 汇文明朝：上一轮因许可范围被标 skip
    items.append(
        {
            "status": "ready",
            "repo": "bosswnx/huiwenmincho-improved",
            "norm": "Hwmc",
            "family": "wenfeng-hwmc",
            "name": "汇文明朝",
            "assetUrl": "https://github.com/bosswnx/huiwenmincho-improved/releases/download/20241203/Huiwenmincho-improved.otf",
            "source": "release",
        }
    )
    # 谐灵附体 release 里不止 Regular
    for item in items:
        if item.get("norm") == "AllPun":
            item["extraUrls"] = [
                "https://github.com/justfont/AllPunType/releases/download/1.0/AllPunType-Light.otf",
                "https://github.com/justfont/AllPunType/releases/download/1.0/AllPunType-Bold.otf",
                "https://github.com/justfont/AllPunType/releases/download/1.0/AllPunType-SemiBold.otf",
            ]
    return items


def stage_one(item: dict) -> dict:
    norm = item["norm"]
    url = item.get("assetUrl") or ""
    if not url:
        return {"status": "fail", "norm": norm, "reason": "no url"}
    folder = DL / norm
    folder.mkdir(parents=True, exist_ok=True)
    urls = [url] + list(item.get("extraUrls") or [])
    extracted: list[Path] = []
    for u in urls:
        name = u.rsplit("/", 1)[-1].split("?")[0]
        dest = folder / name
        download(u, dest)
        extracted.extend(extract_fonts(dest, folder / "extract"))
    chosen = select(extracted)
    if not chosen:
        return {"status": "fail", "norm": norm, "reason": "no weights", "files": [p.name for p in extracted[:12]]}
    out = FONTS / norm
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for w, src in chosen.items():
        target = out / f"{w}{src.suffix.lower()}"
        shutil.copy2(src, target)
        print(f"  staged {norm}/{target.name} <= {src.name}", flush=True)
    return {"status": "staged", "norm": norm, "weights": list(chosen)}


def main() -> int:
    results = []
    for item in load_items():
        print(f"== {item['norm']} {item.get('name')} ==", flush=True)
        try:
            result = stage_one(item)
        except Exception as e:
            result = {"status": "fail", "norm": item.get("norm"), "reason": str(e)}
        print("  ->", result, flush=True)
        results.append(result)
    out = ROOT / "logs" / "oss-batch3-download.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print("wrote", out, flush=True)
    return 1 if any(r.get("status") == "fail" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
