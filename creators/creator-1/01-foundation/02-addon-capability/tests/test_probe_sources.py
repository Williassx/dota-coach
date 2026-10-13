"""Static source checks for the C1-01-02 probe (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "addon_game_mode.lua"
INFO = HERE.parent / "src" / "addoninfo.txt"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


class ProbeSourceTests(unittest.TestCase):
    def test_activation_log_prefix_exists(self):
        self.assertIn("D1C102 activated", source())

    def test_only_allowed_order_types(self):
        text = source()
        self.assertIn("DOTA_UNIT_ORDER_MOVE_TO_POSITION", text)
        self.assertIn("DOTA_UNIT_ORDER_ATTACK_TARGET", text)
        self.assertNotIn("DOTA_UNIT_ORDER_", text.replace(
            "DOTA_UNIT_ORDER_MOVE_TO_POSITION", "").replace(
            "DOTA_UNIT_ORDER_ATTACK_TARGET", ""))
        self.assertNotIn("DOTA_UNIT_ORDER_STREAM_STREAM", text)

    def test_orders_go_through_execute_order(self):
        text = source()
        self.assertEqual(text.count("ExecuteOrderFromTable"), 2)

    def test_no_network_or_file_access(self):
        text = source()
        for forbidden in ("io.open", "os.execute", "require(", "http", "ResourceManager"):
            self.assertNotIn(forbidden, text)

    def test_units_not_recreated_after_death(self):
        text = source()
        self.assertIn("if self.heroIndex == nil then", text)
        self.assertIn("if self.lastPosX ~= nil and origin.x ~= self.lastPosX then", text)

    def test_target_health_facts_are_logged(self):
        text = source()
        self.assertIn("GetHealth()", text)
        self.assertIn("GetMaxHealth()", text)
        self.assertIn("self.tick % 5 == 0", text)
        self.assertIn("D1C102 state origin=", text)
        self.assertIn("IsAttacking()", text)
        self.assertIn("GetAttackTarget()", text)
        self.assertIn("GetRangeToUnit( self.targetIndex )", text)

    def test_attack_order_issued_once_only(self):
        text = source()
        self.assertEqual(text.count("self:OrderAttack()"), 1)

    def test_player_control_transfer_logged(self):
        text = source()
        self.assertIn("SetControllableByPlayer( 0, true )", text)
        self.assertIn("SetOwner( hPlayer )", text)
        self.assertIn("PlayerResource:GetPlayer( 0 )", text)
        self.assertIn("player-missing", text)
        self.assertEqual(text.count("GetPlayerOwnerID"), 2)
        self.assertIn("owner-before", text)
        self.assertIn("owner-after", text)

    def test_addoninfo_marks_template_map_playable(self):
        text = INFO.read_text(encoding="utf-8", errors="replace")
        self.assertIn('maps\t\t\t"template_map"', text)
        self.assertIn('"IsPlayable"\t"1"', text)


if __name__ == "__main__":
    unittest.main()
