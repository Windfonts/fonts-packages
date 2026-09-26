#!/usr/bin/env bash
# Build+upload one batch of norms from _lxgw_staging into fonts/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BATCH_NAME="${1:-batch}"
shift || true
NORMS=("$@")
if [ ${#NORMS[@]} -eq 0 ]; then
  echo "usage: $0 <batch-name> Norm1 Norm2 ..."
  exit 1
fi

mkdir -p fonts dist logs
# clear fonts of previous batch by moving back to staging if any leftovers
for d in fonts/*/; do
  [ -d "$d" ] || continue
  base=$(basename "$d")
  mv "fonts/$base" "_lxgw_staging/$base" 2>/dev/null || true
done

for n in "${NORMS[@]}"; do
  if [ -d "_lxgw_staging/$n" ]; then
    mv "_lxgw_staging/$n" "fonts/$n"
  else
    echo "WARN missing $n"
  fi
done

echo "==== fonts in this batch ===="
ls fonts

rm -rf dist fonts-subset
python3 python-scripts/analyze-fonts.py
python3 python-scripts/create-font-subsets.py
node scripts/convert.js
node scripts/upload.js

# park built sources back
for n in "${NORMS[@]}"; do
  if [ -d "fonts/$n" ]; then
    mv "fonts/$n" "_lxgw_staging/$n"
  fi
done

echo "==== $BATCH_NAME done ===="
