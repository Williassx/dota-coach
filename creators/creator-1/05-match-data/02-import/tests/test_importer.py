"""Behavior checks for the C1-05-02 reproducible importer (unit tests)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from importer import (TRANSFORM_VERSION, import_batch, is_valid_teams,
                      normalize_record)


def load_raw():
    doc = json.loads((HERE / "fixtures" / "raw-sample.json")
                     .read_text(encoding="utf-8"))
    return doc["records"]


class ImporterTests(unittest.TestCase):
    def test_finished_record_normalizes_with_source(self):
        norm, reason = normalize_record(load_raw()[0])
        self.assertEqual(reason, "ok")
        self.assertEqual(norm["source"], "opendota-publicMatches")
        self.assertEqual(norm["transform"], TRANSFORM_VERSION)
        self.assertIsNone(norm["patch"])

    def test_unfinished_and_bad_teams_quarantined(self):
        _, reason = normalize_record(load_raw()[1])
        self.assertEqual(reason, "unfinished")
        _, reason = normalize_record(load_raw()[2])
        self.assertEqual(reason, "bad-teams")

    def test_batch_splits_and_dedups(self):
        norm, quar, note = import_batch(load_raw())
        self.assertEqual(len(norm), 1)
        reasons = sorted(q["reason"] for q in quar)
        self.assertEqual(reasons, ["bad-teams", "duplicate", "unfinished"])
        self.assertIn("computed", note)

    def test_reimport_creates_no_duplicates(self):
        first, _, _ = import_batch(load_raw())
        ids = [n["match_id"] for n in first]
        second, quar, _ = import_batch(load_raw(), existing_ids=ids)
        self.assertEqual(second, [])
        dupes = [q for q in quar if q["match_id"] in ids]
        self.assertTrue(dupes)
        self.assertTrue(all(q["reason"] == "duplicate" for q in dupes))

    def test_all_zero_teams_invalid(self):
        self.assertFalse(is_valid_teams({"radiant_team": [0] * 5,
                                         "dire_team": [1, 2, 3, 4, 5]}))


if __name__ == "__main__":
    unittest.main()
