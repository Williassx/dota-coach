"""Static source checks for the C1-02-01 lifecycle (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "addon_game_mode.lua"
INFO = HERE.parent / "src" / "addoninfo.txt"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


class LifecycleSourceTests(unittest.TestCase):
    def test_single_activation_guard(self):
        text = source()
        self.assertIn("_G.D1C201_ACTIVE", text)
        self.assertIn("double-activate ignored", text)
        self.assertEqual(text.count("SetThink"), 1)

    def test_stop_is_logged_and_think_stops(self):
        text = source()
        self.assertIn('"D1C201 stop"', text)
        self.assertIn("return nil", text)
        self.assertIn("tick-after-stop", text)

    def test_no_global_unit_or_timer_cache(self):
        text = source()
        for line in text.splitlines():
            if "_G." in line:
                # Only the lifecycle guard flag is ever allowed in globals.
                self.assertIn("D1C201_ACTIVE", line)

    def test_no_player_ownership_logic(self):
        text = source()
        for forbidden in ("SetOwner", "SetControllableByPlayer", "GetPlayerOwnerID"):
            self.assertNotIn(forbidden, text)

    def test_one_phase_log_per_state(self):
        text = source()
        self.assertIn("phaseSeen[state] ~= true", text)

    def test_addoninfo_marks_template_map_playable(self):
        text = INFO.read_text(encoding="utf-8", errors="replace")
        self.assertIn('"IsPlayable"\t"1"', text)


if __name__ == "__main__":
    unittest.main()
