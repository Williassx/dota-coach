"""Checks for the C1-10-02 diagnostics builder on TEST data (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from diag_report import build_report, reproduce_plan


class DiagReportTests(unittest.TestCase):
    def test_report_links_error_to_command_and_versions(self):
        report, reason = build_report("stale-revision", "o7",
                                      {"transform": "c1-import-v1"},
                                      ["import", "normalize"])
        self.assertEqual(reason, "ok")
        self.assertEqual(report["orderId"], "o7")
        self.assertIn("transform", report["versions"])

    def test_secrets_fail_loudly(self):
        report, reason = build_report("boom", "o1",
                                      {"api_token": "zzz"}, ["s1"])
        self.assertIsNone(report)
        self.assertTrue(reason.startswith("forbidden:"))

    def test_steps_required(self):
        report, reason = build_report("boom", "o1", {}, [])
        self.assertIsNone(report)
        self.assertEqual(reason, "no-steps")

    def test_reproduce_plan_from_report(self):
        report, _ = build_report("boom", "o2", {"bundle": "c1-result-v1"},
                                 ["import", "decide"])
        plan = reproduce_plan(report)
        self.assertEqual(plan, ["step1:import", "step2:decide"])
        self.assertIsNone(reproduce_plan({"nope": 1}))

    def test_diagnostics_note_exists(self):
        text = (HERE.parent / "notes" / "diagnostics.md").read_text(
            encoding="utf-8")
        self.assertIn("секрет", text.lower())


if __name__ == "__main__":
    unittest.main()
