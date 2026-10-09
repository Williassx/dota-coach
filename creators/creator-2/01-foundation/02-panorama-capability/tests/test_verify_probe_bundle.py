"""Check the read-only CLI against real source bundles and damaged inputs."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
SCRIPT = TOOLS / "verify_probe_bundle.py"
spec = importlib.util.spec_from_file_location("bundle_fixture_builder", TOOLS / "build_probe_bundle.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
PREFIX = "creators/creator-2/01-foundation/02-panorama-capability/src/panorama/"


class VerifyBundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "read-only bundle verifier not implemented")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        copied_tools = self.repo / "creators/creator-2/01-foundation/02-panorama-capability/tools"
        copied_tools.mkdir(parents=True)
        for name in ["build_probe_bundle.py", "verify_probe_bundle.py"]:
            shutil.copy2(TOOLS / name, copied_tools / name)
        self.script = copied_tools / "verify_probe_bundle.py"
        self.bundle = self.repo / "build/dota_coach/probe"
        self.resources = {
            "scripts/custom_game/coach_probe_state.js": b"var DotaCoachProbe = {};",
            "scripts/custom_game/coach_probe.js": b"void DotaCoachProbe;",
            "styles/custom_game/coach_probe.css": b".Probe { width: 100px; }",
            "layout/custom_game/custom_ui_manifest.xml": b'<root><CustomUIElement layoutfile="file://{resources}/layout/custom_game/coach_probe.xml" /></root>',
            "layout/custom_game/coach_probe.xml": b'<root><include src="file://{resources}/styles/custom_game/coach_probe.css" /><include src="file://{resources}/scripts/custom_game/coach_probe_state.js" /><include src="file://{resources}/scripts/custom_game/coach_probe.js" /></root>',
        }
        self.manifest = {"schema_version": 1, "kind": "panorama_source_probe", "assets": []}
        for relative, data in self.resources.items():
            source = self.repo / (PREFIX + relative)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(data)
            self.manifest["assets"].append({"source": PREFIX + relative, "target": "content/panorama/" + relative})
        self.manifest_file = self.repo / "manifest.json"
        self.manifest_file.write_text(json.dumps(self.manifest), encoding="utf-8")
        builder.build_bundle(self.repo, self.manifest, self.bundle)
        self.report_file = self.bundle / "bundle-report.json"

    def snapshot(self):
        result = {}
        for path in self.repo.rglob("*"):
            if path.is_symlink():
                result[str(path.relative_to(self.repo))] = ("link", os.readlink(path))
            elif path.is_file():
                result[str(path.relative_to(self.repo))] = (path.read_bytes(), path.stat().st_mtime_ns)
        return result

    def run_cli(self, expected=2):
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(self.script), "--repository", str(self.repo),
                                 "--manifest", str(self.manifest_file), "--bundle", str(self.bundle)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before, "verification changed existing files")
        if expected:
            self.assertEqual(result.stdout, "")
            self.assertIn("Bundle verification failed:", result.stderr)
        return result

    def change_report(self, transform):
        report = json.loads(self.report_file.read_text())
        transform(report)
        self.report_file.write_text(json.dumps(report), encoding="utf-8")

    def refresh_xml(self, content):
        name = "layout/custom_game/coach_probe.xml"
        payload = content.encode()
        (self.repo / (PREFIX + name)).write_bytes(payload)
        (self.bundle / ("content/panorama/" + name)).write_bytes(payload)

        def update(report):
            asset = next(a for a in report["assets"] if a["target"].endswith(name))
            asset["bytes"] = len(payload)
            asset["sha256"] = hashlib.sha256(payload).hexdigest()

        self.change_report(update)

    def test_valid_package_returns_integrity_result_without_native_claims(self):
        result = self.run_cli(expected=0)
        data = json.loads(result.stdout)
        self.assertIs(data["package_verified"], True)
        self.assertEqual(data["assets"], 5)
        self.assertEqual(data["xml_resource_links"], 4)
        self.assertIs(data["source2_compiled"], False)
        self.assertIs(data["runtime_verified"], False)
        self.assertEqual(result.stderr, "")

    def test_changed_asset_fails(self):
        (self.bundle / "content/panorama/scripts/custom_game/coach_probe.js").write_bytes(b"changed")
        self.run_cli()

    def test_forged_hash_cannot_make_changed_asset_match_source(self):
        entry = self.manifest["assets"][0]
        payload = b"forged but internally consistent"
        (self.bundle / entry["target"]).write_bytes(payload)
        self.change_report(lambda report: report["assets"][0].update(
            bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()))
        self.run_cli()

    def test_missing_asset_fails(self):
        (self.bundle / self.manifest["assets"][0]["target"]).unlink()
        self.run_cli()

    def test_unexpected_file_or_empty_directory_fails(self):
        for name, is_directory in [("unexpected.txt", False), ("unexpected", True)]:
            with self.subTest(name=name):
                path = self.bundle / name
                path.mkdir() if is_directory else path.write_bytes(b"preserve")
                self.run_cli()
                path.rmdir() if is_directory else path.unlink()

    def test_newer_source_marks_package_as_not_matching_current_sources(self):
        (self.repo / self.manifest["assets"][0]["source"]).write_bytes(b"newer source")
        result = self.run_cli()
        self.assertIn("current source", result.stderr)

    def test_missing_or_invalid_report_fails(self):
        for data in [None, b"{bad json", b"[]"]:
            with self.subTest(data=data):
                if data is None:
                    self.report_file.unlink()
                else:
                    self.report_file.write_bytes(data)
                self.run_cli()

    def test_report_cannot_claim_native_readiness_or_incomplete_success(self):
        original = self.report_file.read_bytes()
        for field, value in [("source2_compiled", True), ("runtime_verified", 0),
                             ("complete", False), ("schema_version", True)]:
            with self.subTest(field=field):
                self.report_file.write_bytes(original)
                self.change_report(lambda report: report.update({field: value}))
                self.run_cli()

    def test_report_asset_list_and_metadata_must_match(self):
        original = self.report_file.read_bytes()
        transforms = [lambda report: report["assets"].pop(),
                      lambda report: report["assets"].append(report["assets"][0]),
                      lambda report: report["assets"][0].update(bytes=True),
                      lambda report: report["assets"][0].update(source="other.js")]
        for transform in transforms:
            with self.subTest(transform=transform):
                self.report_file.write_bytes(original)
                self.change_report(transform)
                self.run_cli()

    def test_changed_manifest_cannot_be_accepted_by_old_report(self):
        self.manifest["assets"].reverse()
        self.manifest_file.write_text(json.dumps(self.manifest))
        self.run_cli()

    def test_invalid_xml_fails_even_when_hashes_match(self):
        self.refresh_xml("<root>")
        self.run_cli()

    def test_missing_escaping_external_or_dtd_xml_reference_fails(self):
        for text in ['<root><include src="file://{resources}/missing.js" /></root>',
                     '<root><include src="file://{resources}/../outside.js" /></root>',
                     '<root><include src="https://example.test/script.js" /></root>',
                     '<!DOCTYPE root [<!ENTITY x "data">]><root>&x;</root>']:
            with self.subTest(xml=text):
                self.refresh_xml(text)
                self.run_cli()

    def test_resource_symlink_is_rejected(self):
        target = self.bundle / self.manifest["assets"][0]["target"]
        outside = self.repo / "outside.js"
        outside.write_bytes(target.read_bytes())
        target.unlink()
        try:
            target.symlink_to(outside)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        self.run_cli()

    def test_bundle_ancestor_symlink_is_rejected(self):
        original = self.bundle
        try:
            (self.repo / "build/dota_coach/link").symlink_to(original, target_is_directory=True)
        except OSError as error:
            self.skipTest("symbolic links unavailable: " + str(error))
        self.bundle = self.repo / "build/dota_coach/link"
        self.run_cli()

    def test_oversized_json_is_rejected(self):
        self.report_file.write_bytes(b" " * (256 * 1024 + 1))
        self.run_cli()

    def test_deeply_nested_manifest_or_report_has_controlled_cli_failure(self):
        nested = ("[" * 30000 + "0" + "]" * 30000).encode()
        for path in [self.manifest_file, self.report_file]:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                try:
                    path.write_bytes(nested)
                    result = self.run_cli()
                    self.assertNotIn("Traceback", result.stderr)
                finally:
                    path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
