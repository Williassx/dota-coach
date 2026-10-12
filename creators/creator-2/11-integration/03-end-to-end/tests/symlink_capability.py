"""Test precondition only; never weakens production link/reparse guards."""
from pathlib import Path
import sys
import tempfile


def require_symlink(test_case, root, directory=False):
    """Probe a real link in a fresh child of the caller-owned temporary fixture."""
    if type(directory) is not bool:
        raise ValueError('directory must be bool')
    with tempfile.TemporaryDirectory(prefix='symlink-probe-', dir=root) as temporary:
        probe = Path(temporary)
        target, link = probe / 'target', probe / 'link'
        if directory:
            target.mkdir()
            sentinel = target / 'keep'
        else:
            sentinel = target
        sentinel.write_text('probe preserved', encoding='utf-8')
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            if sys.platform == 'win32' and getattr(error, 'winerror', None) == 1314:
                kind = 'directory' if directory else 'file'
                test_case.skipTest('unsupported_' + kind + '_symlink: WinError 1314')
            raise
        test_case.assertTrue(link.is_symlink(), 'Probe did not create a symbolic link')
        test_case.assertEqual(link.is_dir(), directory)
        test_case.assertEqual(link.is_file(), not directory)
        link.unlink()
        test_case.assertTrue(target.exists(), 'Removing probe link changed its target')
        test_case.assertEqual(sentinel.read_text(encoding='utf-8'), 'probe preserved')
