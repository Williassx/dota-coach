"""Checks for the C1-08-03 team distribution on TEST data (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from team_orders import TEAM_ORDERS, confirm, distribute

POLICIES = {"r1": ["t1", "t2"], "r4": ["t2"], "r5": ["t1", "t2"]}


class TeamOrderTests(unittest.TestCase):
    def test_agreed_order_set(self):
        self.assertEqual(set(TEAM_ORDERS),
                         {"attack", "retreat", "farm", "gather"})

    def test_distribution_needs_confirmation(self):
        assigns, reason = distribute("attack", ["r1", "r4"],
                                     ["t1", "t2"], POLICIES)
        self.assertEqual(reason, "ok")
        self.assertTrue(all(v["needs_confirm"] for v in assigns.values()))
        done, reason = confirm(assigns, ["r1", "r4"], 5, 5)
        self.assertEqual(reason, "ok")
        self.assertTrue(all(v["confirmed"] for v in done.values()))

    def test_conflict_and_unreachable_refused(self):
        _, reason = distribute("attack", ["r1", "r5"], ["t1", "t1"],
                               POLICIES)
        self.assertEqual(reason, "resource-conflict")
        _, reason = distribute("attack", ["r1", "r9"], ["t1", "t2"],
                               POLICIES)
        self.assertEqual(reason, "unreachable:r9")
        _, reason = distribute("attack", ["r4"], ["t1"], POLICIES)
        self.assertEqual(reason, "policy-refuses:r4:t1")

    def test_stale_confirmation_rejected(self):
        assigns, _ = distribute("farm", ["r5"], ["t2"], POLICIES)
        done, reason = confirm(assigns, ["r5"], 4, 5)
        self.assertIsNone(done)
        self.assertEqual(reason, "stale-confirmation")

    def test_team_orders_note_exists(self):
        text = (HERE.parent / "notes" / "team-orders.md").read_text(
            encoding="utf-8")
        self.assertIn("подтверждение", text.lower())


if __name__ == "__main__":
    unittest.main()
