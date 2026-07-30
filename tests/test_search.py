from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "scripts" / "search.py"
sys.path.insert(0, str(ROOT))

from scripts import search  # noqa: E402


class SearchCliTests(unittest.TestCase):
    def run_search(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SEARCH), *args],
            cwd=ROOT,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

    def test_extended_han_characters_do_not_crash_windows_output(self) -> None:
        result = self.run_search("白通汤", "--limit", "5")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("引用:", result.stdout)
        self.assertNotIn("UnicodeEncodeError", result.stderr)

    def test_book_filter_does_not_report_success_for_empty_index_results(self) -> None:
        result = self.run_search(
            "补坎益离丹", "--index", "formulas", "--book", "yilizhenchuan"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("未找到", result.stdout)

    def test_section_parser_accepts_crlf_line_endings(self) -> None:
        text = (
            "# Test\r\n\r\n"
            "<!-- id: yilizhenchuan#j1-s001 -->\r\n"
            "### 乾坤大旨\r\n\r\n"
            "正文内容。\r\n"
        )

        sections = search.parse_sections(text, "yilizhenchuan")

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["id"], "yilizhenchuan#j1-s001")
        self.assertEqual(sections[0]["text"], "正文内容。")

    def test_heading_only_section_does_not_swallow_the_next_section(self) -> None:
        """Regression: an empty body used to merge the following section."""
        text = (
            "<!-- id: shanghanheng#j2-s000 -->\n### 卷2·首\n\n"
            "<!-- id: shanghanheng#j2-s001 -->\n### 太阳中篇\n\n凡寒伤营之证。\n"
        )

        sections = search.parse_sections(text, "shanghanheng")

        self.assertEqual([s["id"] for s in sections], ["shanghanheng#j2-s000", "shanghanheng#j2-s001"])
        self.assertEqual(sections[0]["text"], "")
        self.assertEqual(sections[1]["title"], "太阳中篇")
        self.assertEqual(sections[1]["text"], "凡寒伤营之证。")

    def test_full_text_hit_is_attributed_to_the_correct_section(self) -> None:
        result = self.run_search("烧针令其汗", "--limit", "3")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("shanghanheng#j1-s001", result.stdout)
        self.assertIn("太阳上篇", result.stdout)
        self.assertNotIn("shanghanheng#j1-s000", result.stdout)

    def test_doc_id_route_returns_the_whole_section(self) -> None:
        result = self.run_search("--id", "yilizhenchuan#j2-s001", "--max-chars", "0")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("阳虚症门问答", result.stdout)
        self.assertIn("原文:", result.stdout)
        self.assertGreater(len(result.stdout), 20000)

    def test_unknown_doc_id_fails_loudly(self) -> None:
        result = self.run_search("--id", "yilizhenchuan#j9-s999")

        self.assertEqual(result.returncode, 1)
        self.assertIn("未找到 doc ID", result.stdout)

    def test_bare_doc_id_argument_uses_the_doc_id_route(self) -> None:
        result = self.run_search("shanghanheng#j2-s001", "--max-chars", "300")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("太阳中篇", result.stdout)
        self.assertIn("已截断", result.stdout)

    def test_explicit_index_does_not_silently_fall_back_to_full_text(self) -> None:
        """奔豚 occurs in the corpus but is not a formulas key."""
        strict = self.run_search("奔豚", "--index", "formulas")
        default = self.run_search("奔豚", "--limit", "2")

        self.assertEqual(strict.returncode, 1)
        self.assertIn("formulas 索引中未找到", strict.stdout)
        self.assertIn("不会回退全文", strict.stdout)
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertIn("[全文检索]", default.stdout)

    def test_term_present_in_two_indexes_reports_both(self) -> None:
        result = self.run_search("回阳饮", "--limit", "1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[索引: formulas]", result.stdout)
        self.assertIn("[索引: themes]", result.stdout)

    def test_traditional_query_is_normalized_when_it_misses(self) -> None:
        result = self.run_search("白通湯", "--limit", "2")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("白通湯 → 白通汤", result.stdout)
        self.assertIn("引用:", result.stdout)

    def test_normalization_can_be_disabled(self) -> None:
        result = self.run_search("白通湯", "--no-variants")

        self.assertEqual(result.returncode, 1)
        self.assertIn("未找到", result.stdout)

    def test_character_forms_used_by_the_corpus_are_not_rewritten(self) -> None:
        """乾 exists in the corpus (乾坤大旨) and must not be normalized to 干."""
        self.assertEqual(search.to_simplified("乾坤大旨"), "乾坤大旨")
        result = self.run_search("乾坤大旨", "--limit", "1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("yilizhenchuan#j1-s001", result.stdout)

    def test_show_full_respects_the_per_section_budget(self) -> None:
        result = self.run_search("四逆汤", "--show-full", "--limit", "2", "--max-chars", "400")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("已截断至 400 字", result.stdout)
        self.assertLess(len(result.stdout), 4000)

    def test_show_full_respects_the_total_budget(self) -> None:
        result = self.run_search(
            "附子", "--show-full", "--limit", "20", "--max-chars", "0", "--max-total-chars", "3000"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("字上限", result.stdout)
        self.assertLess(len(result.stdout), 30000)


if __name__ == "__main__":
    unittest.main()
