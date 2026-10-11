"""Two canonical panel scopes, one explicit binder; source evidence only."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from test_intervention_bundle import builder, verifier

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
LAYOUT = 'content/panorama/layout/custom_game/coach_match_observation.xml'


class MatchObservationBundle(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads((TASK / 'match-observation-manifest.json').read_text())
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name); self.output = self.repo / 'build/dota_coach/match-observation'
        for item in self.recipe['assets'] + self.recipe['layout_inputs']:
            file = self.repo / item['source']; file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes((REPO / item['source']).read_bytes())

    def build(self):
        return builder.build_bundle(self.repo, self.recipe, self.output)

    def reject(self, source, change):
        file = self.repo / source; raw = file.read_bytes(); root = ET.fromstring(raw)
        change(root); file.write_bytes(ET.tostring(root))
        try:
            with self.assertRaises(ValueError): self.build()
            self.assertFalse(self.output.exists())
        finally: file.write_bytes(raw)

    def test_ten_assets_nine_links_two_fingerprints_and_source_only(self):
        report = self.build()
        self.assertEqual((report['kind'], len(report['assets'])), ('panorama_source_match_observation', 10))
        self.assertFalse(report['source2_compiled']); self.assertFalse(report['runtime_verified'])
        result = verifier.verify_bundle(self.repo, self.recipe, self.output)
        self.assertEqual((result['assets'], result['xml_resource_links']), (10, 9))
        generated = (self.output / LAYOUT).read_text()
        for item in self.recipe['layout_inputs']:
            self.assertIn('source=' + item['source'], generated)
            self.assertIn(hashlib.sha256((self.repo / item['source']).read_bytes()).hexdigest(), generated)
        for item in self.recipe['assets']:
            if item['target'] != LAYOUT:
                self.assertEqual((self.output / item['target']).read_bytes(), (self.repo / item['source']).read_bytes())

    def test_exact_recipe_assets_and_two_input_scopes(self):
        recipes = [copy.deepcopy(self.recipe) for _ in range(8)]
        recipes[0]['assets'].pop(); recipes[1]['layout_inputs'].pop()
        recipes[2]['layout_inputs'][0]['host_id'] = 'MatchHistoryHost'
        recipes[3]['layout_inputs'][0]['source'] = '../outside.xml'
        recipes[4]['assets'][0]['target'] = 'content/panorama/another.xml'
        recipes[5]['assets'].append(recipes[5]['assets'][0])
        recipes[6]['schema_version'] = True; recipes[7]['extra'] = True
        for recipe in recipes:
            with self.assertRaises(ValueError): builder.build_bundle(self.repo, recipe, self.output)
            self.assertFalse(self.output.exists())

    def test_exact_shell_empty_hosts_dependency_order_and_inert_state(self):
        source = next(e['source'] for e in self.recipe['assets'] if e['target'] == LAYOUT)
        self.reject(source, lambda r: r.find('Panel').set('visible', 'true'))
        self.reject(source, lambda r: r.find('Panel').set('onload', 'run()'))
        self.reject(source, lambda r: r.find('.//*[@id="MatchObservationStatus"]').set('html', 'true'))
        self.reject(source, lambda r: r.find('.//*[@id="MatchObservationStatus"]').set('text', 'stale'))
        self.reject(source, lambda r: r.find('.//*[@id="MatchOpponentHost"]').append(ET.Element('Panel')))
        self.reject(source, lambda r: r.find('scripts').insert(0, r.find('scripts')[-1]))

    def test_canonical_input_slot_ownership_and_history_topology_cannot_change(self):
        first, second = self.recipe['layout_inputs']
        self.reject(first['source'], lambda r: r.find('.//*[@id="OpponentName0"]').set('id', 'OtherName'))
        self.reject(first['source'], lambda r: r.find('.//*[@id="OpponentCard4"]').set('visible', 'false'))
        self.reject(second['source'], lambda r: r.find('.//*[@id="TimelineEvent0"]').set('html', 'true'))
        self.reject(second['source'], lambda r: r.find('Panel').insert(0, r.find('Panel')[-1]))

    def test_generated_scope_ids_and_hosts_are_exact(self):
        self.build(); tree = ET.parse(self.output / LAYOUT).getroot()
        ids = [n.get('id') for n in tree.iter() if n.get('id')]
        self.assertEqual((len(ids), len(set(ids))), (38, 38))
        for item in self.recipe['layout_inputs']:
            host = tree.find('.//*[@id="' + item['host_id'] + '"]')
            self.assertEqual(len(host), 1); self.assertEqual(host[0].get('id'), item['root_id'])
            original = ET.parse(self.repo / item['source']).getroot().find('Panel')
            self.assertEqual(ET.tostring(host[0]), ET.tostring(original))

    def test_input_fingerprint_current_source_and_output_tamper_detected(self):
        self.build(); file = self.repo / self.recipe['layout_inputs'][0]['source']; raw = file.read_bytes()
        file.write_bytes(raw + b'\n')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)
        file.write_bytes(raw); (self.output / LAYOUT).write_text('tampered')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo, self.recipe, self.output)

    def test_source_links_and_existing_output_preserved(self):
        file = self.repo / self.recipe['layout_inputs'][0]['source']; raw = file.read_bytes()
        other = self.repo / 'actual.xml'; other.write_bytes(raw); file.unlink(); file.symlink_to(other)
        with self.assertRaises(ValueError): self.build()
        self.assertFalse(self.output.exists()); file.unlink(); file.write_bytes(raw)
        self.build(); marker = self.output / 'keep'; marker.write_text('keep')
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(marker.read_text(), 'keep')

    def test_actual_packaged_context_two_private_panels_independent_sources_and_dispose(self):
        self.build(); tree = ET.parse(self.output / LAYOUT).getroot()
        data = {'ids': [n.get('id') for n in tree.iter() if n.get('id')],
                'scripts': [str(self.output / ('content/panorama/' + n.get('src').removeprefix('file://{resources}/')))
                            for n in tree.find('scripts')]}
        program = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(0,'utf8')),nodes={};
for(const id of data.ids)nodes[id]={visible:true,html:true,text:'',IsValid(){return true;},FindChildTraverse(id){return nodes[id];}};
const root=nodes.CoachMatchObservation;
root.visible=nodes.OpponentRosterRoot.visible=nodes.OrdersTimelineRoot.visible=false;
const native=new Proxy({}, {get(){throw Error('no native API');}});
const context=vm.createContext({$:native,Game:native,GameEvents:native});
for(const file of data.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);
assert.equal(root.visible,false);const panel=context.DotaCoachMatchObservationPanels.bind(root);
assert.equal(panel.updateOpponents({revision:1,players:[{id:'a',playerName:'Enemy',heroName:null}]}),true);
assert.equal(panel.recordOrder({recipientText:'Selected B',modeText:'AI',requestRecipientText:'Captured A',actionText:'Move',
stageText:'Untrusted',reasonText:'',eligibilityText:'View only',canIssue:false,ticket:1,stage:'accepted',closed:false}),true);
assert.equal(nodes.OpponentName0.text,'Enemy');assert.match(nodes.TimelineEvent0.text,/Captured A/);
assert.equal(panel.view().nativeConfirmed,false);assert.equal(panel.view().opponents.sourceAuthorizationConfirmed,false);
assert.equal(panel.updateOpponents(null),false);assert.equal(panel.view().history.ready,true);
assert.equal(nodes.OpponentName0.text,'');assert.match(nodes.TimelineEvent0.text,/Captured A/);
panel.dispose();assert.equal(root.visible,false);assert.equal(nodes.TimelineEvent0.text,'');
assert.equal(panel.isDisposed(),true);
'''
        result = subprocess.run(['node', '-e', program], input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__': unittest.main()
