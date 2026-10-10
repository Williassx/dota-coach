"""Inert pre-match source graph; not Panorama compilation or native appearance."""
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
PANORAMA = TASK / "src/panorama"
LAYOUT = PANORAMA / "layout/custom_game/hero_role_picker.xml"


class HeroRoleLayoutTests(unittest.TestCase):
    def setUp(self):
        self.root = ET.parse(LAYOUT).getroot()

    def test_unique_required_ids_match_adapter_and_labels_are_plain(self):
        required = {"HeroRoleRoot", "HeroRoleStatus", "HeroRoleCount", "HeroRoleRecipient", "HeroRolePage",
                    "HeroRolePrevious", "HeroRoleNext", "HeroRoleClear"}
        for n in range(5):
            for group, fields in [("Player", ["Name", "Version", "Origin", "Action"]),
                                  ("Option", ["Hero", "Position", "Coverage", "Action"]),
                                  ("Assigned", ["Name", "Choice", "Warnings", "Action"])]:
                required.add(f"HeroRole{group}{n}")
                required.update(f"HeroRole{group}{field}{n}" for field in fields)
        ids = [node.get("id") for node in self.root.iter() if node.get("id")]
        self.assertEqual(set(ids), required)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(node.get("html") == "false" for node in self.root.iter("Label")))

    def test_exact_local_resources_exist_without_bootstrap_or_external_assets(self):
        resources = [node.get("src") for node in self.root.iter("include")]
        self.assertEqual(resources, ["file://{resources}/styles/custom_game/hero_role_picker.css",
                                    "file://{resources}/scripts/custom_game/hero_role_state.js",
                                    "file://{resources}/scripts/custom_game/hero_role_panel.js"])
        for resource in resources:
            self.assertTrue((PANORAMA / resource.removeprefix("file://{resources}/")).is_file())
        for node in self.root.iter():
            self.assertNotIn(node.tag, ["Image", "CustomUIElement", "run"])
            self.assertTrue(all(not key.lower().startswith("on") for key in node.attrib))
            self.assertNotIn("layoutfile", node.attrib)
        self.assertNotIn("<!DOCTYPE", LAYOUT.read_text())

    def test_static_empty_controls_are_disabled_and_draft_is_not_match_start(self):
        buttons = list(self.root.iter("Button"))
        self.assertEqual(len(buttons), 18)
        self.assertTrue(all(node.get("enabled") == "false" for node in buttons))
        slots = [node for node in buttons if re.fullmatch(r"HeroRole(?:Player|Option|Assigned)[0-4]", node.get("id", ""))]
        self.assertTrue(all(node.get("visible") == "false" for node in slots))
        texts = " ".join(node.get("text", "") for node in self.root.iter("Label"))
        self.assertIn("Черновик героев и позиций", texts)
        self.assertIn("Локальные назначения: 0/5", texts)
        self.assertNotIn("Начать матч", texts)

    def test_definition_load_does_not_access_panorama_or_native_apis(self):
        paths = [str(PANORAMA / "scripts/custom_game/hero_role_state.js"),
                 str(PANORAMA / "scripts/custom_game/hero_role_panel.js")]
        script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const deny=new Proxy({}, {get(){throw Error('native access on load');}});
const context=vm.createContext({$:deny,Game:deny,GameUI:deny,Entities:deny,GameEvents:deny});
for(const file of JSON.parse(process.argv[1]))vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(typeof context.DotaCoachHeroRoles.create,'function');
assert.equal(typeof context.DotaCoachHeroRolePanels.bind,'function');
"""
        result = subprocess.run(["node", "-e", script, json.dumps(paths)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_screen_is_not_automatically_included_in_match_hud_bundle(self):
        repository = TASK.parents[3]
        manifest = json.loads((repository / "creators/creator-2/11-integration/02-addon-packaging/bundle-manifest.json").read_text())
        self.assertFalse(any("hero_role" in item["source"] for item in manifest["assets"]))
        self.assertFalse((PANORAMA / "layout/custom_game/custom_ui_manifest.xml").exists())
