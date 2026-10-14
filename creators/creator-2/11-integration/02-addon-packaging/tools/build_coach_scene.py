"""Exact C1/C2 coach scene source package; never installs, compiles or launches."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import xml.etree.ElementTree as ET

REPOSITORY = Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location('coach_scene_paths', REPOSITORY / 'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py')
policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(policy)
C1 = 'creators/creator-1/'
C2 = 'creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/'
WRAPPER_SOURCE = C1 + '11-integration/01-ui-contracts/src/scripts/vscripts/coach_scene_game_mode.lua'
MANUAL_SOURCE = C2 + 'layout/custom_game/manual_move.xml'
ROSTER_SOURCE = 'creators/creator-2/11-integration/01-ui-binding/src/panorama/scripts/custom_game/server_roster_panel.js'
INPUTS = {
    C1+'04-intervention/01-manual-actions/src/scripts/vscripts/manual_move_controller.lua':'game/scripts/vscripts/manual_move_controller.lua',
    C1+'04-intervention/01-manual-actions/src/scripts/vscripts/manual_move_game_mode.lua':'game/scripts/vscripts/manual_move_game_mode.lua',
    WRAPPER_SOURCE:'game/scripts/vscripts/addon_game_mode.lua',
    **{C1+part+'/src/scripts/vscripts/'+name+'.lua':'game/scripts/vscripts/'+name+'.lua' for part,name in (
        ('07-coach-preparation/01-roster-roles','roster_confirmation'),('03-ai-baseline/01-observation','observation'),
        ('03-ai-baseline/02-synthetic-policy','synthetic_policy'),('03-ai-baseline/03-order-arbiter','order_arbiter'),
        ('02-runtime/03-time-events','event_log'))},
    **{C2+name:'content/panorama/'+name for name in ('scripts/custom_game/manual_move_state.js','scripts/custom_game/manual_move_panel.js','layout/custom_game/manual_move.xml','styles/custom_game/manual_move.css')},
    ROSTER_SOURCE:'content/panorama/scripts/custom_game/server_roster_panel.js',
}
FIXTURE_LUA = C1+'02-runtime/03-time-events/tests/01-native-lifecycle/coach_scene_fixture.lua'
FIXTURE_JS = 'creators/creator-2/11-integration/03-end-to-end/tests/01-native-coach-scene/fixture.js'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'
MANUAL_LAYOUT = 'content/panorama/layout/custom_game/manual_move.xml'
SCENE_LAYOUT = 'content/panorama/layout/custom_game/coach_scene.xml'
FIXTURE_LAYOUT = 'content/panorama/layout/custom_game/coach_scene_fixture.xml'
RESOURCE = 'file://{resources}/'
SCRIPT_LINKS = [RESOURCE+'scripts/custom_game/'+n for n in ('manual_move_state.js','manual_move_panel.js','server_roster_panel.js')]
MANUAL_IDS = {'MoveRoot':'Panel','MoveCard':'Button','MoveCardText':'Label','MoveAcquire':'Button','MoveCancel':'Button','MoveSync':'Button',**{'Move'+n:'Label' for n in ('Status','Mode','Result','History')}}

def parse_layout(raw, scripts):
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper(): raise ValueError('DTD/entities refused')
    tree=ET.fromstring(raw)
    if tree.tag!='root' or tree.attrib or [n.tag for n in tree]!=['styles','scripts','Panel']:raise ValueError('Invalid scene root')
    for section,links in (('styles',[RESOURCE+'styles/custom_game/manual_move.css']),('scripts',scripts)):
        nodes=list(tree.find(section))
        if tree.find(section).attrib or len(nodes)!=len(links) or any(n.tag!='include' or n.attrib!={'src':link} or len(n) for n,link in zip(nodes,links)):raise ValueError('Unexpected scene dependency')
    ids={}
    for node in tree.iter():
        if (node.text or '').strip() or (node.tail or '').strip():raise ValueError('Mixed/executable text refused')
        if any(k.lower().startswith('on') for k in node.attrib):raise ValueError('Inline handler refused')
        if node.tag not in ('root','styles','scripts','include','Panel','Button','Label'):raise ValueError('Unexpected scene tag')
        if node.tag in ('Panel','Button','Label') and set(node.attrib)-{'id','class','hittest','hittestchildren','text','style','html','enabled'}:raise ValueError('Unexpected scene attribute')
        if node.tag not in ('include',) and any(k in node.attrib for k in ('src','layoutfile')):raise ValueError('Nested resource refused')
        if node.tag=='Label' and (len(node) or node.get('html','false')!='false'):raise ValueError('Plain leaf labels required')
        if 'id' in node.attrib:
            identity=node.attrib['id']
            if identity in ids:raise ValueError('Duplicate scene id')
            ids[identity]=node.tag
    canvas=tree.find('Panel')
    if canvas.attrib!={'hittest':'false','class':'MoveCanvas'}:raise ValueError('Anonymous MoveCanvas required')
    return tree,ids

def compose(raw, fixture=False):
    tree,ids=parse_layout(raw,SCRIPT_LINKS[:2])
    canvas=tree.find('Panel')
    if ids!=MANUAL_IDS or len(canvas)!=1 or canvas[0].get('id')!='MoveRoot':raise ValueError('Canonical manual scope mismatch')
    ET.SubElement(tree.find('scripts'),'include',src=SCRIPT_LINKS[2])
    roster=ET.SubElement(canvas,'Panel',id='RosterServerRoot',hittest='true',style='position: 20px 80px 0px; width: 430px; height: fit-children; flow-children: down; background-color: #152833f0; padding: 10px;')
    label_style='font-size: 16px; color: #ffffff; width: 100%; height: fit-children; white-space: normal;'
    ET.SubElement(roster,'Label',id='RosterServerStatus',text='TEST — ожидается сервер',hittest='false',style=label_style)
    sync=ET.SubElement(roster,'Button',id='RosterServerSync',style='width: 100%; height: 38px; background-color: #2d4c62; padding: 8px; margin: 6px 0;')
    ET.SubElement(sync,'Label',text='Обновить серверный состав',hittest='false',style=label_style)
    for i in range(1,6):ET.SubElement(roster,'Label',id='RosterServer'+str(i),hittest='false',style=label_style)
    if fixture:ET.SubElement(tree.find('scripts'),'include',src=RESOURCE+'scripts/custom_game/coach_scene_fixture.js')
    result=ET.tostring(tree,encoding='utf-8',xml_declaration=False)+b'\n'
    _,derived_ids=parse_layout(result,SCRIPT_LINKS+([RESOURCE+'scripts/custom_game/coach_scene_fixture.js'] if fixture else []))
    if derived_ids!={**MANUAL_IDS,'RosterServerRoot':'Panel','RosterServerSync':'Button',**{'RosterServer'+n:'Label' for n in ('Status','1','2','3','4','5')}}:raise ValueError('Derived scope mismatch')
    return result

def prepare(repository, test_fixture=False):
    if type(test_fixture) is not bool:raise ValueError('Fixture selector must be boolean')
    root=Path(repository).resolve()
    mapping=dict(INPUTS)
    if test_fixture:
        mapping[WRAPPER_SOURCE]='game/scripts/vscripts/coach_scene_game_mode.lua'
        mapping[FIXTURE_LUA]='game/scripts/vscripts/addon_game_mode.lua'
        mapping[FIXTURE_JS]='content/panorama/scripts/custom_game/coach_scene_fixture.js'
    values=[(s,t,policy.read_source(root,s),False) for s,t in mapping.items()]
    canonical=next(b for s,t,b,d in values if s==MANUAL_SOURCE)
    values.append(('generated:coach-scene-layout',SCENE_LAYOUT,compose(canonical),True))
    if test_fixture:values.append(('generated:coach-scene-fixture-layout',FIXTURE_LAYOUT,compose(canonical,True),True))
    layout=FIXTURE_LAYOUT if test_fixture else SCENE_LAYOUT
    manifest=ET.Element('root'); panel=ET.SubElement(manifest,'Panel')
    ET.SubElement(panel,'CustomUIElement',type='Hud',layoutfile=RESOURCE+layout.removeprefix('content/panorama/'))
    values.append(('generated:coach-scene-manifest',MANIFEST,ET.tostring(manifest,encoding='utf-8')+b'\n',True))
    if len(values)!=(18 if test_fixture else 15) or len({t.casefold() for s,t,b,d in values})!=len(values):raise ValueError('Recipe collision/count mismatch')
    return values

def assets(values):
    return [dict(source=s,target=t,derived=d,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for s,t,b,d in values]

def source_inputs(values):
    return [dict(source=s,sha256=hashlib.sha256(b).hexdigest()) for s,t,b,d in values if not d]

def build_bundle(repository, output, test_fixture=False):
    root=Path(repository).resolve(); target=policy.output_path(root,Path(output)); values=prepare(root,test_fixture)
    target.parent.mkdir(parents=True,exist_ok=True); target.mkdir()
    for s,t,b,d in values:
        path=target/t;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(b)
    report=dict(schema_version=1,stage='coach_scene_native_test_fixture' if test_fixture else 'coach_scene_source_bundle',
                source2_compiled=False,runtime_verified=False,assets=assets(values),source_inputs=source_inputs(values),
                generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with (target/'bundle-report.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return report

def verify_bundle(repository, output):
    root=Path(repository).resolve();target=Path(os.path.abspath(output if Path(output).is_absolute() else root/output));boundary=root/'build/dota_coach'
    if not target.is_relative_to(boundary) or target==boundary:raise ValueError('Output outside child boundary')
    policy.check_ancestors(root,target)
    report=json.loads(policy.read_source(root,(target/'bundle-report.json').relative_to(root).as_posix()))
    if not isinstance(report,dict) or set(report)!={'schema_version','stage','source2_compiled','runtime_verified','assets','source_inputs','generated_at_utc'} or type(report.get('schema_version')) is not int or report['schema_version']!=1 or report.get('stage') not in ('coach_scene_source_bundle','coach_scene_native_test_fixture') or report.get('source2_compiled') is not False or report.get('runtime_verified') is not False or not isinstance(report.get('generated_at_utc'),str):raise ValueError('Receipt scope mismatch')
    values=prepare(root,report['stage']=='coach_scene_native_test_fixture')
    if report['assets']!=assets(values) or report['source_inputs']!=source_inputs(values):raise ValueError('Receipt/source mismatch')
    seen=set()
    for path in target.rglob('*'):
        policy.check_ancestors(root,path)
        if path.is_file():seen.add(path.relative_to(target).as_posix())
    if seen!={t for s,t,b,d in values}|{'bundle-report.json'}:raise ValueError('Unexpected/missing bundle files')
    for s,t,b,d in values:
        if policy.read_source(root,(target/t).relative_to(root).as_posix())!=b:raise ValueError('Bundle bytes changed')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=REPOSITORY);parser.add_argument('--output',type=Path);parser.add_argument('--verify',type=Path);parser.add_argument('--test-fixture',action='store_true');args=parser.parse_args()
    try:
        if args.verify:
            report=verify_bundle(args.repository,args.verify);print(json.dumps({'verified':True,'assets':len(report['assets'])}));return 0
        output=args.output or args.repository/'build/dota_coach'/('coach-scene-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3))
        report=build_bundle(args.repository,output,args.test_fixture);verify_bundle(args.repository,output)
        print(json.dumps({'output':str(output),'assets':len(report['assets'])}));return 0
    except (OSError,ValueError,ET.ParseError) as error:print('Coach scene bundle refused: '+str(error),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
