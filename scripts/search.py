#!/usr/bin/env python3
"""search.py — 郑钦安三书通用检索。

用法:
  python scripts/search.py <term>              # 全库搜(优先精确)
  python scripts/search.py <term> --book yilizhenchuan
  python scripts/search.py <term> --index formulas
  python scripts/search.py <term> --limit 15
  python scripts/search.py <term> --show-full

对输入 <term>:
1. 先在三份索引(formulas/symptoms/themes)中查有无同名 key,有则输出所有引用条目。
2. 若无同名 key,回退到全文 grep,按 book+juan+section 顺序返回段落摘录。

输出每条含:
  引用: <doc_id>   出处: <book> <juan> "<title>"
  摘录: <text 或 上下文摘录>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

SKILL_ROOT = Path(__file__).resolve().parents[1]
INDEXES_DIR = SKILL_ROOT / "indexes"
REFERENCES_DIR = SKILL_ROOT / "references"

BOOK_TITLES = {
    "yilizhenchuan": "医理真传",
    "yifayuantong": "医法圆通",
    "shanghanheng": "伤寒恒论",
}

SAFETY_NOTICE = (
    "安全提示：以下仅为郑钦安三书文本定位,不构成个人诊断/处方/剂量建议。"
    "附子/干姜/桂枝等热药、四逆汤辈、承气汤辈、癌症/阴实/孕产儿童等场景,"
    "须由合格中医师面诊,不得据此自行用药。"
)


def parse_sections(text: str, book: str) -> list[dict]:
    """Parse stable-ID sections from one reference markdown document."""
    sections = []
    pattern = re.compile(
        r"<!-- id: (?P<id>[^\s>]+) -->\r?\n"
        r"### (?P<title>[^\r\n]+)\r?\n\r?\n"
        r"(?P<body>.*?)(?=\r?\n<!-- id: |\Z)",
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        section_id = match.group("id").strip()
        juan_match = re.search(r"#j(\d+)-s(\d+)", section_id)
        sections.append(
            {
                "book": book,
                "juan": int(juan_match.group(1)) if juan_match else 0,
                "id": section_id,
                "title": match.group("title").strip(),
                "text": match.group("body").strip(),
            }
        )
    return sections


def load_sections() -> list[dict]:
    """Load full sections rebuilt from the reference markdown files."""
    sections = []
    for book, title in BOOK_TITLES.items():
        md_path = REFERENCES_DIR / f"{book}.md"
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8")
        sections.extend(parse_sections(text, book))
    return sections


def build_excerpt(text: str, term: str, radius: int = 100) -> str:
    idx = text.find(term)
    if idx < 0:
        return text[:radius] + ("…" if len(text) > radius else "")
    left = max(0, idx - radius)
    right = min(len(text), idx + len(term) + radius)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return f"{prefix}{text[left:right].replace(chr(10), ' ')}{suffix}"


def search_index(term: str, index_name: str) -> list[dict] | None:
    path = INDEXES_DIR / f"{index_name}.json"
    if not path.exists():
        return None
    idx = json.loads(path.read_text(encoding="utf-8"))
    return idx.get(term)


def full_text_search(sections: list[dict], term: str, book: str | None) -> list[dict]:
    results = []
    for s in sections:
        if book and s["book"] != book:
            continue
        if term in s["title"] or term in s["text"]:
            results.append({
                "id": s["id"],
                "book": s["book"],
                "juan": s["juan"],
                "title": s["title"],
                "excerpt": build_excerpt(s["text"], term),
                "text": s["text"],
            })
    return results


def print_hit(hit: dict, show_full: bool):
    book_zh = BOOK_TITLES.get(hit["book"], hit["book"])
    print(f"引用: {hit['id']}")
    print(f"出处: 《{book_zh}》 卷{hit['juan']}   {hit['title']}")
    if show_full and hit.get("text"):
        print(f"原文:\n{hit['text']}")
    else:
        print(f"摘录: {hit.get('excerpt') or hit.get('text','')[:200]}")
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("term", help="要查的方名/症状/主题/自由词")
    parser.add_argument("--book", choices=list(BOOK_TITLES), help="限定某一本")
    parser.add_argument("--index", choices=["formulas", "symptoms", "themes"], help="强制走某个索引")
    parser.add_argument("--limit", type=int, default=20, help="最多输出条数,0=不限")
    parser.add_argument("--show-full", action="store_true", help="打印完整段落(默认只显示摘录)")
    args = parser.parse_args()

    print(SAFETY_NOTICE)
    print(f"检索: {args.term}\n" + "-" * 40)

    sections = load_sections()
    section_map = {s["id"]: s for s in sections}

    # 1) index lookup (unless explicitly disabled)
    if args.index is None:
        for name in ("formulas", "symptoms", "themes"):
            hits = search_index(args.term, name)
            if not hits:
                continue
            filtered = [h for h in hits if args.book is None or h["book"] == args.book]
            if not filtered:
                continue
            print(f"[索引: {name}] {len(filtered)} 条")
            for h in filtered[: args.limit or None]:
                sec = section_map.get(h["id"], {})
                enriched = {**h, "text": sec.get("text", "")}
                print_hit(enriched, args.show_full)
            return 0
    else:
        hits = search_index(args.term, args.index)
        if hits:
            filtered = [h for h in hits if args.book is None or h["book"] == args.book]
            if filtered:
                print(f"[索引: {args.index}] {len(filtered)} 条")
                for h in filtered[: args.limit or None]:
                    sec = section_map.get(h["id"], {})
                    enriched = {**h, "text": sec.get("text", "")}
                    print_hit(enriched, args.show_full)
                return 0

    # 2) fallback: full-text scan
    results = full_text_search(sections, args.term, args.book)
    if not results:
        print(f"未找到 “{args.term}” 相关内容。")
        return 1
    print(f"[全文检索] {len(results)} 条")
    for r in results[: args.limit or None]:
        print_hit(r, args.show_full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
