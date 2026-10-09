"""Filesystem checks for an exclusive, portable UI source bundle."""
import hashlib
import importlib.util
import json
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "tools/build_probe_bundle.py"
PREFIX = "creators/creator-2/01-foundation/02-panorama-capability/src/panorama/"


class ProbeBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SCRIPT.is_file():
            spec = importlib.util.spec_from_file_location("probe_bundle", SCRIPT)
            cls.bundle = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.bundle)

    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "bundle builder not implemented")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        self.output = self.repo / "build/dota_coach/probe"
        self.assets = []
        for name in ["scripts/custom_game/probe.js", "styles/custom_game/probe.css"]:
            source = self.repo / (PREFIX + name)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(("source " + name).encode())
            self.assets.append({"source": PREFIX + name, "target": "content/panorama/" + name})
        self.manifest = {"schema_version": 1, "kind": "panorama_source_probe", "assets": self.assets}

    def test_bytes_hashes_and_source_files_are_preserved(self):
        before = {a["source"]: (self.repo / a["source"]).read_bytes() for a in self.assets}
        report = self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertTrue(report["complete"])
        self.assertFalse(report["runtime_verified"])
        self.assertFalse(report["source2_compiled"])
        for asset in report["assets"]:
            data = (self.output / asset["target"]).read_bytes()
            self.assertEqual(data, before[asset["source"]])
            self.assertEqual(asset["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual((self.repo / asset["source"]).read_bytes(), data)
        self.assertEqual(json.loads((self.output / "bundle-report.json").read_text()), report)

    def test_existing_output_is_not_modified(self):
        self.output.mkdir(parents=True)
        sentinel = self.output / "user.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(list(self.output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(), "preserve")

    def test_missing_second_source_does_not_create_partial_output(self):
        (self.repo / self.assets[1]["source"]).unlink()
        with self.assertRaises((ValueError, OSError)):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse((self.repo / "build").exists())

    def test_escape_and_nonportable_manifest_paths_are_rejected(self):
        invalid = ["../outside.js", "/tmp/outside.js", "content/panorama/../outside.js",
                   "content/panorama/C:outside.js", "content/panorama/a\\b.js",
                   "content/panorama/CON.js", "content/panorama/Lpt1.js",
                   "content/panorama/trailing. /file.js", "content/panorama/a./file.js",
                   "content/panorama/a?/file.js", "content/panorama/CON .js"]
        for target in invalid:
            with self.subTest(target=target):
                self.assets[0]["target"] = target
                with self.assertRaises(ValueError):
                    self.bundle.build_bundle(self.repo, self.manifest, self.output)
                self.assertFalse(self.output.exists())

    def test_source_outside_own_panorama_library_is_rejected(self):
        self.assets[0]["source"] = "creators/creator-1/server.js"
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_windows_case_and_file_directory_collisions_are_rejected(self):
        self.assets[1]["source"] = self.assets[0]["source"]
        for targets in [["content/panorama/probe.js", "content/panorama/PROBE.JS"],
                        ["content/panorama/parent.js", "content/panorama/parent.js/child.js"]]:
            with self.subTest(targets=targets):
                for asset, target in zip(self.assets, targets):
                    asset["target"] = target
                with self.assertRaises(ValueError):
                    self.bundle.build_bundle(self.repo, self.manifest, self.output)
                self.assertFalse(self.output.exists())

    def test_source_symlink_is_rejected_before_output_creation(self):
        source = self.repo / self.assets[0]["source"]
        outside = self.repo / "outside.js"
        outside.write_text("user source", encoding="utf-8")
        source.unlink()
        try:
            source.symlink_to(outside)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(outside.read_text(), "user source")

    def test_output_ancestor_symlink_is_rejected_without_writing_through_it(self):
        outside = self.repo / "outside"
        outside.mkdir()
        (self.repo / "build").mkdir()
        try:
            (self.repo / "build/dota_coach").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(list(outside.iterdir()), [])

    def test_reparse_flag_in_source_ancestor_is_rejected(self):
        blocked = (self.repo / self.assets[0]["source"]).parent
        original = Path.lstat

        def reparse(path, *args, **kwargs):
            if path == blocked:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "lstat", reparse):
            with self.assertRaises(ValueError):
                self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_output_outside_build_library_is_rejected(self):
        target = self.repo / "creators/replace-me"
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, target)
        self.assertFalse(target.exists())

    def test_resource_and_manifest_limits_reject_before_writing(self):
        source = self.repo / self.assets[0]["source"]
        source.write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse(self.output.exists())
        source.write_bytes(b"small")
        self.manifest["assets"] = self.assets * 51
        with self.assertRaises(ValueError):
            self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_write_failure_has_no_success_report_and_keeps_partial_files(self):
        failed = self.output / self.assets[1]["target"]
        original = Path.open

        def fail_write(path, *args, **kwargs):
            if path == failed:
                raise OSError("simulated disk full")
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "open", fail_write):
            with self.assertRaises(OSError):
                self.bundle.build_bundle(self.repo, self.manifest, self.output)
        self.assertFalse((self.output / "bundle-report.json").exists())
        self.assertEqual((self.output / self.assets[0]["target"]).read_bytes(),
                         (self.repo / self.assets[0]["source"]).read_bytes())


if __name__ == "__main__":
    unittest.main()
