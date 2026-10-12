"""Source-only package for local text preview; no microphone or native claims."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_intervention_bundle import builder, verifier, load

TASK = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[5]
LAYOUT = 'content/panorama/layout/custom_game/voice_text.xml'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'


class VoiceTextBundle(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((TASK / 'voice-text-manifest.json').read_text())
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.output = self.repo / 'build/dota_coach/voice-text'
        for entry in self.recipe['assets']:
            destination = self.repo / entry['source']
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((REPOSITORY / entry['source']).read_bytes())

    def source(self, target):
        return self.repo / next(e['source'] for e in self.recipe['assets'] if e['target'] == target)

    def build(self):
        return builder.build_bundle(self.repo, self.recipe, self.output)

    def reject(self, target, mutation):
        file = self.source(target)
        original = file.read_bytes()
        root = ET.fromstring(original)
        mutation(root)
        file.write_bytes(ET.tostring(root))
        try:
            with self.assertRaises(ValueError):
                self.build()
            self.assertFalse(self.output.exists())
        finally:
            file.write_bytes(original)

    def test_six_byte_copies_five_links_source_only(self):
        report = self.build()
        self.assertEqual(report['kind'], 'panorama_source_voice_text')
        self.assertEqual(len(report['assets']), 6)
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        for entry in self.recipe['assets']:
            self.assertEqual((self.output / entry['target']).read_bytes(), (self.repo / entry['source']).read_bytes())
        verified = verifier.verify_bundle(self.repo, self.recipe, self.output)
        self.assertEqual(verified['assets'], 6)
        self.assertEqual(verified['xml_resource_links'], 5)
        self.assertFalse(verified['runtime_verified'])

    def test_fixed_mapping_complete_unique_exact_recipe(self):
        candidates = [copy.deepcopy(self.recipe) for _ in range(7)]
        candidates[0]['assets'].pop()
        candidates[1]['assets'].append(candidates[1]['assets'][0])
        candidates[2]['assets'][0]['target'] = 'content/panorama/layout/custom_game/another.xml'
        candidates[3]['assets'][0]['source'] = '../outside.xml'
        candidates[4]['schema_version'] = True
        candidates[5]['extra'] = True
        candidates[6]['assets'][0]['extra'] = True
        for recipe in candidates:
            with self.subTest(recipe=recipe):
                with self.assertRaises(ValueError):
                    builder.build_bundle(self.repo, recipe, self.output)
                self.assertFalse(self.output.exists())

    def test_dependency_order_and_resource_reach(self):
        self.reject(LAYOUT, lambda r: r.find('scripts').insert(0, r.find('scripts')[-1]))
        self.reject(LAYOUT, lambda r: r.find('scripts')[0].set('src', 'https://example.invalid/a.js'))
        self.reject(LAYOUT, lambda r: r.find('Panel').append(ET.Element('include', {'src': 'nested.xml'})))

    def test_plain_scope_exact_required_ids_and_topology(self):
        self.reject(LAYOUT, lambda r: r.find('Panel').set('id', 'UnexpectedRoot'))
        self.reject(LAYOUT, lambda r: r.find('Panel').append(ET.Element('Panel')))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="VoiceTextHint"]').set('id', 'Wrong'))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="VoiceTextAddress"]').set('html', 'true'))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="VoiceTextAction"]').set('id', 'VoiceTextAddress'))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="VoiceTextPreviewButton"]').set('enabled', 'true'))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="VoiceTextPreviewButton"]').append(ET.Element('Panel')))
        def misplaced(r):
            window = r.find('Panel/Panel/Panel')
            row = window[3]
            button = row[0]
            row.remove(button)
            window.append(button)
        self.reject(LAYOUT, misplaced)

    def test_text_entry_leaf_disabled_empty_exact_attrs(self):
        for key, value in [('enabled', 'true'), ('text', 'керри фарми'), ('ontextentrychange', 'run()'), ('src', 'another.xml'), ('multiline', 'true')]:
            self.reject(LAYOUT, lambda r, k=key, v=value: r.find('.//TextEntry').set(k, v))
        self.reject(LAYOUT, lambda r: r.find('.//TextEntry').append(ET.Element('Label', {'html': 'false'})))

    def test_dtd_entities_mixed_text_unknown_tags_and_events(self):
        file = self.source(LAYOUT)
        original = file.read_bytes()
        for prefix in [b'<!DOCTYPE root>', b'<!DOCTYPE root [<!ENTITY x "bad">]>']:
            file.write_bytes(prefix + original)
            with self.assertRaises(ValueError):
                self.build()
            self.assertFalse(self.output.exists())
        file.write_bytes(original)
        self.reject(LAYOUT, lambda r: setattr(r.find('Panel'), 'text', 'run()'))
        self.reject(LAYOUT, lambda r: r.find('Panel').append(ET.Element('script')))
        self.reject(LAYOUT, lambda r: r.find('Panel').set('onload', 'bind()'))

    def test_manifest_exact_parent_loader(self):
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('type', 'Different'))
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('layoutfile', 'file://{resources}/layout/custom_game/another.xml'))
        def bypass(r):
            loader = r[0][0]
            r[0].remove(loader)
            r.append(loader)
        self.reject(MANIFEST, bypass)
        self.reject(MANIFEST, lambda r: r[0].set('class', 'extra'))

    def test_symlink_source_and_current_source_tamper(self):
        file = self.source(LAYOUT)
        original = file.read_bytes()
        outside = self.repo / 'another.xml'
        outside.write_bytes(original)
        file.unlink()
        file.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.build()
        file.unlink()
        file.write_bytes(original)
        self.build()
        file.write_bytes(original + b'\n')
        with self.assertRaises(ValueError):
            verifier.verify_bundle(self.repo, self.recipe, self.output)

    def test_existing_output_preserved_and_output_tamper_rejected(self):
        self.build()
        marker = self.output / 'marker'
        marker.write_text('keep')
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(marker.read_text(), 'keep')
        marker.unlink()
        (self.output / LAYOUT).write_text('tampered')
        with self.assertRaises(ValueError):
            verifier.verify_bundle(self.repo, self.recipe, self.output)

    def test_old_intervention_screen_still_refuses_text_entry(self):
        policy = load('voice_shared_policy_test', TASK / 'tools/intervention_screen_layout.py')
        with self.assertRaises(ValueError):
            policy.parse(b'<root><TextEntry id="X" enabled="false" text="" /></root>')

    def test_actual_packaged_context_input_and_button_preview(self):
        self.build()
        root = ET.parse(self.output / LAYOUT).getroot()
        def tree(node):
            return {'tag': node.tag, 'attrs': node.attrib, 'children': [tree(n) for n in node]}
        payload = {'tree': tree(root.find('Panel/Panel')), 'scripts': [
            str(self.output / ('content/panorama/' + n.get('src').removeprefix('file://{resources}/')))
            for n in root.find('scripts')]}
        program = r'''
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const payload=JSON.parse(fs.readFileSync(0,'utf8')), timers=new Map(), calls=[];let serial=0;
function node(data){const n={id:data.attrs.id,valid:true,visible:true,enabled:data.attrs.enabled!=='false',text:data.attrs.text||'',html:data.attrs.html!=='false',events:{},children:data.children.map(node),IsValid(){return this.valid;},SetPanelEvent(k,f){this.events[k]=f;},ClearPanelEvent(k){delete this.events[k];},FindChildTraverse(id){for(const c of this.children){if(c.id===id)return c;const f=c.FindChildTraverse(id);if(f)return f;}return null;}};return n;}
const root=node(payload.tree), native=new Proxy({}, {get(_t,k){calls.push(String(k));throw Error('native');}});
const context=vm.createContext({$: {Schedule(d,f){const h=serial++;timers.set(h,f);return h;},CancelScheduled(h){timers.delete(h);}},Game:native,GameEvents:native,Players:native,Entities:native});
for(const file of payload.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(timers.size,0);const ui=context.DotaCoachVoicePanels.bind(root);
assert.equal(ui.updateRoster({revision:1,players:[{id:'a',playerName:'Synthetic A',heroName:'Hero',role:1,source:'synthetic',side:'own',availability:'alive'}]}),true);
root.FindChildTraverse('VoiceTextInput').text='керри, фарми';root.FindChildTraverse('VoiceTextPreviewButton').events.onactivate();
assert.equal(ui.view().result.status,'ready');assert.equal(ui.view().result.proposal.recipientIds[0],'a');assert.equal(root.FindChildTraverse('VoiceTextAddress').text,'Synthetic A');assert.equal(ui.view().parser.consumed,1);assert.deepEqual(calls,[]);ui.dispose();assert.equal(timers.size,0);console.log('one packaged context preview A; no game calls');
'''
        result = subprocess.run(['node', '--eval', program], input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('one packaged context preview A', result.stdout)


if __name__ == '__main__':
    unittest.main()
