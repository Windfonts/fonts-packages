#!/usr/bin/env bash
# Build+upload one batch of norms from fonts/ (SUBSET_ONLY=full by default)
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

export SUBSET_ONLY="${SUBSET_ONLY:-full}"
mkdir -p fonts dist logs

echo "==== fonts in this batch ($BATCH_NAME) SUBSET_ONLY=$SUBSET_ONLY ===="
for n in "${NORMS[@]}"; do
  if [ ! -d "fonts/$n" ]; then
    echo "MISSING fonts/$n"
    exit 1
  fi
  echo " - $n: $(ls "fonts/$n")"
done

# Keep only requested norms in fonts/ for this build (park others)
PARK="$ROOT/_oss_batch_park"
mkdir -p "$PARK"
for d in fonts/*/; do
  [ -d "$d" ] || continue
  base=$(basename "$d")
  keep=0
  for n in "${NORMS[@]}"; do
    if [ "$base" = "$n" ]; then keep=1; break; fi
  done
  if [ "$keep" -eq 0 ]; then
    mv "$d" "$PARK/$base"
  fi
done

rm -rf dist fonts-subset
python3 python-scripts/analyze-fonts.py
python3 python-scripts/create-font-subsets.py
node scripts/convert.js
node scripts/upload.js

# park built sources back to _fonts_park staging
PARK_SRC="/Users/feibisi-studio/Projects/_fonts_park/oss-batch1-staging"
mkdir -p "$PARK_SRC"
for n in "${NORMS[@]}"; do
  if [ -d "fonts/$n" ]; then
    rm -rf "$PARK_SRC/$n"
    mv "fonts/$n" "$PARK_SRC/$n"
  fi
  # free local dist after upload
  if [ -d "dist/$n" ]; then
    rm -rf "dist/$n"
  fi
done

# restore parked unrelated fonts
for d in "$PARK"/*/; do
  [ -d "$d" ] || continue
  base=$(basename "$d")
  mv "$d" "fonts/$base"
done
rmdir "$PARK" 2>/dev/null || true

echo "==== $BATCH_NAME done ===="
