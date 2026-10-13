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
        self.assertEqual(cmd["source"], "coach")
        self.assertEqual(cmd["origin"], "voice")
        self.assertEqual(cmd, {**good(), "source": "coach", "origin": "voice"})
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

    def test_payload_requires_exact_plain_fields(self):
        class UnreadableDict(dict):
            def __getitem__(self, key):
                raise AssertionError('Subclass getters must not run')
        for payload in [None, [], 'voice', True, UnreadableDict(good()),
                        {**good(), 'source': 'manual'}, {**good(), 'unexpected': 1}]:
            with self.subTest(payload_type=type(payload).__name__):
                command, reason = parse_structured(payload)
                self.assertIsNone(command)
                self.assertNotEqual(reason, 'ok')

    def test_identifiers_are_typed_nonempty_bounded_and_not_normalized(self):
        for field in ['orderId', 'target']:
            for value in [None, False, 1, [], {}, '', ' ', 'x' * 65,
                          ' x', 'x ', 'x\n', 'x\x00']:
                with self.subTest(field=field, value=value):
                    payload = {**good(), field: value}
                    command, reason = parse_structured(payload)
                    self.assertIsNone(command)
                    self.assertEqual(reason, 'invalid-order-id' if field == 'orderId' else 'invalid-target')
        payload = {**good(), 'orderId': 'i' * 64, 'target': 't' * 64}
        command, reason = parse_structured(payload)
        self.assertEqual(reason, 'ok')
        self.assertEqual(command['orderId'], payload['orderId'])
        self.assertEqual(command['target'], payload['target'])

    def test_revision_requires_a_nonnegative_integer_and_rejects_bool(self):
        for value in [None, True, False, -1, '4', 4.0, 9007199254740992, 10 ** 100,
                      float('nan'), float('inf'),
                      float('-inf'), [], {}]:
            with self.subTest(revision=value):
                command, reason = parse_structured({**good(), 'revision': value})
                self.assertIsNone(command)
                self.assertEqual(reason, 'invalid-revision')
        command, reason = parse_structured({**good(), 'revision': 0})
        self.assertEqual(reason, 'ok')
        self.assertEqual(command['revision'], 0)
        command, reason = parse_structured({**good(), 'revision': 9007199254740991})
        self.assertEqual(reason, 'ok')
        self.assertEqual(command['revision'], 9007199254740991)

    def test_action_requires_an_exact_allowed_string(self):
        for value in [None, True, 1, [], {}, '', 'ATTACK', 'attack ', 'move']:
            with self.subTest(action=value):
                command, reason = parse_structured({**good(), 'action': value})
                self.assertIsNone(command)
                self.assertEqual(reason, 'action-not-allowed')

    def test_manual_blocks_every_voice_action(self):
        for action in ['attack', 'retreat', 'farm', 'gather']:
            with self.subTest(action=action):
                command, reason = parse_structured({**good(), 'action': action})
                self.assertEqual(reason, 'ok')
                admitted, reason = admit(command, set(), True)
                self.assertIsNone(admitted)
                self.assertEqual(reason, 'manual-holds-action')

    def test_admit_requires_a_valid_parsed_command(self):
        valid = {**good(), 'source': 'coach', 'origin': 'voice'}
        malformed = [None, [], good(), {}, {**valid, 'source': 'voice'},
                     {**valid, 'source': 'manual'}, {**valid, 'origin': 'buttons'},
                     {**valid, 'revision': True}, {**valid, 'orderId': []},
                     {**valid, 'action': 'move'}, {**valid, 'target': None},
                     {**valid, 'execution_token': 'untrusted'}]
        for command in malformed:
            with self.subTest(command=command):
                admitted, reason = admit(command, set(), False)
                self.assertIsNone(admitted)
                self.assertEqual(reason, 'invalid-command')

    def test_admit_requires_external_set_and_boolean_mode(self):
        command = {**good(), 'source': 'coach', 'origin': 'voice'}
        for seen_ids in [None, [], {}, frozenset()]:
            with self.subTest(seen_ids_type=type(seen_ids).__name__):
                admitted, reason = admit(command, seen_ids, False)
                self.assertIsNone(admitted)
                self.assertEqual(reason, 'invalid-seen-ids')
        for mode in [None, 0, 1, 'AI', {}, []]:
            with self.subTest(mode=mode):
                admitted, reason = admit(command, set(), mode)
                self.assertIsNone(admitted)
                self.assertEqual(reason, 'invalid-manual-mode')

    def test_preliminary_admission_never_commits_seen_ids_or_mutates_inputs(self):
        payload = good()
        original_payload = dict(payload)
        command, reason = parse_structured(payload)
        self.assertEqual(reason, 'ok')
        original_command = dict(command)
        seen_ids = {'other'}
        for mode in [False, True, False]:
            admit(command, seen_ids, mode)
            self.assertEqual(seen_ids, {'other'})
            self.assertEqual(command, original_command)
            self.assertEqual(payload, original_payload)
        self.assertEqual(admit(command, seen_ids, False)[1], 'ok')
        seen_ids.add(command['orderId'])  # The common arbiter owns the eventual commit.
        self.assertEqual(admit(command, seen_ids, False)[1], 'duplicate')

    def test_report_states_real_speech_open(self):
        text = (HERE.parent / "reports" / "voice-integration.md").read_text(
            encoding="utf-8")
        self.assertIn("Настоящая речь", text)


if __name__ == "__main__":
    unittest.main()
