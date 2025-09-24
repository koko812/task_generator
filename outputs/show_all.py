#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("long_outputs")

def main():
    for file in sorted(ROOT.rglob("*.txt")):
        if not file.is_file():
            continue

        text = file.read_text().strip()
        print("=" * 80)
        print(f"[{file}]")
        print(text)
        print("=" * 80, "\n")

if __name__ == "__main__":
    main()

