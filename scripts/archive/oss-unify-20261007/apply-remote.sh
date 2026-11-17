#!/bin/bash
# Apply vault normalized_name + oss_path to family shorts on feicode-prod.
# Run as root after wave1 OSS copy. Two-phase UNIQUE-safe UPDATE.
set -euo pipefail

DATA=/www/wwwroot/fonts-vault/data
DB="$DATA/prod.db"
STAMP=20261007-oss-unify
WORK=/www/wwwroot/fonts-vault/data/_oss-unify-20261007
BAK_DB="$DATA/prod.db.bak-$STAMP"

die() { echo "FATAL: $*" >&2; exit 1; }

[[ -f "$WORK/expected.json" ]] || die "missing $WORK/expected.json"
[[ -f "$DB" ]] || die "missing $DB"
command -v sqlite3 >/dev/null || die "no sqlite3"
command -v python3 >/dev/null || die "no python3"
docker inspect fonts-vault >/dev/null 2>&1 || die "fonts-vault container missing"

echo "== filter expected against copy jsonl (skip empty-src / fail) =="
python3 - "$WORK/expected.json" "$WORK/copy-wave1.jsonl" "$WORK/copy-overwrite.jsonl" "$WORK/apply-rows.json" <<'PY'
import json, sys
exp = json.load(open(sys.argv[1]))
rows = exp["rows"] if isinstance(exp, dict) else exp
copy = {}
try:
    with open(sys.argv[2]) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            copy[o.get("id")] = o
except FileNotFoundError:
    print("WARN no copy jsonl; applying all expected rows", file=sys.stderr)
over = {}
try:
    with open(sys.argv[3]) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            over[o.get("id")] = o
except FileNotFoundError:
    pass
skip = []
keep = []
for r in rows:
    o = over.get(r["id"])
    if o and o.get("ok") and o.get("failed", 0) == 0:
        keep.append(r)
        continue
    c = copy.get(r["id"])
    if not c:
        skip.append({**r, "why": "no-copy-row"})
        continue
    if c.get("skip") == "empty-src":
        skip.append({**r, "why": "empty-src"})
        continue
    if c.get("failed", 0) > 0 or c.get("ok") is False:
        skip.append({**r, "why": "copy-fail", "failed": c.get("failed"), "errors": c.get("errors")})
        continue
    keep.append(r)
json.dump({"n": len(keep), "skipped": skip, "rows": keep}, open(sys.argv[4], "w"), ensure_ascii=False, indent=2)
print("apply_rows", len(keep), "skipped", len(skip))
for s in skip[:30]:
    print("  skip", s.get("name"), s.get("old"), "->", s.get("new"), s.get("why"))
if len(skip) > 30:
    print("  ...", len(skip) - 30, "more")
PY

echo "== pre-verify current normalized_name matches expected old =="
python3 - "$DB" "$WORK/apply-rows.json" <<'PY'
import json, sqlite3, sys
db, exp_path = sys.argv[1], sys.argv[2]
exp = json.load(open(exp_path))["rows"]
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
bad = []
missing = []
already = []
for r in exp:
    row = con.execute(
        "SELECT font_family, status, normalized_name, oss_path FROM fonts WHERE id=?",
        (r["id"],),
    ).fetchone()
    if row is None:
        missing.append(r["id"])
        continue
    got = str(row["normalized_name"] or "")
    if got.lower() == r["new"]:
        already.append(r["id"])
        continue
    if got != r["old"]:
        bad.append(
            {
                "id": r["id"],
                "want_old": r["old"],
                "got": got,
                "status": row["status"],
                "family": row["font_family"],
            }
        )
print("expected", len(exp), "already_new", len(already), "mismatch", len(bad), "missing", len(missing))
if missing or bad:
    print(json.dumps({"missing": missing[:10], "bad": bad[:10]}, ensure_ascii=False, indent=2))
    sys.exit(2)
PY

echo "== backup =="
if [[ -f "$BAK_DB" ]]; then
  echo "backup already exists: $BAK_DB"
else
  sqlite3 "$DB" ".backup '$BAK_DB'"
fi
ls -l "$BAK_DB"
python3 - "$BAK_DB" <<'PY'
import os, sys
p = sys.argv[1]
n = os.path.getsize(p)
print("bak_db_bytes", n)
if n < 1_000_000:
    raise SystemExit("backup too small")
PY

echo "== apply two-phase UPDATE normalized_name + oss_path =="
python3 - "$DB" "$WORK/apply-rows.json" <<'PY'
import json, sqlite3, sys
db, exp_path = sys.argv[1], sys.argv[2]
exp = json.load(open(exp_path))["rows"]
# skip already-new
con = sqlite3.connect(db, timeout=30)
con.execute("PRAGMA busy_timeout=30000")
todo = []
for r in exp:
    row = con.execute("SELECT normalized_name FROM fonts WHERE id=?", (r["id"],)).fetchone()
    if not row:
        raise SystemExit("missing " + r["id"])
    if str(row[0] or "").lower() == r["new"]:
        continue
    todo.append(r)
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
            (r["new"], oss, r["id"], r["old"] + "__tmp"),
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

