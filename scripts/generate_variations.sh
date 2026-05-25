#!/usr/bin/env bash
set -euo pipefail

INPUT_MIDI="${1:-input.mid}"
OUTPUT_DIR="${2:-output/generated_variations}"
MAX_NEW_TOKENS="${3:-128}"
CHECKPOINT="${4:-moonbeam_style_model.pt}"

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
    --input "$INPUT_MIDI" \
    --output-dir "$OUTPUT_DIR" \
    --max-new-tokens "$MAX_NEW_TOKENS" \
    --checkpoint "$CHECKPOINT"

echo "Generated MIDI variations in $OUTPUT_DIR"
