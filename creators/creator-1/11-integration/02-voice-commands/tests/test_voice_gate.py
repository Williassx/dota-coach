"""Checks for the C1-11-02 voice gate on TEST payloads (unit tests)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from voice_gate import admit, parse_structured


def good():
    return {"action": "attack", "target": "t1", "orderId": "v1",
            "revision": 4}


class VoiceGateTests(unittest.TestCase):
    def test_structured_allowed_passes(self):
        cmd, reason = parse_structured(good())
        self.assertEqual(reason, "ok")
        self.assertEqual(cmd["source"], "voice")
        admitted, reason = admit(cmd, set(), False)
        self.assertEqual(reason, "ok")

    def test_ambiguity_never_invents_order(self):
        cmd, reason = parse_structured({"action": "attack"})
        self.assertIsNone(cmd)
        self.assertEqual(reason, "ambiguous")

    def test_repeat_rejected(self):
        cmd, _ = parse_structured(good())
        _, reason = admit(cmd, {"v1"}, False)
        self.assertEqual(reason, "duplicate")

    def test_manual_holds_attack(self):
        cmd, _ = parse_structured(good())
        _, reason = admit(cmd, set(), True)
        self.assertEqual(reason, "manual-holds-action")

    def test_report_states_real_speech_open(self):
        text = (HERE.parent / "reports" / "voice-integration.md").read_text(
            encoding="utf-8")
        self.assertIn("Настоящая речь", text)


if __name__ == "__main__":
    unittest.main()
