#!/usr/bin/env python3
# save_as: dump_task_examples.py
"""
Usage:
  python dump_task_examples.py --src /path/to/eval_prompts.py --out ./task_examples
  python dump_task_examples.py --src https://raw.githubusercontent.com/SakanaAI/text-to-lora/refs/heads/main/src/hyper_llm_modulator/utils/eval_prompts.py --out ./task_examples --skip-empty
"""
import argparse
import os
import re
import sys
import ast
from pathlib import Path
from urllib.request import urlopen

def load_text(src: str) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        with urlopen(src) as r:
            return r.read().decode("utf-8", errors="replace")
    else:
        return Path(src).read_text(encoding="utf-8")

def extract_examples_ast(py_code: str):
    """
    安全寄り：ASTで IN_CONTEXT_EXAMPLES を辞書リテラルとして抽出＆評価。
    失敗したら None を返す（その後 exec フォールバック）。
    """
    try:
        module = ast.parse(py_code)
        for node in module.body:
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "IN_CONTEXT_EXAMPLES":
                        if isinstance(node.value, (ast.Dict)):
                            return ast.literal_eval(node.value)
        return None
    except Exception:
        return None

def extract_examples_exec(py_code: str):
    """
    フォールバック：最小限の名前空間で exec して取り出す。
    （外部コードを実行するので、信頼できるファイル/URLにのみ使用してください）
    """
    ns = {}
    exec(compile(py_code, "<eval_prompts.py>", "exec"), ns, ns)
    examples = ns.get("IN_CONTEXT_EXAMPLES", {})
    if not isinstance(examples, dict):
        raise ValueError("IN_CONTEXT_EXAMPLES が dict ではありません。")
    return examples

def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "unnamed"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="eval_prompts.py のパス or raw URL")
    ap.add_argument("--out", required=True, help="出力ディレクトリ")
    ap.add_argument("--skip-empty", action="store_true", help="中身が空のタスクはスキップ")
    args = ap.parse_args()

    py_code = load_text(args.src)
    examples = extract_examples_ast(py_code)
    if examples is None:
        # ASTで取れなければ exec にフォールバック
        examples = extract_examples_exec(py_code)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for key, val in examples.items():
        if not isinstance(val, str):
            # 文字列でない場合はスキップ
            continue
        if args.skip_empty and (val.strip() == ""):
            continue
        fname = f"{safe_name(str(key))}.txt"
        (out_dir / fname).write_text(val, encoding="utf-8")
        written += 1
        print(f"Wrote: {out_dir / fname}")

    if written == 0:
        print("No files written (IN_CONTEXT_EXAMPLES が空、または --skip-empty により全スキップ)。", file=sys.stderr)

if __name__ == "__main__":
    main()

