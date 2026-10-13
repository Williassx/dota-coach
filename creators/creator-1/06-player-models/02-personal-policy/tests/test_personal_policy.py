"""Checks for the C1-06-02 personal policy on TEST data (unit tests)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from personal_policy import BASELINE_ID, choose, to_arbiter_command


def load_doc():
    return json.loads((HERE / "fixtures" / "policy-contexts.json")
                      .read_text(encoding="utf-8"))


class PersonalPolicyTests(unittest.TestCase):
    def test_same_context_same_choice(self):
        doc = load_doc()
        ctx = doc["contexts"][0]
        prof = doc["profiles"]["TEST-aggressive"]
        first = choose(ctx, prof)
        second = choose(ctx, prof)
        self.assertEqual(first, second)

    def test_difference_explained_by_feature(self):
        doc = load_doc()
        ctx = doc["contexts"][0]
        agg, expl_agg = choose(ctx, doc["profiles"]["TEST-aggressive"])
        cau, expl_cau = choose(ctx, doc["profiles"]["TEST-cautious"])
        self.assertNotEqual(agg, cau)
        self.assertIn("aggression=", expl_agg)
        self.assertIn("aggression=", expl_cau)

    def test_empty_visible_waits(self):
        doc = load_doc()
        choice, expl = choose(doc["contexts"][1],
                              doc["profiles"]["TEST-aggressive"])
        self.assertEqual(choice["kind"], "wait")

    def test_command_fits_arbiter_shape(self):
        doc = load_doc()
        choice, _ = choose(doc["contexts"][0],
                           doc["profiles"]["TEST-aggressive"])
        cmd = to_arbiter_command(choice, "o1", 3)
        self.assertEqual(cmd["orderId"], "o1")
        self.assertEqual(cmd["source"], "ai")
        self.assertEqual(cmd["revision"], 3)

    def test_baseline_exists_as_reference(self):
        self.assertEqual(BASELINE_ID, "synthetic-baseline")


if __name__ == "__main__":
    unittest.main()
