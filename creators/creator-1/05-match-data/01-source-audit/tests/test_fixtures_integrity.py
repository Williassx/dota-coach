"""Integrity checks for the C1-05-01 small provenance fixtures (unit tests).

Fixtures are tiny permitted samples with recorded provenance, not bulk data
and not micro-action data. These tests pin their shape and the no-personal-data
rule; they do not fetch anything from the network.
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE.parent / "fixtures"

PERSONAL_KEYS = ("account_id", "personaname", "steamid", "avatar", "name")


def load_json(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class FixtureIntegrityTests(unittest.TestCase):
    def test_herostats_sample_shape(self):
        doc = load_json("opendota-herostats-sample.json")
        recs = doc if isinstance(doc, list) else doc.get("sample", [])
        self.assertEqual(len(recs), 3)
        for rec in recs:
            for field in ("1_pick", "1_win", "attack_point", "agi_gain"):
                self.assertIn(field, rec)

    def test_publicmatches_sample_shape(self):
        doc = load_json("opendota-publicmatches-sample.json")
        self.assertEqual(doc["sample_count"], 5)
        self.assertEqual(len(doc["sample"]), 5)
        for rec in doc["sample"]:
            for field in ("match_id", "match_seq_num", "duration",
                          "radiant_team", "dire_team"):
                self.assertIn(field, rec)
            self.assertEqual(len(rec["radiant_team"]), 5)
            self.assertEqual(len(rec["dire_team"]), 5)

    def test_unfinished_matches_visible_for_filter(self):
        doc = load_json("opendota-publicmatches-sample.json")
        unfinished = [r for r in doc["sample"] if r["duration"] == 0]
        self.assertGreater(len(unfinished), 0,
                           "sample must show unfinished matches so the "
                           "duration > 0 import filter stays justified")

    def test_no_personal_data_in_opendota_samples(self):
        for name in ("opendota-herostats-sample.json",
                     "opendota-publicmatches-sample.json"):
            text = (FIX / name).read_text(encoding="utf-8").lower()
            for key in PERSONAL_KEYS:
                self.assertNotIn(f'"{key}"', text)

    def test_dota2ru_head_provenance(self):
        doc = load_json("dota2ru-matches-page-head.json")
        self.assertEqual(doc["source"], "https://dota2.ru/esport/matches/")
        self.assertEqual(doc["full_bytes"], 259592)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", doc["full_sha256"]))
        self.assertLessEqual(len(doc["head"].encode("utf-8")),
                             doc["head_bytes"])

    def test_dota2ru_robots_rules(self):
        raw = (FIX / "dota2ru-robots.txt").read_bytes()
        self.assertEqual(len(raw), 1753)
        text = raw.decode("utf-8")
        self.assertIn("Disallow:", text)
        self.assertIn("/esport/matches/", text)


if __name__ == "__main__":
    unittest.main()
