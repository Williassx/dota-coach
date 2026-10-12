"""Acceptance fixture isolation and refusal semantics for native observation."""
import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACK = Path(__file__).resolve().parents[1]
FIXTURE = 'creators/creator-2/11-integration/01-ui-binding/tests/native-observation/'
BUILDER = PACK / 'tools/build_native_observation_fixture.py'


class NativeObservationFixtureTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Native observation fixture builder missing')
        spec = importlib.util.spec_from_file_location('native_observation_fixture_test_builder', BUILDER)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.manifest = json.loads((PACK / 'match-observation-manifest.json').read_text(encoding='utf-8'))
        sources = [a['source'] for a in self.manifest['assets']] + [a['source'] for a in self.manifest['layout_inputs']] + [FIXTURE + name for name in
            ['custom_ui_manifest.xml', 'observation_fixture.js']]
        self.before = {}
        for source in sources:
            raw = (ROOT / source).read_bytes()
            self.before[source] = raw
            dest = self.repo / source
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        manifest = self.repo / PACK.relative_to(ROOT) / 'match-observation-manifest.json'
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes((PACK / 'match-observation-manifest.json').read_bytes())
        self.output = self.repo / 'build/dota_coach/native-observation-fixture'

    def test_preserves_canonical_bytes_and_exact_derived_graph(self):
        report = self.builder.build_fixture(self.repo, self.output)
        self.assertEqual(report['fixture_type'], 'native_observation_test_only')
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        self.assertEqual(len(report['assets']), 12)
        self.assertEqual(report['canonical_outputs'], 10)
        self.assertEqual(sum(a['derived'] for a in report['assets']), 2)
        for source, raw in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), raw)
        canonical = self.builder.policy.prepare_assets(self.repo, self.manifest)
        original = ET.fromstring(next(raw for _, target, raw in canonical if target.endswith('/coach_match_observation.xml')))
        derived = ET.parse(self.output / 'content/panorama/layout/custom_game/observation_fixture.xml').getroot()
        self.assertNotIn('id', derived.find('./Panel').attrib)
        self.assertEqual([n.get('src') for n in original.findall('./scripts/include')],
                         [n.get('src') for n in derived.findall('./scripts/include')][:-1])
        self.assertTrue(derived.findall('./scripts/include')[-1].get('src').endswith('/observation_fixture.js'))
        left, right = original.find('./Panel/Panel'), derived.find('./Panel/Panel')
        left.tail = right.tail = None
        self.assertEqual(ET.tostring(left), ET.tostring(right))
        self.assertEqual(derived.find('./Panel/Label').get('html'), 'false')
        self.assertEqual(len(report['source_input_hashes']), 12)
        self.assertEqual(len(report['layout_input_hashes']), 2)
        import hashlib
        for row in report['source_input_hashes']:
            self.assertEqual(row['sha256'], hashlib.sha256(self.before[row['source']]).hexdigest())
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
        (self.repo / FIXTURE / 'observation_fixture.js').unlink()
        with self.assertRaises((ValueError, FileNotFoundError)): self.builder.build_fixture(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_fixed_mapping_refuses_before_writes(self):
        self.manifest['assets'][0]['target'] = 'content/panorama/layout/custom_game/other.xml'
        (self.repo / PACK.relative_to(ROOT) / 'match-observation-manifest.json').write_text(json.dumps(self.manifest))
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
        second = self.builder.build_fixture(self.repo, self.repo / 'build/dota_coach/another-observation-fixture')
        self.assertEqual(first['assets'], second['assets'])


if __name__ == '__main__':
    unittest.main()
