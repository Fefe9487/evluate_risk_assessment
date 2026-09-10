# -*- coding: utf-8 -*-
"""Invariants for A01/A02/A03 expert review packs."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
ASSIGN = ROOT / "data" / "assignments.json"
LIBRARY = ROOT / "data" / "library.json"
IMAP = ROOT / "data" / "industryMapping.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ExpertPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assign = _load(ASSIGN)
        cls.lib = _load(LIBRARY)
        cls.imap = _load(IMAP)
        cls.lib_ids = [t["taskId"] for t in cls.lib["tasks"]]
        by_task = defaultdict(set)
        for row in cls.imap:
            by_task[row.get("taskId")].add(row.get("sector"))
        cls.construction = sorted(
            tid for tid in cls.lib_ids if "營造業" in by_task.get(tid, set())
        )

    def test_codes(self):
        codes = self.assign["codes"]
        self.assertEqual(set(codes), {"A01", "A02", "A03", "superpower"})
        self.assertEqual(codes["A01"]["role"], "inspector")
        self.assertEqual(codes["A02"]["role"], "inspector")
        self.assertEqual(codes["A03"]["role"], "inspector")
        self.assertEqual(codes["superpower"]["role"], "admin")

    def test_each_inspector_has_70_unique(self):
        for code in ("A01", "A02", "A03"):
            ids = self.assign["codes"][code]["taskIds"]
            self.assertEqual(len(ids), 70, code)
            self.assertEqual(len(set(ids)), 70, code)
            self.assertTrue(set(ids) <= set(self.lib_ids), code)

    def test_covers_all_library_tasks(self):
        union = set()
        for code in ("A01", "A02", "A03"):
            union |= set(self.assign["codes"][code]["taskIds"])
        self.assertEqual(union, set(self.lib_ids))
        self.assertEqual(len(self.lib_ids), 173)

    def test_construction_only_on_a01(self):
        a01 = set(self.assign["codes"]["A01"]["taskIds"])
        a02 = set(self.assign["codes"]["A02"]["taskIds"])
        a03 = set(self.assign["codes"]["A03"]["taskIds"])
        self.assertEqual(len(self.construction), 50)
        self.assertTrue(set(self.construction) <= a01)
        self.assertFalse(set(self.construction) & a02)
        self.assertFalse(set(self.construction) & a03)

    def test_pairwise_overlap(self):
        a01 = set(self.assign["codes"]["A01"]["taskIds"])
        a02 = set(self.assign["codes"]["A02"]["taskIds"])
        a03 = set(self.assign["codes"]["A03"]["taskIds"])
        self.assertEqual(len(a01 & a02 & a03), 0)
        self.assertEqual(len(a01 & a02), 10)
        self.assertEqual(len(a01 & a03), 10)
        self.assertEqual(len(a02 & a03), 17)
        ov = self.assign["overlap"]
        self.assertEqual(set(ov["A01_A02"]), a01 & a02)
        self.assertEqual(set(ov["A01_A03"]), a01 & a03)
        self.assertEqual(set(ov["A02_A03"]), a02 & a03)

    def test_a01_leads_with_construction(self):
        a01 = self.assign["codes"]["A01"]["taskIds"]
        self.assertEqual(a01[:50], self.assign["constructionTaskIds"])

    def test_index_gate_uses_localstorage_key(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("ra-phase1-expert-code", html)
        self.assertIn("gate-code", html)
        self.assertIn("assignments.json", html)


if __name__ == "__main__":
    unittest.main()
