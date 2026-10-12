"""Acceptance fixture isolation and refusal semantics for native text preview."""
import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACK = Path(__file__).resolve().parents[1]
FIXTURE = 'creators/creator-2/06-voice/03-voice-feedback/tests/native-text-preview/'
BUILDER = PACK / 'tools/build_native_voice_fixture.py'


class NativeVoiceFixtureTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Native voice fixture builder missing')
        spec = importlib.util.spec_from_file_location('native_voice_fixture_test_builder', BUILDER)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.manifest = json.loads((PACK / 'voice-text-manifest.json').read_text(encoding='utf-8'))
        sources = [a['source'] for a in self.manifest['assets']] + [FIXTURE + name for name in
            ['custom_ui_manifest.xml', 'voice_fixture.js']]
        self.before = {}
        for source in sources:
            raw = (ROOT / source).read_bytes()
            self.before[source] = raw
            dest = self.repo / source
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        manifest = self.repo / PACK.relative_to(ROOT) / 'voice-text-manifest.json'
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes((PACK / 'voice-text-manifest.json').read_bytes())
        self.output = self.repo / 'build/dota_coach/native-voice-fixture'

    def test_preserves_canonical_bytes_and_exact_derived_graph(self):
        report = self.builder.build_fixture(self.repo, self.output)
        self.assertEqual(report['fixture_type'], 'native_voice_text_test_only')
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        self.assertEqual(len(report['assets']), 8)
        self.assertEqual(report['canonical_inputs'], 6)
        self.assertEqual(sum(a['derived'] for a in report['assets']), 1)
        for source, raw in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), raw)
        original = ET.fromstring(self.before[next(s for s in self.before if s.endswith('/voice_text.xml'))])
        derived = ET.parse(self.output / 'content/panorama/layout/custom_game/voice_fixture.xml').getroot()
        self.assertNotIn('id', derived.find('./Panel').attrib)
        self.assertEqual([n.get('src') for n in original.findall('./scripts/include')],
                         [n.get('src') for n in derived.findall('./scripts/include')][:-1])
        self.assertTrue(derived.findall('./scripts/include')[-1].get('src').endswith('/voice_fixture.js'))
        self.assertEqual(ET.tostring(original.find('./Panel')), ET.tostring(derived.find('./Panel/Panel')))
        self.assertEqual(derived.find('./Panel/Label').get('html'), 'false')
        for asset in report['assets']:
            if not asset['derived']:
                self.assertEqual((self.output / asset['target']).read_bytes(), self.before[asset['source']])

    def test_existing_output_is_preserved(self):
        self.output.mkdir(parents=True)
        sentinel = self.output / 'keep.txt'
        sentinel.write_text('keep', encoding='utf-8')
        with self.assertRaises(FileExistsError): self.builder.build_fixture(self.repo, self.output)
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_output_escape_refuses_before_writes(self):
        target = self.repo / 'outside'
        with self.assertRaises(ValueError): self.builder.build_fixture(self.repo, target)
        self.assertFalse(target.exists())

    def test_missing_driver_refuses_before_writes(self):
        (self.repo / FIXTURE / 'voice_fixture.js').unlink()
        with self.assertRaises((ValueError, FileNotFoundError)): self.builder.build_fixture(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_fixed_mapping_refuses_before_writes(self):
        self.manifest['assets'][0]['target'] = 'content/panorama/layout/custom_game/other.xml'
        (self.repo / PACK.relative_to(ROOT) / 'voice-text-manifest.json').write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError): self.builder.build_fixture(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_executable_manifest_attribute_refuses_before_writes(self):
        manifest = self.repo / FIXTURE / 'custom_ui_manifest.xml'
        tree = ET.fromstring(manifest.read_bytes())
        tree.find('./Panel').set('onload', 'unexpected()')
        manifest.write_bytes(ET.tostring(tree))
        with self.assertRaises(ValueError): self.builder.build_fixture(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_two_fresh_builds_have_identical_assets(self):
        first = self.builder.build_fixture(self.repo, self.output)
        second = self.builder.build_fixture(self.repo, self.repo / 'build/dota_coach/another-voice-fixture')
        self.assertEqual(first['assets'], second['assets'])


if __name__ == '__main__':
    unittest.main()
