"""Checks for the C1-08-02 capability gate on the TEST set (unit tests)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from hero_actions import attempt, load_set


def test_set():
    doc = load_set(HERE / "fixtures" / "supported-actions.json")
    doc["_test_ok"] = True
    return doc


class HeroActionTests(unittest.TestCase):
    def test_action_kind_cannot_borrow_other_capability_pool(self):
        doc = {"patch": "test", "heroes": {"axe": {
            "abilities": ["call"], "items": ["blink"]}}}
        self.assertEqual(attempt(doc, "axe", "blink", "ability"),
                         (False, "ability-unavailable"))
        self.assertEqual(attempt(doc, "axe", "call", "item"),
                         (False, "ability-unavailable"))
        self.assertEqual(attempt(doc, "axe", "call", "ability"), (True, "ok"))
        self.assertEqual(attempt(doc, "axe", "blink", "item"), (True, "ok"))

    def test_supported_lists_allowed(self):
        ok, reason = attempt(test_set(), "npc_dota_hero_crystal_maiden",
                             "crystal_nova", "ability")
        self.assertTrue(ok, reason)

    def test_unavailable_ability_cooldown_profile(self):
        base = test_set()
        ok, reason = attempt(base, "npc_dota_hero_crystal_maiden",
                             "freezing_field", "ability")
        self.assertFalse(ok)
        self.assertEqual(reason, "ability-unavailable")
        ok, reason = attempt(base, "npc_dota_hero_crystal_maiden",
                             "crystal_nova", "ability", on_cooldown=True)
        self.assertFalse(ok)
        self.assertEqual(reason, "on-cooldown")
        ok, reason = attempt(base, "npc_dota_hero_crystal_maiden",
                             "crystal_nova", "ability",
                             profile_heroes=("npc_dota_hero_axe",))
        self.assertFalse(ok)
        self.assertEqual(reason, "incompatible-profile")

    def test_unconfirmed_patch_blocks(self):
        doc = json.loads((HERE / "fixtures" / "supported-actions.json")
                         .read_text(encoding="utf-8"))
        ok, reason = attempt(doc, "npc_dota_hero_axe",
                             "berserkers_call", "ability")
        self.assertFalse(ok)
        self.assertEqual(reason, "patch-unconfirmed")

    def test_capabilities_not_predictions(self):
        text = (HERE.parent / "src" / "hero_actions.py").read_text(
            encoding="utf-8")
        self.assertIn("never what the person WILL do", text)


if __name__ == "__main__":
    unittest.main()
