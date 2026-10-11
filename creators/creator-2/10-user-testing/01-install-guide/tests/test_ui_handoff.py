import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TASK = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[5]
TOOL = TASK / 'tools/prepare_ui_handoff.py'


def load():
    spec = importlib.util.spec_from_file_location('ui_handoff_test', TOOL)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


class UIHandoffTests(unittest.TestCase):
    def setUp(self):
        self.helper = load()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)

    def copy_screen(self, screen):
        relative, kind = self.helper.SCREENS[screen]
        recipe = json.loads((REPOSITORY / relative).read_text())
        file = self.repo / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(recipe))
        for item in recipe['assets'] + recipe.get('layout_inputs', []):
            destination = self.repo / item['source']
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((REPOSITORY / item['source']).read_bytes())
        return recipe, kind

    def report(self, result):
        return json.loads((self.repo / result['report']).read_text())

    def test_default_probe_verified_companion_outside_bundle_no_native_claims(self):
        recipe, kind = self.copy_screen('probe')
        result = self.helper.prepare_handoff(self.repo)
        report = self.report(result)
        self.assertEqual(report['screen'], 'probe')
        self.assertEqual(report['kind'], kind)
        self.assertEqual(report['source_verification']['assets'], 5)
        self.assertTrue(report['source_verification']['package_verified'])
        self.assertFalse(report['installation_performed'])
        self.assertIsNone(report['native_destination'])
        self.assertTrue(all(value == 'not_run' for value in report['native_checks'].values()))
        self.assertFalse(report['source_verification']['runtime_verified'])
        self.assertEqual(len(report['assets']), len(recipe['assets']))
        self.assertEqual(Path(result['report']).parent, Path(result['bundle']).parent)
        self.assertNotIn(Path(result['bundle']), Path(result['report']).parents)
        self.assertEqual(report['git']['head'], None)
        self.assertEqual(report['git']['dirty'], None)

    def test_all_seven_fixed_screens_build_and_verify(self):
        expected = {'probe': (5, 4), 'hud': (13, 12), 'preparation': (15, 14),
                    'intervention': (6, 5), 'intervention-screen': (13, 12), 'voice-text': (6, 5),
                    'orders-timeline': (5, 4)}
        self.assertEqual(set(expected), set(self.helper.SCREENS))
        for screen, counts in expected.items():
            with self.subTest(screen=screen):
                self.copy_screen(screen)
                report = self.report(self.helper.prepare_handoff(self.repo, screen))
                self.assertEqual((report['source_verification']['assets'], report['source_verification']['xml_resource_links']), counts)

    def test_unknown_screen_rejected_before_output(self):
        with self.assertRaises(ValueError):
            self.helper.prepare_handoff(self.repo, '../../outside')
        self.assertFalse((self.repo / 'build').exists())

    def test_recipe_kind_cannot_change_screen_meaning(self):
        self.copy_screen('probe')
        path = self.repo / self.helper.SCREENS['probe'][0]
        recipe = json.loads(path.read_text())
        recipe['kind'] = 'panorama_source_voice_text'
        path.write_text(json.dumps(recipe))
        with self.assertRaises(ValueError):
            self.helper.prepare_handoff(self.repo)
        self.assertFalse((self.repo / 'build').exists())

    def test_missing_invalid_large_recipe_fail_before_output(self):
        path = self.repo / self.helper.SCREENS['probe'][0]
        path.parent.mkdir(parents=True)
        for data in ['{', ' ' * (256 * 1024 + 1)]:
            path.write_text(data)
            with self.assertRaises(ValueError):
                self.helper.prepare_handoff(self.repo)
            self.assertFalse((self.repo / 'build').exists())
        path.unlink()
        with self.assertRaises(OSError):
            self.helper.prepare_handoff(self.repo)

    def test_recipe_and_source_symlinks_rejected_without_outputs(self):
        recipe, _ = self.copy_screen('probe')
        for relative in [self.helper.SCREENS['probe'][0], recipe['assets'][0]['source']]:
            file = self.repo / relative
            data = file.read_bytes()
            outside = self.repo / 'outside'
            outside.write_bytes(data)
            file.unlink()
            file.symlink_to(outside)
            with self.assertRaises((ValueError, RuntimeError)):
                self.helper.prepare_handoff(self.repo)
            self.assertFalse((self.repo / 'build').exists())
            file.unlink()
            file.write_bytes(data)

    def test_existing_companion_report_preserved_without_new_bundle(self):
        self.copy_screen('probe')
        result = self.helper.prepare_handoff(self.repo)
        report_path = self.repo / result['report']
        original = report_path.read_bytes()
        directories = list((self.repo / 'build/dota_coach').iterdir())
        with self.assertRaises(FileExistsError):
            self.helper.prepare_handoff(self.repo, bundle=Path(result['bundle']))
        self.assertEqual(report_path.read_bytes(), original)
        self.assertEqual(list((self.repo / 'build/dota_coach').iterdir()), directories)

    def test_existing_bundle_verified_without_rebuilding(self):
        self.copy_screen('voice-text')
        result = self.helper.prepare_handoff(self.repo, 'voice-text')
        (self.repo / result['report']).unlink()
        repeated = self.helper.prepare_handoff(self.repo, 'voice-text', Path(result['bundle']))
        self.assertEqual(repeated['bundle'], result['bundle'])
        self.assertEqual(self.report(repeated)['source_verification']['assets'], 6)

    def test_tampered_existing_bundle_cannot_receive_handoff(self):
        recipe, _ = self.copy_screen('probe')
        result = self.helper.prepare_handoff(self.repo)
        (self.repo / result['report']).unlink()
        asset = self.repo / result['bundle'] / recipe['assets'][0]['target']
        asset.write_text('tampered')
        with self.assertRaises(ValueError):
            self.helper.prepare_handoff(self.repo, bundle=Path(result['bundle']))
        self.assertFalse((self.repo / result['report']).exists())

    def test_current_source_change_invalidates_existing_bundle(self):
        recipe, _ = self.copy_screen('voice-text')
        result = self.helper.prepare_handoff(self.repo, 'voice-text')
        (self.repo / result['report']).unlink()
        file = self.repo / recipe['assets'][-1]['source']
        file.write_bytes(file.read_bytes() + b'\n')
        with self.assertRaises(ValueError):
            self.helper.prepare_handoff(self.repo, 'voice-text', Path(result['bundle']))
        self.assertFalse((self.repo / result['report']).exists())

    def test_external_or_symlink_bundle_rejected(self):
        self.copy_screen('probe')
        result = self.helper.prepare_handoff(self.repo)
        (self.repo / result['report']).unlink()
        link = self.repo / 'build/dota_coach/link'
        link.symlink_to(self.repo / result['bundle'], target_is_directory=True)
        for bundle in [self.repo, link, self.repo / 'build/dota_coach']:
            with self.assertRaises(ValueError):
                self.helper.prepare_handoff(self.repo, bundle=bundle)

    def test_wrong_screen_existing_bundle_rejected(self):
        self.copy_screen('probe')
        self.copy_screen('voice-text')
        result = self.helper.prepare_handoff(self.repo)
        (self.repo / result['report']).unlink()
        with self.assertRaises(ValueError):
            self.helper.prepare_handoff(self.repo, 'voice-text', Path(result['bundle']))

    def test_cli_default_and_voice_text_return_source_only_metadata(self):
        for screen in ['probe', 'voice-text']:
            self.copy_screen(screen)
            command = [sys.executable, str(TOOL), '--repository', str(self.repo)]
            if screen != 'probe':
                command += ['--screen', screen]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertTrue(data['source_verified'])
            self.assertFalse(data['runtime_verified'])
            self.assertEqual(self.report(data)['screen'], screen)

    def test_exact_git_root_head_and_dirty_metadata_without_origin(self):
        self.copy_screen('probe')
        (self.repo / '.gitignore').write_text('/build/\n')
        for command in [['git', 'init', '-q', str(self.repo)], ['git', '-C', str(self.repo), 'add', '.'],
                        ['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-q', '-m', 'fixture']]:
            subprocess.run(command, check=True, capture_output=True)
        head = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD'], text=True).strip()
        report = self.report(self.helper.prepare_handoff(self.repo))
        self.assertEqual(report['git'], {'head': head, 'dirty': False, 'status': 'recorded'})
        self.assertNotIn('origin', json.dumps(report))
        (self.repo / 'new-file').write_text('untracked')
        dirty = self.report(self.helper.prepare_handoff(self.repo))
        self.assertTrue(dirty['git']['dirty'])


if __name__ == '__main__':
    unittest.main()
