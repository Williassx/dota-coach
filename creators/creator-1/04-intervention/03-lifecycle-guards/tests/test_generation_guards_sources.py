"""Static source checks for the C1-04-03 generation guards (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "generation_guards.lua"


def source():
    return SRC.read_text(encoding="utf-8")


class GenerationGuardSourceTests(unittest.TestCase):
    def test_no_native_calls(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_generation_bumps(self):
        text = source()
        self.assertIn("function CD1C403Guards:Begin", text)
        self.assertIn("function CD1C403Guards:Interrupt", text)
        self.assertIn("self.generation = self.generation + 1", text)

    def test_interrupt_kinds_covered(self):
        text = source()
        for kind in ('"death"', '"loss"', '"disconnect"', '"replace"',
                     '"pause"'):
            self.assertIn(kind, text)

    def test_stale_pair_rejected(self):
        text = source()
        self.assertIn("function CD1C403Guards:Accepts", text)
        self.assertIn("generation ~= self.generation", text)
        self.assertIn("return false", text)


if __name__ == "__main__":
    unittest.main()
