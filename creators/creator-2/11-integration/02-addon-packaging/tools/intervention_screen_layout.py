"""Fixed thirteen-resource composition of the canonical roster and request scopes."""
import copy,hashlib,xml.etree.ElementTree as ET
BASE='creators/creator-2/'
BINDING=BASE+'11-integration/01-ui-binding/src/panorama/'
TARGET='content/panorama/'
LAYOUT=TARGET+'layout/custom_game/coach_intervention.xml'
UI_MANIFEST=TARGET+'layout/custom_game/custom_ui_manifest.xml'
SCRIPTS=('preparation_panel_port.js','roster_cards_state.js','roster_cards.js','orders_state.js','intervention_request_state.js','intervention_request_panel.js','intervention_selection_state.js','intervention_screen_binding.js')
STYLES=('coach_hud.css','intervention_request.css','coach_intervention.css')
HUD_SCRIPTS=('roster_cards_state.js','roster_cards.js','orders_state.js','orders_panel.js','input_routing.js','camera_native.js','camera_panel.js','targets_state.js','targets_panel.js','coach_hud_binding.js')
INPUTS=[{'source':BASE+'07-match-screen/01-own-cards/src/panorama/layout/custom_game/coach_hud.xml','root_id':'CoachRoster','host_id':'CoachInterventionRosterHost','output_root_id':'CoachInterventionRoster'},
 {'source':BASE+'05-intervention-ui/01-request-ack/src/panorama/layout/custom_game/intervention_request.xml','root_id':'ManualRequestRoot','host_id':'CoachInterventionManualHost','output_root_id':'ManualRequestRoot'}]
ASSETS={BINDING+'layout/custom_game/intervention_screen_manifest.xml':UI_MANIFEST,BINDING+'layout/custom_game/coach_intervention.xml':LAYOUT,BINDING+'styles/custom_game/coach_intervention.css':TARGET+'styles/custom_game/coach_intervention.css'}
for section,style,scripts in [('07-match-screen/01-own-cards','coach_hud.css',()),('02-coach-interface/01-roster-cards',None,('roster_cards_state.js','roster_cards.js')),('02-coach-interface/02-status-orders',None,('orders_state.js',)),('05-intervention-ui/01-request-ack','intervention_request.css',('intervention_request_state.js','intervention_request_panel.js')),('11-integration/01-ui-binding',None,('preparation_panel_port.js','intervention_selection_state.js','intervention_screen_binding.js'))]:
 prefix=BASE+section+'/src/panorama/'
 if style:ASSETS[prefix+'styles/custom_game/'+style]=TARGET+'styles/custom_game/'+style
 for name in scripts:ASSETS[prefix+'scripts/custom_game/'+name]=TARGET+'scripts/custom_game/'+name
ATTRS={'root':set(),'styles':set(),'scripts':set(),'include':{'src'},'Panel':{'id','class','hittest','hittestchildren'},'Label':{'id','class','html','text','hittest'},'Button':{'id','class','enabled','visible','hittest'}}
def parse(payload,manifest=False,extra_tags=None):
 text=payload.decode('utf-8-sig')
 if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():raise ValueError('Unsupported XML DTD/entities')
 try:root=ET.fromstring(text)
 except ET.ParseError as e:raise ValueError('Invalid source XML') from e
 if root.tag!='root':raise ValueError('XML requires root')
 ids=set()
 for n in root.iter():
  allowed={'type','layoutfile'} if manifest and n.tag=='CustomUIElement' else (extra_tags or {}).get(n.tag,ATTRS.get(n.tag))
  if allowed is None or not set(n.attrib)<=allowed:raise ValueError('XML must preserve inert attribute allowlist')
  if (n.text or '').strip() or (n.tail or '').strip():raise ValueError('XML text must be declared attributes')
  if n.tag in ('Label','include','CustomUIElement') and len(n):raise ValueError('Resource/label nodes must be leaves')
  if n.tag=='Label' and n.get('html')!='false':raise ValueError('Labels require plain text')
  if n.tag=='Button' and n.get('enabled')!='false':raise ValueError('Buttons must start disabled')
  identity=n.get('id')
  if identity is not None:
   if not identity or identity in ids:raise ValueError('IDs must be unique and nonempty')
   ids.add(identity)
 return root

def dependencies(root,scripts,styles):
 if [n.tag for n in root]!=['styles','scripts','Panel'] or sum(1 for n in root.iter('root'))!=1:raise ValueError('Exact top-level source sections required')
 for tag,names in [('scripts',scripts),('styles',styles)]:
  section=root.find(tag);nodes=list(section)
  expected=['file://{resources}/'+tag+'/custom_game/'+name for name in names]
  if section.attrib or any(n.tag!='include' or set(n.attrib)!={'src'} or len(n) for n in nodes) or [n.get('src') for n in nodes]!=expected:raise ValueError('Dependency order/mapping must be exact')
 if len(list(root.iter('include')))!=len(scripts)+len(styles) or len(list(root.iter('scripts')))!=1 or len(list(root.iter('styles')))!=1:raise ValueError('Nested dependency sections unsupported')

def ids(panel):return {n.get('id'):n.tag for n in panel.iter() if n.get('id')}
def hud_manifest(payload,layout):
 root=parse(payload,True)
 if [n.tag for n in root.iter()]!=['root','Panel','CustomUIElement'] or len(root)!=1 or root[0].attrib or len(root[0])!=1 or root[0][0].attrib!={'type':'Hud','layoutfile':'file://{resources}/layout/custom_game/'+layout}:raise ValueError('Exact one-parent Hud loader required')
 return root
