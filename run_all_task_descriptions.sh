#!/bin/bash
set -euo pipefail

# ベースディレクトリ
EXAMPLES_DIR="prompts/task_examples"
OUTDIR="outputs/long_outputs"

# 共通オプション
IN_CONTEXT="prompts/in_context.txt"
TAIL="prompts/tail_instructions_long.txt"
MODEL="gpt-4o-mini"
TEMP=0.5

mkdir -p "$OUTDIR"

for qa in "$EXAMPLES_DIR"/*.txt; do
    task_name=$(basename "$qa" .txt)
    echo "[RUN] $task_name"

    uv run make_long_descriptions.py \
        --examples-dir "$EXAMPLES_DIR" \
        --outdir "$OUTDIR" \
        --in-context "$IN_CONTEXT" \
        --tail "$TAIL" \
        --model "$MODEL" \
        --temperature "$TEMP"
done

