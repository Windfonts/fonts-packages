#!/usr/bin/env python3
"""Download LXGW TTFs from lxgw-batch-map.json into fonts/{Norm}/{Weight}.ttf."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "scripts" / "lxgw-batch-map.json"
FONTS = ROOT / "fonts"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  skip exists {dest.relative_to(ROOT)}")
        return
    print(f"  GET {dest.name} ...")
    subprocess.run(
        ["curl", "-fsSL", "--retry", "3", "-o", str(dest), url],
        check=True,
    )


def main() -> int:
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    data = json.loads(MAP.read_text())
    for fam in data["families"]:
        if only and fam["norm"] not in only:
            continue
        print(fam["norm"], fam["name"])
        for weight, url in fam["files"].items():
            download(url, FONTS / fam["norm"] / f"{weight}.ttf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
