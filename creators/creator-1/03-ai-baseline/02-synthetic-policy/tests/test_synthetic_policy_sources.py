"""Static source checks for the C1-03-02 synthetic policy (unit tests)."""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "synthetic_policy.lua"
FIX = HERE / "fixtures" / "synthetic-intents.json"


def source():
    return SRC.read_text(encoding="utf-8")


class SyntheticPolicySourceTests(unittest.TestCase):
    def test_no_native_calls(self):
        text = source()
        for forbidden in ("GameRules", "PlayerResource", "GetPlayer",
                          "SetThink", "ExecuteOrder", "SetOwner",
                          "SetControllableByPlayer"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("_G.", text)

    def test_single_controller_entry(self):
        text = source()
        self.assertIn("function CD1C302Synthetic:Decide", text)
        self.assertEqual(text.count("function CD1C302Synthetic:"), 2)

    def test_every_intent_marked_synthetic(self):
        text = source()
        self.assertIn("synthetic = true", text)
        self.assertNotIn("synthetic = false", text)
        for kind in ('"move"', '"attack"'):
            self.assertIn(kind, text)

    def test_fixture_intents_all_marked(self):
        doc = json.loads(FIX.read_text(encoding="utf-8"))
        self.assertTrue(doc["synthetic_only"])
        for intent in doc["intents"]:
            self.assertTrue(intent["synthetic"])
            self.assertIn(intent["kind"], ("move", "attack"))


if __name__ == "__main__":
    unittest.main()
