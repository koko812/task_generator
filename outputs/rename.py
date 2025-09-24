#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("long_outputs")

def main():
    for file in ROOT.rglob("*.txt"):
        if not file.is_file():
            continue

        # すでに char_ が付いているならスキップ
        if file.name.startswith("char_"):
            continue

        new_name = "char_" + file.name
        new_path = file.with_name(new_name)

        print(f"{file} -> {new_path}")
        file.rename(new_path)

if __name__ == "__main__":
    main()

