"""Real filesystem checks for bounded, read-only Panorama discovery."""
import importlib.util
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "inspect_ui_workspace.py"


class UIWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SCRIPT.is_file():
            spec = importlib.util.spec_from_file_location("ui_audit", SCRIPT)
            cls.audit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.audit)

    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "UI workspace helper not implemented")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def resource(self, relative, content="user-owned resource"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_absent_installation_does_not_claim_tools_work(self):
        report = self.audit.inspect_panorama(self.root / "missing")
        self.assertFalse(report["directory_exists"])
        self.assertFalse(report["runtime_verified"])
        self.assertEqual(report["resources"], [])

    def test_source_and_compiled_resources_are_distinct_in_both_trees(self):
        self.resource("content/dota_addons/probe/panorama/layout/custom_game/hud.xml")
        self.resource("game/dota_addons/probe/panorama/layout/custom_game/hud.vxml_c")
        self.resource("game/dota_addons/probe/panorama/scripts/custom_game/hud.js")
        self.resource("game/dota_addons/probe/scripts/vscripts/not-panorama.js")
        report = self.audit.inspect_panorama(self.root)
        resources = {(r["tree"], r["kind"], r["path"]) for r in report["resources"]}
        self.assertIn(("content", "source", "content/dota_addons/probe/panorama/layout/custom_game/hud.xml"), resources)
        self.assertIn(("game", "compiled", "game/dota_addons/probe/panorama/layout/custom_game/hud.vxml_c"), resources)
        self.assertEqual(len(resources), 3)
        self.assertFalse(report["runtime_verified"])

    def test_external_link_is_not_traversed(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.xml").write_text("do not read", encoding="utf-8")
        game = self.root / "dota"
        parent = game / "content/dota_addons/probe/panorama"
        parent.mkdir(parents=True)
        try:
            (parent / "linked").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        report = self.audit.inspect_panorama(game)
        self.assertEqual(report["resources"], [])
        self.assertTrue(any(i["status"] == "link_or_escape_skipped" for i in report["issues"]))

    def test_entry_budget_limits_even_unrelated_files(self):
        for number in range(30):
            self.resource("content/dota_addons/probe/panorama/irrelevant-" + str(number) + ".txt")
        report = self.audit.inspect_panorama(self.root, max_entries=6)
        self.assertLessEqual(report["entries_examined"], 6)
        self.assertTrue(report["truncated"])

    def test_addons_without_panorama_also_consume_the_budget(self):
        for number in range(30):
            (self.root / "content/dota_addons" / str(number)).mkdir(parents=True)
        report = self.audit.inspect_panorama(self.root, max_entries=6)
        self.assertLessEqual(report["entries_examined"], 6)
        self.assertTrue(report["truncated"])

    def test_entry_budget_is_shared_between_game_and_content(self):
        for number in range(12):
            self.resource("content/dota_addons/probe/panorama/" + str(number) + ".xml")
        self.resource("game/dota_addons/probe/panorama/game.xml")
        report = self.audit.inspect_panorama(self.root, max_entries=9)
        self.assertLessEqual(report["entries_examined"], 9)
        self.assertTrue(report["truncated"])
        self.assertFalse(any(r["tree"] == "game" for r in report["resources"]))

    def test_intermediate_symlink_is_not_traversed(self):
        outside = self.root / "outside"
        outside.mkdir()
        dota = self.root / "dota"
        dota.mkdir()
        try:
            (dota / "content").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        report = self.audit.inspect_panorama(dota)
        self.assertEqual(report["resources"], [])
        self.assertTrue(any(i["status"] == "link_or_escape_skipped" for i in report["issues"]))

    def test_windows_reparse_attribute_blocks_a_directory(self):
        resource = self.resource("content/dota_addons/probe/panorama/hud.xml")
        blocked = resource.parents[2]  # dota_addons
        original = Path.lstat

        def lstat_with_reparse(path, *args, **kwargs):
            if path == blocked:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "lstat", lstat_with_reparse):
            report = self.audit.inspect_panorama(self.root)
        self.assertEqual(report["resources"], [])
        self.assertTrue(any(i["status"] == "link_or_escape_skipped" for i in report["issues"]))

    def test_file_budget_reports_partial_inventory(self):
        for number in range(10):
            self.resource("content/dota_addons/probe/panorama/" + str(number) + ".xml")
        report = self.audit.inspect_panorama(self.root, max_files=3)
        self.assertEqual(len(report["resources"]), 3)
        self.assertTrue(report["truncated"])

    def test_deep_tree_does_not_depend_on_python_recursion_limit(self):
        directory = self.root / "content/dota_addons/probe/panorama"
        directory.mkdir(parents=True)
        try:
            for _ in range(90):
                directory = directory / "d"
                directory.mkdir()
            (directory / "hud.xml").write_text("preserve this", encoding="utf-8")
        except OSError as error:
            self.skipTest("deep filesystem paths unavailable: " + str(error))
        previous = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(80)
            report = self.audit.inspect_panorama(self.root)
        finally:
            sys.setrecursionlimit(previous)
        self.assertEqual(len(report["resources"]), 1)
        self.assertFalse(report["truncated"])

    def test_inspection_does_not_change_resource_bytes(self):
        path = self.resource("content/dota_addons/probe/panorama/hud.xml", "preserve me")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.audit.inspect_panorama(self.root)
        after = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(path.read_text(encoding="utf-8"), "preserve me")

    def test_existing_report_is_preserved(self):
        target = self.resource("report.json", "keep old report")
        result = subprocess.run([sys.executable, str(SCRIPT), "--repository", str(self.root),
                                 "--dota-root", str(self.root), "--output", str(target)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(encoding="utf-8"), "keep old report")

    def test_discovered_steam_installation_is_inspected_without_copying_audit(self):
        steam = self.root / "Steam"
        self.resource("Steam/steamapps/appmanifest_570.acf", '"installdir" "dota 2 beta"')
        self.resource("Steam/steamapps/common/dota 2 beta/content/dota_addons/probe/panorama/hud.css")
        report = self.audit.build_report(self.root, [steam], [])
        self.assertEqual(len(report["panorama_installations"]), 1)
        self.assertEqual(report["panorama_installations"][0]["resources"][0]["kind"], "source")
        self.assertFalse(report["runtime_verified"])
        self.assertNotIn("origin", report["environment"]["git"])


if __name__ == "__main__":
    unittest.main()
