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


if __name__ == "__main__":
    unittest.main()
