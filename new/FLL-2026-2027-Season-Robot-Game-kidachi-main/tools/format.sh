reload
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "$0")/.." && pwd)"
TARGETS=(
  "$ROOT_DIR/runs"
  "$ROOT_DIR/selector.py"
  "$ROOT_DIR/setup.py"
  "$ROOT_DIR/utils"
)

if ! command -v ruff >/dev/null 2>&1; then
  echo "ruff が見つかりません。'pip install -r requirements.txt' を実行してください。" >&2
  exit 1
fi

if ! command -v black >/dev/null 2>&1; then
  echo "black が見つかりません。'pip install -r requirements.txt' を実行してください。" >&2
  exit 1
fi

echo "== Ruff (lint + auto-fix) =="
ruff check "${TARGETS[@]}" --fix

echo "== Ruff (format) =="
ruff format "${TARGETS[@]}"

echo "== Black (format) =="
black "${TARGETS[@]}"

echo "完了しました。"
