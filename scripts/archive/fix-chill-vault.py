#!/usr/bin/env python3
"""Fix chilltype vault metadata after batch1 QA (Hckht/Hclck2/Hcth/Hcwjt/Hcdht)."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path

CHARS_PATH = Path(__file__).resolve().parent.parent / "logs" / "chars-fix-chill.json"
# On server:
# CHAR_JSON=/tmp/chars-fix-chill.json DB=/www/wwwroot/fonts-vault/data/prod.db

import os

CHARS = json.loads(Path(os.environ.get("CHAR_JSON", str(CHARS_PATH))).read_text())
DB = os.environ.get("DB", "/www/wwwroot/fonts-vault/data/prod.db")


def main() -> None:
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    now = int(time.time() * 1000)

    def get(fam: str):
        return c.execute("select * from fonts where font_family=?", (fam,)).fetchone()

    def mk_weight(fam: str, wname: str, wnum: int, chars: int, glyphs: int, file_name: str):
        return {
            "font_family": fam if wname in ("Regular", "Normal") else f"{fam}-{wname}",
            "weight_name": wname,
            "font_weight": wnum,
            "versions": {
                "original": {
                    "file": file_name,
                    "char_count": chars,
                    "glyph_count": glyphs,
                    "subfamily_name": wname,
                }
            },
        }

    # Hckht → Medium
    ch = CHARS["Hckht"]["Medium"]
    w = {
        "Medium": {
            "font_family": "wenfeng-Hckht-Medium",
            "weight_name": "Medium",
            "font_weight": 500,
            "versions": {
                "original": {
                    "file": "Medium.otf",
                    "char_count": ch["chars"],
                    "glyph_count": ch["glyphs"],
                    "subfamily_name": "Medium",
                    "typographic_subfamily": "Medium",
                }
            },
        }
    }
    c.execute(
        "update fonts set weights=?, chinese_name=?, english_name=?, name=?, updated_at=? where font_family=?",
        (json.dumps(w, ensure_ascii=False), "寒蝉宽黑体", "Chill K Sans", "寒蝉宽黑体", now, "wenfeng-hckht"),
    )
    c.commit()
    print("hckht", list(w))

    # Hclck2 four weights
    w = {}
    for wn, num in (("Regular", 400), ("Medium", 500), ("Bold", 700), ("ExtraBold", 800)):
        ch = CHARS["Hclck2"][wn]
        ww = mk_weight("wenfeng-hclck2", wn, num, ch["chars"], ch["glyphs"], f"{wn}.otf")
        if wn != "Regular":
            ww["font_family"] = f"wenfeng-hclck2-{wn}"
        w[wn] = ww
    c.execute(
        "update fonts set weights=?, chinese_name=?, english_name=?, name=?, description=?, updated_at=? where font_family=?",
        (
            json.dumps(w, ensure_ascii=False),
            "寒蝉龙藏楷",
            "Chill LongCang Kai",
            "寒蝉龙藏楷",
            "寒蝉龙藏楷。基于龙藏体风格化拓展。SIL OFL 1.1。",
            now,
            "wenfeng-hclck2",
        ),
    )
    c.commit()
    print("hclck2", list(w))

    # Hcth → 有机体
    ch_r, ch_m = CHARS["Hcth"]["Regular"], CHARS["Hcth"]["Medium"]
    w = {
        "Regular": mk_weight("wenfeng-hcth", "Regular", 400, ch_r["chars"], ch_r["glyphs"], "Regular.otf"),
        "Medium": mk_weight("wenfeng-hcth", "Medium", 500, ch_m["chars"], ch_m["glyphs"], "Medium.otf"),
    }
    w["Medium"]["font_family"] = "wenfeng-hcth-Medium"
    c.execute(
        "update fonts set weights=?, chinese_name=?, english_name=?, name=?, description=?, updated_at=? where font_family=?",
        (
            json.dumps(w, ensure_ascii=False),
            "寒蝉有机体",
            "Chill Organic",
            "寒蝉有机体",
            "寒蝉谭黑系列·有机体。SIL OFL 1.1。",
            now,
            "wenfeng-hcth",
        ),
    )
    c.commit()
    print("hcth organic")

    # Hcwjt 无机体 — clone hcth row
    ch_r, ch_m = CHARS["Hcwjt"]["Regular"], CHARS["Hcwjt"]["Medium"]
    w = {
        "Regular": mk_weight("wenfeng-hcwjt", "Regular", 400, ch_r["chars"], ch_r["glyphs"], "Regular.otf"),
        "Medium": mk_weight("wenfeng-hcwjt", "Medium", 500, ch_m["chars"], ch_m["glyphs"], "Medium.otf"),
    }
    w["Medium"]["font_family"] = "wenfeng-hcwjt-Medium"
    existing = get("wenfeng-hcwjt")
    if existing:
        c.execute(
            "update fonts set weights=?, chinese_name=?, english_name=?, name=?, description=?, status=?, normalized_name=?, updated_at=? where font_family=?",
            (
                json.dumps(w, ensure_ascii=False),
                "寒蝉无机体",
                "Chill Inorganic",
                "寒蝉无机体",
                "寒蝉谭黑系列·无机体。SIL OFL 1.1。",
                "published",
                "Hcwjt",
                now,
                "wenfeng-hcwjt",
            ),
        )
        print("hcwjt updated")
    else:
        src = get("wenfeng-hcth")
        cols = [r[1] for r in c.execute("pragma table_info(fonts)")]
        row = {k: src[k] for k in cols}
        row["id"] = str(uuid.uuid4())
        row["font_family"] = "wenfeng-hcwjt"
        row["name"] = "寒蝉无机体"
        row["chinese_name"] = "寒蝉无机体"
        row["english_name"] = "Chill Inorganic"
        row["normalized_name"] = "Hcwjt"
        row["oss_path"] = "fonts-packages/Hcwjt"
        row["weights"] = json.dumps(w, ensure_ascii=False)
        row["description"] = "寒蝉谭黑系列·无机体。SIL OFL 1.1。"
        row["version"] = row.get("version") or "1.0"
        row["status"] = "published"
        row["created_at"] = now
        row["updated_at"] = now
        c.execute(
            f"insert into fonts ({','.join(cols)}) values ({','.join('?' * len(cols))})",
            [row[k] for k in cols],
        )
        print("hcwjt inserted", row["id"])
    c.commit()

    # Hcdht display names
    row = get("wenfeng-hcdht")
    if row:
        ww = json.loads(row["weights"])
        if "Light" in ww:
            ww["Light"]["font_weight"] = 200
        c.execute(
            "update fonts set weights=?, chinese_name=?, english_name=?, name=?, description=?, updated_at=? where font_family=?",
            (
                json.dumps(ww, ensure_ascii=False),
                "寒蝉端黑体",
                "Chill Duan Sans",
                "寒蝉端黑体",
                "寒蝉端黑体（ChillDuanSans）。字重含 ExtraLight（目录键 Light）与 Black。SIL OFL 1.1。",
                now,
                "wenfeng-hcdht",
            ),
        )
        c.commit()
        print("hcdht renamed")

    print("done")
    return

if __name__ == "__main__":
    main()
