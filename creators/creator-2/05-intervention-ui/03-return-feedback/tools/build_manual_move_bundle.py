"""Exact isolated manual-move source bundle, no native activation on import."""
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

REPOSITORY=Path(__file__).resolve().parents[5]
_spec=importlib.util.spec_from_file_location('manual_move_paths',REPOSITORY/'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py')
policy=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(policy)
C1='creators/creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/'
C2='creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/'
INPUTS={C1+'manual_move_controller.lua':'game/scripts/vscripts/manual_move_controller.lua',C1+'manual_move_game_mode.lua':'game/scripts/vscripts/addon_game_mode.lua',
        **{C2+name:'content/panorama/'+name for name in ('scripts/custom_game/manual_move_state.js','scripts/custom_game/manual_move_panel.js','layout/custom_game/manual_move.xml','styles/custom_game/manual_move.css')}}
MANIFEST='content/panorama/layout/custom_game/custom_ui_manifest.xml'
MANIFEST_BYTES=b'<root><Panel><CustomUIElement type="Hud" layoutfile="file://{resources}/layout/custom_game/manual_move.xml" /></Panel></root>\n'

def graph(raw):
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('DTD/entities refused')
    tree=ET.fromstring(raw)
    expected={'styles':['styles/custom_game/manual_move.css'],'scripts':['scripts/custom_game/manual_move_state.js','scripts/custom_game/manual_move_panel.js']}
    if tree.tag!='root' or tree.attrib or [n.tag for n in tree]!=['styles','scripts','Panel']:raise ValueError('Invalid root layout')
    for tag,names in expected.items():
        nodes=list(tree.find(tag))
        if len(nodes)!=len(names) or any(n.tag!='include' or n.attrib!={'src':'file://{resources}/'+name} or len(n) for n,name in zip(nodes,names)):raise ValueError('Unexpected dependency')
    ids=[]
    for n in tree.iter():
        if (n.text or '').strip() or (n.tail or '').strip():raise ValueError('Mixed executable text refused')
        if any(k.startswith('on') for k in n.attrib):raise ValueError('Inline handler refused')
        if 'id' in n.attrib:
            if n.attrib['id'] in ids:raise ValueError('Duplicate id')
            ids.append(n.attrib['id'])

def prepare(repository):
    root=Path(repository).resolve()
    values=[(s,t,policy.read_source(root,s),False) for s,t in INPUTS.items()]
    graph(next(b for s,t,b,d in values if s.endswith('.xml')))
    return values+[('generated:manual-move-manifest',MANIFEST,MANIFEST_BYTES,True)]

def build_bundle(repository,output):
    root=Path(repository).resolve();target=policy.output_path(root,Path(output));values=prepare(root)
    target.parent.mkdir(parents=True,exist_ok=True);target.mkdir()
    assets=[]
    for source,name,raw,derived in values:
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:f.write(raw)
        assets.append(dict(source=source,target=name,derived=derived,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    report={'schema_version':1,'stage':'manual_move_source_bundle','source2_compiled':False,'runtime_verified':False,'assets':assets,
            'source_inputs':[{'source':s,'sha256':hashlib.sha256(b).hexdigest()} for s,t,b,d in values if not d],
            'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with (target/'bundle-report.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return report

def verify_bundle(output,repository=REPOSITORY):
    root=Path(repository).resolve();target=Path(os.path.abspath(output if Path(output).is_absolute() else root/output));boundary=root/'build/dota_coach'
    if not target.is_relative_to(boundary) or target==boundary:raise ValueError('Output outside child boundary')
    policy.check_ancestors(root,target)
    raw=policy.read_source(root,(target/'bundle-report.json').relative_to(root).as_posix())
    report=json.loads(raw)
    if (set(report)!=set(('schema_version','stage','source2_compiled','runtime_verified','assets','source_inputs','generated_at_utc')) or type(report.get('schema_version')) is not int or report.get('schema_version')!=1 or report.get('stage')!='manual_move_source_bundle' or report.get('source2_compiled') is not False or report.get('runtime_verified') is not False):raise ValueError('Receipt scope mismatch')
    values=prepare(root)
    expected=[dict(source=s,target=t,derived=d,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for s,t,b,d in values]
    if report.get('assets')!=expected or report.get('source_inputs')!=[{'source':s,'sha256':hashlib.sha256(b).hexdigest()} for s,t,b,d in values if not d]:raise ValueError('Receipt/source mismatch')
    seen=set()
    for p in target.rglob('*'):
        policy.check_ancestors(root,p)
        if p.is_file():seen.add(p.relative_to(target).as_posix())
    if seen!={t for s,t,b,d in values}|{'bundle-report.json'}:raise ValueError('Unexpected/missing bundle files')
    for s,t,b,d in values:
        copied=policy.read_source(root,(target/t).relative_to(root).as_posix())
        if copied!=b:raise ValueError('Copied input changed')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=REPOSITORY);p.add_argument('--output',type=Path);p.add_argument('--verify',type=Path);a=p.parse_args()
    try:
        if a.verify:result=verify_bundle(a.verify,a.repository);print(json.dumps({'verified':True,'assets':len(result['assets'])}));return 0
        output=a.output or a.repository/'build/dota_coach'/('manual-move-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3))
        result=build_bundle(a.repository,output);verify_bundle(output,a.repository);print(json.dumps({'output':str(output),'assets':len(result['assets'])}));return 0
    except (OSError,ValueError,ET.ParseError) as e:print('Manual move bundle refused: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
