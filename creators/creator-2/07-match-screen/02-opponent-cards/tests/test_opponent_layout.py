"""Static source layout checks; no native compilation or hit-test evidence."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "src" / "panorama"


class OpponentLayoutTests(unittest.TestCase):
    def layout(self):
        file = ROOT / "layout/custom_game/opponent_roster.xml"
        self.assertTrue(file.is_file(), "opponent layout must exist")
        return ET.parse(file).getroot()

    def test_exact_plain_labels_containers_and_initial_hidden_root(self):
        root = self.layout()
        expected = {"OpponentRosterRoot": "Panel", "OpponentCards": "Panel",
                    "OpponentRosterStatus": "Label", "OpponentRosterHint": "Label"}
        for i in range(5):
            expected[f"OpponentCard{i}"] = "Panel"
            for name in ("Name", "Hero", "Information"):
                expected[f"Opponent{name}{i}"] = "Label"
        nodes = [node for node in root.iter() if "id" in node.attrib]
        self.assertEqual(len(nodes), 24)
        self.assertEqual({node.attrib["id"]: node.tag for node in nodes}, expected)
        for node in nodes:
            self.assertFalse(list(node.attrib.keys() - {"id", "class", "visible", "html", "text"}))
            if node.tag == "Label":
                self.assertEqual(node.attrib.get("html"), "false")
                self.assertEqual(node.attrib.get("text"), "")
                self.assertEqual(len(node), 0)
        panel = root.find("Panel")
        self.assertEqual(panel.attrib["visible"], "false")
        strip = panel.find("Panel")
        self.assertEqual(strip.attrib["id"], "OpponentCards")
        self.assertEqual([n.attrib["id"] for n in strip], [f"OpponentCard{i}" for i in range(5)])

    def test_definition_dependencies_exist_in_order_and_no_inline_events(self):
        root = self.layout()
        self.assertEqual([node.tag for node in root], ["styles", "scripts", "Panel"])
        paths = [node.attrib["src"] for node in root.find("scripts")]
        self.assertEqual(paths, ["file://{resources}/scripts/custom_game/opponent_roster_state.js",
                                 "file://{resources}/scripts/custom_game/opponent_roster_panel.js"])
        styles = [node.attrib["src"] for node in root.find("styles")]
        self.assertEqual(styles, ["file://{resources}/styles/custom_game/opponent_roster.css"])
        for uri in styles + paths:
            self.assertTrue((ROOT / uri.removeprefix("file://{resources}/")).is_file())
        for node in root.iter():
            self.assertFalse(any(key.startswith("on") for key in node.attrib))


if __name__ == "__main__":
    unittest.main()
