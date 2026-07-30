from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOKS = ("yilizhenchuan", "yifayuantong", "shanghanheng")
INDEXES = ("formulas", "symptoms", "themes")
ID_PATTERN = re.compile(r"<!-- id: ([^\s>]+) -->")
# 索引 key 应当是词，不是从句子里截出来的短语。顿号保留（方名本身含顿号，
# 例如 桂枝加龙、牡、附子汤）。
PHRASE_PUNCTUATION = re.compile(r"[，。；：？！,.\s]")

sys.path.insert(0, str(ROOT))
from scripts import search  # noqa: E402


class DataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference_ids = []
        cls.corpus_chars: set[str] = set()
        for book in BOOKS:
            text = (ROOT / "references" / f"{book}.md").read_text(encoding="utf-8")
            cls.reference_ids.extend(ID_PATTERN.findall(text))
            cls.corpus_chars |= set(text)

        cls.manifest = json.loads(
            (ROOT / "indexes" / "section-manifest.json").read_text(encoding="utf-8")
        )
        cls.manifest_ids = [item["id"] for item in cls.manifest]
        cls.manifest_by_id = {item["id"]: item for item in cls.manifest}
        cls.indexes = {
            name: json.loads(
                (ROOT / "indexes" / f"{name}.json").read_text(encoding="utf-8")
            )
            for name in INDEXES
        }
        cls.sections_by_id = {s["id"]: s for s in search.load_sections()}

    def test_reference_ids_are_unique_and_match_manifest(self) -> None:
        self.assertEqual(len(self.reference_ids), len(set(self.reference_ids)))
        self.assertEqual(set(self.reference_ids), set(self.manifest_ids))

    def test_parser_recovers_every_manifest_section(self) -> None:
        """The retrieval layer must reach every documented doc ID.

        A parser that merges sections silently hides doc IDs and mis-attributes
        their text to the previous heading, which produces wrong citations.
        """
        self.assertEqual(set(self.sections_by_id), set(self.manifest_ids))
        for item in self.manifest:
            with self.subTest(doc_id=item["id"]):
                section = self.sections_by_id[item["id"]]
                self.assertEqual(section["title"], item["title"])
                self.assertEqual(section["book"], item["book"])
                self.assertEqual(section["juan"], item["juan"])

    def test_index_hits_match_manifest_metadata(self) -> None:
        for index_name, index in self.indexes.items():
            for key, hits in index.items():
                for hit in hits:
                    with self.subTest(index=index_name, key=key, doc_id=hit["id"]):
                        entry = self.manifest_by_id.get(hit["id"])
                        self.assertIsNotNone(entry, "hit points at an unknown doc ID")
                        self.assertEqual(hit["title"], entry["title"])
                        self.assertEqual(hit["book"], entry["book"])
                        self.assertEqual(hit["juan"], entry["juan"])

    def test_index_keys_occur_in_the_sections_they_point_at(self) -> None:
        for index_name, index in self.indexes.items():
            for key, hits in index.items():
                for hit in hits:
                    section = self.sections_by_id[hit["id"]]
                    with self.subTest(index=index_name, key=key, doc_id=hit["id"]):
                        self.assertTrue(
                            key in section["text"] or key in section["title"],
                            f"{key!r} not present in {hit['id']}",
                        )

    def test_index_keys_are_terms_not_sentence_fragments(self) -> None:
        for index_name, index in self.indexes.items():
            for key in index:
                with self.subTest(index=index_name, key=key):
                    self.assertIsNone(
                        PHRASE_PUNCTUATION.search(key),
                        f"{key!r} looks like an extraction artifact",
                    )

    def test_variant_map_normalizes_advertised_traditional_titles(self) -> None:
        variants = json.loads(
            (ROOT / "indexes" / "variants.json").read_text(encoding="utf-8")
        )
        self.assertGreater(len(variants), 500)
        for variant, simplified in variants.items():
            with self.subTest(variant=variant):
                self.assertEqual(len(variant), 1)
                self.assertEqual(len(simplified), 1)
                self.assertIn(simplified, self.corpus_chars)
                # 语料自己在用的字形不能被改写，否则《乾坤大旨》这类标题会查不到。
                self.assertNotIn(variant, self.corpus_chars)

        for traditional, expected in (
            ("醫理真傳", "医理真传"),
            ("醫法圓通", "医法圆通"),
            ("傷寒恆論", "伤寒恒论"),
            ("白通湯", "白通汤"),
            ("潛陽丹", "潜阳丹"),
            ("坎中一陽", "坎中一阳"),
        ):
            with self.subTest(traditional=traditional):
                self.assertEqual(search.to_simplified(traditional), expected)

    def test_skill_evals_have_unique_ids_and_expected_outputs(self) -> None:
        payload = json.loads(
            (ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
        )
        evals = payload["evals"]
        ids = [item["id"] for item in evals]

        self.assertEqual(payload["skill_name"], "zheng-qinan")
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(evals), 3)
        for item in evals:
            self.assertTrue(item["prompt"].strip())
            self.assertTrue(item["expected_output"].strip())
            self.assertIsInstance(item["files"], list)


if __name__ == "__main__":
    unittest.main()
