"""Static source checks for the C1-04-02 pure return manager (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "return_manager.lua"


def source():
    return SRC.read_text(encoding="utf-8")


class ReturnSourceTests(unittest.TestCase):
    def test_no_native_calls(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_return_path_states(self):
        text = source()
        self.assertIn("function CD1C402Return:StartReturn", text)
        self.assertIn("function CD1C402Return:FinishReturn", text)
        self.assertIn('"REASSESS"', text)
        self.assertIn('"MANUAL"', text)
        self.assertIn('"AI"', text)

    def test_manual_cancelled_and_reassessed(self):
        text = source()
        self.assertIn("manualCancelled = true", text)
        self.assertIn("reassessed = true", text)
        self.assertIn("completedCycles", text)

    def test_resume_rules_note(self):
        notes = (HERE.parent / "notes" / "resume-rules.md").read_text(
            encoding="utf-8")
        self.assertIn("REASSESS", notes)
        self.assertIn("возврат", notes.lower())


if __name__ == "__main__":
    unittest.main()
