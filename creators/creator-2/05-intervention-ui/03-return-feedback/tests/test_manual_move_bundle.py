"""Source-only checks for the exact manual-move bundle; no engine execution."""

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

PART = Path(__file__).resolve().parents[1]
BUILDER = PART / 'tools/build_manual_move_bundle.py'
C1 = 'creators/creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/'
C2 = 'creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'
INPUTS = {
    C1 + 'manual_move_controller.lua': 'game/scripts/vscripts/manual_move_controller.lua',
    C1 + 'manual_move_game_mode.lua': 'game/scripts/vscripts/addon_game_mode.lua',
    C2 + 'scripts/custom_game/manual_move_state.js': 'content/panorama/scripts/custom_game/manual_move_state.js',
    C2 + 'scripts/custom_game/manual_move_panel.js': 'content/panorama/scripts/custom_game/manual_move_panel.js',
    C2 + 'layout/custom_game/manual_move.xml': 'content/panorama/layout/custom_game/manual_move.xml',
    C2 + 'styles/custom_game/manual_move.css': 'content/panorama/styles/custom_game/manual_move.css',
}
LAYOUT = b'''<root><styles><include src="file://{resources}/styles/custom_game/manual_move.css"/></styles>
<scripts><include src="file://{resources}/scripts/custom_game/manual_move_state.js"/>
<include src="file://{resources}/scripts/custom_game/manual_move_panel.js"/></scripts>
<Panel id="ManualMoveRoot"><Label text="TEST A &amp; B"/></Panel></root>'''


class ManualMoveBundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Missing build_manual_move_bundle.py implementation (expected RED)')
        spec = importlib.util.spec_from_file_location('manual_move_bundle_tests', BUILDER)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.output = self.repo / 'build/dota_coach/manual-move-test'
        self.before = {}
        for source in INPUTS:
            raw = LAYOUT if source.endswith('.xml') else ('// source ' + source).encode('utf-8')
            if source.endswith('.lua'):
                raw = b'-- TEST source, not executed\nreturn {}\n'
            if source.endswith('.css'):
                raw = b'.ManualMoveRoot { width:100%; height:100%; }\n'
            target = self.repo / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            self.before[source] = raw

    def build(self):
        return self.builder.build_bundle(self.repo, self.output)

    def verify(self):
        return self.builder.verify_bundle(self.output, repository=self.repo)

    def test_exact_seven_outputs_hashes_sources_and_source_only_receipt(self):
        report = self.build()
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['stage'], 'manual_move_source_bundle')
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        assets = report['assets']
        self.assertEqual(len(assets), 7)
        self.assertEqual({asset['target'] for asset in assets}, set(INPUTS.values()) | {MANIFEST})
        self.assertEqual(len({asset['target'].casefold() for asset in assets}), 7)
        self.assertEqual(sum(asset['derived'] for asset in assets), 1)
        for asset in assets:
            raw = (self.output / asset['target']).read_bytes()
            self.assertEqual(asset['bytes'], len(raw))
            self.assertEqual(asset['sha256'], hashlib.sha256(raw).hexdigest())
            if not asset['derived']:
                self.assertEqual(INPUTS[asset['source']], asset['target'])
                self.assertEqual(raw, self.before[asset['source']])
        self.assertEqual(len(report['source_inputs']), 6)
        self.assertEqual({entry['source']: entry['sha256'] for entry in report['source_inputs']},
                         {source: hashlib.sha256(raw).hexdigest() for source, raw in self.before.items()})
        self.assertEqual(self.verify(), report)
        self.assertEqual(json.loads((self.output / 'bundle-report.json').read_text(encoding='utf-8')), report)
        for source, raw in self.before.items():
            self.assertEqual((self.repo / source).read_bytes(), raw)

    def test_generated_manifest_targets_only_manual_move_and_preserves_layout_bytes(self):
        self.build()
        root = ET.parse(self.output / MANIFEST).getroot()
        self.assertEqual([node.tag for node in root.iter()], ['root', 'Panel', 'CustomUIElement'])
        self.assertEqual(root.find('./Panel/CustomUIElement').attrib,
                         {'type': 'Hud', 'layoutfile': 'file://{resources}/layout/custom_game/manual_move.xml'})
        self.assertEqual((self.output / INPUTS[C2 + 'layout/custom_game/manual_move.xml']).read_bytes(), LAYOUT)
        self.assertEqual(ET.parse(self.output / INPUTS[C2 + 'layout/custom_game/manual_move.xml'])
                         .find('.//Label').get('text'), 'TEST A & B')

    def test_boolean_schema_version_is_not_an_integer_version(self):
        report = self.build()
        report['schema_version'] = True
        (self.output / 'bundle-report.json').write_text(json.dumps(report), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()

    def test_existing_output_is_preserved(self):
        self.output.mkdir(parents=True)
        sentinel = self.output / 'user.txt'
        sentinel.write_bytes(b'preserve user work')
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(sentinel.read_bytes(), b'preserve user work')
        self.assertEqual([path.name for path in self.output.iterdir()], ['user.txt'])

    def test_build_and_verify_reject_output_escape(self):
        for output in (self.repo / 'creators/overwrite', self.repo / 'build/dota_coach',
                       self.repo.parent / 'move-bundle-outside'):
            with self.subTest(output=output):
                with self.assertRaises(ValueError):
                    self.builder.build_bundle(self.repo, output)
                with self.assertRaises(ValueError):
                    self.builder.verify_bundle(output, repository=self.repo)
                self.assertFalse(output.exists())

    def test_missing_or_oversized_input_refuses_before_output_creation(self):
        for source in INPUTS:
            path = self.repo / source
            raw = path.read_bytes()
            path.unlink()
            try:
                with self.subTest(source=source), self.assertRaises((ValueError, FileNotFoundError)):
                    self.build()
                self.assertFalse(self.output.exists())
            finally:
                path.write_bytes(raw)
        last = self.repo / list(INPUTS)[-1]
        last.write_bytes(b'x' * (1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_verifier_rejects_receipt_and_generated_manifest_tampering(self):
        report = self.build()
        receipt = self.output / 'bundle-report.json'
        for field, value in (('stage', 'other'), ('source2_compiled', True), ('runtime_verified', True)):
            changed = copy.deepcopy(report)
            changed[field] = value
            receipt.write_text(json.dumps(changed), encoding='utf-8')
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify()
        changed = copy.deepcopy(report)
        changed['assets'][0]['target'] = 'game/scripts/vscripts/unexpected.lua'
        receipt.write_text(json.dumps(changed), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()
        receipt.write_text(json.dumps(report), encoding='utf-8')
        target = self.output / MANIFEST
        payload = b'<root><Panel><CustomUIElement type="Hud" layoutfile="file://{resources}/layout/custom_game/other.xml"/></Panel></root>'
        target.write_bytes(payload)
        changed = copy.deepcopy(report)
        asset = next(entry for entry in changed['assets'] if entry['target'] == MANIFEST)
        asset.update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        receipt.write_text(json.dumps(changed), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()

    def test_verifier_rejects_changed_input_copied_bytes_and_unexpected_files(self):
        self.build()
        extra = self.output / 'unexpected.txt'
        extra.write_bytes(b'not in the exact recipe')
        with self.assertRaises(ValueError):
            self.verify()
        extra.unlink()
        copied = self.output / INPUTS[C2 + 'scripts/custom_game/manual_move_state.js']
        original = copied.read_bytes()
        copied.write_bytes(original + b'\n// modified')
        with self.assertRaises(ValueError):
            self.verify()
        copied.write_bytes(original)
        source = self.repo / C1 / 'manual_move_controller.lua'
        source.write_bytes(source.read_bytes() + b'\n-- source changed')
        with self.assertRaises(ValueError):
            self.verify()

    def test_reparse_input_and_output_ancestors_are_refused(self):
        (self.repo / 'build/dota_coach').mkdir(parents=True)
        original = Path.lstat
        for blocked in (self.repo / C1, self.repo / C2 / 'scripts/custom_game', self.repo / 'build/dota_coach'):
            def reparse(path, *args, **kwargs):
                if path == blocked:
                    return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                return original(path, *args, **kwargs)
            with self.subTest(blocked=blocked), mock.patch.object(Path, 'lstat', reparse):
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())
        self.build()
        blocked = self.output / 'content/panorama/scripts'
        def output_reparse(path, *args, **kwargs):
            if path == blocked:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'lstat', output_reparse), self.assertRaises(ValueError):
            self.verify()


if __name__ == '__main__':
    unittest.main()
