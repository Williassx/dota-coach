"""Checks for the C1-09-02 opponent controller on TEST data (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from opponent import OPPONENT_POLICIES, opponent_choice, to_arbiter_command

VIS = [{"id": 611, "visible": True}, {"id": 612, "visible": True}]


class OpponentTests(unittest.TestCase):
    def test_limited_policy_set(self):
        self.assertEqual(set(OPPONENT_POLICIES), {"defensive", "greedy"})
        target, reason = opponent_choice("sneaky", VIS)
        self.assertIsNone(target)
        self.assertEqual(reason, "unknown-policy")

    def test_shared_controller_shape(self):
        target, reason = opponent_choice("greedy", VIS)
        self.assertEqual((target, reason), (611, "ok"))
        cmd = to_arbiter_command(target, "op1", 1)
        self.assertEqual(cmd["source"], "ai")
        self.assertEqual(cmd["side"], "opponent")

    def test_hidden_read_refused(self):
        poisoned = list(VIS) + [{"id": 999, "visible": True, "hidden": True}]
        target, reason = opponent_choice("defensive", poisoned)
        self.assertIsNone(target)
        self.assertEqual(reason, "hidden-read-refused")

    def test_invisible_entry_refused(self):
        target, reason = opponent_choice("greedy",
                                         [{"id": 1, "visible": False}])
        self.assertIsNone(target)
        self.assertEqual(reason, "not-allowed-observation")

    def test_no_target_without_coach(self):
        target, reason = opponent_choice("defensive", [])
        self.assertIsNone(target)
        self.assertEqual(reason, "no-target")


if __name__ == "__main__":
    unittest.main()
