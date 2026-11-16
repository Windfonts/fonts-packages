#!/bin/bash
# Wave2 vault pointers: 4 ids only. Skip 水木 and shop-only Kaisei Opti.
# Two-phase UNIQUE-safe UPDATE. Drop steal aliases kaiseiopti→kisjp.
set -euo pipefail

DATA=/www/wwwroot/fonts-vault/data
DB="$DATA/prod.db"
STAMP=20261007-wave2
WORK=/www/wwwroot/fonts-vault/data/_oss-unify-20261007
BAK_DB="$DATA/prod.db.bak-$STAMP"
ALIAS="$DATA/family-aliases.json"
BAK_ALIAS="$DATA/family-aliases.json.bak-$STAMP"
ROWS="$WORK/apply-wave2-rows.json"

die() { echo "FATAL: $*" >&2; exit 1; }

[[ -f "$ROWS" ]] || die "missing $ROWS"
[[ -f "$DB" ]] || die "missing $DB"
[[ -f "$ALIAS" ]] || die "missing $ALIAS"
command -v sqlite3 >/dev/null || die "no sqlite3"
command -v python3 >/dev/null || die "no python3"
docker inspect fonts-vault >/dev/null 2>&1 || die "fonts-vault container missing"

echo "== preflight UNIQUE + current rows =="
python3 - "$DB" "$ROWS" <<'PY'
import json, sqlite3, sys
db, path = sys.argv[1], sys.argv[2]
exp = json.load(open(path))
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
dests = [r["new"] for r in exp["rows"]]
print("dests", dests)
for d in dests:
    hits = con.execute(
        "SELECT id, name, status, font_family, normalized_name, oss_path FROM fonts WHERE lower(normalized_name)=?",
        (d,),
    ).fetchall()
    print("OCCUPY", d, [dict(h) for h in hits] or "FREE")
    if hits:
        raise SystemExit(f"dest taken: {d}")
print("--- current ---")
bad = []
for r in exp["rows"]:
    row = con.execute(
        "SELECT id, name, status, font_family, normalized_name, oss_path FROM fonts WHERE id=?",
        (r["id"],),
    ).fetchone()
    if row is None:
        bad.append({"id": r["id"], "why": "missing"})
        continue
    got = str(row["normalized_name"] or "")
    print("ROW", dict(row))
    if got.lower() == r["new"]:
        print(" already_new", r["id"])
        continue
    if got.lower() != r["old_ci"]:
        bad.append({"id": r["id"], "want_old_ci": r["old_ci"], "got": got})
if bad:
    print("BAD", json.dumps(bad, ensure_ascii=False))
    raise SystemExit(2)
# occupants stay
stay = {
    "3efb5b84-658f-4f0c-8647-a6c4b1bb1b48": "cjksxz",
    "2b7561ea-edc0-4f55-85ec-18303243f156": "hcyjt",
    "35ffde1f-cf4a-4b0b-a6da-d177e8fa9e0f": "ddxsyt",
    "68a951f1-c727-42c7-831c-5e89c950911b": "kisjp",
    "7f48fdc1-8032-4d2d-8f94-5f64cce36943": "zhi-mang-xing",
    "789827af-a406-49b3-9bbb-f6df92784d32": "smht",
    "58c3fe9d-41fb-4507-95b5-b203233c3018": "mizukigothic",
}
for i, want in stay.items():
    row = con.execute(
        "SELECT name, normalized_name FROM fonts WHERE id=?", (i,)
    ).fetchone()
    if row is None:
        print("stay_missing", i, want)
        continue
    got = str(row["normalized_name"] or "").lower()
    print("STAY", i[:8], row["name"], got, "want", want)
    if got != want:
        raise SystemExit(f"occupant moved unexpectedly {i} {got} != {want}")
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
    bad2 = []
    for r in todo:
        oss = "/fonts-packages/" + r["new"]
        cur = con.execute(
            "UPDATE fonts SET normalized_name=?, oss_path=? WHERE id=? AND normalized_name=?",
            (r["new"], oss, r["id"], r["old_exact"] + "__tmp"),
        )
        if cur.rowcount != 1:
            bad2.append(r["id"])
    if bad2:
        raise SystemExit(f"phase2 missed {len(bad2)} e.g. {bad2[:5]}")
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

echo "== drop steal aliases kaiseiopti -> kisjp =="
if [[ ! -f "$BAK_ALIAS" ]]; then
  cp -a "$ALIAS" "$BAK_ALIAS"
fi
python3 - "$ALIAS" "$ROWS" <<'PY'
import json, sys
alias_path, rows_path = sys.argv[1], sys.argv[2]
exp = json.load(open(rows_path))
drop = set(exp.get("drop_alias_keys") or [])
doc = json.load(open(alias_path))
al = doc.get("aliases") if isinstance(doc, dict) and "aliases" in doc else doc
removed = {}
for k in list(al):
    if k in drop:
        removed[k] = al.pop(k)
