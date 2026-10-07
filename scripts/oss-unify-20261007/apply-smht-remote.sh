#!/bin/bash
# Point vault English 水木 (id 58c3fe9d) at dest smht. Dest UNIQUE must be free.
# Two-phase UNIQUE-safe UPDATE. Do not drop aliases. IPA still blocks /api/css.
set -euo pipefail

DATA=/www/wwwroot/fonts-vault/data
DB="$DATA/prod.db"
STAMP=20261007-smht
WORK=/www/wwwroot/fonts-vault/data/_oss-unify-20261007
BAK_DB="$DATA/prod.db.bak-$STAMP"
ROWS="$WORK/apply-smht-rows.json"

die() { echo "FATAL: $*" >&2; exit 1; }

[[ -f "$ROWS" ]] || die "missing $ROWS"
[[ -f "$DB" ]] || die "missing $DB"
command -v sqlite3 >/dev/null || die "no sqlite3"
command -v python3 >/dev/null || die "no python3"
docker inspect fonts-vault >/dev/null 2>&1 || die "fonts-vault container missing"

echo "== preflight UNIQUE + current row =="
python3 - "$DB" "$ROWS" <<'PY'
import json, sqlite3, sys
db, path = sys.argv[1], sys.argv[2]
exp = json.load(open(path))
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
r = exp["rows"][0]
dest = r["new"]
hits = con.execute(
    "SELECT id, name, status, font_family, normalized_name, oss_path FROM fonts WHERE lower(normalized_name)=?",
    (dest,),
).fetchall()
print("OCCUPY", dest, [dict(h) for h in hits] or "FREE")
if hits:
    raise SystemExit(f"dest taken: {dest}")
row = con.execute(
    "SELECT id, name, status, font_family, normalized_name, oss_path FROM fonts WHERE id=?",
    (r["id"],),
).fetchone()
if row is None:
    raise SystemExit("missing id " + r["id"])
print("ROW", dict(row))
got = str(row["normalized_name"] or "")
if got.lower() == r["new"]:
    print("already_new")
elif got.lower() != r["old_ci"]:
    raise SystemExit(f"unexpected old {got!r} want {r['old_ci']!r}")
print("PREFLIGHT_OK")
PY

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

echo "== two-phase UPDATE =="
python3 - "$DB" "$ROWS" <<'PY'
import json, sqlite3, sys
db, path = sys.argv[1], sys.argv[2]
exp = json.load(open(path))["rows"]
con = sqlite3.connect(db, timeout=30)
con.execute("PRAGMA busy_timeout=30000")
todo = []
for r in exp:
    row = con.execute("SELECT normalized_name FROM fonts WHERE id=?", (r["id"],)).fetchone()
    if not row:
        raise SystemExit("missing " + r["id"])
    got = str(row[0] or "")
    if got.lower() == r["new"]:
        continue
    todo.append({**r, "old_exact": got})
print("todo", len(todo), "already", len(exp) - len(todo))
if not todo:
    print("nothing to apply")
    raise SystemExit(0)
ids = [r["id"] for r in todo]
try:
    con.execute("BEGIN IMMEDIATE")
    q = "UPDATE fonts SET normalized_name = normalized_name || '__tmp' WHERE id IN ({})".format(
        ",".join("?" * len(ids))
    )
    cur = con.execute(q, ids)
    phase1 = cur.rowcount
    if phase1 != len(ids):
        raise SystemExit(f"phase1 rowcount {phase1} != {len(ids)}")
    for r in todo:
        oss = "/fonts-packages/" + r["new"]
        cur = con.execute(
            "UPDATE fonts SET normalized_name=?, oss_path=? WHERE id=? AND normalized_name=?",
            (r["new"], oss, r["id"], r["old_exact"] + "__tmp"),
        )
        if cur.rowcount != 1:
            raise SystemExit("phase2 missed " + r["id"])
    tmp = con.execute(
        "SELECT COUNT(*) FROM fonts WHERE normalized_name LIKE '%__tmp'"
    ).fetchone()[0]
    if tmp:
        raise SystemExit(f"tmp leftover {tmp}")
    dups = con.execute(
        """
        SELECT lower(normalized_name) nn, COUNT(*) n
        FROM fonts WHERE status='published'
        GROUP BY 1 HAVING n>1
        """
    ).fetchall()
    if dups:
        raise SystemExit("published normalized dups " + str(dups[:8]))
    con.execute("COMMIT")
    print("phase1", phase1, "phase2", len(todo), "committed")
except Exception:
    try:
        con.execute("ROLLBACK")
    except Exception:
        pass
    raise
finally:
    con.close()
PY

echo "== post-verify =="
python3 - "$DB" "$ROWS" <<'PY'
import json, sqlite3, sys
db, path = sys.argv[1], sys.argv[2]
r = json.load(open(path))["rows"][0]
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
row = con.execute(
    "SELECT name, font_family, normalized_name, oss_path, status FROM fonts WHERE id=?",
    (r["id"],),
).fetchone()
want_oss = "/fonts-packages/" + r["new"]
print("AFTER", row)
if not row or str(row[2]).lower() != r["new"] or row[3] != want_oss:
    raise SystemExit("post-verify fail " + str(row))
print("updated_ok")
PY

echo "== chown db =="
sqlite3 "$DB" "PRAGMA wal_checkpoint(TRUNCATE);" || true
chown mysql:65533 "$DB" || true
chown mysql:65533 "$DB"-wal "$DB"-shm 2>/dev/null || true
ls -l "$DB"

echo "== docker restart fonts-vault =="
docker restart fonts-vault
ok=0
for i in $(seq 1 40); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 2 "http://127.0.0.1:4000/api/css?family=wenfeng-xwwkb" || true)
  if [[ "$code" == "200" ]]; then ok=1; break; fi
  echo "wait $i code=$code"
  sleep 1
done
[[ "$ok" == "1" ]] || die "fonts-vault did not serve xwwkb after restart"

echo "== probe (smht IPA expected 500; xwwkb 200; pack path in DB already verified) =="
probe() {
  local fam="$1"
  local tmp="/www/wwwroot/fonts-vault/data/_oss-unify-20261007/css-probe-smht-$fam.css"
  local code
  code=$(curl -sS -o "$tmp" -w '%{http_code}' --max-time 8 "http://127.0.0.1:4000/api/css?family=$fam" || echo ERR)
  local bytes=0
  [[ -f "$tmp" ]] && bytes=$(wc -c < "$tmp" | tr -d ' ')
  echo "PROBE $fam code=$code bytes=$bytes body=$(head -c 180 "$tmp" | tr '\n' ' ')"
}
probe wenfeng-smht
probe wenfeng-xwwkb
python3 - "$DB" <<'PY'
import sqlite3, sys
con = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
row = con.execute(
    "SELECT id, name, font_family, normalized_name, oss_path FROM fonts WHERE id='58c3fe9d-41fb-4507-95b5-b203233c3018'"
).fetchone()
print("DB", row)
PY
echo "SMHT_APPLY_OK"
