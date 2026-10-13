"""Checks for the C1-07-03 morale bounds on TEST params (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from morale import MAX_PUSH, apply_support


class MoraleTests(unittest.TestCase):
    def test_support_moves_params_within_bounds(self):
        new_params, labels = apply_support({"focus": 0.5, "steadiness": 0.5},
                                           "praise", 0.0)
        self.assertAlmostEqual(new_params["focus"], 0.5 + MAX_PUSH)
        self.assertEqual(new_params["steadiness"], 0.5)
        self.assertFalse(labels["about_person"])
        self.assertEqual(labels["assumption"], "game-only")

    def test_resistance_caps_push(self):
        full, _ = apply_support({"focus": 0.5, "steadiness": 0.5},
                                "calm", 0.0)
        resisted, _ = apply_support({"focus": 0.5, "steadiness": 0.5},
                                    "calm", 1.0)
        self.assertGreater(full["steadiness"], resisted["steadiness"])
        self.assertEqual(resisted["steadiness"], 0.5)

    def test_values_clamped(self):
        new_params, _ = apply_support({"focus": 0.99, "steadiness": 0.99},
                                      "rally", 0.0)
        self.assertLessEqual(new_params["focus"], 1.0)
        self.assertLessEqual(new_params["steadiness"], 1.0)

    def test_bad_input_rejected(self):
        params, reason = apply_support({"focus": 0.5}, "hug", 0.0)
        self.assertIsNone(params)
        self.assertEqual(reason, "bad-input")

    def test_morale_note_marks_assumptions(self):
        text = (HERE.parent / "notes" / "morale.md").read_text(
            encoding="utf-8")
        self.assertIn("допущение", text.lower())
        self.assertIn("about_person", text)


if __name__ == "__main__":
    unittest.main()
