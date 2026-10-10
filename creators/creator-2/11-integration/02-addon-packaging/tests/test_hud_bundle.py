"""Checks for one inert HUD layout and an exact multi-library source package."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / "creators/creator-2/01-foundation/02-panorama-capability/tools"
HUD = "content/panorama/layout/custom_game/coach_hud.xml"
SCRIPT_ORDER = ["roster_cards_state.js", "roster_cards.js", "orders_state.js", "orders_panel.js",
                "input_routing.js", "camera_native.js", "camera_panel.js", "targets_state.js", "targets_panel.js", "coach_hud_binding.js"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    before = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = before
    return module


builder = load("hud_fixture_builder", TOOLS / "build_probe_bundle.py")
sys.path.insert(0, str(TOOLS))
try:
    verifier = load("hud_fixture_verifier", TOOLS / "verify_probe_bundle.py")
finally:
    sys.path.pop(0)


class HudBundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((TASK / "bundle-manifest.json").is_file(), "HUD manifest not implemented")
        self.manifest = json.loads((TASK / "bundle-manifest.json").read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.output = self.repo / "build/dota_coach/hud"
        for entry in self.manifest["assets"]:
            source = REPOSITORY / entry["source"]
            self.assertTrue(source.is_file(), str(source))
            destination = self.repo / entry["source"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

    def build(self):
        return builder.build_bundle(self.repo, self.manifest, self.output)

    def source_for(self, target):
        entry = next(a for a in self.manifest["assets"] if a["target"] == target)
        return self.repo / entry["source"]

    def test_real_source_package_roundtrip_preserves_bytes_and_false_runtime(self):
        before = {a["source"]: (self.repo / a["source"]).read_bytes() for a in self.manifest["assets"]}
        report = self.build()
        self.assertEqual(report["kind"], "panorama_source_hud")
        self.assertFalse(report["source2_compiled"])
        self.assertFalse(report["runtime_verified"])
        for row in report["assets"]:
            self.assertEqual((self.output / row["target"]).read_bytes(), before[row["source"]])
            self.assertEqual((self.repo / row["source"]).read_bytes(), before[row["source"]])
            self.assertEqual(row["sha256"], hashlib.sha256(before[row["source"]]).hexdigest())
        result = verifier.verify_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(result["assets"], 13)
        self.assertEqual(result["xml_resource_links"], 12)
        self.assertFalse(result["source2_compiled"])
        self.assertFalse(result["runtime_verified"])

    def test_common_layout_has_unique_scoped_ids_and_correct_dependencies(self):
        root = ET.parse(self.source_for(HUD)).getroot()
        ids = [n.attrib["id"] for n in root.iter() if "id" in n.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        scopes = {n.attrib["id"]: n for n in root.iter() if n.get("id") in
                  ["CoachRoster", "CoachOrders", "CoachCamera", "CoachTargets"]}
        self.assertEqual(len(scopes), 4)
        for scope, required in {
            "CoachRoster": ["RosterStatus"] + ["RosterCard" + str(n) for n in range(5)] +
                ["Roster" + field + str(n) for n in range(5) for field in
                 ["Name", "Hero", "Role", "Source", "Availability", "Hint"]],
            "CoachOrders": ["OrderRecipient", "OrderMode", "OrderRequestRecipient", "OrderAction",
                "OrderResult", "OrderReason", "OrderEligibility", "OrderMove", "OrderAttack"],
            "CoachCamera": ["CameraRecipient", "CameraAvailability", "CameraResult", "CameraFocus"],
            "CoachTargets": ["TargetTitle", "TargetDetails", "TargetStatus"],
        }.items():
            local_ids = {n.get("id") for n in scopes[scope].iter()}
            self.assertTrue(set(required) <= local_ids, scope)
        scripts = [Path(n.attrib["src"]).name for n in root.findall("./scripts/include")]
        self.assertEqual(scripts, SCRIPT_ORDER)
        self.assertTrue(all(n.get("html") == "false" for n in root.iter("Label")))

    def test_static_empty_state_is_inert_and_explains_disabled_buttons(self):
        root = ET.parse(self.source_for(HUD)).getroot()
        labels = {n.get("id"): n.get("text", "") for n in root.iter("Label")}
        self.assertIn("не получены", labels["RosterStatus"])
        self.assertIn("не выбран", labels["OrderRecipient"])
        self.assertIn("не получен", labels["OrderMode"])
        self.assertIn("не подключ", labels["OrderEligibility"])
        self.assertIn("Нет текущего", labels["OrderResult"])
        self.assertIn("не подключ", labels["CameraAvailability"])
        self.assertIn("не выбрана", labels["TargetTitle"])
        self.assertTrue(all(n.get("enabled") == "false" for n in root.iter("Button")))
        for node in root.iter():
            self.assertFalse(any(k.startswith("on") for k in node.attrib))
        scopes = {n.get("id"): n for n in root.iter()}
        self.assertEqual(scopes["CoachTargets"].get("hittestchildren"), "false")
        for n in range(5):
            self.assertEqual(scopes["RosterCard" + str(n)].get("visible"), "false")

    def test_loading_every_declared_script_has_no_native_or_startup_side_effects(self):
        root = ET.parse(self.source_for(HUD)).getroot()
        sources = [str(self.source_for("content/panorama/" + n.attrib["src"].split("file://{resources}/", 1)[1]))
                   for n in root.findall("./scripts/include")]
        code = """const fs=require('node:fs'),vm=require('node:vm');
