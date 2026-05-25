#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-output/generated_songs}"
BARS="${2:-32}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

if [[ -x ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="${PYTHON:-python3}"
fi

mkdir -p "$OUTPUT_DIR"

"$PYTHON" -m generation.batch \
    --output-dir "$OUTPUT_DIR" \
    --bars "$BARS"

echo "Generated MIDI songs in $OUTPUT_DIR"
