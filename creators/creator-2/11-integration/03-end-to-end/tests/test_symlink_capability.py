import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HELPER = Path(__file__).with_name('symlink_capability.py')


class SymlinkCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HELPER.is_file(), 'Test-only symlink capability helper missing')
        spec = importlib.util.spec_from_file_location('capability_under_test', HELPER)
        self.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.helper)
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.sentinel = self.root / 'keep'; self.sentinel.write_text('unchanged')

    def error(self, number):
        error = OSError('fixture error'); error.winerror = number; return error

    def test_windows_file_privilege_error_is_explicit_skip_before_mutation(self):
        with patch.object(self.helper.sys, 'platform', 'win32'), patch.object(Path, 'symlink_to', side_effect=self.error(1314)):
            with self.assertRaisesRegex(unittest.SkipTest, 'unsupported_file_symlink: WinError 1314'):
                self.helper.require_symlink(self, self.root)
        self.assertEqual(list(self.root.iterdir()), [self.sentinel])
        self.assertEqual(self.sentinel.read_text(), 'unchanged')

    def test_windows_directory_privilege_error_has_distinct_skip(self):
        with patch.object(self.helper.sys, 'platform', 'win32'), patch.object(Path, 'symlink_to', side_effect=self.error(1314)):
            with self.assertRaisesRegex(unittest.SkipTest, 'unsupported_directory_symlink: WinError 1314'):
                self.helper.require_symlink(self, self.root, directory=True)

    def test_other_windows_errors_remain_errors(self):
        error = self.error(5)
        with patch.object(self.helper.sys, 'platform', 'win32'), patch.object(Path, 'symlink_to', side_effect=error):
            with self.assertRaises(OSError) as caught: self.helper.require_symlink(self, self.root)
        self.assertIs(caught.exception, error)

    def test_non_windows_privilege_number_is_not_silently_skipped(self):
        with patch.object(self.helper.sys, 'platform', 'linux'), patch.object(Path, 'symlink_to', side_effect=self.error(1314)):
            with self.assertRaises(OSError): self.helper.require_symlink(self, self.root)

    def test_not_implemented_remains_error(self):
        with patch.object(Path, 'symlink_to', side_effect=NotImplementedError('fixture')):
            with self.assertRaises(NotImplementedError): self.helper.require_symlink(self, self.root)

    def test_ordinary_file_cannot_fake_probe_success(self):
        def ordinary(link, target, target_is_directory=False): link.write_text('not a link')
        with patch.object(Path, 'symlink_to', ordinary):
            with self.assertRaises(AssertionError): self.helper.require_symlink(self, self.root)

    def test_real_file_probe_preserves_owned_fixture(self):
        self.helper.require_symlink(self, self.root)
        self.assertEqual(list(self.root.iterdir()), [self.sentinel])

    def test_real_directory_probe_preserves_owned_fixture(self):
        self.helper.require_symlink(self, self.root, directory=True)
        self.assertEqual(list(self.root.iterdir()), [self.sentinel])
