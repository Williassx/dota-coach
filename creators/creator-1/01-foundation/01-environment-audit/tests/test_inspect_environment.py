"""Checks for read-only diagnostics using real Git and filesystem fixtures."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "inspect_environment.py"


class EnvironmentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            return
        spec = importlib.util.spec_from_file_location("inspect_environment", SCRIPT)
        cls.audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.audit)

    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "diagnostic helper not implemented")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def make_git(self, remote):
        repo = self.root / "repository"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", remote], check=True)
        (repo / "user-file.txt").write_text("preserve this", encoding="utf-8")
        return repo

    def test_steam_libraries_deduplicate_and_read_escaped_paths(self):
        steam = self.root / "Steam"
        external = self.root / "OtherLibrary"
        (steam / "steamapps").mkdir(parents=True)
        external.mkdir()
        value = str(external).replace("\\", "\\\\")
        (steam / "steamapps" / "libraryfolders.vdf").write_text(
            '"libraryfolders" { "0" { "path" "' + value + '" } '
            '"1" { "path" "' + value + '" } }', encoding="utf-8")
        self.assertEqual(self.audit.steam_libraries(steam), [steam, external])

    def test_manifest_without_game_does_not_claim_runtime(self):
        (self.root / "steamapps").mkdir()
        (self.root / "steamapps" / "appmanifest_570.acf").write_text(
            '"AppState" { "appid" "570" "installdir" "dota 2 beta" "buildid" "123" }',
            encoding="utf-8")
        result = self.audit.inspect_dota_library(self.root)
        self.assertTrue(result["manifest_found"])
        self.assertEqual(result["build_id"], "123")
        self.assertFalse(result["game_directory_exists"])
        self.assertFalse(result["runtime_verified"])

    def test_installdir_outside_common_is_rejected(self):
        (self.root / "steamapps").mkdir()
        (self.root / "steamapps" / "appmanifest_570.acf").write_text(
            '"installdir" "../../outside" "buildid" "123"', encoding="utf-8")
        result = self.audit.inspect_dota_library(self.root)
        self.assertEqual(result["status"], "invalid_install_directory")
        self.assertNotIn("game_path", result)

    def test_git_credentials_are_not_reported_and_user_files_unchanged(self):
        repo = self.make_git("https://username:secret-value@github.com/Williassx/dota-coach.git")
        before = {p.relative_to(repo): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
        result = self.audit.inspect_git(repo)
        self.assertTrue(result["origin_matches_expected"])
        self.assertTrue(result["dirty"])
        self.assertNotIn("secret-value", json.dumps(result))
        self.assertNotIn("username", json.dumps(result))
        after = {p.relative_to(repo): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_another_github_project_is_not_the_expected_clone(self):
        repo = self.make_git("https://github.com/Williassx/another-project.git")
        self.assertFalse(self.audit.inspect_git(repo)["origin_matches_expected"])

    def test_status_does_not_refresh_the_index_of_a_tracked_file(self):
        repo = self.make_git("https://github.com/Williassx/dota-coach.git")
        subprocess.run(["git", "-C", str(repo), "add", "user-file.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Audit fixture",
                        "-c", "user.email=audit@example.invalid", "-c", "commit.gpgsign=false",
                        "commit", "-qm", "fixture"], check=True)
        file = repo / "user-file.txt"
        original = file.stat()
        os.utime(file, ns=(original.st_atime_ns, original.st_mtime_ns + 3_000_000_000))
        index = repo / ".git" / "index"
        before = index.read_bytes()
        self.audit.inspect_git(repo)
        self.assertEqual(before, index.read_bytes(), "audit must not refresh Git index")

    def test_existing_report_is_preserved(self):
        report = self.root / "report.json"
        report.write_text("user-owned report", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repository", str(self.root), "--output", str(report)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report.read_text(encoding="utf-8"), "user-owned report")

    def test_cloud_report_does_not_claim_windows_or_dota_tested(self):
        result = self.audit.build_report(self.root, [])
        self.assertFalse(result["runtime_verified"])
        self.assertEqual(result["windows_repository"], r"D:\AI\dota2coach")
        if sys.platform != "win32":
            self.assertEqual(result["windows_access"], "not_accessible_from_this_runtime")


if __name__ == "__main__":
    unittest.main()
