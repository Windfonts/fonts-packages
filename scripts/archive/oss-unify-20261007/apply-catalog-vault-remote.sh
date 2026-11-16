#!/bin/bash
# Unpublish duplicate 寒蝉端黑; lowercase leftover vault normalized_name for 6 BDF + hcdht.
# Does not change oss_path. Does not overlay shop aliases.
set -euo pipefail

DATA=/www/wwwroot/fonts-vault/data
DB="$DATA/prod.db"
STAMP=20261007-catalog-mem
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

echo "== unpublish clduan + lowercase normalized_name =="
python3 - "$DB" <<'PY'
import sqlite3, sys
db = sys.argv[1]
con = sqlite3.connect(db, timeout=30)
con.execute("PRAGMA busy_timeout=30000")
con.row_factory = sqlite3.Row

# unpublish shop-dropped duplicate
cid = "84edb5e0-c977-4570-92a8-61f09cfeca2c"
row = con.execute("SELECT id, name, font_family, status FROM fonts WHERE id=?", (cid,)).fetchone()
if row is None:
    print("missing clduan row", cid)
else:
    if row["status"] == "published":
        con.execute("UPDATE fonts SET status='archived' WHERE id=?", (cid,))
        print("archived", cid, row["name"], row["font_family"])
    else:
        print("already", cid, row["status"])

jobs = [
    ("fd299190-67eb-4ea8-a7e5-ebf770362d2c", "hcdht"),
    ("c0754a33-c53b-46cd-96d6-501ba0adb1ff", "bestten"),
    ("9bcab8ba-4793-4309-b677-276a9ad87148", "chusung"),
    ("da9743c0-853d-41eb-896d-e9dcc7f98a08", "fonsung"),
    ("2aa12e56-6e03-4350-abc9-31ca73904e74", "lyusung"),
]
for fid, dest in jobs:
    row = con.execute(
        "SELECT id, name, normalized_name FROM fonts WHERE id=?", (fid,)
    ).fetchone()
    if row is None:
        print("missing", fid, dest)
        continue
    cur = row["normalized_name"]
    if cur == dest:
        print("already", fid, row["name"], cur)
        continue
    occ = con.execute(
        "SELECT id, name FROM fonts WHERE normalized_name=? AND id!=?",
        (dest, fid),
    ).fetchone()
    if occ:
        print("skip dest occupied", fid, cur, "->", dest, "occ", occ["id"], occ["name"])
        continue
    con.execute("UPDATE fonts SET normalized_name=? WHERE id=?", (dest, fid))
    print("normalized", fid, row["name"], cur, "->", dest)

con.commit()
print("COMMIT")
for fid, dest in jobs + [(cid, "Clduan")]:
    row = con.execute(
        "SELECT name, normalized_name, status, font_family FROM fonts WHERE id=?",
        (fid,),
    ).fetchone()
    if row:
        print("verify", fid[:8], row["name"], row["normalized_name"], row["status"], row["font_family"])
PY

echo "== done =="
