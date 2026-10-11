"""One generated context from canonical roster/request scopes; source evidence only."""
import copy, hashlib, importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
import xml.etree.ElementTree as ET
REPOSITORY=Path(__file__).resolve().parents[5]
TASK=Path(__file__).resolve().parents[1]
TOOLS=REPOSITORY/'creators/creator-2/01-foundation/02-panorama-capability/tools'
LAYOUT='content/panorama/layout/custom_game/coach_intervention.xml'
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,file);module=importlib.util.module_from_spec(spec)
 old=sys.dont_write_bytecode;sys.dont_write_bytecode=True
 try:spec.loader.exec_module(module)
 finally:sys.dont_write_bytecode=old
 return module
builder=load('screen_builder',TOOLS/'build_probe_bundle.py')
sys.path.insert(0,str(TOOLS))
try:verifier=load('screen_verifier',TOOLS/'verify_probe_bundle.py')
finally:sys.path.pop(0)
class ScreenBundleTests(unittest.TestCase):
 def setUp(self):
  self.manifest=json.loads((TASK/'intervention-screen-manifest.json').read_text())
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.repo=Path(temp.name)
  self.output=self.repo/'build/dota_coach/screen'
  for e in self.manifest['assets']+self.manifest['layout_inputs']:
   p=self.repo/e['source'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((REPOSITORY/e['source']).read_bytes())
 def build(self):return builder.build_bundle(self.repo,self.manifest,self.output)
 def source(self,target):return self.repo/next(e['source'] for e in self.manifest['assets'] if e['target']==target)
 def reject(self,manifest=None):
  with self.assertRaises((ValueError,OSError)):builder.build_bundle(self.repo,manifest or self.manifest,self.output)
  self.assertFalse(self.output.exists())
 def test_roundtrip_exact13_resources12_links_and_false_native(self):
  report=self.build();self.assertEqual(len(report['assets']),13)
  self.assertFalse(report['source2_compiled']);self.assertFalse(report['runtime_verified'])
  for e in report['assets']:
   data=(self.output/e['target']).read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),e['sha256'])
   if e['target']!=LAYOUT:self.assertEqual(data,(self.repo/e['source']).read_bytes())
  result=verifier.verify_bundle(self.repo,self.manifest,self.output)
  self.assertEqual(result['xml_resource_links'],12);self.assertTrue(result['package_verified'])
 def test_generated_scopes_equal_sources_with_only_declared_root_rename(self):
  self.build();root=ET.parse(self.output/LAYOUT).getroot();ids=[n.get('id') for n in root.iter() if n.get('id')]
  self.assertEqual(len(ids),50);self.assertEqual(len(ids),len(set(ids)))
  for e in self.manifest['layout_inputs']:
   expected=copy.deepcopy(next(n for n in ET.parse(self.repo/e['source']).getroot().iter('Panel') if n.get('id')==e['root_id']))
   expected.set('id',e['output_root_id']);expected.tail=None
   host=next(n for n in root.iter('Panel') if n.get('id')==e['host_id']);self.assertEqual(len(host),1)
   actual=copy.deepcopy(host[0]);actual.tail=None;self.assertEqual(ET.tostring(actual),ET.tostring(expected))
 def test_fingerprints_change_when_raw_input_changes_outside_extracted_scope(self):
  prepared=builder.prepare_assets(self.repo,self.manifest)
  old=next(data for _,target,data in prepared if target==LAYOUT)
  p=self.repo/self.manifest['layout_inputs'][0]['source'];p.write_bytes(p.read_bytes().replace(b'CoachHudStatus',b'CoachHudStatusChanged'))
  new=next(data for _,target,data in builder.prepare_assets(self.repo,self.manifest) if target==LAYOUT)
  self.assertNotEqual(old,new)
  for e in self.manifest['layout_inputs']:
   self.assertIn(hashlib.sha256((self.repo/e['source']).read_bytes()).hexdigest().encode(),new)
 def test_exact_recipe_rejects_mapping_inputs_duplicates_schema_and_extra_fields(self):
  for mode in ('missing','extra','remap','duplicate','input','input_extra','schema','field'):
   with self.subTest(mode=mode):
    m=copy.deepcopy(self.manifest)
    if mode=='missing':m['assets'].pop()
    if mode=='extra':m['assets'].append(copy.deepcopy(m['assets'][0]))
    if mode=='remap':m['assets'][0]['target']='content/panorama/layout/custom_game/x.xml'
    if mode=='duplicate':m['assets'][1]=copy.deepcopy(m['assets'][0])
    if mode=='input':m['layout_inputs'][0]['output_root_id']='Unknown'
    if mode=='input_extra':m['layout_inputs'].append(copy.deepcopy(m['layout_inputs'][0]))
    if mode=='schema':m['schema_version']=True
    if mode=='field':m['bootstrap']=True
    self.reject(m)
 def test_dependencies_and_loader_parent_are_exact(self):
  files=[self.source(LAYOUT),self.source('content/panorama/layout/custom_game/custom_ui_manifest.xml')]
  for p in files:
   original=p.read_bytes()
   edits=[original.replace(b'<scripts>',b'<scripts onload="evil()">'),original.replace(b'type="Hud"',b'type="Other"'),original.replace(b'</Panel>',b'</Panel><Panel />',1)] if p==files[0] else [original.replace(b'type="Hud"',b'type="Other"'),original.replace(b'</Panel>',b'</Panel><Panel />',1)]
   for edit in edits:
    if edit==original:continue
    with self.subTest(path=p.name):p.write_bytes(edit);self.reject();p.write_bytes(original)
 def test_inert_attributes_text_dtd_plain_labels_disabled_buttons(self):
  p=self.repo/self.manifest['layout_inputs'][1]['source'];original=p.read_bytes()
  for before,after in [(b'html="false"',b'html="true"'),(b'enabled="false"',b'enabled="true"'),(b'class="ManualRequestTitle"',b'class="ManualRequestTitle" onactivate="evil()"'),(b'class="ManualRequestTitle"',b'class="ManualRequestTitle" src="file://evil"'),(b'<root>',b'<!DOCTYPE root [<!ENTITY x "evil">]><root>'),(b'<root>',b'<root>evil'),(b'class="ManualRequestTitle"',b'class="ManualRequestTitle" unexpected="yes"')]:
   with self.subTest(change=after):p.write_bytes(original.replace(before,after,1));self.reject();p.write_bytes(original)
 def test_shell_hosts_must_be_empty_and_in_the_declared_parent(self):
  p=self.source(LAYOUT);original=p.read_bytes()
  for edit in [original.replace(b'id="CoachInterventionRosterHost"',b'id="Wrong"'),original.replace(b'<Panel id="CoachInterventionRosterHost"',b'<Label id="CoachInterventionRosterHost"'),original.replace(b'id="CoachInterventionRosterHost"',b'id="CoachInterventionRosterHost" text="occupied"'),original.replace(b'<Panel class="CoachInterventionRow"',b'<Panel id="Unexpected" class="CoachInterventionRow"')]:
   p.write_bytes(edit);self.reject();p.write_bytes(original)
 def test_required_ids_types_and_button_label_scope(self):
  p=self.repo/self.manifest['layout_inputs'][0]['source'];original=p.read_bytes()
  for edit in [original.replace(b'RosterHint4',b'WrongHint'),original.replace(b'id="RosterCard0"',b'id="RosterCard1"'),original.replace(b'id="RosterName0"',b'id="RosterName1"')]:
   p.write_bytes(edit);self.reject();p.write_bytes(original)
 def test_bounded_input_symlink_and_current_source_tamper(self):
  p=self.repo/self.manifest['layout_inputs'][0]['source'];raw=p.read_bytes();p.unlink()
  outside=self.repo/'outside.xml';outside.write_bytes(raw);p.symlink_to(outside);self.reject();p.unlink();p.write_bytes(raw)
  self.build();target=self.output/LAYOUT;target.write_bytes(target.read_bytes()+b'\n')
  with self.assertRaises(ValueError):verifier.verify_bundle(self.repo,self.manifest,self.output)
 def test_existing_output_is_preserved(self):
  self.output.mkdir(parents=True);marker=self.output/'keep';marker.write_text('user')
  with self.assertRaises(FileExistsError):self.build()
  self.assertEqual(marker.read_text(),'user')
 def test_actual_generated_context_bind_and_card_click_send_once(self):
  self.build();root=ET.parse(self.output/LAYOUT).getroot()
  def tree(n):return {'tag':n.tag,'attrs':n.attrib,'children':[tree(c) for c in n]}
  probe=self.repo/'probe.json';probe.write_text(json.dumps({'tree':tree(root.find('Panel')),'scripts':[str(self.output/'content/panorama'/n.get('src').split('file://{resources}/')[1]) for n in root.findall('./scripts/include')]}))
  js=r"""const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const input=JSON.parse(fs.readFileSync(process.argv[1],'utf8')),timers=new Map();let serial=0;
function node(data){const attrs=data.attrs,children=data.children.map(node);return {id:attrs.id,visible:attrs.visible!=='false',enabled:false,text:attrs.text||'',events:{},classes:new Set(),IsValid(){return true;},FindChildTraverse(id){for(const c of children){if(c.id===id)return c;const found=c.FindChildTraverse(id);if(found)return found;}},SetPanelEvent(k,v){this.events[k]=v;},ClearPanelEvent(k){delete this.events[k];},SetHasClass(k,on){if(on)this.classes.add(k);else this.classes.delete(k);}};}
const root=node(input.tree),deny=new Proxy({},{get(){throw Error('native');}}),context=vm.createContext({Game:deny,GameUI:deny,GameEvents:deny,Entities:deny,$:{Schedule(d,f){const id=++serial;timers.set(id,f);return id;},CancelScheduled(id){timers.delete(id);}}});
for(const file of input.scripts)vm.runInContext(fs.readFileSync(file,'utf8'),context);assert.equal(timers.size,0);
let sent=[];const ui=context.DotaCoachInterventionScreenPanels.bind(root,intent=>sent.push(intent));
ui.replaceRoster([{id:'a',playerName:'Synthetic',heroName:'Axe',role:3,source:'synthetic',side:'own',availability:'alive'}]);
ui.updateControl({id:'a',playerName:'Synthetic',mode:'AI',epoch:1,revision:1,side:'own',availability:'alive'});
root.FindChildTraverse('RosterCard0').events.onactivate();assert.match(root.FindChildTraverse('ManualRequestRecipient').text,/\[a\]/);
root.FindChildTraverse('ManualRequestButton').events.onactivate();assert.equal(sent.length,1);assert.equal(sent[0].recipientId,'a');ui.dispose();assert.equal(timers.size,0);
process.stdout.write(JSON.stringify({definitions:input.scripts.length,sent:sent.length,timers:timers.size}));"""
  r=subprocess.run(['node','--eval',js,str(probe)],check=True,capture_output=True,text=True)
  self.assertEqual(json.loads(r.stdout),{'definitions':8,'sent':1,'timers':0})
