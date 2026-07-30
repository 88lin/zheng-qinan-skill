#!/usr/bin/env python3
"""search.py — 郑钦安三书通用检索。

用法(skill 装在任意目录,下面用 S 代指 "${CLAUDE_SKILL_DIR}/scripts/search.py"):
  python3 "$S" <term>                     # 三份索引 + 全文回退
  python3 "$S" <term> --book yilizhenchuan
  python3 "$S" <term> --index formulas    # 只走该索引,不回退全文
  python3 "$S" <term> --limit 15          # 每组最多输出条数
  python3 "$S" <term> --show-full         # 输出完整段落(受字数上限约束)
  python3 "$S" --id yilizhenchuan#j2-s001 # 按稳定 doc ID 取整段

对输入 <term>:
1. 先在三份索引(formulas/symptoms/themes)中查同名 key,命中则输出全部引用条目;
   一个词同时属于多份索引时,三组结果都会给出。
2. 三份索引都没有同名 key 时,回退到全文检索,按 book+juan+section 顺序返回摘录。
   指定 --index 时不做全文回退,以免"强制走索引"被静默改写成全文搜索。
3. 原词无命中时,自动按 indexes/variants.json 做繁体/异体 → 简体归一化后重试一次
   (语料本身为简体;--no-variants 可关闭)。

输出每条含:
  引用: <doc_id>   出处: 《书名》 卷N  <标题>
  摘录: <上下文摘录>   或   原文: <完整段落,超长时截断并提示>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SKILL_ROOT = Path(__file__).resolve().parents[1]
INDEXES_DIR = SKILL_ROOT / "indexes"
REFERENCES_DIR = SKILL_ROOT / "references"

BOOK_TITLES = {
    "yilizhenchuan": "医理真传",
    "yifayuantong": "医法圆通",
    "shanghanheng": "伤寒恒论",
}
INDEX_NAMES = ("formulas", "symptoms", "themes")

SECTION_ID_PATTERN = re.compile(r"<!-- id: ([^\s>]+) -->[ \t]*\r?\n")
DOC_ID_PATTERN = re.compile(r"^[a-z]+#j\d+-s\d+$")

# 单段与单次调用的输出上限:三书里最长的段落接近 3 万字,不设上限会挤爆调用方的上下文。
DEFAULT_MAX_CHARS = 4000
DEFAULT_MAX_TOTAL_CHARS = 20000

SAFETY_NOTICE = (
    "安全提示：以下仅为郑钦安三书的文本定位，不构成诊断、辨证、选方或剂量建议；"
    "原文中的药名、用量与煎服法仅供文献查证。"
)


def parse_sections(text: str, book: str) -> list[dict]:
    """Parse stable-ID sections from one reference markdown document.

    Splitting on the id anchors keeps heading-only sections addressable. A
    ``heading + lazy body`` regex cannot: when a section body is empty, the
    lazy body expands past the next anchor and silently swallows the following
    section, which both hides doc IDs and mis-attributes their text.
    """
    sections: list[dict] = []
    parts = SECTION_ID_PATTERN.split(text)
    for section_id, chunk in zip(parts[1::2], parts[2::2]):
        section_id = section_id.strip()
        lines = chunk.splitlines()
        title, body_start = "", 0
        if lines and lines[0].startswith("### "):
            title, body_start = lines[0][4:].strip(), 1
        juan_match = re.search(r"#j(\d+)-s(\d+)", section_id)
        sections.append(
            {
                "book": book,
                "juan": int(juan_match.group(1)) if juan_match else 0,
                "id": section_id,
                "title": title,
                "text": "\n".join(lines[body_start:]).strip(),
            }
        )
    return sections


_sections_cache: list[dict] | None = None


def load_sections() -> list[dict]:
    """Load full sections rebuilt from the reference markdown files (cached)."""
    global _sections_cache
    if _sections_cache is None:
        sections: list[dict] = []
        for book in BOOK_TITLES:
            md_path = REFERENCES_DIR / f"{book}.md"
            if not md_path.exists():
                continue
            sections.extend(parse_sections(md_path.read_text(encoding="utf-8"), book))
        _sections_cache = sections
    return _sections_cache


def section_map() -> dict[str, dict]:
    return {s["id"]: s for s in load_sections()}


_variants_cache: dict[str, str] | None = None


def load_variants() -> dict[str, str]:
    """繁体/异体 → 简体 单字映射;文件缺失时返回空表(功能降级,不报错)。"""
    global _variants_cache
    if _variants_cache is None:
        path = INDEXES_DIR / "variants.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            _variants_cache = data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            _variants_cache = {}
    return _variants_cache


def to_simplified(term: str) -> str:
    variants = load_variants()
    return "".join(variants.get(char, char) for char in term)


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
    index = json.loads(path.read_text(encoding="utf-8"))
    return index.get(term)


def full_text_search(sections: list[dict], term: str, book: str | None) -> list[dict]:
    results = []
    for section in sections:
        if book and section["book"] != book:
            continue
        if term in section["title"] or term in section["text"]:
            results.append(
                {
                    "id": section["id"],
                    "book": section["book"],
                    "juan": section["juan"],
                    "title": section["title"],
                    "excerpt": build_excerpt(section["text"], term),
                    "text": section["text"],
                }
            )
    return results


def collect_groups(term: str, index_name: str | None, book: str | None) -> list[tuple[str, list[dict]]]:
    """Index lookup first (all matching indexes), then full-text fallback."""
    groups: list[tuple[str, list[dict]]] = []
    names = (index_name,) if index_name else INDEX_NAMES
    for name in names:
        hits = search_index(term, name) or []
        hits = [h for h in hits if book is None or h["book"] == book]
        if hits:
            groups.append((f"索引: {name}", hits))
    if groups:
        return groups
    if index_name:
        # --index 表示"只用这份索引";静默回退到全文会让调用方误以为索引里有该词。
        return []
    hits = full_text_search(load_sections(), term, book)
    return [("全文检索", hits)] if hits else []


def format_source(hit: dict) -> str:
    book_zh = BOOK_TITLES.get(hit["book"], hit["book"])
    juan = f"卷{hit['juan']}" if hit.get("juan") else "卷首"
    return f"《{book_zh}》 {juan}   {hit.get('title', '')}".rstrip()


def print_hit(hit: dict, show_full: bool, max_chars: int) -> int:
    """Print one hit; return the number of body characters printed."""
    print(f"引用: {hit['id']}")
    print(f"出处: {format_source(hit)}")
    text = hit.get("text") or ""
    if show_full:
        if text:
            body = text
            if max_chars and len(body) > max_chars:
                body = (
                    body[:max_chars]
                    + f"\n…（本段共 {len(text)} 字，已截断至 {max_chars} 字；"
                    f"用 --max-chars 0 取全文，或 --id {hit['id']} 单独打开）"
                )
            print(f"原文:\n{body}")
            print()
            return len(body)
        print(f"摘录: {hit.get('excerpt') or ''}")
        print(
            f"警告: 无法在 references/ 中定位 {hit['id']} 的正文，已退回索引摘录；"
            "索引与语料可能不一致，请核对 indexes/section-manifest.json。"
        )
        print()
        return len(hit.get("excerpt") or "")
    body = hit.get("excerpt") or text[:200]
    print(f"摘录: {body}")
    print()
    return len(body)


def print_groups(
    groups: list[tuple[str, list[dict]]],
    sections_by_id: dict[str, dict],
    show_full: bool,
    limit: int,
    max_chars: int,
    max_total_chars: int,
) -> None:
    printed_chars = 0
    stopped = False
    for label, hits in groups:
        shown = hits[: limit or None]
        suffix = f"（共 {len(hits)} 条，显示 {len(shown)} 条）" if len(shown) < len(hits) else f"{len(hits)} 条"
        print(f"[{label}] {suffix}")
        for hit in shown:
            if stopped:
                continue
            if max_total_chars and printed_chars >= max_total_chars:
                print(
                    f"…（本次输出已达 {max_total_chars} 字上限，剩余条目未展开；"
                    "请缩小 --limit、去掉 --show-full，或用 --id 逐段打开）"
                )
                print()
                stopped = True
                continue
            section = sections_by_id.get(hit["id"], {})
            enriched = {**hit, "text": hit.get("text") or section.get("text", "")}
            printed_chars += print_hit(enriched, show_full, max_chars)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("term", nargs="?", help="要查的方名/症状/主题/自由词,或直接给 doc ID")
    parser.add_argument("--id", dest="doc_id", help="按稳定 doc ID 取整段,例 yilizhenchuan#j2-s001")
    parser.add_argument("--book", choices=list(BOOK_TITLES), help="限定某一本")
    parser.add_argument("--index", choices=list(INDEX_NAMES), help="只用某个索引(不回退全文)")
    parser.add_argument("--limit", type=int, default=20, help="每组最多输出条数,0=不限")
    parser.add_argument("--show-full", action="store_true", help="打印完整段落(默认只显示摘录)")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"单段正文字数上限,0=不限(默认 {DEFAULT_MAX_CHARS})",
    )
    parser.add_argument(
        "--max-total-chars",
        type=int,
        default=DEFAULT_MAX_TOTAL_CHARS,
        help=f"单次调用正文总字数上限,0=不限(默认 {DEFAULT_MAX_TOTAL_CHARS})",
    )
    parser.add_argument("--no-variants", action="store_true", help="关闭繁体/异体→简体归一化重试")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    doc_id = args.doc_id
    if doc_id is None and args.term and DOC_ID_PATTERN.match(args.term):
        doc_id = args.term
    if doc_id is None and not args.term:
        parser.error("需要 <term> 或 --id 之一")

    print(SAFETY_NOTICE)

    if doc_id:
        print(f"取段: {doc_id}\n" + "-" * 40)
        section = section_map().get(doc_id)
        if section is None:
            print(f"未找到 doc ID “{doc_id}”。可用 ID 见 indexes/section-manifest.json。")
            return 1
        print_hit({**section, "excerpt": None}, True, args.max_chars)
        return 0

    print(f"检索: {args.term}\n" + "-" * 40)
    groups = collect_groups(args.term, args.index, args.book)
    if not groups and not args.no_variants:
        normalized = to_simplified(args.term)
        if normalized != args.term:
            groups = collect_groups(normalized, args.index, args.book)
            if groups:
                print(f"提示: 原词未命中，已按繁体/异体→简体归一化重检索：{args.term} → {normalized}\n")

    if not groups:
        scope = f"{args.index} 索引" if args.index else "三书索引与全文"
        print(f"在{scope}中未找到 “{args.term}” 相关内容。")
        if args.index:
            print("提示: --index 表示只查这份索引，不会回退全文；去掉 --index 可做全文检索。")
        return 1

    print_groups(
        groups,
        section_map(),
        args.show_full,
        args.limit,
        args.max_chars,
        args.max_total_chars,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
