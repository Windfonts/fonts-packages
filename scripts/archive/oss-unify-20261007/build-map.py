#!/usr/bin/env python3
"""Build OSS dir rename map: lowercase(normalized) -> family short.

Shop fonts.json is the public catalog. Vault published rows fill vault-only packs.
Copy is additive; do not delete old prefixes. Wave2 = copy would overwrite another
font's current prefix (recycle/swap).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOP = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts.json")
VAULT = HERE / "vault-fonts.json"
OUT = HERE / "map.json"


def short_of(family: str) -> str:
    fam = str(family or "").strip()
    if fam.lower().startswith("wenfeng-"):
        return fam[8:].lower()
    return fam.lower()


def main() -> None:
    shop = json.loads(SHOP.read_text(encoding="utf-8"))
    vault = json.loads(VAULT.read_text(encoding="utf-8"))
    by_id = {}
    by_old = {}

    def add(rec, source):
        oid = rec["id"]
        if oid in by_id and by_id[oid]["source"] == "shop" and source == "vault":
            # shop already owns this id; keep shop family/normalized, note vault
            by_id[oid]["in_vault"] = True
            return
        by_id[oid] = rec
        by_old.setdefault(rec["old"], []).append(rec)

    for f in shop:
        old = str(f.get("normalized") or "").strip()
        rec = {
            "id": f["id"],
            "name": f.get("name"),
            "family": f.get("family"),
            "normalized": old,
            "old": old.lower(),
            "new": short_of(f.get("family") or ""),
            "source": "shop",
            "in_shop": True,
            "in_vault": False,
            "status": "published",
        }
        add(rec, "shop")

    for r in vault["rows"]:
        old = str(r.get("normalized_name") or "").strip()
        rec = {
            "id": r["id"],
            "name": r.get("chinese_name") or r.get("name"),
            "family": r.get("font_family"),
            "normalized": old,
            "old": old.lower(),
            "new": short_of(r.get("font_family") or ""),
            "source": "vault",
            "in_shop": False,
            "in_vault": True,
            "status": r.get("status"),
            "oss_path": r.get("oss_path"),
        }
        if rec["id"] in by_id:
            by_id[rec["id"]]["in_vault"] = True
            by_id[rec["id"]]["vault_normalized"] = old
            by_id[rec["id"]]["vault_family"] = r.get("font_family")
            by_id[rec["id"]]["vault_status"] = r.get("status")
            continue
        if rec["status"] != "published":
            continue
        add(rec, "vault")

    items = list(by_id.values())
    current_olds = {x["old"]: x for x in items if x["old"]}
    same = [x for x in items if x["old"] and x["old"] == x["new"]]
    need = [x for x in items if x["old"] and x["new"] and x["old"] != x["new"]]

    wave1 = []
    wave2 = []
    for x in need:
        occ = current_olds.get(x["new"])
        if occ and occ["id"] != x["id"]:
            wave2.append(
                {
                    **x,
                    "occupied_by": {
                        "id": occ["id"],
                        "name": occ["name"],
                        "old": occ["old"],
                        "new": occ["new"],
                        "family": occ["family"],
                    },
                }
            )
        else:
            wave1.append(x)

    # One copy per destination. Prefer the shop row when two UUIDs share a short.
    dest_best = {}
    for x in wave1:
        cur = dest_best.get(x["new"])
        if not cur:
            dest_best[x["new"]] = x
            continue
        if x.get("in_shop") and not cur.get("in_shop"):
            dest_best[x["new"]] = x
    dropped = [x for x in wave1 if dest_best.get(x["new"]) is not x]
    wave1 = list(dest_best.values())

    new_dups = defaultdict(list)
    for x in items:
        if x.get("new"):
            new_dups[x["new"]].append(x)
    new_collisions = {
        k: [{"id": v["id"], "name": v["name"], "old": v["old"]} for v in vs]
        for k, vs in new_dups.items()
        if len(vs) > 1
    }

    out = {
        "shop": len(shop),
        "vault_published": vault["published"],
        "union": len(items),
        "already_unified": len(same),
        "need": len(need),
        "wave1": len(wave1),
        "wave1_dropped_dup_dest": [
            {"id": x["id"], "name": x["name"], "old": x["old"], "new": x["new"]}
            for x in dropped
        ],
        "wave2_overwrite": len(wave2),
        "new_collisions": new_collisions,
        "wave1_copies": [
            {
                "id": x["id"],
                "name": x["name"],
                "old": x["old"],
                "new": x["new"],
                "normalized": x["normalized"],
                "family": x["family"],
                "source": x["source"],
                "in_shop": x.get("in_shop"),
                "in_vault": x.get("in_vault"),
            }
            for x in sorted(wave1, key=lambda r: r["old"])
        ],
        "wave2_copies": [
            {
                "id": x["id"],
                "name": x["name"],
                "old": x["old"],
                "new": x["new"],
                "normalized": x["normalized"],
                "family": x["family"],
                "source": x["source"],
                "occupied_by": x["occupied_by"],
            }
            for x in sorted(wave2, key=lambda r: r["old"])
        ],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT} union={out['union']} same={out['already_unified']} "
        f"wave1={out['wave1']} wave2={out['wave2_overwrite']} "
        f"new_collisions={len(new_collisions)}"
    )
    for x in out["wave2_copies"]:
        o = x["occupied_by"]
        print(
            f"  wave2 {x['name']} {x['old']}->{x['new']} occupied by "
            f"{o['name']} {o['old']}->{o['new']}"
        )


if __name__ == "__main__":
    main()
