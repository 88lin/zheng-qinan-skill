from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOKS = ("yilizhenchuan", "yifayuantong", "shanghanheng")
INDEXES = ("formulas", "symptoms", "themes")
ID_PATTERN = re.compile(r"<!-- id: ([^\s>]+) -->")


class DataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference_ids = []
        for book in BOOKS:
            text = (ROOT / "references" / f"{book}.md").read_text(encoding="utf-8")
            cls.reference_ids.extend(ID_PATTERN.findall(text))

        cls.manifest = json.loads(
            (ROOT / "indexes" / "section-manifest.json").read_text(encoding="utf-8")
        )
        cls.manifest_ids = [item["id"] for item in cls.manifest]

    def test_reference_ids_are_unique_and_match_manifest(self) -> None:
        self.assertEqual(len(self.reference_ids), len(set(self.reference_ids)))
        self.assertEqual(set(self.reference_ids), set(self.manifest_ids))

    def test_index_hits_reference_existing_sections(self) -> None:
        manifest_ids = set(self.manifest_ids)

        for index_name in INDEXES:
            with self.subTest(index=index_name):
                index = json.loads(
                    (ROOT / "indexes" / f"{index_name}.json").read_text(
                        encoding="utf-8"
                    )
                )
                hit_ids = {
                    hit["id"] for hits in index.values() for hit in hits
                }
                self.assertLessEqual(hit_ids, manifest_ids)

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