json.dump(doc, open(alias_path, "w"), ensure_ascii=False, indent=2)
open(alias_path, "a").write("\n")
print("removed", removed)
print("alias_keys", len(al))
PY

echo "== post-verify =="
python3 - "$DB" "$ROWS" <<'PY'
import json, sqlite3, sys
db, path = sys.argv[1], sys.argv[2]
exp = json.load(open(path))["rows"]
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
bad = []
tmp = con.execute("SELECT COUNT(*) FROM fonts WHERE normalized_name LIKE '%__tmp'").fetchone()[0]
if tmp:
    raise SystemExit(f"tmp leftover {tmp}")
for r in exp:
    row = con.execute(
        "SELECT name, font_family, normalized_name, oss_path, status FROM fonts WHERE id=?",
        (r["id"],),
    ).fetchone()
    want_oss = "/fonts-packages/" + r["new"]
    print("AFTER", r["name"], row)
    if not row or str(row[2]).lower() != r["new"] or row[3] != want_oss:
        bad.append({"id": r["id"], "want": r["new"], "got": None if not row else list(row)})
print("updated_ok", len(exp) - len(bad), "bad", len(bad))
if bad:
    print(json.dumps(bad, ensure_ascii=False))
    raise SystemExit(3)
PY

echo "== chown db =="
sqlite3 "$DB" "PRAGMA wal_checkpoint(TRUNCATE);" || true
chown mysql:65533 "$DB" || true
chown mysql:65533 "$DB"-wal "$DB"-shm 2>/dev/null || true
chown mysql:65533 "$ALIAS" || true
ls -l "$DB" "$ALIAS"

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

echo "== probe =="
probe() {
  local fam="$1"
  local tmp="/www/wwwroot/fonts-vault/data/_oss-unify-20261007/css-probe-w2-$fam.css"
  local code
  code=$(curl -sS -o "$tmp" -w '%{http_code}' --max-time 8 "http://127.0.0.1:4000/api/css?family=$fam" || echo ERR)
  local bytes=0
  [[ -f "$tmp" ]] && bytes=$(wc -c < "$tmp" | tr -d ' ')
  local face="no"
  grep -q '@font-face' "$tmp" 2>/dev/null && face=yes
  echo -n "PROBE $fam code=$code bytes=$bytes face=$face packs="
  grep -oE 'fonts-packages/[^/]+' "$tmp" 2>/dev/null | sort -u | tr '\n' ' '
  echo
  [[ "$code" == "200" && "$face" == "yes" ]]
}

fail=0
probe wenfeng-cjkfqlt || fail=1
probe wenfeng-hcth || fail=1
probe wenfeng-ddxstyx || fail=1
probe wenfeng-zmxs || fail=1
probe wenfeng-cjksxz || fail=1
probe wenfeng-hcyjt || fail=1
probe wenfeng-ddxsyt || fail=1
probe wenfeng-kisjp || fail=1
probe wenfeng-zhi-mang-xing || fail=1
probe wenfeng-smht || fail=1
probe wenfeng-xwwkb || fail=1
probe wenfeng-hcdht || fail=1

python3 - <<'PY'
import re, sys
pairs = [
    ("wenfeng-cjkfqlt", "cjkfqlt"),
    ("wenfeng-hcth", "hcth"),
    ("wenfeng-ddxstyx", "ddxstyx"),
    ("wenfeng-zmxs", "zmxs"),
    ("wenfeng-cjksxz", "cjksxz"),
    ("wenfeng-hcyjt", "hcyjt"),
    ("wenfeng-ddxsyt", "ddxsyt"),
    ("wenfeng-kisjp", "kisjp"),
    ("wenfeng-zhi-mang-xing", "zhi-mang-xing"),
    ("wenfeng-smht", "smht"),
]
fail = 0
base = "/www/wwwroot/fonts-vault/data/_oss-unify-20261007/css-probe-w2-"
for fam, want in pairs:
    p = base + fam + ".css"
    try:
        t = open(p).read()
    except FileNotFoundError:
        print("missing", p)
        fail += 1
        continue
    packs = sorted(set(re.findall(r"fonts-packages/([^/]+)", t)))
    print("path", fam, packs, "want", want)
    if want not in packs:
        print("FAIL pack path", fam, packs)
        fail += 1
import urllib.error, urllib.request
for fam in ("wenfeng-kaiseiopti", "kaiseiopti", "wenfeng-kaiso"):
    code = None
    body = ""
    try:
        with urllib.request.urlopen("http://127.0.0.1:4000/api/css?family=" + fam, timeout=8) as r:
            body = r.read().decode("utf-8", "replace")
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
    except Exception as e:
        code = type(e).__name__
        body = ""
    packs = sorted(set(re.findall(r"fonts-packages/([^/]+)", body)))
    print("alias_or_missing", fam, "code", code, "packs", packs)
    if "kisjp" in packs:
        print("FAIL steal still maps to kisjp", fam)
        fail += 1
sys.exit(1 if fail else 0)
PY

if [[ "$fail" != "0" ]]; then
  die "probe failures"
fi
echo "WAVE2_APPLY_OK"
