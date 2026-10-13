"""Static source checks for the C1-03-03 pure arbiter (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "order_arbiter.lua"


def source():
    return SRC.read_text(encoding="utf-8")


class ArbiterSourceTests(unittest.TestCase):
    def test_no_native_calls(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_priority_and_sources(self):
        text = source()
        self.assertIn("MANUAL (coach, confirmed) > coach order > AI intent",
                      text)
        for src in ('"manual"', '"coach"', '"ai"'):
            self.assertIn(src, text)

    def test_repeat_and_stale_rejected(self):
        text = source()
        self.assertIn("duplicate-or-missing-id", text)
        self.assertIn("stale-revision", text)
        self.assertIn("manual-outside-manual", text)

    def test_priorities_note_exists(self):
        notes = (HERE.parent / "notes" / "priorities.md").read_text(
            encoding="utf-8")
        self.assertIn("MANUAL", notes)
        self.assertIn("арбитр", notes.lower())


if __name__ == "__main__":
    unittest.main()
