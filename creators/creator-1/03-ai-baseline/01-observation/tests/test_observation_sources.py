"""Static source checks for the C1-03-01 pure observation layer (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "observation.lua"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


class ObservationSourceTests(unittest.TestCase):
    def test_no_native_or_hidden_channels(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_filter_drops_hidden_and_future(self):
        text = source()
        self.assertIn("function CD1C301Observation:FilterVisible", text)
        self.assertIn("c.hidden ~= true", text)
        self.assertIn("c.future ~= true", text)
        self.assertIn("c.visible == true", text)

    def test_projection_rejects_forbidden_targets(self):
        text = source()
        self.assertIn("function CD1C301Observation:BuildProjection", text)
        self.assertIn("forbidden-target", text)
        self.assertIn("revision", text)

    def test_choice_is_pure_function_of_seed(self):
        text = source()
        self.assertIn("function CD1C301Observation:Choose", text)
        self.assertIn("projection.visible", text)
        self.assertIn("seed", text)

    def test_no_stored_hidden_state(self):
        text = source()
        self.assertNotIn("hidden_state", text.lower())
        self.assertNotIn("future_event", text.lower())


if __name__ == "__main__":
    unittest.main()
