"""Checks for the C1-09-01 version binding on TEST configs (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from match_config import bind_version

FIVE = ["p1", "p2", "p3", "p4", "p5"]


def good():
    return {"launchVersion": "v1-test", "map": "template_map",
            "patch": "7.XX-test", "rosters": [list(FIVE), list(FIVE)],
            "content": "test-set"}


class MatchConfigTests(unittest.TestCase):
    def test_bound_launch(self):
        bound, reason = bind_version(good())
        self.assertEqual(reason, "ok")
        self.assertTrue(bound["bound"])

    def test_patch_null_blocks(self):
        cfg = good()
        cfg["patch"] = None
        _, reason = bind_version(cfg)
        self.assertEqual(reason, "patch-unconfirmed")

    def test_rosters_must_be_two_fives(self):
        cfg = good()
        cfg["rosters"] = [list(FIVE)]
        _, reason = bind_version(cfg)
        self.assertEqual(reason, "need-two-fives")

    def test_missing_field_open(self):
        cfg = good()
        del cfg["map"]
        _, reason = bind_version(cfg)
        self.assertEqual(reason, "missing-map")

    def test_spec_note_exists(self):
        text = (HERE.parent / "notes" / "match-spec.md").read_text(
            encoding="utf-8")
        self.assertIn("launchVersion", text)


if __name__ == "__main__":
    unittest.main()
