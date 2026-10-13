"""C1-11-01 conformance vs the proposal contract: stale/repeat/foreign."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRUSTED_SENDERS = ("coach-seat-0",)


def judge(case):
    if case["sender"] not in TRUSTED_SENDERS:
        return "foreign-sender"
    if case["orderId"] in case["seen"]:
        return "repeat"
    if case["revision"] < case["current_revision"]:
        return "stale-snapshot"
    return "ok"


class UiContractTests(unittest.TestCase):
    def load_cases(self):
        doc = json.loads((HERE / "fixtures" / "snapshots.json")
                         .read_text(encoding="utf-8"))
        return doc["cases"]

    def test_all_cases_judged(self):
        for case in self.load_cases():
            with self.subTest(case["name"]):
                self.assertEqual(judge(case), case["expect"])

    def test_old_answer_never_restores_mode(self):
        self.assertEqual(judge({"sender": "coach-seat-0", "orderId": "old",
                                "seen": [], "revision": 1,
                                "current_revision": 9}), "stale-snapshot")

    def test_integration_report_states_open_ui(self):
        text = (HERE.parent / "reports" / "ui-integration.md").read_text(
            encoding="utf-8")
        self.assertIn("Panorama", text)


if __name__ == "__main__":
    unittest.main()
