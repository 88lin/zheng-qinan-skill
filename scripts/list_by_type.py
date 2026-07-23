#!/usr/bin/env python3
"""list_by_type.py — 列出郑钦安三书索引里所有的 key。

用法:
  python scripts/list_by_type.py formulas
  python scripts/list_by_type.py symptoms
  python scripts/list_by_type.py themes
  python scripts/list_by_type.py all          # 三份索引汇总
  python scripts/list_by_type.py formulas --with-counts   # 显示每个 key 命中的段数
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
INDEXES_DIR = SKILL_ROOT / "indexes"

NAMES = {"formulas": "方剂", "symptoms": "症状", "themes": "主题"}


def load(name: str) -> dict:
    path = INDEXES_DIR / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def render(name: str, idx: dict, with_counts: bool):
    print(f"\n=== {NAMES[name]} ({name}) — {len(idx)} keys ===\n")
    keys = sorted(idx.keys(), key=lambda k: (-len(idx[k]) if with_counts else 0, k))
    for k in keys:
        if with_counts:
            print(f"  {k}  ({len(idx[k])} 段)")
        else:
            print(f"  {k}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["formulas", "symptoms", "themes", "all"])
    parser.add_argument("--with-counts", action="store_true", help="附加每个 key 的命中段数")
    args = parser.parse_args()

    kinds = ["formulas", "symptoms", "themes"] if args.kind == "all" else [args.kind]
    for k in kinds:
        idx = load(k)
        render(k, idx, args.with_counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