def roster_scope(panel):
 expected={'CoachRoster':'Panel','RosterStatus':'Label'}
 for i in range(5):
  expected['RosterCard'+str(i)]='Button'
  for name in ('Name','Hero','Role','Source','Availability','Hint'):expected['Roster'+name+str(i)]='Label'
 if ids(panel)!=expected or [n.tag for n in panel]!=['Label','Label','Panel'] or panel[1].get('id')!='RosterStatus':raise ValueError('Canonical roster scope must preserve required IDs/topology')
 strip=panel[2]
 if len(strip)!=5:raise ValueError('Roster requires five buttons')
 for i,button in enumerate(strip):
  if button.tag!='Button' or button.get('id')!='RosterCard'+str(i) or [n.get('id') for n in button]!=['Roster'+name+str(i) for name in ('Name','Hero','Role','Source','Availability','Hint')]:raise ValueError('Roster fields must belong to their declared slot')
def manual_scope(panel):
 expected={'ManualRequestRoot':'Panel','ManualRequestButton':'Button'}
 for name in ('Recipient','Mode','Actor','State','Reason','Message','Hint'):expected['ManualRequest'+name]='Label'
 if ids(panel)!=expected or len(panel)!=1 or panel[0].tag!='Panel' or len(panel[0])!=10 or [n.tag for n in panel[0]]!=['Label']*9+['Button']:raise ValueError('Canonical manual scope required')
 button=panel[0][-1]
 if button.get('id')!='ManualRequestButton' or len(button)!=1 or button[0].get('id')!='ManualRequestHint':raise ValueError('Request hint must belong to the button')
def shell(root):
 group=root.find('Panel')
 expected={'CoachInterventionScreen':'Panel','CoachInterventionStatus':'Label','CoachInterventionRosterHost':'Panel','CoachInterventionManualHost':'Panel'}
 if ids(group)!=expected or group.get('id')!='CoachInterventionScreen' or [n.tag for n in group]!=['Label','Label','Panel'] or group[1].get('id')!='CoachInterventionStatus':raise ValueError('Exact shell status/topology required')
 hosts=list(group[2])
 if [n.tag for n in hosts]!=['Panel','Panel'] or [n.get('id') for n in hosts]!=[e['host_id'] for e in INPUTS] or any(len(n) for n in hosts):raise ValueError('Exact empty hosts required')
 return hosts

def prepare(repository,manifest,read_source):
 if not isinstance(manifest,dict) or set(manifest)!={'schema_version','kind','assets','layout_inputs'} or type(manifest['schema_version']) is not int or manifest['schema_version']!=1 or manifest['kind']!='panorama_source_intervention_screen':raise ValueError('Unsupported screen recipe')
 entries=manifest['assets'];mapping={}
 if not isinstance(entries,list) or len(entries)!=13:raise ValueError('Exactly13 resources required')
 for e in entries:
  if not isinstance(e,dict) or set(e)!={'source','target'} or not isinstance(e['source'],str) or not isinstance(e['target'],str) or e['source'] in mapping:raise ValueError('Unique exact resource mapping required')
  mapping[e['source']]=e['target']
 if mapping!=ASSETS or manifest['layout_inputs']!=INPUTS:raise ValueError('Fixed mapping and two fixed layout inputs required')
 prepared=[(e['source'],e['target'],read_source(repository,e['source'])) for e in entries]
 payloads={target:raw for _,target,raw in prepared}
 root=parse(payloads[LAYOUT]);dependencies(root,SCRIPTS,STYLES);hosts=shell(root)
 for i,(entry,host) in enumerate(zip(INPUTS,hosts)):
  raw=read_source(repository,entry['source']);source=parse(raw)
  dependencies(source,HUD_SCRIPTS if i==0 else ('orders_state.js','intervention_request_state.js','intervention_request_panel.js'),('coach_hud.css',) if i==0 else ('intervention_request.css',))
  found=[n for n in source.iter('Panel') if n.get('id')==entry['root_id']]
  if len(found)!=1:raise ValueError('Input scope missing')
  panel=found[0];roster_scope(panel) if i==0 else manual_scope(panel)
  clone=copy.deepcopy(panel);clone.set('id',entry['output_root_id']);host.append(clone)
  root.insert(0,ET.Comment(' source='+entry['source']+' sha256='+hashlib.sha256(raw).hexdigest()+' '))
 generated=ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'
 if len(generated)>1024*1024:raise ValueError('Generated layout exceeds1MiB')
 checked=parse(generated);dependencies(checked,SCRIPTS,STYLES)
 expected=set(shell_ids for shell_ids in ('CoachInterventionScreen','CoachInterventionStatus','CoachInterventionRosterHost','CoachInterventionManualHost'))
 expected.update('CoachInterventionRoster' if name=='CoachRoster' else name for name in ids(hosts[0][0]))
 expected.update(ids(hosts[1][0]))
 if set(ids(checked.find('Panel')))!=expected or len(expected)!=50:raise ValueError('Composition must preserve exactly50 IDs')
 hud_manifest(payloads[UI_MANIFEST],'coach_intervention.xml')
 reached={UI_MANIFEST,LAYOUT}
 for node in checked.findall('./scripts/include')+checked.findall('./styles/include'):
  value=node.get('src');name=TARGET+value[len('file://{resources}/'):]
  if name not in payloads:raise ValueError('Undeclared resource')
  reached.add(name)
 if reached!=set(payloads):raise ValueError('Every output must be reachable')
 return [(source,target,generated if target==LAYOUT else raw) for source,target,raw in prepared]
