"""Static source checks for the C1-04-01 pure manual-mode machine (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "manual_mode.lua"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


class ManualModeSourceTests(unittest.TestCase):
    def test_no_native_order_calls(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer", "DOTA_UNIT_ORDER"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_request_confirm_leave_cycle(self):
        text = source()
        self.assertIn("function CD1C401Manual:Request", text)
        self.assertIn("function CD1C401Manual:Confirm", text)
        self.assertIn("function CD1C401Manual:Leave", text)
        self.assertIn('"REQUESTED"', text)
        self.assertIn('"MANUAL"', text)
        self.assertIn('"AI"', text)

    def test_entry_cancels_ai_queue_and_action(self):
        text = source()
        self.assertIn("aiQueueCancelled = true", text)
        self.assertIn("currentActionCancelled = true", text)

    def test_refusals_are_explicit(self):
        text = source()
        self.assertIn("server-refused", text)
        self.assertIn("no-request", text)
        self.assertIn("not-manual", text)
        self.assertIn("manualRevision", text)


if __name__ == "__main__":
    unittest.main()
