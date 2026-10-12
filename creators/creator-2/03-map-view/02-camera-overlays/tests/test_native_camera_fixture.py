"""Isolated native camera fixture: exact sources and refusals before output writes."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
PACKAGE = 'creators/creator-2/11-integration/02-addon-packaging/'
FIXTURE = 'creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/'
RESOURCE = 'content/panorama/'
LAYOUT = RESOURCE + 'layout/custom_game/coach_hud.xml'
DERIVED = RESOURCE + 'layout/custom_game/camera_fixture.xml'
MANIFEST = RESOURCE + 'layout/custom_game/custom_ui_manifest.xml'
DRIVER = RESOURCE + 'scripts/custom_game/camera_fixture.js'
BUILDER = TASK / 'tools/build_native_camera_fixture.py'


class NativeCameraFixtureTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Native camera fixture builder missing')
        spec = importlib.util.spec_from_file_location('native_camera_fixture_builder', BUILDER)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.recipe = json.loads((ROOT / PACKAGE / 'bundle-manifest.json').read_bytes())
        sources = [entry['source'] for entry in self.recipe['assets']] + [
            FIXTURE + 'custom_ui_manifest.xml', FIXTURE + 'camera_fixture.js',
            PACKAGE + 'bundle-manifest.json']
        self.before = {}
        for source in sources:
            raw = (ROOT / source).read_bytes()
            self.before[source] = raw
            target = self.repo / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.output = self.repo / 'build/dota_coach/native-camera'

    def no_output(self):
        self.assertFalse((self.repo / 'build').exists())

    def test_exact_sources_derived_subtree_include_order_and_false_flags(self):
        report = self.builder.build_fixture(self.repo, self.output)
        self.assertEqual(report['fixture_type'], 'native_camera_test_only')
        self.assertEqual(report['canonical_inputs'], 13)
        self.assertEqual(len(report['assets']), 15)
        self.assertEqual(len({a['target'].casefold() for a in report['assets']}), 15)
        self.assertEqual(sum(a['derived'] for a in report['assets']), 1)
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        expected = [{'source': e['source'], 'target': e['target'],
                     'sha256': hashlib.sha256(self.before[e['source']]).hexdigest()}
                    for e in self.recipe['assets']]
        self.assertEqual(report['canonical_input_hashes'], expected)
        for source, raw in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), raw)
        for entry in report['assets']:
            raw = (self.output / entry['target']).read_bytes()
            self.assertEqual(entry['bytes'], len(raw))
            self.assertEqual(entry['sha256'], hashlib.sha256(raw).hexdigest())
            if not entry['derived']:
                self.assertEqual(raw, self.before[entry['source']])
        canonical = ET.fromstring(self.before[next(e['source'] for e in self.recipe['assets']
                                                   if e['target'] == LAYOUT)])
        derived = ET.parse(self.output / DERIVED).getroot()
        original_scripts = [e.attrib for e in canonical.findall('./scripts/include')]
        actual_scripts = [e.attrib for e in derived.findall('./scripts/include')]
        self.assertEqual(actual_scripts[:-1], original_scripts)
        self.assertEqual(actual_scripts[-1], {'src': 'file://{resources}/scripts/custom_game/camera_fixture.js'})
        self.assertIsNotNone(derived.find('.//Panel[@id="CoachCamera"]'))
        status = derived.find('./Panel/Label[@id="NativeCameraFixtureStatus"]')
        self.assertIsNotNone(status)
        self.assertEqual(status.get('html'), 'false')
        self.assertEqual(status.get('hittest'), 'false')
        for rule in ['horizontal-align: left', 'vertical-align: bottom', 'margin-bottom: 44px', 'width: 740px']:
            self.assertIn(rule, status.get('style'))
        derived.find('./Panel').remove(status)
        derived.find('./scripts').remove(derived.find('./scripts/include[last()]'))
        self.assertEqual(ET.tostring(derived), ET.tostring(canonical))
        ids = [e.get('id') for e in derived.iter() if e.get('id')]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual((self.output / MANIFEST).read_bytes(), self.before[FIXTURE + 'custom_ui_manifest.xml'])

    def test_existing_output_preserves_user_file(self):
        self.output.mkdir(parents=True)
        sentinel = self.output / 'keep'
        sentinel.write_bytes(b'untouched')
        with self.assertRaises(FileExistsError): self.builder.build_fixture(self.repo, self.output)
        self.assertEqual(list(self.output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b'untouched')

    def test_escape_and_boundary_refuse_before_writes(self):
        for output in [self.repo / 'outside', self.repo / 'build/dota_coach',
                       self.repo / 'build/dota_coach/../../../escape']:
            with self.subTest(output=output):
                with self.assertRaises(ValueError): self.builder.build_fixture(self.repo, output)
                self.no_output()
        self.assertFalse((self.repo.parent / 'escape').exists())

    def test_missing_driver_refuses_before_writes(self):
        (self.repo / FIXTURE / 'camera_fixture.js').unlink()
        with self.assertRaises((OSError, ValueError)): self.builder.build_fixture(self.repo, self.output)
        self.no_output()

    def test_changed_recipe_refuses_before_writes(self):
        for change in ['kind', 'mapping', 'missing', 'extra']:
            with self.subTest(change=change):
                recipe = copy.deepcopy(self.recipe)
                if change == 'kind': recipe['kind'] = 'panorama_source_probe'
                elif change == 'mapping': recipe['assets'][0]['target'] = 'content/panorama/layout/custom_game/wrong.xml'
                elif change == 'missing': recipe['assets'].pop()
                else: recipe['unexpected'] = True
                (self.repo / PACKAGE / 'bundle-manifest.json').write_text(json.dumps(recipe), encoding='utf-8')
                with self.assertRaises(ValueError): self.builder.build_fixture(self.repo, self.output)
                self.no_output()

    def test_executable_or_wrong_manifest_refuses_before_writes(self):
        original = self.before[FIXTURE + 'custom_ui_manifest.xml']
        for change in ['executable', 'wrong-layout', 'mixed-text', 'dtd']:
            with self.subTest(change=change):
                tree = ET.fromstring(original)
                if change == 'executable': tree.find('./Panel').set('onload', 'evil()')
                elif change == 'wrong-layout': tree.find('./Panel/CustomUIElement').set('layoutfile', 'file://evil')
                elif change == 'mixed-text': tree.text = 'unexpected'
                raw = ET.tostring(tree)
                if change == 'dtd': raw = b'<!DOCTYPE root [<!ENTITY x "evil">]>' + raw
                (self.repo / FIXTURE / 'custom_ui_manifest.xml').write_bytes(raw)
                with self.assertRaises((ValueError, ET.ParseError)): self.builder.build_fixture(self.repo, self.output)
                self.no_output()

    def test_fresh_outputs_have_identical_assets_and_canonical_hashes(self):
        first = self.builder.build_fixture(self.repo, self.output)
        second = self.builder.build_fixture(self.repo, self.repo / 'build/dota_coach/native-camera-2')
        self.assertEqual(first['assets'], second['assets'])
        self.assertEqual(first['canonical_input_hashes'], second['canonical_input_hashes'])

    def test_motion_variant_uses_exact_owned_driver_preserves_canonical(self):
        motion = self.repo / FIXTURE / 'camera_motion.js'
        raw = b'/* TEST ONLY: motion driver */\n'
        motion.write_bytes(raw)
        report = self.builder.build_fixture(self.repo, self.output, variant='motion')
        self.assertEqual(report['diagnostic_variant'], 'motion')
        self.assertEqual(len(report['assets']), 15)
        entry = next(a for a in report['assets'] if a['target'] == DRIVER)
        self.assertEqual(entry['source'], FIXTURE + 'camera_motion.js')
        self.assertEqual((self.output / DRIVER).read_bytes(), raw)
        self.assertFalse(report['runtime_verified'])
        for source, before in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), before)

    def test_unknown_variant_refuses_before_reads_or_writes(self):
        for variant in [None, True, '../escape', 'demo', {'path': 'camera_motion.js'}]:
            with self.subTest(variant=variant):
                with self.assertRaises(ValueError):
                    self.builder.build_fixture(self.repo, self.output, variant=variant)
                self.no_output()

    def test_missing_motion_driver_refuses_before_output(self):
        with self.assertRaises((OSError, ValueError)):
            self.builder.build_fixture(self.repo, self.output, variant='motion')
        self.no_output()


if __name__ == '__main__':
    unittest.main()
