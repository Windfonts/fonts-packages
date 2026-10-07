#!/bin/bash
# Add Regular to vault weights for 字咍粉圓 and 寒蝉高黑.
# OSS Regular/full already exists. Do not change normalized_name.
set -euo pipefail

DATA=/www/wwwroot/fonts-vault/data
DB="$DATA/prod.db"
STAMP=20261007-pack14
WORK=/www/wwwroot/fonts-vault/data/_oss-unify-20261007
BAK_DB="$DATA/prod.db.bak-$STAMP"

die() { echo "FATAL: $*" >&2; exit 1; }

[[ -f "$DB" ]] || die "missing $DB"
command -v sqlite3 >/dev/null || die "no sqlite3"
command -v python3 >/dev/null || die "no python3"
docker inspect fonts-vault >/dev/null 2>&1 || die "fonts-vault container missing"

echo "== backup db =="
if [[ -f "$BAK_DB" ]]; then
  echo "backup already exists: $BAK_DB"
else
  sqlite3 "$DB" ".backup '$BAK_DB'"
fi
ls -l "$BAK_DB"
python3 - "$BAK_DB" <<'PY'
import os, sys
n = os.path.getsize(sys.argv[1])
print("bak_db_bytes", n)
if n < 1_000_000:
    raise SystemExit("backup too small")
PY

echo "== merge Regular into weights =="
python3 - "$DB" <<'PY'
import json, sqlite3, sys
db = sys.argv[1]
jobs = [
    ("df9c334a-9152-4f25-801f-22ef87057517", "字咍粉圓"),
    ("23c746ef-3b93-44de-930c-128462b62323", "寒蝉高黑"),
]
con = sqlite3.connect(db, timeout=30)
con.execute("PRAGMA busy_timeout=30000")
con.row_factory = sqlite3.Row
for fid, name in jobs:
    row = con.execute("SELECT id, name, weights FROM fonts WHERE id=?", (fid,)).fetchone()
    if row is None:
        raise SystemExit("missing " + fid)
    w = json.loads(row["weights"] or "{}")
    if not isinstance(w, dict):
        raise SystemExit("weights not object " + fid)
    if "Regular" in w and isinstance(w["Regular"], dict) and w["Regular"].get("font_weight") == 400:
        print("already", fid, name, list(w))
        continue
    new = {"Regular": {"font_weight": 400}}
    for k, v in w.items():
        if k == "Regular":
            continue
        new[k] = v
    con.execute("UPDATE fonts SET weights=? WHERE id=?", (json.dumps(new, ensure_ascii=False), fid))
    print("updated", fid, name, "keys", list(new))
con.commit()
print("COMMIT")
for fid, name in jobs:
    row = con.execute("SELECT weights FROM fonts WHERE id=?", (fid,)).fetchone()
    print("verify", name, list(json.loads(row["weights"])))
PY

echo "== done =="
