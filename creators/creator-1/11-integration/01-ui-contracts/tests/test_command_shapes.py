"""C1-11-01 cross-check (role 146): producers fit the arbiter shape.

personal_policy, voice_gate and opponent emit arbiter commands; this test
imports all three producers and asserts every emitted command carries
(orderId, source, revision) with a known source. Engine execution stays
open; shape conformance is pure and checked here.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
C1 = HERE.parents[2]
sys.path.insert(0, str(C1 / "06-player-models" / "02-personal-policy" / "src"))
sys.path.insert(0, str(C1 / "11-integration" / "02-voice-commands" / "src"))
sys.path.insert(0, str(C1 / "09-full-match" / "02-opponent-policy" / "src"))

from personal_policy import choose as personal_choose
from personal_policy import to_arbiter_command as personal_cmd
from voice_gate import parse_structured as voice_parse
from opponent import opponent_choice, to_arbiter_command as opponent_cmd

KNOWN_SOURCES = ("ai", "voice", "coach", "manual")


class CommandShapeTests(unittest.TestCase):
    def collect(self):
        prof = {"identity": "TEST-x", "synthetic": True,
                "measured": [{"name": "aggression", "value": 0.9,
                              "matches": 5, "origin": "TEST"}]}
        ctx = {"visible": [{"id": 511}]}
        choice, _ = personal_choose(ctx, prof)
        cmds = [personal_cmd(choice, "pp1", 2)]
        vcmd, _ = voice_parse({"action": "farm", "target": "t1",
                               "orderId": "v1", "revision": 2})
        cmds.append(vcmd)
        tgt, _ = opponent_choice("greedy", [{"id": 611, "visible": True}])
        cmds.append(opponent_cmd(tgt, "op1", 2))
        return cmds

    def test_all_commands_carry_arbiter_shape(self):
        for cmd in self.collect():
            with self.subTest(cmd):
                for field in ("orderId", "source", "revision"):
                    self.assertIn(field, cmd)
                self.assertIn(cmd["source"], KNOWN_SOURCES)
                self.assertIsInstance(cmd["revision"], int)

    def test_none_producer_emits_nothing(self):
        prof = {"identity": "TEST-x", "synthetic": True, "measured": []}
        choice, _ = personal_choose({"visible": []}, prof)
        cmd = personal_cmd(choice, "pp9", 1)
        self.assertIn("orderId", cmd)
        tgt, _ = opponent_choice("greedy", [])
        self.assertIsNone(tgt)
        self.assertIsNone(opponent_cmd(tgt, "op9", 1))


if __name__ == "__main__":
    unittest.main()
