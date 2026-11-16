#!/bin/bash
# After wave1 copy process exits: overwrite archived dests, refresh prefix list, audit copy phase.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/../.."
python3 - <<'PY'
import json
from pathlib import Path
p=Path('scripts/oss-unify-20261007/copy-wave1.jsonl')
ok=empty=mm=fail=0
for line in p.read_text().splitlines():
    o=json.loads(line)
    if o.get('skip')=='empty-src' or o.get('src')==0:
        empty+=1; continue
    errs=o.get('errors') or []
    mismatch_only=bool(errs) and all('dest-exists-size-mismatch' in str(e) for e in errs)
    if o.get('failed',0)>0 or o.get('ok') is False:
        if mismatch_only: mm+=1
        else: fail+=1
        continue
    ok+=1
print(f'wave1 jsonl ok={ok} empty={empty} mismatch={mm} fail={fail} lines={ok+empty+mm+fail}')
if fail:
    raise SystemExit('real copy failures')
if ok+empty+mm+fail < 569:
    raise SystemExit('copy incomplete')
PY

echo '== overwrite archived dests (live pack is still the old dir) =='
node scripts/oss-unify-20261007/copy-packs.js --go --overwrite-mismatch --conc=8 \
  --only=hclck2,hxbsb,hzpy,mysxt,pangzhenguipmzd \
  --log=copy-overwrite.jsonl

echo '== refresh OSS prefixes =='
node scripts/oss-unify-20261007/list-prefixes.js

echo '== verify copy phase =='
python3 scripts/oss-unify-20261007/verify-align.py --phase copy
echo FINISH_COPY_OK
