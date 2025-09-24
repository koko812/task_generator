#!/usr/bin/env python3
import argparse, subprocess, re, sys
from pathlib import Path

DESC_RE = re.compile(
    r"^Description\s+(\d+):\s*(.+?)(?=(?:\nDescription\s+\d+:)|\Z)",
    re.DOTALL | re.MULTILINE,
)

def run_generator(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError("formatted_generator.py failed")
    return proc.stdout

def split_descriptions(text):
    parts = DESC_RE.findall(text)
    # returns list of tuples [(idx_str, body_str), ...]
    return [(int(i), body.strip()) for i, body in parts]

def char_count_with_spaces(s: str) -> int:
    # 改行は空白に、連続空白はそのまま。ファイル名の数字は安定化させる。
    return len(s.replace("\r", "").replace("\n", " "))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--examples-dir", default="prompts/task_examples", help="qa-pairs を置いたディレクトリ")
    ap.add_argument("--outdir", default="outputs/long_descriptions", help="保存先ルート")
    ap.add_argument("--in-context", default=None)
    ap.add_argument("--tail", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--temperature", default=None)
    ap.add_argument("--outfile-prefix", default=None)
    ap.add_argument("--runner", default="uv", help="例: uv / python")
    ap.add_argument("--script", default="formatted_generator.py")
    args = ap.parse_args()

    examples_dir = Path(args.examples_dir)
    out_root = Path(args.outdir)

    qa_files = sorted(p for p in examples_dir.iterdir() if p.is_file())
    if not qa_files:
        print(f"No qa-pairs in {examples_dir}", file=sys.stderr)
        sys.exit(1)

    for qa in qa_files:
        task_name = qa.stem  # 例: arc_challenge
        out_dir = out_root / task_name
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [args.runner, "run", args.script, "--qa-pairs", str(qa)]
        if args.in_context:   cmd += ["--in-context", args.in_context]
        if args.tail:         cmd += ["--tail", args.tail]
        if args.model:        cmd += ["--model", args.model]
        if args.temperature:  cmd += ["--temperature", args.temperature]
        if args.outfile_prefix: cmd += ["--outfile-prefix", args.outfile_prefix]

        print(f"[RUN] {task_name}")
        out_text = run_generator(cmd)

        descs = split_descriptions(out_text)
        if not descs:
            print(f"  ! No 'Description X:' blocks found in {task_name}", file=sys.stderr)
            continue

        for idx, body in descs:
            char_num = char_count_with_spaces(body)
            out_path = out_dir / f"{char_num}_ex{idx}.txt"
            out_path.write_text(body + "\n")
            print(f"  -> {out_path}")

if __name__ == "__main__":
    main()

