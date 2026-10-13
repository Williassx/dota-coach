"""Checks for the C1-05-03 replay gate on synthetic events (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from replay_gate import GATE_VERSION, normalize_event


class ReplayGateTests(unittest.TestCase):
    def test_observed_kept_intent_marked_guess(self):
        kept, reason = normalize_event({
            "match_id": 1, "seq": 7, "action": "move",
            "intent": "retreat", "source": "TEST"})
        self.assertEqual(reason, "ok")
        self.assertEqual(kept["observed_action"], "move")
        self.assertTrue(kept["intent_is_guess"])
        self.assertEqual(kept["gate"], GATE_VERSION)

    def test_future_and_hidden_dropped(self):
        for ev in ({"match_id": 1, "action": "move", "future": True},
                   {"match_id": 1, "action": "move", "hidden": True}):
            kept, reason = normalize_event(ev)
            self.assertIsNone(kept)
            self.assertEqual(reason, "future-or-hidden")

    def test_missing_action_or_match_rejected(self):
        kept, reason = normalize_event({"match_id": 1})
        self.assertIsNone(kept)
        self.assertEqual(reason, "missing-action-or-match")

    def test_coverage_note_records_no_parser(self):
        text = (HERE.parent / "notes" / "replay-coverage.md").read_text(
            encoding="utf-8")
        self.assertIn("недоступны", text.lower())
        self.assertIn("ограничена явно", text.lower())


if __name__ == "__main__":
    unittest.main()
