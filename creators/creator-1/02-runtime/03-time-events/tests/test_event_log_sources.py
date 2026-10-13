"""Static source checks for the C1-02-03 pure event log (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "event_log.lua"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


def code_only():
    return "\n".join(ln for ln in source().splitlines()
                      if not ln.lstrip().startswith("--"))


class EventLogSourceTests(unittest.TestCase):
    def test_no_native_clock_calls(self):
        code = code_only()
        for forbidden in ("GetGameTime", "GameRules", "SetThink",
                          "PauseGame", "IsPaused"):
            self.assertNotIn(forbidden, code)

    def test_seq_type_actor_payload_shape(self):
        text = source()
        self.assertIn("CD1C203EventLog", text)
        self.assertIn("function CD1C203EventLog:Append", text)
        self.assertIn("seq", text)
        self.assertIn("actorRef", text)
        self.assertIn("payload", text)
        self.assertIn("self.seq = self.seq + 1", text)

    def test_fresh_instance_no_globals(self):
        code = code_only()
        self.assertNotIn("_G.", code)
        self.assertIn("function CD1C203EventLog:Init", text := source())
        self.assertIn("self.entries = {}", text)

    def test_rejects_bad_type_and_actor(self):
        text = source()
        self.assertIn("bad-type", text)
        self.assertIn("bad-actor", text)


if __name__ == "__main__":
    unittest.main()
