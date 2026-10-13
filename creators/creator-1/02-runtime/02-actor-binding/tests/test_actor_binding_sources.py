"""Static source checks for the C1-02-02 pure binding map (unit tests)."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "scripts" / "vscripts" / "actor_binding.lua"


def source():
    return SRC.read_text(encoding="utf-8", errors="replace")


class ActorBindingSourceTests(unittest.TestCase):
    def test_no_native_ownership_calls(self):
        # Same whole-text style as C1-02-01: the pure module (comments included)
        # must not reference engine ownership APIs at all.
        text = source()
        for forbidden in ("SetOwner", "SetControllableByPlayer",
                          "GetPlayerOwnerID", "CreateUnitByName",
                          "PlayerResource", "GetPlayer"):
            self.assertNotIn(forbidden, text)

    def test_triple_and_revision_guards(self):
        text = source()
        self.assertIn("CD1C202Binding", text)
        self.assertIn("function CD1C202Binding:Bind", text)
        self.assertIn("function CD1C202Binding:Accepts", text)
        self.assertIn("function CD1C202Binding:Unbind", text)
        self.assertIn("revision", text)
        self.assertIn("seat-or-entity-taken", text)

    def test_stale_entity_and_revision_rejected(self):
        text = source()
        self.assertIn("b.entity ~= entity", text)
        self.assertIn("b.revision ~= revision", text)
        self.assertIn("return false", text)

    def test_no_global_unit_cache(self):
        text = source()
        for line in text.splitlines():
            if "_G." in line:
                self.fail(f"globals not allowed here: {line.strip()}")

    def test_single_think_or_timer_free(self):
        text = source()
        self.assertNotIn("SetThink", text)


if __name__ == "__main__":
    unittest.main()
