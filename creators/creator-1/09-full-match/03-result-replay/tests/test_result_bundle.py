"""Checks for the C1-09-03 result bundle on TEST data (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from result_bundle import BUNDLE_VERSION, restore_review, seal_result


def good():
    return ("radiant-win", [{"orderId": "o1"}], {"transform": "v1"},
            [{"seq": 1}])


class ResultBundleTests(unittest.TestCase):
    def test_seal_and_restore(self):
        bundle, reason = seal_result(*good())
        self.assertEqual(reason, "ok")
        self.assertEqual(bundle["bundle"], BUNDLE_VERSION)
        review, reason = restore_review(bundle)
        self.assertEqual(reason, "ok")
        self.assertEqual(review["ending"], "radiant-win")

    def test_unconfirmed_ending_refused(self):
        ending, cmds, vers, evs = good()
        _, reason = seal_result("maybe-win", cmds, vers, evs)
        self.assertEqual(reason, "unconfirmed-ending")

    def test_review_stays_limited(self):
        bundle, _ = seal_result(*good())
        self.assertFalse(bundle["full_replay"])
        tampered = dict(bundle, full_replay=True)
        _, reason = restore_review(tampered)
        self.assertEqual(reason, "must-stay-limited")

    def test_foreign_bundle_rejected(self):
        _, reason = restore_review({"bundle": "other-v9"})
        self.assertEqual(reason, "unsupported-bundle")

    def test_format_note_exists(self):
        text = (HERE.parent / "notes" / "replay-format.md").read_text(
            encoding="utf-8")
        self.assertIn("ограниченный", text.lower())


if __name__ == "__main__":
    unittest.main()
