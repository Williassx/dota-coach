"""Filesystem evidence tests; fixtures are synthetic, never Dota resources."""
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "tools/inspect_map_workspace.py"


class MapWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SCRIPT.is_file():
            spec = importlib.util.spec_from_file_location("map_workspace_audit", SCRIPT)
            cls.audit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.audit)

    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "Map workspace helper not implemented")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        self.install = self.base / "dota"
        self.install.mkdir()
        (self.install / "game/dota").mkdir(parents=True)

    def file(self, name, data=b"synthetic file, not a map", root=None):
        p = (root or self.install) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def manifest(self, text=None):
        library = self.base / "steam"
        self.install = library / "steamapps/common/dota"
        self.install.mkdir(parents=True, exist_ok=True)
        (self.install / "game/dota").mkdir(parents=True)
        p = library / "steamapps/appmanifest_570.acf"
        p.write_text(text or '"AppState" { "appid" "570" "installdir" "dota" "buildid" "112233" }')
        return library, p

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), "--dota-root", str(self.install),
                               *map(str, arguments)], capture_output=True, text=True)

    def link(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            self.skipTest("Platform cannot create test symbolic links: " + str(error))

    def test_missing_installation_never_claims_map_runtime_or_geometry(self):
        r = self.audit.inspect_maps(self.install / "missing")
        self.assertFalse(r["directory_exists"])
        self.assertEqual(r["resources"], [])
        self.assertIsNone(r["actual_loaded_map"])
        self.assertIsNone(r["patch"])
        for name in ["runtime_verified", "geometry_verified", "compatibility_verified"]:
            self.assertFalse(r[name])
        self.assertEqual(r["concept_reference"]["patch"], "7.40")
        self.assertFalse(r["concept_reference"]["runtime_evidence"])

    def test_core_addon_and_source_compiled_navigation_archives_are_separate(self):
        expected = {
            "content/dota/maps/dota.vmap": ("core", "source_candidate"),
            "game/dota/maps/dota.vmap_c": ("core", "compiled_candidate"),
            "content/dota_addons/probe/maps/probe.vmap": ("addon", "source_candidate"),
            "game/dota_addons/probe/maps/probe.vnav_c": ("addon", "navigation_candidate"),
            "game/dota/pak01_dir.vpk": ("core", "archive_candidate"),
        }
        for name in [*expected, "content/dota/maps/reference.jpg", "game/dota/not-map.js",
                     "game/dota_addons/probe/scripts/unit.vmap"]:
            self.file(name)
        r = self.audit.inspect_maps(self.install)
        actual = {x["path"]: (x["scope"], x["kind"]) for x in r["resources"]}
        self.assertEqual(actual, expected)
        self.assertEqual([x["path"] for x in r["resources"]], sorted(expected))

    def test_hash_is_complete_and_inventory_preserves_original_bytes(self):
        data = b"synthetic geometry bytes\x00\xff"
        p = self.file("content/dota/maps/probe.vmap", data)
        before = p.stat().st_mtime_ns
        r = self.audit.inspect_maps(self.install)
        row = r["resources"][0]
        self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(row["hash_status"], "complete")
        self.assertEqual(r["hash_bytes_read"], len(data))
        self.assertEqual(p.read_bytes(), data)
        self.assertEqual(p.stat().st_mtime_ns, before)

    def test_archive_only_inventory_does_not_prove_the_map_is_absent(self):
        self.file("game/dota/pak01_dir.vpk")
        r = self.audit.inspect_maps(self.install)
        self.assertEqual(r["status"], "inventory_only")
        self.assertEqual(r["resources"][0]["kind"], "archive_candidate")
        self.assertIsNone(r["actual_loaded_map"])
        self.assertFalse(r["geometry_verified"])

    def test_build_id_is_bound_to_manifest_installation_and_not_a_patch(self):
        library, p = self.manifest()
        for text in [p.read_text(), '// "appid" "999"\n"AppState" { "appid" "570" '
                     '"installdir" "dota" "buildid" "112233" "UserConfig" { "appid" "999" } }']:
            with self.subTest(text=text):
                p.write_text(text)
                r = self.audit.inspect_maps(self.install, library)
                self.assertEqual(r["build_evidence"]["status"], "associated")
                self.assertEqual(r["build_evidence"]["build_id"], "112233")
                self.assertIsNone(r["patch"])
                self.assertFalse(r["compatibility_verified"])

    def test_another_manifest_installation_cannot_assign_this_build(self):
        library, _ = self.manifest()
        other = self.base / "other"
        other.mkdir()
        r = self.audit.inspect_maps(other, library)
        self.assertEqual(r["build_evidence"]["status"], "installation_mismatch")
        self.assertIsNone(r["build_evidence"]["build_id"])

    def test_manifest_escape_wrong_app_or_oversize_is_rejected(self):
        library, p = self.manifest()
        for text in ['"appid" "570" "installdir" "../elsewhere" "buildid" "secret"',
                     '"appid" "999" "installdir" "dota" "buildid" "secret"', "x" * 65537]:
            with self.subTest(text=text[:35]):
                p.write_text(text)
                r = self.audit.inspect_maps(self.install, library)
                self.assertNotEqual(r["build_evidence"]["status"], "associated")
                self.assertIsNone(r["build_evidence"]["build_id"])

    def test_links_inside_map_tree_are_skipped_without_reading_outside(self):
        outside = self.base / "outside"
        self.file("secret.vmap", root=outside)
        maps = self.install / "content/dota/maps"
        maps.mkdir(parents=True)
        self.link(maps / "linked", outside, True)
        self.link(maps / "linked.vmap", outside / "secret.vmap")
        r = self.audit.inspect_maps(self.install)
        self.assertEqual(r["resources"], [])
        self.assertEqual(r["hash_bytes_read"], 0)
        self.assertTrue(any(i["status"] == "link_or_reparse_skipped" for i in r["issues"]))

    def test_symlink_in_root_ancestor_or_tree_ancestor_is_not_followed(self):
        self.file("content/dota/maps/probe.vmap")
        link = self.base / "alias"
        self.link(link, self.base, True)
        r = self.audit.inspect_maps(link / "dota")
        self.assertFalse(r["directory_exists"])
        self.assertEqual(r["resources"], [])
        other = self.base / "other"
        other.mkdir()
        self.link(other / "content", self.install / "content", True)
        self.assertEqual(self.audit.inspect_maps(other)["resources"], [])

    def test_windows_reparse_flag_skips_map_directory(self):
        p = self.file("content/dota/maps/probe.vmap")
        original = Path.lstat
        def flag(path, *args, **kwargs):
            if path == p.parent:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "lstat", flag):
            r = self.audit.inspect_maps(self.install)
        self.assertEqual(r["resources"], [])
        self.assertTrue(any(i["status"] == "link_or_reparse_skipped" for i in r["issues"]))

    def test_all_entries_share_one_budget_including_irrelevant_addons(self):
        for n in range(30): self.file(f"content/dota_addons/addon{n}/readme.txt")
        self.file("game/dota/maps/later.vmap_c")
        r = self.audit.inspect_maps(self.install, max_entries=8)
        self.assertEqual(r["entries_examined"], 8)
        self.assertTrue(r["truncated"])
        self.assertEqual(r["status"], "partial_inventory")

    def test_map_and_archive_candidates_share_one_file_budget(self):
        self.file("content/dota/maps/a.vmap")
        self.file("game/dota/pak01_dir.vpk")
        r = self.audit.inspect_maps(self.install, max_files=1)
        self.assertEqual(len(r["resources"]), 1)
        self.assertTrue(r["truncated"])

    def test_per_file_and_total_hash_budgets_never_create_partial_sha(self):
        self.file("content/dota/maps/a.vmap", b"abcd")
        self.file("content/dota/maps/b.vmap", b"efgh")
        self.file("game/dota/large.vpk", b"x" * 100)
        r = self.audit.inspect_maps(self.install, max_hash_bytes=5, max_file_hash_bytes=10)
        self.assertEqual(r["hash_bytes_read"], 4)
        statuses = {x["hash_status"] for x in r["resources"]}
        self.assertEqual(statuses, {"complete", "total_limit", "size_limit"})
        self.assertTrue(all(x["sha256"] is None for x in r["resources"] if x["hash_status"] != "complete"))

    def test_unreadable_map_root_is_visible_as_incomplete_inventory(self):
        p = self.file("content/dota/maps/probe.vmap")
        original = os.scandir
        def denied(path):
            if Path(path) == p.parent: raise PermissionError("synthetic denial")
            return original(path)
        with mock.patch.object(self.audit.os, "scandir", denied):
            r = self.audit.inspect_maps(self.install)
        self.assertEqual(r["status"], "partial_inventory")
        self.assertTrue(any(i["status"] == "unreadable" for i in r["issues"]))

    def test_file_changed_after_open_has_no_authoritative_hash(self):
        p = self.file("content/dota/maps/probe.vmap", b"before")
        original = Path.open
        def changing(path, *args, **kwargs):
            handle = original(path, *args, **kwargs)
            if path == p and args and args[0] == "rb":
                with original(p, "wb") as writer: writer.write(b"after change")
            return handle
        with mock.patch.object(Path, "open", changing):
            r = self.audit.inspect_maps(self.install)
        self.assertIsNone(r["resources"][0]["sha256"])
        self.assertEqual(r["resources"][0]["hash_status"], "changed")

    def test_deep_map_tree_uses_iterative_traversal(self):
        relative = "content/dota/maps/" + "/".join(["d"] * 160) + "/probe.vmap"
        try:
            self.file(relative)
        except OSError as error:
            if os.name == "nt" and getattr(error, "winerror", None) == 206:
                self.skipTest("Windows long-path support is unavailable")
            raise
        r = self.audit.inspect_maps(self.install, max_entries=600)
        self.assertEqual(len(r["resources"]), 1)
        self.assertFalse(r["truncated"])

    def test_cli_new_output_is_json_and_existing_output_is_preserved(self):
        self.file("content/dota/maps/probe.vmap")
        target = self.base / "report.json"
        result = self.cli("--output", target)
        self.assertEqual(result.returncode, 0, result.stderr)
        r = json.loads(target.read_text())
        self.assertFalse(r["runtime_verified"])
        before = target.read_bytes()
        again = self.cli("--output", target)
        self.assertEqual(again.returncode, 2)
        self.assertEqual(target.read_bytes(), before)

    def test_cli_output_inside_installation_or_steam_is_refused(self):
        library, _ = self.manifest()
        for target in [self.install / "report.json", library / "report.json"]:
            r = self.cli("--steam-library", library, "--output", target)
            self.assertEqual(r.returncode, 2, r.stdout)
            self.assertFalse(target.exists())

    def test_cli_stdout_does_not_claim_real_map_from_fixture(self):
        self.file("content/dota/maps/dota_740.vmap")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        r = json.loads(result.stdout)
        self.assertIsNone(r["patch"])
        self.assertIsNone(r["actual_loaded_map"])

    def test_invalid_limits_are_refused_before_traversal(self):
        for key in ["max_entries", "max_files", "max_hash_bytes", "max_file_hash_bytes"]:
            for value in [0, -1, True, 1.5, 10**12]:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.audit.inspect_maps(self.install, **{key: value})

    def test_missing_or_invalid_build_id_does_not_claim_association(self):
        library, p = self.manifest()
        for tail in ["", '"buildid" "7.40"', '"buildid" ""', '"buildid" "' + '9' * 33 + '"']:
            with self.subTest(tail=tail):
                p.write_text('"appid" "570" "installdir" "dota" ' + tail)
                r = self.audit.inspect_maps(self.install, library)
                self.assertNotEqual(r["build_evidence"]["status"], "associated")
                self.assertIsNone(r["build_evidence"]["build_id"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is Unix-specific")
    def test_special_files_are_skipped_before_open(self):
        p = self.install / "content/dota/maps/fifo.vmap"
        p.parent.mkdir(parents=True)
        os.mkfifo(p)
        r = self.audit.inspect_maps(self.install)
        self.assertEqual(r["resources"], [])
        self.assertEqual(r["hash_bytes_read"], 0)
        self.assertTrue(any(i["status"] == "special_file_skipped" for i in r["issues"]))

    def test_output_symlink_parent_and_inferred_steam_library_are_protected(self):
        library, _ = self.manifest()
        alias = self.base / "alias"
        self.link(alias, library, True)
        for target in [alias / "report.json", library / "report.json"]:
            r = self.cli("--output", target)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(target.exists())

    def test_cli_import_does_not_write_bytecode_to_creator_one(self):
        repository = SCRIPT.parents[5]
        c1 = repository / "creators/creator-1/01-foundation/01-environment-audit/tools"
        before = {str(p): (p.stat().st_mtime_ns, p.read_bytes()) for p in c1.rglob("*.pyc")}
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stderr)
        after = {str(p): (p.stat().st_mtime_ns, p.read_bytes()) for p in c1.rglob("*.pyc")}
        self.assertEqual(after, before)

    def test_arbitrary_empty_folder_is_explicitly_unavailable_not_a_dota_install(self):
        empty = self.base / "empty"
        empty.mkdir()
        r = self.audit.inspect_maps(empty)
        self.assertTrue(r["directory_exists"])
        self.assertIn("game_directory_observed", r)
        self.assertFalse(r["game_directory_observed"])
        self.assertEqual(r["status"], "root_unavailable")
        self.assertEqual(r["entries_examined"], 0)
        self.assertTrue(any(i["status"] == "missing_game_directory" for i in r["issues"]))
        result = subprocess.run([sys.executable, str(SCRIPT), "--dota-root", str(empty)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)

    def test_missing_loose_directories_are_reported_separately_from_archives(self):
        self.file("game/dota/pak01_dir.vpk")
        r = self.audit.inspect_maps(self.install)
        self.assertIn("locations", r)
        locations = {x["path"]: x["present"] for x in r["locations"]}
        self.assertFalse(locations["content/dota/maps"])
        self.assertFalse(locations["game/dota/maps"])
        self.assertTrue(locations["game/dota"])
        self.assertEqual(r["entries_examined"], 2)  # existing archive directory + one entry

    def test_cli_errors_identify_invalid_limit_and_existing_target(self):
        invalid = self.cli("--max-files", 0)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("max_files", invalid.stderr)
        self.assertNotIn("Report not saved", invalid.stderr)
        target = self.base / "existing.json"
        target.write_text("user data")
        existing = self.cli("--output", target)
        self.assertEqual(existing.returncode, 2)
        self.assertIn("exists", existing.stderr)
        self.assertEqual(target.read_text(), "user data")

    def test_stdout_json_supports_cyrillic_names_in_narrow_windows_encoding(self):
        self.file("content/dota/maps/карта.vmap")
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run([sys.executable, str(SCRIPT), "--dota-root", str(self.install)],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["resources"][0]["path"], "content/dota/maps/карта.vmap")

    def test_unsafe_supplied_steam_library_cannot_allow_output_in_its_real_target(self):
        library, _ = self.manifest()
        alias = self.base / "steam_alias"
        self.link(alias, library, True)
        self.install = self.base / "nonstandard"
        (self.install / "game/dota").mkdir(parents=True)
        output = library / "report.json"
        result = self.cli("--steam-library", alias, "--output", output)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertFalse(output.exists())

    def test_manifest_comments_nested_fields_and_duplicates_cannot_forge_appstate(self):
        library, p = self.manifest()
        fixtures = [
            '// "appid" "570"\n"AppState" { "appid" "999" "installdir" "dota" "buildid" "123" }',
            '"AppState" { "UserConfig" { "appid" "570" } "appid" "999" "installdir" "dota" "buildid" "123" }',
            '"AppState" { "appid" "570" "appid" "999" "installdir" "dota" "buildid" "123" }',
        ]
        for text in fixtures:
            with self.subTest(text=text):
                p.write_text(text)
                r = self.audit.inspect_maps(self.install, library)
                self.assertNotEqual(r["build_evidence"]["status"], "associated")
                self.assertIsNone(r["build_evidence"]["build_id"])


if __name__ == "__main__": unittest.main()
