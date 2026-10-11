"""Fixed mouse proposal source package; native/game authorization untested."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_intervention_bundle import builder, verifier, load

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
LAYOUT = 'content/panorama/layout/custom_game/mouse_proposal.xml'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'


class MouseProposalBundle(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((TASK / 'mouse-proposal-manifest.json').read_text())
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.output = self.repo / 'build/dota_coach/mouse-proposal'
        for entry in self.recipe['assets']:
            file = self.repo / entry['source']
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes((REPO / entry['source']).read_bytes())

    def source(self, target):
        return self.repo / next(e['source'] for e in self.recipe['assets'] if e['target'] == target)

    def build(self):
        return builder.build_bundle(self.repo, self.recipe, self.output)

    def reject(self, target, change):
        file = self.source(target)
        raw = file.read_bytes()
        tree = ET.fromstring(raw)
        change(tree)
        file.write_bytes(ET.tostring(tree))
        try:
            with self.assertRaises(ValueError): self.build()
            self.assertFalse(self.output.exists())
        finally:
            file.write_bytes(raw)

    def test_five_copies_four_links_current_sources_no_native_claims(self):
        report = self.build()
        self.assertEqual((report['kind'], len(report['assets'])), ('panorama_source_mouse_proposal', 5))
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        for entry in self.recipe['assets']:
            self.assertEqual((self.output / entry['target']).read_bytes(), (self.repo / entry['source']).read_bytes())
        result = verifier.verify_bundle(self.repo, self.recipe, self.output)
        self.assertEqual((result['assets'], result['xml_resource_links']), (5, 4))

    def test_fixed_mapping_rejects_extra_missing_duplicate_and_redirected_assets(self):
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

    def test_exact_ordered_plain_labels_and_hidden_initial_root(self):
        for field,value in [('id','Wrong'),('visible','true'),('onload','run()')]:
            self.reject(LAYOUT,lambda r,k=field,v=value:r.find('Panel').set(k,v))
        for field,value in [('id','MouseAction'),('html','true'),('text','stale')]:
            self.reject(LAYOUT,lambda r,k=field,v=value:r.find('.//*[@id="MouseActor"]').set(k,v))
        self.reject(LAYOUT,lambda r:r.find('.//*[@id="MouseActor"]').append(ET.Element('Label',{'html':'false'})))
        self.reject(LAYOUT,lambda r:r.find('Panel').insert(0,r.find('Panel')[-1]))
        self.reject(LAYOUT,lambda r:r.find('Panel').remove(r.find('Panel')[-1]))
        self.reject(LAYOUT,lambda r:r.find('Panel').append(ET.Element('Button',{'enabled':'false'})))

    def test_exact_ordered_dependencies_and_one_inert_hud_loader(self):
        self.reject(LAYOUT, lambda r: r.find('scripts').insert(0, r.find('scripts')[-1]))
        self.reject(LAYOUT, lambda r: r.find('scripts')[0].set('src', 'https://example.invalid/script.js'))
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('type', 'Other'))
        self.reject(MANIFEST, lambda r: r.find('.//CustomUIElement').set('layoutfile', 'other.xml'))
        self.reject(MANIFEST, lambda r: r.find('Panel').append(ET.Element('CustomUIElement')))

    def test_dtd_entities_mixed_text_rejected_old_parser_defaults_unchanged(self):
        file = self.source(LAYOUT)
        raw = file.read_bytes()
        for prefix in (b'<!DOCTYPE root>', b'<!DOCTYPE root [<!ENTITY x "bad">]>'):
            file.write_bytes(prefix + raw)
            with self.assertRaises(ValueError): self.build()
            self.assertFalse(self.output.exists())
        file.write_bytes(raw)
        self.reject(LAYOUT, lambda r: setattr(r.find('Panel'), 'text', 'run()'))
        policy = load('opponent_old_defaults', TASK / 'tools/intervention_screen_layout.py')
        with self.assertRaises(ValueError): policy.parse(b'<root><Panel visible="false" /></root>')

    def test_linked_source_current_source_and_output_integrity(self):
        file = self.source(LAYOUT)
        raw = file.read_bytes()
        actual = self.repo / 'actual.xml'
        actual.write_bytes(raw); file.unlink(); file.symlink_to(actual)
        with self.assertRaises(ValueError): self.build()
        file.unlink(); file.write_bytes(raw)
        self.build(); file.write_bytes(raw + b'\n')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)
        file.write_bytes(raw); (self.output / LAYOUT).write_text('tampered')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)

    def test_existing_output_is_preserved(self):
        self.build()
        marker = self.output / 'keep'; marker.write_text('keep')
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(marker.read_text(), 'keep')

    def test_actual_packaged_context_fixed_actor_actions_unknown_lease_and_dispose(self):
        self.build()
        tree=ET.parse(self.output/LAYOUT).getroot()
        payload={'ids':[n.attrib['id'] for n in tree.iter() if 'id' in n.attrib],
                 'scripts':[str(self.output/('content/panorama/'+n.get('src').removeprefix('file://{resources}/'))) for n in tree.find('scripts')]}
        program=r'''const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(0,'utf8')),nodes={};
for(const id of data.ids)nodes[id]={visible:true,html:true,text:'',IsValid(){return true;}};
const root=nodes.MouseProposalRoot;root.visible=false;root.FindChildTraverse=id=>nodes[id];
const native=new Proxy({}, {get(){throw Error('native API forbidden');}});
const context=vm.createContext({$:native,Game:native,GameEvents:native,Entities:native});
for(const file of data.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(root.visible,false);const p=context.DotaCoachMouseProposalPanels.bind(root);
assert.equal(p.captureActor({id:'a',playerName:'<b>A</b>',epoch:1}),true);
assert.equal(p.proposeMove({x:1,y:2,z:0}),true);assert.equal(nodes.MouseAction.text,'Движение');
for(const [team,kind,action] of [['enemy','hero','attack'],['enemy','creep','last_hit'],['ally','creep','deny']]){
 assert.equal(p.proposeTarget({status:'ready',message:'',target:{id:'t',label:'<b>T</b>',team,kind,alive:true,entityIndex:3}}),true);
 assert.equal(p.view().proposal.action,action);assert.equal(nodes.MouseTarget.text,'<b>T</b>');assert.equal(nodes.MouseTarget.html,false);
}
assert.equal(p.captureActor({id:'b',playerName:'B',epoch:2}),false);assert.equal(p.view().actor.id,'a');
assert.match(nodes.MouseLease.text,/неизвестно/);assert.equal(p.view().canSend,false);
assert.equal(p.view().nativeConfirmed,false);assert.equal(p.view().sourceAuthorizationConfirmed,false);
assert.equal(p.proposeTarget(null),false);assert.equal(nodes.MouseAction.text,'');assert.equal(nodes.MouseActor.text,'<b>A</b>');
p.dispose();assert.equal(root.visible,false);assert.equal(nodes.MouseActor.text,'');assert.equal(p.isDisposed(),true);
'''
        result=subprocess.run(['node','-e',program],input=json.dumps(payload),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__ == '__main__':
    unittest.main()
