import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_intervention_bundle import builder, verifier, load, require_symlink

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
LAYOUT = 'content/panorama/layout/custom_game/orders_timeline.xml'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'


class OrdersTimelineBundle(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((TASK / 'orders-timeline-manifest.json').read_text())
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.output = self.repo / 'build/dota_coach/orders-timeline'
        for entry in self.recipe['assets']:
            target = self.repo / entry['source']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPO / entry['source']).read_bytes())

    def source(self, target):
        return self.repo / next(e['source'] for e in self.recipe['assets'] if e['target'] == target)

    def build(self):
        return builder.build_bundle(self.repo, self.recipe, self.output)

    def reject(self, target, change):
        file = self.source(target)
        raw = file.read_bytes()
        root = ET.fromstring(raw)
        change(root)
        file.write_bytes(ET.tostring(root))
        try:
            with self.assertRaises(ValueError): self.build()
            self.assertFalse(self.output.exists())
        finally:
            file.write_bytes(raw)

    def test_five_copies_four_links_current_source_only(self):
        report = self.build()
        self.assertEqual((report['kind'], len(report['assets'])), ('panorama_source_orders_timeline', 5))
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        for entry in self.recipe['assets']:
            self.assertEqual((self.output / entry['target']).read_bytes(), (self.repo / entry['source']).read_bytes())
        verified = verifier.verify_bundle(self.repo, self.recipe, self.output)
        self.assertEqual((verified['assets'], verified['xml_resource_links']), (5, 4))

    def test_fixed_exact_unique_recipe_mapping(self):
        recipes = [copy.deepcopy(self.recipe) for _ in range(7)]
        recipes[0]['assets'].pop()
        recipes[1]['assets'].append(recipes[1]['assets'][0])
        recipes[2]['assets'][0]['source'] = '../outside.xml'
        recipes[3]['assets'][0]['target'] = 'content/panorama/layout/custom_game/another.xml'
        recipes[4]['schema_version'] = True
        recipes[5]['extra'] = 1
        recipes[6]['assets'][0]['extra'] = 1
        for recipe in recipes:
            with self.subTest(recipe=recipe):
                with self.assertRaises(ValueError): builder.build_bundle(self.repo, recipe, self.output)
                self.assertFalse(self.output.exists())

    def test_exact_plain_ids_leaf_order_and_hidden_empty_initial_state(self):
        for field, value in [('id', 'Wrong'), ('visible', 'true'), ('onload', 'run()')]:
            self.reject(LAYOUT, lambda r, k=field, v=value: r.find('Panel').set(k, v))
        for field, value in [('id', 'TimelineEvent1'), ('html', 'true'), ('text', 'stale')]:
            self.reject(LAYOUT, lambda r, k=field, v=value: r.find('.//*[@id="TimelineEvent0"]').set(k, v))
        self.reject(LAYOUT, lambda r: r.find('.//*[@id="TimelineEvent0"]').append(ET.Element('Label', {'html': 'false'})))
        self.reject(LAYOUT, lambda r: r.find('Panel').insert(0, r.find('Panel')[-1]))
        self.reject(LAYOUT, lambda r: r.find('Panel').append(ET.Element('TextEntry', {'id': 'Input'})))

    def test_exact_dependencies_hud_loader_and_reachability(self):
        self.reject(LAYOUT, lambda r: r.find('scripts').insert(0, r.find('scripts')[-1]))
        self.reject(LAYOUT, lambda r: r.find('scripts')[0].set('src', 'https://example.invalid/script.js'))
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('type', 'Other'))
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('layoutfile', 'other.xml'))
        self.reject(MANIFEST, lambda r: r.find('Panel').append(ET.Element('CustomUIElement')))

    def test_dtd_entities_mixed_text_rejected_old_panel_defaults_unchanged(self):
        file = self.source(LAYOUT)
        raw = file.read_bytes()
        for prefix in (b'<!DOCTYPE root>', b'<!DOCTYPE root [<!ENTITY x "bad">]>'):
            file.write_bytes(prefix + raw)
            with self.assertRaises(ValueError): self.build()
            self.assertFalse(self.output.exists())
        file.write_bytes(raw)
        self.reject(LAYOUT, lambda r: setattr(r.find('Panel'), 'text', 'run()'))
        policy = load('timeline_old_defaults', TASK / 'tools/intervention_screen_layout.py')
        with self.assertRaises(ValueError): policy.parse(b'<root><Panel visible="false" /></root>')

    def test_source_links_rejected(self):
        require_symlink(self, self.repo)
        file = self.source(LAYOUT)
        raw = file.read_bytes()
        actual = self.repo / 'actual.xml'
        actual.write_bytes(raw)
        file.unlink()
        file.symlink_to(actual)
        with self.assertRaises(ValueError): self.build()
        self.assertFalse(self.output.exists())
        file.unlink()
        file.write_bytes(raw)

    def test_current_source_and_output_integrity(self):
        file = self.source(LAYOUT)
        raw = file.read_bytes()
        self.build()
        file.write_bytes(raw + b'\n')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)
        file.write_bytes(raw)
        (self.output / LAYOUT).write_text('tampered')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)

    def test_existing_output_is_preserved(self):
        self.build()
        marker = self.output / 'keep'
        marker.write_text('keep')
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(marker.read_text(), 'keep')

    def test_actual_packaged_xml_two_scripts_bind_and_capture(self):
        self.build()
        layout = ET.parse(self.output / LAYOUT).getroot()
        payload = {'ids': [node.attrib['id'] for node in layout.iter() if 'id' in node.attrib],
                   'scripts': [str(self.output / ('content/panorama/' + node.get('src').removeprefix('file://{resources}/')))
                               for node in layout.find('scripts')]}
        program = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(0,'utf8')),nodes={};
for(const id of data.ids)nodes[id]={visible:true,html:true,text:'',IsValid(){return true;}};
const root=nodes.OrdersTimelineRoot;root.visible=false;root.FindChildTraverse=id=>nodes[id];
const native=new Proxy({}, {get(){throw Error('native API forbidden');}});
const context=vm.createContext({$:native,Game:native,GameEvents:native,Entities:native});
for(const file of data.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(root.visible,false);const panel=context.DotaCoachOrdersTimelinePanels.bind(root);
assert.equal(panel.record({recipientText:'Selected B',modeText:'AI',requestRecipientText:'Captured A',actionText:'Move',
stageText:'Untrusted text',reasonText:'',eligibilityText:'View only',canIssue:false,ticket:1,stage:'accepted',closed:false}),true);
assert.equal(panel.view().events[0].actorName,'Captured A');assert.equal(panel.view().events[0].nativeConfirmed,false);
assert.equal(nodes.TimelineEvent0.html,false);assert.match(nodes.TimelineEvent0.text,/Captured A/);
assert.doesNotMatch(nodes.TimelineEvent0.text,/Untrusted/);panel.dispose();assert.equal(root.visible,false);
'''
        result = subprocess.run(['node', '-e', program], input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