echo "== post-verify =="
python3 - "$DB" "$WORK/apply-rows.json" <<'PY'
import json, sqlite3, sys
db, exp_path = sys.argv[1], sys.argv[2]
exp = json.load(open(exp_path))["rows"]
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
bad = []
tmp = con.execute("SELECT COUNT(*) FROM fonts WHERE normalized_name LIKE '%__tmp'").fetchone()[0]
if tmp:
    raise SystemExit(f"tmp leftover {tmp}")
for r in exp:
    row = con.execute(
        "SELECT normalized_name, oss_path, status FROM fonts WHERE id=?",
        (r["id"],),
    ).fetchone()
    want_oss = "/fonts-packages/" + r["new"]
    if not row or str(row[0]).lower() != r["new"] or row[1] != want_oss:
        bad.append({"id": r["id"], "want": r["new"], "got": None if not row else list(row)})
dups = con.execute(
    """
    SELECT lower(normalized_name) nn, COUNT(*) n
    FROM fonts WHERE status='published'
    GROUP BY 1 HAVING n>1
    """
).fetchall()
print("updated_ok", len(exp) - len(bad), "bad", len(bad), "published_dups", len(dups))
if bad or dups:
    print(json.dumps({"bad": bad[:10], "dups": dups[:10]}, ensure_ascii=False))
    sys.exit(3)
for name, want in (
    ("霞鹜文楷 Bright", "xwwkb"),
    ("HarmonyOS Sans", "harmsa"),
    ("カイソウ", "kisjp"),
    ("钟齐志莽行书", "zhi-mang-xing"),
    ("志莽行书", "ZhiMangXing"),
    ("CJK手写字", "cjksxz"),
    ("cjkFonts 全濑体", "AllSeto"),
    ("Kaisei Opti", "Kaiseiopti"),
    ("水木黑体", None),
):
    rows = con.execute(
        "SELECT name, font_family, normalized_name, oss_path, status FROM fonts WHERE name=?",
        (name,),
    ).fetchall()
    print("spot", name, rows)
PY

echo "== chown db (container user mysql:65533) =="
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

echo "== probe =="
probe() {
  local fam="$1" expect="$2"
  local tmp="/tmp/css-probe-norm-$fam.css"
  local code
  code=$(curl -sS -o "$tmp" -w '%{http_code}' --max-time 8 "http://127.0.0.1:4000/api/css?family=$fam" || echo ERR)
  local bytes=0
  [[ -f "$tmp" ]] && bytes=$(wc -c < "$tmp" | tr -d ' ')
  local face="no"
  grep -q '@font-face' "$tmp" 2>/dev/null && face=yes
  echo -n "PROBE $fam expect=$expect code=$code bytes=$bytes face=$face packs="
  grep -oE 'fonts-packages/[^/]+' "$tmp" 2>/dev/null | sort -u | tr '\n' ' '
  echo
  if [[ "$expect" == "200" && "$code" != "200" ]]; then
    echo "FAIL $fam" >&2
    return 1
  fi
  if [[ "$expect" == "200" && "$face" != "yes" ]]; then
    echo "FAIL $fam no @font-face" >&2
    return 1
  fi
  return 0
}

fail=0
probe wenfeng-xwwkb 200 || fail=1
probe wenfeng-xwbright 200 || fail=1
probe wenfeng-harmsa 200 || fail=1
probe wenfeng-harmony 200 || fail=1
probe wenfeng-kisjp 200 || fail=1
probe wenfeng-zmxs 200 || fail=1
probe wenfeng-zhi-mang-xing 200 || fail=1
probe wenfeng-hcdht 200 || fail=1
probe wenfeng-cjksxz 200 || fail=1
probe xwwkb 200 || fail=1

# pack path must be new short for renamed rows
python3 - <<'PY'
import re, sys
pairs = [
    ("wenfeng-xwwkb", "xwwkb"),
    ("wenfeng-xwbright", "xwwkb"),
    ("wenfeng-harmsa", "harmsa"),
    ("wenfeng-zhi-mang-xing", "zhi-mang-xing"),
    ("wenfeng-cjksxz", "cjksxz"),
]
fail = 0
for fam, want in pairs:
    p = f"/tmp/css-probe-norm-{fam}.css"
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
sys.exit(1 if fail else 0)
PY

if [[ "$fail" != "0" ]]; then
  die "probe failures"
fi
echo "APPLY_OK"