const deny=new Proxy({}, {get(){throw Error('Native API used during source load')}});
const context=vm.createContext({$:deny,Game:deny,GameUI:deny,GameEvents:deny,Entities:deny,Players:deny});
for(const source of JSON.parse(process.argv[1]))vm.runInContext(fs.readFileSync(source,'utf8'),context);
for(const name of ['DotaCoachRoster','DotaCoachRosterPanels','DotaCoachOrders','DotaCoachOrderPanels',
'DotaCoachInputRouting','DotaCoachCameraNative','DotaCoachCameraPanels','DotaCoachTargets','DotaCoachTargetPanels','DotaCoachHudPanels'])
if(!context[name])throw Error('Missing definition '+name);
"""
        result = subprocess.run(["node", "-e", code, json.dumps(sources)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_static_copy_does_not_offer_missing_map_input_or_generalize_test_intents(self):
        root = ET.parse(self.source_for(HUD)).getroot()
        nodes = {n.get("id"): n for n in root.iter()}
        for name, expected in [("OrderMove", "К контрольной точке"), ("OrderAttack", "Атаковать тестовую цель")]:
            with self.subTest(name=name):
                self.assertEqual(nodes[name].find("Label").get("text"), expected)
        self.assertIn("не подключено", nodes["TargetStatus"].get("text"))

    def test_exact_hud_policy_rejects_demo_extra_remap_and_missing_resource(self):
        for mode in ["demo", "extra", "remap", "missing", "wrong_kind", "extra_field"]:
            with self.subTest(mode=mode):
                manifest = copy.deepcopy(self.manifest)
                if mode == "demo":
                    manifest["assets"][3]["source"] = manifest["assets"][3]["source"].replace("roster_cards_state.js", "roster_cards_demo.js")
                elif mode == "extra":
                    manifest["assets"].append({"source": manifest["assets"][3]["source"],
                                               "target": "content/panorama/scripts/custom_game/extra.js"})
                elif mode == "remap": manifest["assets"][3]["target"] = "content/panorama/scripts/custom_game/remapped.js"
                elif mode == "missing": manifest["assets"].pop()
                elif mode == "wrong_kind": manifest["kind"] = "addon_compiled"
                else: manifest["allow_prefix"] = "creators"
                with self.assertRaises(ValueError): builder.build_bundle(self.repo, manifest, self.output)
                self.assertFalse(self.output.exists())

    def test_probe_kind_cannot_use_a_hud_source(self):
        manifest = {"schema_version": 1, "kind": "panorama_source_probe", "assets": [self.manifest["assets"][0]]}
        with self.assertRaises(ValueError): builder.build_bundle(self.repo, manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_hud_kind_cannot_use_another_creators_source_or_probe_source(self):
        for source in ["creators/creator-1/server.js",
                       "creators/creator-2/01-foundation/02-panorama-capability/src/panorama/scripts/custom_game/coach_probe.js"]:
            manifest = copy.deepcopy(self.manifest); manifest["assets"][0]["source"] = source
            with self.assertRaises(ValueError): builder.build_bundle(self.repo, manifest, self.output)
            self.assertFalse(self.output.exists())

    def test_existing_output_and_outside_paths_are_preserved(self):
        self.output.mkdir(parents=True); sentinel = self.output / "user.txt"; sentinel.write_text("keep")
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(sentinel.read_text(), "keep")
        with self.assertRaises(ValueError): builder.build_bundle(self.repo, self.manifest, self.repo / "content/user")
        self.assertFalse((self.repo / "content").exists())

    def test_missing_source_is_rejected_before_creating_output(self):
        self.source_for(HUD).unlink()
        with self.assertRaises((ValueError, OSError)): self.build()
        self.assertFalse((self.repo / "build").exists())

    def test_windows_case_collision_cannot_alias_a_destination(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["assets"][1]["target"] = manifest["assets"][0]["target"].upper()
        with self.assertRaises(ValueError): builder.build_bundle(self.repo, manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_tampered_or_changed_sources_invalidate_an_existing_package(self):
        self.build(); destination = self.output / HUD; original = destination.read_bytes()
        destination.write_bytes(original + b" ")
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.manifest, self.output)
        destination.write_bytes(original); self.source_for(HUD).write_bytes(original + b" ")
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.manifest, self.output)

    def test_report_kind_and_native_claims_must_match_source_package(self):
        self.build(); report_file = self.output / "bundle-report.json"; report = json.loads(report_file.read_text())
        for field, value in [("kind", "panorama_source_probe"), ("source2_compiled", True), ("runtime_verified", True)]:
            changed = copy.deepcopy(report); changed[field] = value; report_file.write_text(json.dumps(changed))
            with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.manifest, self.output)

    def test_unexpected_files_are_rejected_without_mutation(self):
        self.build(); extra = self.output / "extra.js"; extra.write_text("keep")
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(extra.read_text(), "keep")

    def test_resource_graph_rejects_a_reference_outside_declared_assets(self):
        source = self.source_for(HUD)
        source.write_text(source.read_text().replace("roster_cards.js", "missing.js"))
        with self.assertRaises(ValueError): self.build()
        self.assertFalse(self.output.exists())

    def test_hud_graph_rejects_disconnected_layout_orphan_wrong_order_and_xml_bootstrap(self):
        source = self.source_for(HUD); original = source.read_text()
        manifest_source = self.source_for("content/panorama/layout/custom_game/custom_ui_manifest.xml")
        original_manifest = manifest_source.read_text()
        for mode in ["orphan", "order", "bootstrap", "disconnect"]:
            with self.subTest(mode=mode):
                source.write_text(original); manifest_source.write_text(original_manifest)
                if mode == "orphan":
                    root = ET.fromstring(original)
                    includes = root.find("scripts"); includes.remove(includes[-1]); source.write_text(ET.tostring(root, encoding="unicode"))
                elif mode == "order":
                    root = ET.fromstring(original); includes = root.find("scripts")
                    includes[:] = list(includes)[::-1]; source.write_text(ET.tostring(root, encoding="unicode"))
                elif mode == "bootstrap": source.write_text(original.replace('<Panel ', '<Panel onload="run()" ', 1))
                else: manifest_source.write_text('<root><Panel /></root>')
                with self.assertRaises(ValueError): self.build()
                self.assertFalse(self.output.exists())

    def test_nonstring_kind_is_a_controlled_rejection_before_output(self):
        for kind in [[], {}, None, 1]:
            manifest = copy.deepcopy(self.manifest); manifest["kind"] = kind
            with self.assertRaises(ValueError): builder.build_bundle(self.repo, manifest, self.output)
            self.assertFalse(self.output.exists())

    def test_layout_cannot_load_itself_or_another_layout_after_manifest_entry(self):
        source = self.source_for(HUD); original = source.read_text(); self.build()
        for mode in ["custom_element", "layoutfile"]:
            with self.subTest(mode=mode):
                root = ET.fromstring(original); panel = root.find("Panel")
                if mode == "custom_element":
                    ET.SubElement(panel, "CustomUIElement", {"type": "Hud",
                        "layoutfile": "file://{resources}/layout/custom_game/coach_hud.xml"})
                else: panel.set("layoutfile", "file://{resources}/layout/custom_game/custom_ui_manifest.xml")
                source.write_text(ET.tostring(root, encoding="unicode"))
                with self.assertRaisesRegex(ValueError, "HUD layout cannot load"):
                    builder.build_bundle(self.repo, self.manifest, self.repo / ("build/dota_coach/" + mode))
                with self.assertRaisesRegex(ValueError, "HUD layout cannot load"):
                    verifier.verify_bundle(self.repo, self.manifest, self.output)

    def test_actual_cli_build_and_verify_do_not_compile_or_install(self):
        manifest_file = self.repo / "hud.json"; manifest_file.write_text(json.dumps(self.manifest))
        built = subprocess.run([sys.executable, str(TOOLS / "build_probe_bundle.py"), "--repository", str(self.repo),
                                "--manifest", str(manifest_file), "--output", str(self.output)], capture_output=True, text=True)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = subprocess.run([sys.executable, str(TOOLS / "verify_probe_bundle.py"), "--repository", str(self.repo),
                                  "--manifest", str(manifest_file), "--bundle", str(self.output)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertFalse(json.loads(checked.stdout)["runtime_verified"])
        self.assertFalse((self.repo / "game").exists())


if __name__ == "__main__":
    unittest.main()
