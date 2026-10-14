"""Exact scene packaging checks; synthetic files do not claim native acceptance."""
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
BUILDER = PART / 'tools/build_coach_scene.py'
REPO = PART.parents[3]
MANUAL = REPO / 'creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/layout/custom_game/manual_move.xml'

class CoachSceneBundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BUILDER.is_file(), 'Missing coach scene builder (expected RED)')
        spec = importlib.util.spec_from_file_location('coach_scene_tests', BUILDER)
        self.b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.b)
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name); self.out = self.repo / 'build/dota_coach/scene'
        self.original = {}
        for source in set(self.b.INPUTS) | {self.b.FIXTURE_LUA, self.b.FIXTURE_JS}:
            raw = MANUAL.read_bytes() if source.endswith('.xml') else ('-- TEST ' + source).encode()
            path = self.repo / source; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            self.original[source] = raw

    def test_exact_normal_and_fixture_hashes_and_graph(self):
        for fixture, count, stage, active, retained in ((False,15,'coach_scene_source_bundle',6,1),(True,18,'coach_scene_native_test_fixture',7,2)):
            out = self.out.with_name('fixture' if fixture else 'normal')
            report = self.b.build_bundle(self.repo, out, test_fixture=fixture)
            self.assertEqual(len(report['assets']), count)
            self.assertEqual(report['stage'],stage)
            self.assertIs(report['source2_compiled'],False); self.assertIs(report['runtime_verified'],False)
            self.assertEqual(len({a['target'].casefold() for a in report['assets']}),count)
            for asset in report['assets']:
                raw=(out/asset['target']).read_bytes()
                self.assertEqual(asset['sha256'],hashlib.sha256(raw).hexdigest()); self.assertEqual(asset['bytes'],len(raw))
                if not asset['derived']: self.assertEqual(raw,self.original[asset['source']])
            self.assertEqual(self.b.verify_bundle(self.repo,out),report)
            canonical=(out/self.b.MANUAL_LAYOUT).read_bytes(); self.assertEqual(canonical,MANUAL.read_bytes())
            scene=ET.parse(out/self.b.SCENE_LAYOUT)
            self.assertEqual([n.get('src') for n in scene.findall('./scripts/include')],self.b.SCRIPT_LINKS)
            self.assertEqual(len(scene.findall('.//*[@id]')),18)
            self.assertEqual(len(scene.findall('.//*[@id="RosterServerRoot"]')),1)
            for i in range(1,6):
                self.assertEqual(len(scene.findall('.//*[@id="RosterServer'+str(i)+'"]')),1)
            self.assertEqual(scene.find('./Panel').get('id'),None)
            manifest=ET.parse(out/self.b.MANIFEST)
            expected=self.b.FIXTURE_LAYOUT if fixture else self.b.SCENE_LAYOUT
            self.assertEqual(manifest.find('./Panel/CustomUIElement').get('layoutfile'),'file://{resources}/'+expected.removeprefix('content/panorama/'))
            ui=[a for a in report['assets'] if a['target'].startswith('content/')]
            self.assertEqual(len(ui),active+retained)
            mapping={a['source']:a['target'] for a in report['assets'] if not a['derived']}
            self.assertEqual(mapping[self.b.WRAPPER_SOURCE],'game/scripts/vscripts/coach_scene_game_mode.lua' if fixture else 'game/scripts/vscripts/addon_game_mode.lua')
            if fixture:self.assertEqual(mapping[self.b.FIXTURE_LUA],'game/scripts/vscripts/addon_game_mode.lua')
        for source,raw in self.original.items(): self.assertEqual((self.repo/source).read_bytes(),raw)

    def test_missing_each_input_preserves_fresh_output(self):
        for source in self.original:
            path=self.repo/source; raw=path.read_bytes(); path.unlink()
            try:
                fixture=source in (self.b.FIXTURE_LUA,self.b.FIXTURE_JS)
                with self.subTest(source=source),self.assertRaises((ValueError,OSError)): self.b.build_bundle(self.repo,self.out,test_fixture=fixture)
                self.assertFalse(self.out.exists())
            finally: path.write_bytes(raw)

    def test_existing_and_escape_preserved(self):
        self.out.mkdir(parents=True); (self.out/'user').write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):self.b.build_bundle(self.repo,self.out)
        self.assertEqual((self.out/'user').read_bytes(),b'preserve')
        for path in (self.repo/'build/dota_coach',self.repo/'creators/output',self.repo.parent/'outside'):
            with self.assertRaises(ValueError):self.b.build_bundle(self.repo,path)
            with self.assertRaises(ValueError):self.b.verify_bundle(self.repo,path)

    def test_tamper_missing_extra_sources_and_receipt(self):
        report=self.b.build_bundle(self.repo,self.out)
        receipt=self.out/'bundle-report.json'
        for key,value in (('schema_version',True),('stage','wrong'),('runtime_verified',True),('source2_compiled',True)):
            changed=copy.deepcopy(report); changed[key]=value; receipt.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)
        receipt.write_text(json.dumps(report))
        for asset in report['assets']:
            path=self.out/asset['target']; raw=path.read_bytes(); path.write_bytes(raw+b'changed')
            with self.subTest(target=asset['target']),self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)
            path.unlink()
            with self.assertRaises((ValueError,OSError)):self.b.verify_bundle(self.repo,self.out)
            path.write_bytes(raw)
        extra=self.out/'extra'; extra.write_bytes(b'x')
        with self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)
        extra.unlink()
        source=self.repo/next(iter(self.b.INPUTS)); source.write_bytes(b'changed')
        with self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)

    def test_xml_graph_rejects_handlers_dependencies_ids_and_dtd(self):
        source=self.repo/self.b.MANUAL_SOURCE; raw=source.read_bytes()
        for changed in (raw.replace(b'<root>',b'<!DOCTYPE root><root>'),raw.replace(b'id="MoveRoot"',b'id="MoveRoot" onactivate="bad()"'),raw.replace(b'manual_move_state.js',b'other.js'),raw.replace(b'id="MoveMode"',b'id="MoveRoot"'),raw.replace(b'class="MoveCanvas"',b'class="Other"')):
            source.write_bytes(changed)
            with self.assertRaises(ValueError):self.b.build_bundle(self.repo,self.out)
            self.assertFalse(self.out.exists())
        source.write_bytes(raw)

    def test_rehashed_derived_layout_is_not_trusted(self):
        report=self.b.build_bundle(self.repo,self.out)
        path=self.out/self.b.SCENE_LAYOUT
        changed=path.read_bytes().replace(b'RosterServer1',b'OtherServer1')
        path.write_bytes(changed)
        asset=next(a for a in report['assets'] if a['target']==self.b.SCENE_LAYOUT)
        asset.update(bytes=len(changed),sha256=hashlib.sha256(changed).hexdigest())
        (self.out/'bundle-report.json').write_text(json.dumps(report))
        with self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)

    def test_oversized_source_and_selector_refused_before_output(self):
        path=self.repo/self.b.ROSTER_SOURCE;path.write_bytes(b'x'*(1024*1024+1))
        with self.assertRaises(ValueError):self.b.build_bundle(self.repo,self.out)
        self.assertFalse(self.out.exists())
        with self.assertRaises(ValueError):self.b.prepare(self.repo,'true')

    def test_reparse_input_output_and_verification(self):
        (self.repo/'build/dota_coach').mkdir(parents=True)
        original=Path.lstat
        for blocked in (self.repo/self.b.MANUAL_SOURCE,self.repo/'build/dota_coach'):
            def fake(path,*args,**kwargs):
                return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400) if path==blocked else original(path,*args,**kwargs)
            with mock.patch.object(Path,'lstat',fake),self.assertRaises(ValueError):self.b.build_bundle(self.repo,self.out)
        self.b.build_bundle(self.repo,self.out)
        blocked=self.out/'content/panorama'
        def fake(path,*args,**kwargs):
            return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400) if path==blocked else original(path,*args,**kwargs)
        with mock.patch.object(Path,'lstat',fake),self.assertRaises(ValueError):self.b.verify_bundle(self.repo,self.out)

if __name__=='__main__':unittest.main()
