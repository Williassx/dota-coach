"""Generated single-context preparation layout: source integrity, never native proof."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / 'creators/creator-2/01-foundation/02-panorama-capability/tools'
LAYOUT = 'content/panorama/layout/custom_game/coach_preparation.xml'
MANIFEST_TARGET = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'
SCRIPTS = ['preparation_panel_port.js', 'team_picker_state.js', 'team_picker_panel.js',
           'hero_role_state.js', 'hero_role_panel.js', 'preparation_state.js',
           'preparation_panel.js', 'preparation_flow_state.js', 'preparation_binding.js']
STYLES = ['team_picker.css', 'hero_role_picker.css', 'preparation_picker.css', 'coach_preparation.css']

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module

require_symlink = load('preparation_symlink_capability', REPOSITORY /
    'creators/creator-2/11-integration/03-end-to-end/tests/symlink_capability.py').require_symlink

builder = load('prep_builder', TOOLS / 'build_probe_bundle.py')
sys.path.insert(0, str(TOOLS))
try:
    verifier = load('prep_verifier', TOOLS / 'verify_probe_bundle.py')
finally:
    sys.path.pop(0)

class PreparationBundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((TASK / 'preparation-manifest.json').is_file(), 'preparation recipe missing')
        self.manifest = json.loads((TASK / 'preparation-manifest.json').read_text())
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.output = self.repo / 'build/dota_coach/preparation'
        for entry in self.manifest['assets'] + self.manifest['layout_inputs']:
            source = self.repo / entry['source']
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes((REPOSITORY / entry['source']).read_bytes())

    def source(self, target):
        return self.repo / next(e['source'] for e in self.manifest['assets'] if e['target'] == target)

    def build(self):
        return builder.build_bundle(self.repo, self.manifest, self.output)

    def reject(self, manifest=None):
        with self.assertRaises((ValueError, OSError)):
            builder.build_bundle(self.repo, manifest or self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_roundtrip15resources_false_runtime_and_original_copy_bytes(self):
        report = self.build()
        self.assertEqual(len(report['assets']), 15)
        self.assertFalse(report['runtime_verified']); self.assertFalse(report['source2_compiled'])
        for row in report['assets']:
            data = (self.output / row['target']).read_bytes()
            self.assertEqual(row['sha256'], hashlib.sha256(data).hexdigest())
            if row['target'] != LAYOUT:
                self.assertEqual(data, (self.repo / row['source']).read_bytes())
        self.assertNotEqual((self.output / LAYOUT).read_bytes(), self.source(LAYOUT).read_bytes())
        result = verifier.verify_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(result['assets'], 15); self.assertEqual(result['xml_resource_links'], 14)

    def test_generated_roots_match_canonical_panels_and_preserve_unique_ids(self):
        self.build(); root = ET.parse(self.output / LAYOUT).getroot()
        self.assertNotIn('id', root.find('./Panel').attrib)
        self.assertEqual(root.find('./Panel/Panel').get('id'), 'CoachPreparationRoot')
        ids = [n.get('id') for n in root.iter() if n.get('id')]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in self.manifest['layout_inputs']:
            host = next(n for n in root.iter() if n.get('id') == entry['host_id'])
            canonical = ET.parse(self.repo / entry['source']).getroot().find('Panel')
            self.assertEqual(len(host), 1)
            # ElementTree serialization ignores only tail whitespace at attachment.
            left = copy.deepcopy(host[0]); right = copy.deepcopy(canonical)
            left.tail = right.tail = None
            self.assertEqual(ET.tostring(left), ET.tostring(right))
        self.assertTrue(all(n.get('html') == 'false' for n in root.iter('Label')))
        self.assertTrue(all(n.get('enabled') == 'false' for n in root.iter('Button')))

    def test_anonymous_outer_shape_and_binding_root_guards(self):
        source = self.source(LAYOUT)
        original = source.read_bytes()
        mutations = [
            lambda r: r.find('./Panel').set('id', 'UnexpectedRoot'),
            lambda r: r.find('./Panel').set('class', 'UnexpectedCanvas'),
            lambda r: r.find('./Panel').append(ET.Element('Panel')),
            lambda r: r.find('./Panel/Panel').set('id', 'UnexpectedBindingScope'),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                root = ET.fromstring(original)
                mutation(root)
                source.write_bytes(ET.tostring(root))
                self.reject()
        source.write_bytes(original)

    def test_dependencies_exact_order_and_plain_unconfirmed_status(self):
        self.build(); root = ET.parse(self.output / LAYOUT).getroot()
        self.assertEqual([Path(n.get('src')).name for n in root.findall('./scripts/include')], SCRIPTS)
        self.assertEqual([Path(n.get('src')).name for n in root.findall('./styles/include')], STYLES)
        status = next(n for n in root.iter() if n.get('id') == 'CoachPreparationStatus')
        self.assertIn('не подключены', status.get('text')); self.assertEqual(status.get('html'), 'false')

    def test_fingerprints_include_all_raw_input_sources(self):
        self.build(); text = (self.output / LAYOUT).read_text()
        for entry in self.manifest['layout_inputs']:
            self.assertIn(entry['source'], text)
            self.assertIn(hashlib.sha256((self.repo / entry['source']).read_bytes()).hexdigest(), text)

    def test_exact_mapping_missing_extra_remap_duplicate_and_unknown_fields(self):
        for mode in ['missing', 'extra', 'remap', 'duplicate', 'field', 'kind', 'schema']:
            with self.subTest(mode=mode):
                manifest = copy.deepcopy(self.manifest)
                if mode == 'missing': manifest['assets'].pop()
                elif mode == 'extra': manifest['assets'].append({'source':'creators/creator-1/x.js','target':'content/panorama/x.js'})
                elif mode == 'remap': manifest['assets'][0]['target'] = 'content/panorama/layout/custom_game/other.xml'
                elif mode == 'duplicate': manifest['assets'][-1] = manifest['assets'][0]
                elif mode == 'field': manifest['extra'] = True
                elif mode == 'schema': manifest['schema_version'] = True
                else: manifest['kind'] = 'compiled'
                self.reject(manifest)

    def test_inputs_fixed_sources_roots_hosts_order_and_exact_fields(self):
        for mode in ['source','root_id','host_id','extra','missing','order','field']:
            with self.subTest(mode=mode):
                manifest = copy.deepcopy(self.manifest)
                if mode in ['source','root_id','host_id']: manifest['layout_inputs'][0][mode] = 'other'
                elif mode == 'extra': manifest['layout_inputs'].append(manifest['layout_inputs'][0])
                elif mode == 'missing': manifest['layout_inputs'].pop()
                elif mode == 'order': manifest['layout_inputs'].reverse()
                else: manifest['layout_inputs'][0]['extra'] = True
                self.reject(manifest)

    def test_old_kinds_reject_layout_inputs(self):
        for path in [builder.MANIFEST, TASK / 'bundle-manifest.json']:
            manifest = json.loads(path.read_text()); manifest['layout_inputs'] = []
            with self.assertRaises(ValueError): builder.prepare_assets(self.repo, manifest)

    def test_input_missing_symlink_or_oversized_rejected_before_output(self):
        source = self.repo / self.manifest['layout_inputs'][0]['source']
        original = source.read_bytes()
        for mode in ['missing','symlink','size']:
            with self.subTest(mode=mode):
                if mode == 'symlink': require_symlink(self, self.repo)
                if source.exists() or source.is_symlink(): source.unlink()
                if mode == 'symlink':
                    other = self.repo / 'foreign.xml'; other.write_bytes(original); source.symlink_to(other)
                elif mode == 'size': source.write_bytes(b'x' * (builder.MAX_BYTES + 1))
                self.reject()
        source.write_bytes(original)

    def test_module_root_id_extra_sections_and_nested_layout_rejected(self):
        source = self.repo / self.manifest['layout_inputs'][0]['source']; original = source.read_text()
        for text in [original.replace('id="TeamPickerRoot"','id="OtherRoot"'),
                     original.replace('</root>','<Panel id="Extra" /></root>'),
                     original.replace('</root>','<snippets /></root>'),
                     original.replace('<Panel class="TeamPickerWindow"','<Panel layoutfile="file://{resources}/layout/custom_game/x.xml" class="TeamPickerWindow"')]:
            source.write_text(text); self.reject()
        source.write_text(original)

    def test_module_dependencies_or_event_attrs_dtd_and_duplicate_ids_rejected(self):
        source = self.repo / self.manifest['layout_inputs'][0]['source']; original = source.read_text()
        for text in [original.replace('team_picker_state.js','unknown.js'),
                     original.replace('team_picker.css','unknown.css'),
                     original.replace('<root>','<!DOCTYPE root><root>'),
                     original.replace('id="TeamCandidate0"','id="HeroRoleRoot"'),
                     original.replace('id="TeamCandidate0"','id="TeamCandidate0" onactivate="Bad()"')]:
            source.write_text(text); self.reject()
        source.write_text(original)

    def test_shell_missing_host_nonempty_host_and_wrong_dependency_rejected(self):
        source = self.source(LAYOUT); original = source.read_text()
        for text in [original.replace('CoachPreparationTeamHost','OtherHost'),
                     original.replace('class="CoachPreparationHost" hittest="false" hittestchildren="true" />','class="CoachPreparationHost" hittest="false" hittestchildren="true"><Label html="false" /></Panel>',1),
                     original.replace('preparation_binding.js','unknown.js')]:
            source.write_text(text); self.reject()
        source.write_text(original)

    def test_manifest_must_load_only_preparation_hud(self):
        source = self.source(MANIFEST_TARGET); original = source.read_text()
        for text in [original.replace('type="Hud"','type="Other"'),
                     original.replace('coach_preparation.xml','other.xml'),
                     original.replace('<root>','<root><scripts><run>Bad()</run></scripts>')]:
            source.write_text(text); self.reject()
        source.write_text(original)

    def test_nested_dependency_sections_or_manifest_extra_children_rejected(self):
        source = self.repo / self.manifest['layout_inputs'][0]['source']; original = source.read_text()
        source.write_text(original.replace('<Panel class="TeamPickerWindow"', '<Panel><scripts><include src="file://{resources}/scripts/custom_game/team_picker_state.js" /></scripts></Panel><Panel class="TeamPickerWindow"'))
        self.reject(); source.write_text(original)
        source = self.source(MANIFEST_TARGET); original = source.read_text()
        variants = [original.replace(' />', '><styles><include src="file://{resources}/styles/custom_game/coach_preparation.css" /></styles></CustomUIElement>'),
                    original.replace('<Panel>', '<Panel layoutfile="file://{resources}/layout/custom_game/coach_preparation.xml">'),
                    original.replace(' />', '><Panel id="Unexpected" /></CustomUIElement>'),
                    original.replace(' />', '><include src="file://{resources}/scripts/custom_game/preparation_binding.js" /></CustomUIElement>')]
        for text in variants:
            self.assertNotEqual(text, original); source.write_text(text); self.reject()
        source.write_text(original)

    def test_resource_src_is_rejected_on_panels_and_buttons(self):
        for source, token in [(self.source(LAYOUT), 'id="CoachPreparationRoot"'),
                              (self.repo / self.manifest['layout_inputs'][0]['source'], 'id="TeamCandidate0"')]:
            original = source.read_text()
            source.write_text(original.replace(token, token + ' src="file://{resources}/scripts/custom_game/preparation_binding.js"'))
            self.reject(); source.write_text(original)

    def test_current_input_even_comment_change_invalidates_output(self):
        self.build(); source = self.repo / self.manifest['layout_inputs'][1]['source']
        source.write_bytes(source.read_bytes() + b'\n<!-- changed only comment -->\n')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.manifest, self.output)

    def test_generated_layout_or_report_tamper_is_rejected(self):
        self.build(); path = self.output / LAYOUT; original = path.read_bytes(); path.write_bytes(original+b' ')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo,self.manifest,self.output)
        path.write_bytes(original); path = self.output / 'bundle-report.json'; report=json.loads(path.read_text())
        report['runtime_verified']=True; path.write_text(json.dumps(report))
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo,self.manifest,self.output)

    def test_output_preservation_boundary_and_unexpected_file(self):
        self.build(); before=(self.output/LAYOUT).read_bytes()
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(before,(self.output/LAYOUT).read_bytes())
        with self.assertRaises(ValueError): builder.build_bundle(self.repo,self.manifest,self.repo/'content/user')
        (self.output/'unexpected.txt').write_text('foreign')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo,self.manifest,self.output)

    def test_scoped_style_removes_inner_scroll_for_stack(self):
        style=self.source('content/panorama/styles/custom_game/coach_preparation.css').read_text()
        for name in ['TeamPickerList','HeroRoleList','PreparationList']:
            self.assertIn('#CoachPreparationRoot .'+name,style)
        self.assertIn('overflow: squish squish',style); self.assertIn('height: fit-children',style)

    def test_cli_build_and_verify_repeat_existing_output_is_preserved(self):
        path=self.repo/'recipe.json';path.write_text(json.dumps(self.manifest))
        build=[sys.executable,str(TOOLS/'build_probe_bundle.py'),'--repository',str(self.repo),'--manifest',str(path),'--output',str(self.output)]
        first=subprocess.run(build,capture_output=True,text=True);self.assertEqual(first.returncode,0,first.stderr)
        check=subprocess.run([sys.executable,str(TOOLS/'verify_probe_bundle.py'),'--repository',str(self.repo),'--manifest',str(path),'--bundle',str(self.output)],capture_output=True,text=True)
        self.assertEqual(check.returncode,0,check.stderr);self.assertEqual(json.loads(check.stdout)['assets'],15)
        again=subprocess.run(build,capture_output=True,text=True);self.assertEqual(again.returncode,2)

    def test_generated_tree_and_scripts_load_inert_then_bind_click_and_dispose_in_vm(self):
        self.build();root=ET.parse(self.output/LAYOUT).getroot()
        ids=[n.get('id') for n in root.iter() if n.get('id')]
        scripts=[str(self.output/'content/panorama'/n.get('src').split('file://{resources}/')[1]) for n in root.findall('./scripts/include')]
        code=r"""const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const [ids,scripts]=JSON.parse(process.argv[1]);let serial=0;const timers=new Map(),nodes=new Map();
