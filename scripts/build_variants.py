#!/usr/bin/env python3
"""build_variants.py — 生成 indexes/variants.json（繁体/异体 → 简体 单字映射）。

为什么需要:
  SKILL.md 的触发词包含《醫理真傳》《醫法圓通》《傷寒恆論》等繁体写法，
  但语料是简体，繁体查询会零命中。search.py 在原词未命中时用这张表做一次
  归一化重试。

为什么是生成的而不是手写的:
  手写映射容易漏字、错字。这里用 zhconv 逐字推导，并且只收录
  "语料中不存在的字 → 语料中存在的字"，避免把《乾坤大旨》这类语料原有字形
  改写掉（乾 出现在语料中，因此不会被映射为 干）。

依赖:
  仅本脚本需要 zhconv（开发期依赖）:  python3 -m pip install zhconv
  search.py 与测试都不依赖 zhconv；variants.json 缺失时只是不做归一化。

用法:
  python3 scripts/build_variants.py            # 重新生成并写入
  python3 scripts/build_variants.py --check    # 只校验已提交文件是否为最新
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_DIR = SKILL_ROOT / "references"
OUTPUT_PATH = SKILL_ROOT / "indexes" / "variants.json"
BOOKS = ("yilizhenchuan", "yifayuantong", "shanghanheng")

# 基本区 + 扩展 A;三书用字未超出该范围。
CJK_START, CJK_END = 0x3400, 0x9FFF


def corpus_chars() -> set[str]:
    chars: set[str] = set()
    for book in BOOKS:
        chars |= set((REFERENCES_DIR / f"{book}.md").read_text(encoding="utf-8"))
    return chars


def build_map() -> dict[str, str]:
    try:
        import zhconv
    except ImportError:
        sys.exit("需要 zhconv 才能生成映射表: python3 -m pip install zhconv")

    present = corpus_chars()
    mapping: dict[str, str] = {}
    for code_point in range(CJK_START, CJK_END + 1):
        variant = chr(code_point)
        if variant in present:
            continue  # 语料自己在用的字形不改写
        simplified = zhconv.convert(variant, "zh-hans")
        if len(simplified) == 1 and simplified != variant and simplified in present:
            mapping[variant] = simplified
    return dict(sorted(mapping.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只比对，不写文件；不一致时退出码 1")
    args = parser.parse_args()

    mapping = build_map()
    payload = json.dumps(mapping, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

    if args.check:
        current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if current != payload:
            print(f"{OUTPUT_PATH.name} 与重新生成的结果不一致，请运行 python3 scripts/build_variants.py")
            return 1
        print(f"{OUTPUT_PATH.name} 已是最新（{len(mapping)} 条映射）")
        return 0

    OUTPUT_PATH.write_text(payload, encoding="utf-8")
    print(f"已写入 {OUTPUT_PATH.relative_to(SKILL_ROOT)}：{len(mapping)} 条映射")
    return 0


if __name__ == "__main__":
    sys.exit(main())
