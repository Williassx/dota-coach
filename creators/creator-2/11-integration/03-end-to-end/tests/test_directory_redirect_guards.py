"""Actual directory redirects: Windows junctions and POSIX directory symlinks.

These supplement the existing file-symlink tests; they do not replace them.
"""
import base64
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/run_source_checks.py'
SPEC = importlib.util.spec_from_file_location('directory_redirect_runner', SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
CATALOG = 'creators/creator-2/11-integration/03-end-to-end/suite-catalog.json'
SUITE = 'creators/creator-2/11-integration/03-end-to-end/tests'


class DirectoryRedirectGuards(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        external = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.addCleanup(external.cleanup)
        self.root = Path(workspace.name)
        self.external = Path(external.name)
        self.keep = self.external / 'keep.txt'
        self.keep.write_bytes(b'untouched external fixture')

    def redirect(self, relative):
        link = self.root / relative
        self.assertTrue(link.is_relative_to(self.root))
        self.assertFalse(link.exists())
        link.parent.mkdir(parents=True, exist_ok=True)
        if os.name == 'nt':
            powershell = shutil.which('powershell.exe')
            self.assertIsNotNone(powershell, 'Windows junction test requires installed PowerShell')
            def quoted(path):
                return "'" + str(path).replace("'", "''") + "'"
            command = ('New-Item -ItemType Junction -Path ' + quoted(link) +
                       ' -Value ' + quoted(self.external) + ' -ErrorAction Stop | Out-Null')
            encoded = base64.b64encode(command.encode('utf-16-le')).decode('ascii')
            subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
                           capture_output=True, timeout=10, check=True,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            link.symlink_to(self.external, target_is_directory=True)
        self.addCleanup(self.remove_redirect, link)
        info = link.lstat()
        self.assertTrue(stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400)
        return link

    def remove_redirect(self, link):
        # Remove only the observed redirect, never its target or an ordinary tree.
        self.assertTrue(link.is_relative_to(self.root))
        info = link.lstat()
        if stat.S_ISLNK(info.st_mode):
            link.unlink()
        else:
            self.assertTrue(getattr(info, 'st_file_attributes', 0) & 0x400)
            link.rmdir()
        self.assertEqual(self.keep.read_bytes(), b'untouched external fixture')

    def forbid_external_open(self):
        original = Path.open
        def guarded(path, *args, **kwargs):
            self.assertFalse(path.resolve().is_relative_to(self.external), 'External fixture must not be opened')
            return original(path, *args, **kwargs)
        return mock.patch.object(Path, 'open', guarded)

    def test_redirected_source_is_refused_before_external_file_open(self):
        self.redirect('creators/redirect')
        with self.forbid_external_open(), self.assertRaisesRegex(ValueError, 'Symlink/reparse'):
            runner.paths.read_source(self.root, 'creators/redirect/keep.txt')
        self.assertEqual(self.keep.read_bytes(), b'untouched external fixture')

    def test_redirected_output_is_refused_without_creating_external_child(self):
        self.redirect('build/dota_coach/redirect')
        with self.forbid_external_open(), self.assertRaisesRegex(ValueError, 'Symlink/reparse'):
            runner.paths.output_path(self.root, Path('build/dota_coach/redirect/new-output'))
        self.assertFalse((self.external / 'new-output').exists())
        self.assertEqual(list(self.external.iterdir()), [self.keep])

    def test_nested_test_redirect_is_refused_before_discovery_or_outputs(self):
        suite = self.root / SUITE
        suite.mkdir(parents=True)
        (suite / 'test_fixture.py').write_text('import unittest\n', encoding='utf-8')
        catalog = self.root / CATALOG
        catalog.write_text(json.dumps({'schema_version': 1, 'suites': [
            {'id': 'python-fixture', 'framework': 'python-unittest', 'path': SUITE}]}), encoding='utf-8')
        self.redirect(SUITE + '/nested')
        with self.forbid_external_open(), self.assertRaisesRegex(ValueError, 'Symlink/reparse'):
            runner.load_catalog(self.root)
        self.assertFalse((self.root / 'build').exists())
        self.assertEqual(list(self.external.iterdir()), [self.keep])


if __name__ == '__main__':
    unittest.main()
