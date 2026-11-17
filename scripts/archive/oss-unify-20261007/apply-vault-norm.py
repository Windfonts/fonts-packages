#!/usr/bin/env python3
"""Emit two-phase SQL to set vault normalized_name + oss_path to family short.

Only wave1 ids that exist in vault. Skip if dest normalized_name already taken
by another id. Wave2 overwrite rows are listed, not applied.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = json.loads((HERE / "map.json").read_text(encoding="utf-8"))
VAULT = json.loads((HERE / "vault-fonts.json").read_text(encoding="utf-8"))
OUT = HERE / "apply-vault-norm.sql"


def esc(s: str) -> str:
    return s.replace("'", "''")


def main() -> None:
    v_by_id = {r["id"]: r for r in VAULT["rows"]}
    taken = {}
    for r in VAULT["rows"]:
        if r.get("status") == "published":
            taken[str(r.get("normalized_name") or "").lower()] = r["id"]

    rows = []
    skipped = []
    for rec in MAP["wave1_copies"]:
        vr = v_by_id.get(rec["id"])
        if not vr:
            continue
        new = rec["new"]
        old = str(vr.get("normalized_name") or "")
        if old.lower() == new:
            continue
        owner = taken.get(new)
        if owner and owner != rec["id"]:
            skipped.append({"id": rec["id"], "name": rec["name"], "old": old, "new": new, "taken_by": owner})
            continue
        rows.append({"id": rec["id"], "old": old, "new": new, "name": rec["name"]})
        taken[new] = rec["id"]

    lines = [
        "PRAGMA busy_timeout=30000;",
        "BEGIN IMMEDIATE;",
    ]
    if rows:
        ids = ",".join("'" + r["id"] + "'" for r in rows)
        lines.append(
            "UPDATE fonts SET normalized_name = normalized_name || '__tmp' "
            f"WHERE id IN ({ids});"
        )
    for r in rows:
        tmp = esc(r["old"] + "__tmp")
        new = esc(r["new"])
        oss = esc("/fonts-packages/" + r["new"])
        lines.append(
            "UPDATE fonts SET normalized_name = '"
            + new
            + "', oss_path = '"
            + oss
            + "' WHERE id = '"
            + r["id"]
            + "' AND normalized_name = '"
            + tmp
            + "';"
        )
    lines.append("COMMIT;")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "apply-vault-norm-expected.json").write_text(
        json.dumps({"n": len(rows), "skipped": skipped, "rows": rows}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} updates={len(rows)} skipped_taken={len(skipped)}")
    for s in skipped:
        print("  skip", s)


if __name__ == "__main__":
    main()
