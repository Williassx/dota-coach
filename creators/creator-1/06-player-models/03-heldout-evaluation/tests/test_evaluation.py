"""Checks for the C1-06-03 harness on synthetic heldout (unit tests)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from evaluate import PROTOCOL_REVISION, check_split, match_rate, run_evaluation


def load_doc():
    return json.loads((HERE / "fixtures" / "synthetic-heldout.json")
                      .read_text(encoding="utf-8"))


class EvaluationTests(unittest.TestCase):
    def test_disjoint_whole_match_split(self):
        ok, reason = check_split(load_doc()["parts"])
        self.assertTrue(ok, reason)

    def test_leak_detected(self):
        ok, reason = check_split({"train": [1, 2], "test": [2, 3]})
        self.assertFalse(ok)
        self.assertIn("leak:2", reason)

    def test_rates_on_synthetic_heldout(self):
        doc = load_doc()
        metrics = run_evaluation(
            doc["test_matches"],
            baseline_fn=lambda m: "attack",
            personal_fn=lambda m: m["reference"],
            shuffled_fn=lambda m: "hold")
        self.assertEqual(metrics["protocol"], PROTOCOL_REVISION)
        self.assertEqual(metrics["n"], 2)
        self.assertEqual(metrics["personal_rate"], 1.0)
        self.assertEqual(metrics["baseline_rate"], 0.5)

    def test_empty_references_is_none(self):
        self.assertIsNone(match_rate([], []))

    def test_report_states_limits(self):
        text = (HERE.parent / "reports" / "evaluation.md").read_text(
            encoding="utf-8")
        self.assertIn("TEST", text)
        self.assertIn("не доказывает сходство", text.lower())


if __name__ == "__main__":
    unittest.main()
