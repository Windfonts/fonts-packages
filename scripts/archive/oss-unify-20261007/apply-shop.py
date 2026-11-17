#!/usr/bin/env python3
"""Set shop fonts.json normalized to family short for wave1 copies. Rebuild list."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = json.loads((HERE / "map.json").read_text(encoding="utf-8"))
SHOP = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts.json")
SUBSETS = Path("/Users/feibisi-studio/Projects/fonts-front/data/pack-subsets.json")
BUILD = Path("/Users/feibisi-studio/Projects/fonts-front/scripts/build-fonts-list.py")
JSONL = HERE / "copy-wave1.jsonl"


def empty_src_ids() -> set[str]:
    ids: set[str] = set()
    if not JSONL.exists():
        return ids
    with JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            if o.get("skip") == "empty-src" or o.get("src") == 0:
                ids.add(o.get("id"))
    return ids


def main() -> None:
    fonts = json.loads(SHOP.read_text(encoding="utf-8"))
    skip_ids = empty_src_ids()
    by_id = {x["id"]: x for x in MAP["wave1_copies"] if x["id"] not in skip_ids}
    bak = SHOP.with_name(
        "fonts.json.bak-oss-unify-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    )
    shutil.copy2(SHOP, bak)
    n = 0
    url_n = 0
    for f in fonts:
        rec = by_id.get(f["id"])
        if not rec:
            continue
        old = str(f.get("normalized") or "")
        new = rec["new"]
        if str(old).lower() == new:
            continue
        f["normalized"] = new
        n += 1
        for key in ("licenseFileUrl", "licenseUrl"):
            val = f.get(key)
            if not isinstance(val, str) or not val:
                continue
            nxt = val
            if old:
                nxt = nxt.replace("/fonts-packages/" + old + "/", "/fonts-packages/" + new + "/")
                nxt = nxt.replace("/fonts-packages/" + old.lower() + "/", "/fonts-packages/" + new + "/")
            if nxt != val:
                f[key] = nxt
                url_n += 1
    SHOP.write_text(json.dumps(fonts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"fonts.json normalized writes {n} license urls {url_n} bak {bak.name}")

    if SUBSETS.exists():
        sub = json.loads(SUBSETS.read_text(encoding="utf-8"))
        packs = sub.get("packs") or {}
        added = 0
        for rec in MAP["wave1_copies"]:
            src = packs.get(rec["old"])
            if src and rec["new"] not in packs:
                packs[rec["new"]] = src
                added += 1
        sub["packs"] = packs
        SUBSETS.write_text(json.dumps(sub, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"pack-subsets new keys {added}")

    subprocess.check_call([sys.executable, str(BUILD)])


if __name__ == "__main__":
    main()
