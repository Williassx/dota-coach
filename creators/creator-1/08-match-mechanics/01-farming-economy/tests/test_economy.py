"""Checks for the C1-08-01 economy rules on TEST numbers (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from economy import ALLOWED_ACTIONS, attempt


class EconomyTests(unittest.TestCase):
    def test_allowed_set_closed(self):
        self.assertEqual(set(ALLOWED_ACTIONS),
                         {"attack_creep", "deny_creep", "change_plan"})
        ok, _, reason = attempt("cast_spell", "enemy", 500)
        self.assertFalse(ok)
        self.assertEqual(reason, "action-not-allowed")

    def test_no_guarantee_by_click(self):
        ok, detail, _ = attempt("attack_creep", "enemy", 500)
        self.assertTrue(ok)
        self.assertFalse(detail["guaranteed"])

    def test_ally_enemy_sides(self):
        ok, _, reason = attempt("attack_creep", "ally", 500)
        self.assertFalse(ok)
        self.assertEqual(reason, "ally-only-deny")
        ok, _, reason = attempt("deny_creep", "enemy", 500)
        self.assertFalse(ok)
        self.assertEqual(reason, "enemy-only-attack")

    def test_gold_and_invalid_purchase(self):
        ok, _, reason = attempt("attack_creep", "enemy", 10,
                                item="boots")
        self.assertFalse(ok)
        self.assertEqual(reason, "gold-shortage")
        ok, _, reason = attempt("attack_creep", "enemy", 500,
                                item="divine_rapier_x")
        self.assertFalse(ok)
        self.assertEqual(reason, "invalid-purchase")

    def test_plan_change(self):
        ok, detail, reason = attempt("change_plan", "enemy", 0,
                                     plan=["tango", "boots"])
        self.assertTrue(ok)
        self.assertEqual(detail["plan"], ["tango", "boots"])

    def test_economy_note_states_rules(self):
        text = (HERE.parent / "notes" / "economy.md").read_text(
            encoding="utf-8")
        self.assertIn("не гарантирует", text.lower())


if __name__ == "__main__":
    unittest.main()
