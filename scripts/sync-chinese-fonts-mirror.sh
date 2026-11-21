#!/usr/bin/env bash
# Sync fonts-packages/npm-package to the WenPai-org/chinese-fonts GitHub mirror repo.
#
# Usage:
#   bash scripts/sync-chinese-fonts-mirror.sh [--dest /path/to/chinese-fonts] [--commit] [--push]

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/npm-package"
DEST_DIR="${CHINESE_FONTS_DIR:-/Users/feibisi-studio/Projects/chinese-fonts}"
DO_COMMIT=0
DO_PUSH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      DEST_DIR="$2"
      shift 2
      ;;
    --commit)
      DO_COMMIT=1
      shift
      ;;
    --push)
      DO_COMMIT=1
      DO_PUSH=1
      shift
      ;;
    -h|--help)
      sed -n '2,6p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Source npm-package directory not found: $SRC_DIR" >&2
  exit 1
fi

if [[ ! -d "$DEST_DIR/.git" ]]; then
  echo "Destination git repository not found: $DEST_DIR" >&2
  exit 1
fi

VERSION="$(node -p "require('$SRC_DIR/package.json').version")"
echo "[sync-chinese-fonts] Syncing $SRC_DIR (v$VERSION) -> $DEST_DIR"

COPYFILE_DISABLE=1 tar -C "$SRC_DIR" \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.npmrc' \
  --exclude='.DS_Store' \
  --exclude='._*' \
  -cf - . | tar -C "$DEST_DIR" -xf -

# Report any stale tracked files in destination that no longer exist in source
STALE_COUNT=0
while IFS= read -r rel; do
  [[ -z "$rel" ]] && continue
  if [[ ! -e "$SRC_DIR/$rel" ]]; then
    echo "[sync-chinese-fonts] WARN: tracked file in mirror missing from npm-package: $rel"
    STALE_COUNT=$((STALE_COUNT + 1))
  fi
done < <(git -C "$DEST_DIR" ls-files)

git -C "$DEST_DIR" status --short

if [[ "$DO_COMMIT" -eq 1 ]]; then
  cd "$DEST_DIR"
  git add -A
  if git diff --cached --quiet; then
    echo "[sync-chinese-fonts] Mirror already up to date; nothing to commit."
  else
    git commit -m "chore: sync @windfonts/chinese-fonts ${VERSION} from fonts-packages/npm-package"
    if [[ "$DO_PUSH" -eq 1 ]]; then
      git push origin main
    fi
  fi
fi

echo "[sync-chinese-fonts] Done (stale_warnings=$STALE_COUNT)."
