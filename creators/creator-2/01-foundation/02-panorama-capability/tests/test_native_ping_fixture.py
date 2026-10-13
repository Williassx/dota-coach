"""Pure filesystem acceptance for the separate diagnostic ping TEST bundle."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[5]
PART = Path(__file__).resolve().parents[1]
PREFIX = PART.relative_to(ROOT).as_posix() + '/'
BUILDER = PART / 'tools/build_native_ping_fixture.py'
FIXTURE = PREFIX + 'tests/native-ping/'
C1 = 'creators/creator-1/01-foundation/03-command-contract/src/scripts/vscripts/'
RESOURCE = 'content/panorama/'
MANIFEST = RESOURCE + 'layout/custom_game/custom_ui_manifest.xml'
CANONICAL = RESOURCE + 'layout/custom_game/coach_probe.xml'
DERIVED = RESOURCE + 'layout/custom_game/ping_fixture.xml'
DRIVER = RESOURCE + 'scripts/custom_game/ping_fixture.js'


class NativePingFixtureTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Missing build_native_ping_fixture.py implementation (expected RED)')
        spec = importlib.util.spec_from_file_location('native_ping_fixture_test_builder', BUILDER)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.output = self.repo / 'build/dota_coach/native-ping-fixture'
        self.recipe = json.loads((PART / 'bundle-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(self.recipe['assets']), 5)
        self.recipe_path = self.repo / PREFIX / 'bundle-manifest.json'
        self.recipe_path.parent.mkdir(parents=True)
        self.recipe_path.write_bytes((PART / 'bundle-manifest.json').read_bytes())
        sources = [asset['source'] for asset in self.recipe['assets']] + [
            FIXTURE + 'custom_ui_manifest.xml', FIXTURE + 'ping_fixture.js',
            C1 + 'diagnostic_ping.lua', C1 + 'ping_game_mode.lua']
        self.before = {}
        for source in sources:
            raw = (ROOT / source).read_bytes()
            self.before[source] = raw
            target = self.repo / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

    def build(self):
        return self.builder.build_fixture(self.repo, self.output)

    def test_exact_nine_outputs_retained_canonical_inputs_and_lua_mapping(self):
        report = self.build()
        self.assertEqual(report['fixture_type'], 'native_diagnostic_ping_test_only')
        self.assertEqual(report['canonical_inputs'], 5)
        self.assertEqual(len(report['canonical_input_hashes']), 5)
        expected = {asset['target'] for asset in self.recipe['assets']} | {
            DERIVED, DRIVER, 'game/scripts/vscripts/diagnostic_ping.lua',
            'game/scripts/vscripts/addon_game_mode.lua'}
        targets = [asset['target'] for asset in report['assets']]
        self.assertEqual(len(targets), 9)
        self.assertEqual(len({target.casefold() for target in targets}), 9)
        self.assertEqual(set(targets), expected)
        self.assertEqual(sum(target.startswith(RESOURCE) for target in targets), 7)
        self.assertFalse(report['runtime_verified'])
        self.assertFalse(report['source2_compiled'])
        self.assertEqual(sum(asset['derived'] for asset in report['assets']), 1)
        for asset in report['assets']:
            output_bytes = (self.output / asset['target']).read_bytes()
            self.assertEqual(asset['bytes'], len(output_bytes))
            self.assertEqual(asset['sha256'], hashlib.sha256(output_bytes).hexdigest())
            if not asset['derived']:
                self.assertEqual(output_bytes, self.before[asset['source']])
        expected_hashes = {asset['source']: hashlib.sha256(self.before[asset['source']]).hexdigest()
                           for asset in self.recipe['assets']}
        self.assertEqual({entry['source']: entry['sha256'] for entry in report['canonical_input_hashes']},
                         expected_hashes)
        self.assertEqual({entry['source']: entry['target'] for entry in report['canonical_input_hashes']},
                         {entry['source']: entry['target'] for entry in self.recipe['assets']})
        by_target = {asset['target']: asset for asset in report['assets']}
        self.assertEqual(by_target['game/scripts/vscripts/diagnostic_ping.lua']['source'],
                         C1 + 'diagnostic_ping.lua')
        self.assertEqual(by_target['game/scripts/vscripts/addon_game_mode.lua']['source'],
                         C1 + 'ping_game_mode.lua')
        self.assertEqual(by_target[MANIFEST]['source'], FIXTURE + 'custom_ui_manifest.xml')
        self.assertEqual((self.output / CANONICAL).read_bytes(),
                         self.before[PREFIX + 'src/panorama/layout/custom_game/coach_probe.xml'])
        self.assertEqual(json.loads((self.output / 'native-fixture-report.json').read_text(encoding='utf-8')),
                         report)
        for source, raw in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), raw)

    def test_derived_layout_excludes_auto_adapter_preserves_escaped_markup(self):
        source = self.repo / PREFIX / 'src/panorama/layout/custom_game/coach_probe.xml'
        tree = ET.parse(source)
        label = tree.getroot().find('.//Label[@class="CoachProbeTitle"]')
        self.assertIsNotNone(label)
        text = 'TEST A & B < x > "quoted"'
        label.set('text', text)
        tree.write(source, encoding='utf-8', xml_declaration=True)
        original_bytes = source.read_bytes()
        self.build()
        derived = ET.parse(self.output / DERIVED).getroot()
        scripts = [node.get('src') for node in derived.findall('./scripts/include')]
        self.assertEqual(scripts, ['file://{resources}/scripts/custom_game/coach_probe_state.js',
                                   'file://{resources}/scripts/custom_game/ping_fixture.js'])
        self.assertEqual(derived.find('.//Label[@class="CoachProbeTitle"]').get('text'), text)
        self.assertIsNotNone(derived.find('.//Label[@id="ProbeStatus"]'))
        self.assertIsNotNone(derived.find('.//Button[@id="ProbeButton"]'))
        self.assertEqual((self.output / CANONICAL).read_bytes(), original_bytes)
        native_manifest = ET.parse(self.output / MANIFEST).getroot()
        self.assertEqual(native_manifest.find('./Panel/CustomUIElement').get('layoutfile'),
                         'file://{resources}/layout/custom_game/ping_fixture.xml')

    def test_existing_output_is_preserved(self):
        self.output.mkdir(parents=True)
        sentinel = self.output / 'user-data.txt'
        sentinel.write_bytes(b'user work must survive')
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(sentinel.read_bytes(), b'user work must survive')
        self.assertEqual(sorted(path.name for path in self.output.iterdir()), ['user-data.txt'])

    def test_output_outside_build_library_and_boundary_itself_are_refused(self):
        for output in (self.repo / 'creators/replace-me', self.repo.parent / 'escaped-ping-output',
                       self.repo / 'build/dota_coach'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.builder.build_fixture(self.repo, output)
            self.assertFalse(output.exists())

    def test_tampered_recipe_or_test_manifest_refuses_before_writes(self):
        modified = copy.deepcopy(self.recipe)
        modified['kind'] = 'panorama_source_hud'
        self.recipe_path.write_text(json.dumps(modified), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse(self.output.exists())
        self.recipe_path.write_bytes((PART / 'bundle-manifest.json').read_bytes())
        path = self.repo / FIXTURE / 'custom_ui_manifest.xml'
        malformed = [
            b'<!DOCTYPE root [<!ENTITY custom "unexpected">]>' + self.before[FIXTURE + 'custom_ui_manifest.xml'],
            b'<root><Panel><CustomUIElement type="Hud" layoutfile="file://{resources}/layout/custom_game/coach_probe.xml"/></Panel></root>',
            b'<root><Panel><CustomUIElement type="Hud" layoutfile="file://{resources}/layout/custom_game/ping_fixture.xml" extra="unsafe"/></Panel></root>',
            b'<root>unexpected mixed text<Panel><CustomUIElement type="Hud" layoutfile="file://{resources}/layout/custom_game/ping_fixture.xml"/></Panel></root>',
        ]
        for payload in malformed:
            with self.subTest(payload=payload):
                path.write_bytes(payload)
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_missing_canonical_fixture_or_c1_source_refuses_before_output_creation(self):
        for source in (PREFIX + 'src/panorama/styles/custom_game/coach_probe.css',
                       FIXTURE + 'ping_fixture.js', C1 + 'diagnostic_ping.lua', C1 + 'ping_game_mode.lua'):
            path = self.repo / source
            original = path.read_bytes()
            path.unlink()
            try:
                with self.subTest(source=source), self.assertRaises((ValueError, FileNotFoundError)):
                    self.build()
                self.assertFalse(self.output.exists())
            finally:
                path.write_bytes(original)

    def test_reparse_source_ancestors_and_output_ancestor_are_refused(self):
        # Existing path-policy metadata semantics, no symlink privilege needed.
        (self.repo / 'build/dota_coach').mkdir(parents=True)
        blocked_paths = [(self.repo / C1).parent, self.repo / FIXTURE, self.repo / 'build/dota_coach']
        original = Path.lstat
        for blocked in blocked_paths:
            def reparse(path, *args, **kwargs):
                if path == blocked:
                    return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                return original(path, *args, **kwargs)
            with self.subTest(blocked=blocked), mock.patch.object(Path, 'lstat', reparse):
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())


    def test_adapter_variant_retains_original_auto_adapter_and_exact_outputs(self):
        source = self.repo / FIXTURE / 'ping_adapter_fixture.js'
        source.write_text('/* TEST observer */', encoding='utf-8')
        report = self.builder.build_fixture(self.repo, self.output, variant='adapter')
        self.assertEqual(report['diagnostic_variant'], 'adapter')
        self.assertEqual(len(report['assets']), 9)
        tree = ET.fromstring((self.output / DERIVED).read_bytes())
        self.assertEqual([node.attrib['src'] for node in tree.findall('./scripts/include')], [
            'file://{resources}/scripts/custom_game/coach_probe_state.js',
            'file://{resources}/scripts/custom_game/coach_probe.js',
            'file://{resources}/scripts/custom_game/ping_fixture.js'])
        driver = next(item for item in report['assets'] if item['target'] == DRIVER)
        self.assertEqual(driver['source'], FIXTURE + 'ping_adapter_fixture.js')

    def test_unknown_variant_refuses_before_outputs(self):
        for variant in ('unknown', None, False):
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                self.builder.build_fixture(self.repo, self.output, variant=variant)
            self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
