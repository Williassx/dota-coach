"""Checks for the C1-07-02 tactics plan on TEST scenes (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from tactics import TACTICS, apply_plan, make_plan


def choice_fn(context, profile, bias):
    vis = context.get("visible", [])
    if bias["kind"] == "attack" and vis:
        pick = vis[0] if "first" in bias["note"] else vis[-1]
        return {"kind": "attack", "target": pick["id"]}, "bias-applied"
    if bias["kind"] == "hold" and vis:
        return {"kind": "hold", "target": vis[-1]["id"]}, "bias-applied"
    return {"kind": "move", "position": [0, 0]}, "bias-applied"


SCENE = {"visible": [{"id": 511}, {"id": 512}]}
PROFILE = {"identity": "TEST-x"}


class TacticsTests(unittest.TestCase):
    def test_limited_tactic_set(self):
        self.assertEqual(set(TACTICS), {"push", "farm", "split", "regroup"})
        self.assertIsNone(make_plan("blitz"))

    def test_same_scene_different_plans(self):
        push, trail_push = apply_plan(choice_fn, SCENE, PROFILE,
                                      make_plan("push"))
        farm, trail_farm = apply_plan(choice_fn, SCENE, PROFILE,
                                      make_plan("farm"))
        self.assertNotEqual(push, farm)
        self.assertEqual(trail_push["plan"], "push")
        self.assertEqual(trail_farm["plan"], "farm")
        self.assertEqual(trail_push["version"], "tactics-v1")

    def test_bad_plan_rejected(self):
        choice, reason = apply_plan(choice_fn, SCENE, PROFILE, None)
        self.assertIsNone(choice)
        self.assertEqual(reason, "bad-plan")

    def test_tactics_note_exists(self):
        text = (HERE.parent / "notes" / "tactics.md").read_text(
            encoding="utf-8")
        self.assertIn("push", text)
        self.assertIn("намерение", text.lower())


if __name__ == "__main__":
    unittest.main()
