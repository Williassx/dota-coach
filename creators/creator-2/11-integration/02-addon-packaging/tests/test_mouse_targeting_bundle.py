"""Source composition only, with canonical fixtures and reused package guards."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import test_mouse_proposal_bundle as standalone

TASK=Path(__file__).resolve().parents[1]
REPO=TASK.parents[3]
LAYOUT=standalone.LAYOUT
builder,verifier=standalone.builder,standalone.verifier

class MouseTargetingBundle(unittest.TestCase):
    def setUp(self):
        self.recipe=json.loads((TASK/'mouse-targeting-manifest.json').read_text())
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.repo=Path(temporary.name);self.output=self.repo/'build/dota_coach/mouse-targeting'
        for entry in self.recipe['assets']:
            file=self.repo/entry['source'];file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes((REPO/entry['source']).read_bytes())

    source=standalone.MouseProposalBundle.source
    build=standalone.MouseProposalBundle.build
    reject=standalone.MouseProposalBundle.reject
    test_fixed_mapping=standalone.MouseProposalBundle.test_fixed_mapping_rejects_extra_missing_duplicate_and_redirected_assets
    test_exact_plain_layout=standalone.MouseProposalBundle.test_exact_ordered_plain_labels_and_hidden_initial_root
    test_native_root_policy=standalone.MouseProposalBundle.test_rejects_identified_native_root_and_changed_host_input_policy
    test_canonical_dependencies_loader=standalone.MouseProposalBundle.test_exact_ordered_dependencies_and_one_inert_hud_loader
    test_xml_security_old_defaults=standalone.MouseProposalBundle.test_dtd_entities_mixed_text_rejected_old_parser_defaults_unchanged
    test_source_links_rejected=standalone.MouseProposalBundle.test_linked_source_rejected
    test_source_fingerprint_output_integrity=standalone.MouseProposalBundle.test_current_source_and_output_integrity
    test_preserve_output=standalone.MouseProposalBundle.test_existing_output_is_preserved

    def test_seven_assets_six_links_composed_scripts_preserve_source_scope(self):
        file=self.source(LAYOUT);before=file.read_bytes()
        report=self.build();self.assertEqual((report['kind'],len(report['assets'])),('panorama_source_mouse_targeting',7))
        self.assertFalse(report['source2_compiled']);self.assertFalse(report['runtime_verified'])
        verified=verifier.verify_bundle(self.repo,self.recipe,self.output)
        self.assertEqual((verified['assets'],verified['xml_resource_links']),(7,6))
        after=(self.output/LAYOUT).read_bytes();root=ET.fromstring(after)
        self.assertEqual([n.get('src').split('/')[-1] for n in root.find('scripts')],
                         ['targets_state.js','mouse_proposal_state.js','mouse_proposal_panel.js','mouse_targeting_binding.js'])
        self.assertEqual(ET.tostring(root.find('Panel')),ET.tostring(ET.fromstring(before).find('Panel')))
        self.assertIn(b'sha256=',after);self.assertEqual(file.read_bytes(),before)
        for entry in self.recipe['assets']:
            if entry['target']!=LAYOUT:self.assertEqual((self.output/entry['target']).read_bytes(),(self.repo/entry['source']).read_bytes())

    def test_actual_packaged_context_freshness_actor_move_independence_and_dispose(self):
        self.build();tree=ET.parse(self.output/LAYOUT).getroot()
        payload={'ids':[n.get('id') for n in tree.iter() if 'id' in n.attrib],
                 'scripts':[str(self.output/('content/panorama/'+n.get('src').removeprefix('file://{resources}/'))) for n in tree.find('scripts')]}
        program=r'''const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(0,'utf8')),nodes={};
for(const id of data.ids)nodes[id]={visible:true,html:true,text:'',IsValid(){return true;}};
const root=nodes.MouseProposalRoot;root.visible=false;root.FindChildTraverse=id=>nodes[id];
const native=new Proxy({},{get(){throw Error('native API forbidden');}});
const context=vm.createContext({$:native,Game:native,GameEvents:native,Entities:native});
for(const file of data.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(root.visible,false);let time=0;
const p=context.DotaCoachMouseTargetingPanels.bind(root,{now:()=>time,maxAgeMs:1000});
assert.equal(p.captureActor({id:'a',playerName:'<b>A</b>',epoch:1}),true);
const row={id:'t',visibility:'visible',label:'<b>T</b>',team:'enemy',kind:'hero',alive:true,entityIndex:3};
assert.equal(p.updateTargets({revision:1,targets:[row]}),true);assert.equal(p.selectTarget('t'),true);
assert.equal(p.proposeTarget(),true);assert.equal(nodes.MouseTarget.text,'<b>T</b>');assert.equal(nodes.MouseTarget.html,false);
assert.equal(p.captureActor({id:'b',playerName:'B',epoch:2}),false);
time=1000;assert.equal(p.view().mouse.proposal,null);assert.equal(nodes.MouseTarget.text,'');assert.equal(p.view().mouse.actor.id,'a');
assert.equal(p.proposeMove({x:100,y:200,z:0}),true);
assert.equal(p.updateTargets({revision:2,targets:[{id:'t',visibility:'hidden'}]}),true);
assert.equal(p.view().mouse.proposal.action,'move');assert.equal(p.proposeTarget(),false);
assert.match(nodes.MouseLease.text,/неизвестно/);
for(const key of ['canSend','nativeConfirmed','sourceAuthorizationConfirmed'])assert.equal(p.view()[key],false);
p.dispose();assert.equal(root.visible,false);assert.equal(nodes.MouseActor.text,'');assert.equal(p.view().closed,true);
'''
        result=subprocess.run(['node','-e',program],input=json.dumps(payload),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