for(const id of ids)nodes.set(id,{valid:true,IsValid(){return this.valid},FindChildTraverse(key){return nodes.get(key)},SetPanelEvent(key,fn){this[key]=fn},ClearPanelEvent(key){delete this[key]},SetHasClass(){},text:'',html:false,visible:true});
const deny=new Proxy({},{get(){throw Error('native')}});let loading=true;
const context=vm.createContext({$:{Schedule(delay,fn){assert.equal(loading,false);assert.equal(delay,0.25);timers.set(++serial,fn);return serial},CancelScheduled(id){timers.delete(id)}},Game:deny,GameUI:deny,GameEvents:deny,Entities:deny,Players:deny});
for(const file of scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(timers.size,0);loading=false;const ui=context.DotaCoachPreparationBindings.bind(nodes.get('CoachPreparationRoot'));
assert.equal(timers.size,4);assert.equal(ui.updateTeam({revision:0,profiles:[{id:'p0',profileVersion:'v1',playerName:'Тестовый',kind:'synthetic',sourceLabel:'Тест',coverage:'unknown'}]}),true);
nodes.get('TeamCandidate0').onactivate();assert.equal(ui.contexts().team.players[0].id,'p0');assert.equal(ui.contexts().team.serverConfirmed,false);ui.dispose();assert.equal(timers.size,0);assert.equal(nodes.get('CoachPreparationRoot').visible,false);
"""
        result=subprocess.run(['node','-e',code,json.dumps([ids,scripts])],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
