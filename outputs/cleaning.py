#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path("long_outputs")

def clean_text(text: str) -> str:
    # 改行2つ以上のあとは削除
    parts = re.split(r"\n{2,}", text, maxsplit=1)
    return parts[0].strip()

def main():
    for file in ROOT.rglob("*.txt"):
        if not file.is_file():
            continue

        original = file.read_text()
        cleaned = clean_text(original)

        if cleaned != original.strip():
            print(f"[CLEANED] {file}")
            file.write_text(cleaned + "\n")

if __name__ == "__main__":
    main()

