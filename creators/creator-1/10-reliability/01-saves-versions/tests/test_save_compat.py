"""Checks for the C1-10-01 save compatibility on TEST blobs (unit tests)."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from save_compat import load_state, save_state


def load_fixture(name):
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


class SaveCompatTests(unittest.TestCase):
    def test_roundtrip_current(self):
        blob = save_state({"rosters": 2})
        restored, reason = load_state(blob)
        self.assertEqual(reason, "ok")
        self.assertEqual(restored["payload"], {"rosters": 2})

    def test_corrupt_refused(self):
        _, reason = load_state(load_fixture("corrupt-save.json"), current={})
        self.assertEqual(reason, "corrupt")

    def test_old_refused_newer_refused(self):
        _, reason = load_state(load_fixture("old-save.json"))
        self.assertEqual(reason, "too-old")
        _, reason = load_state({"save_version": 99, "payload": {}})
        self.assertEqual(reason, "newer-than-code")

    def test_current_state_untouched(self):
        current = {"live": True}
        load_state(load_fixture("corrupt-save.json"), current=current)
        load_state({"save_version": 99}, current=current)
        self.assertEqual(current, {"live": True})


if __name__ == "__main__":
    unittest.main()
