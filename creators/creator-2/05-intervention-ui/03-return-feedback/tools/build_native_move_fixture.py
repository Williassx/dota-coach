"""Generate a separate TEST composition; normal seven-source kind unchanged."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('native_move_bundle',Path(__file__).with_name('build_manual_move_bundle.py'))
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
TEST='creators/creator-2/05-intervention-ui/03-return-feedback/tests/native-move/manual_move_fixture.js'
DRIVER='content/panorama/scripts/custom_game/manual_move_fixture.js'
LAYOUT='content/panorama/layout/custom_game/manual_move.xml'
DERIVED='content/panorama/layout/custom_game/manual_move_fixture.xml'

def prepare_fixture(root):
 values=bundle.prepare(root)
 if len(values)!=7:raise ValueError('Fixture requires exact normal seven-source recipe')
 raw=next(b for s,t,b,d in values if t==LAYOUT);tree=ET.fromstring(raw)
 ET.SubElement(tree.find('scripts'),'include',{'src':'file://{resources}/scripts/custom_game/manual_move_fixture.js'})
 ET.SubElement(tree.find('Panel'),'Label',{'id':'MoveFixtureStatus','text':'TEST programmatic only','hittest':'false','style':'horizontal-align: left; vertical-align: top; margin: 25px; font-size: 21px; color: #ffffff; background-color: #18212bf0;'})
 values=[(s,t,(b.replace(b'manual_move.xml',b'manual_move_fixture.xml') if t==bundle.MANIFEST else b),d) for s,t,b,d in values]
 values += [(TEST,DRIVER,bundle.policy.read_source(root,TEST),False),('derived:manual-move-test',DERIVED,ET.tostring(tree,encoding='utf-8')+b'\n',True)]
 if len({t.casefold() for s,t,b,d in values})!=9:raise ValueError('Fixture outputs must be unique')
 return values

def build_fixture(repository,output):
 root=Path(repository).resolve();target=bundle.policy.output_path(root,Path(output));values=prepare_fixture(root)
 target.parent.mkdir(parents=True,exist_ok=True);target.mkdir();assets=[]
 for s,t,b,d in values:
  p=target/t;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(b)
  assets.append(dict(source=s,target=t,derived=d,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 report={'schema_version':1,'stage':'manual_move_native_test_fixture','assets':assets,'source2_compiled':False,'runtime_verified':False}
 with (target/'bundle-report.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
 return report
def verify_fixture(repository,output):
 root=Path(repository).resolve();target=Path(os.path.abspath(output if Path(output).is_absolute() else root/output));boundary=root/'build/dota_coach'
 if not target.is_relative_to(boundary) or target==boundary:raise ValueError('Outside build child')
 bundle.policy.check_ancestors(root,target)
 report=json.loads(bundle.policy.read_source(root,(target/'bundle-report.json').relative_to(root).as_posix()))
 if set(report)!=set(('schema_version','stage','assets','source2_compiled','runtime_verified')) or type(report['schema_version']) is not int or report['schema_version']!=1 or report['stage']!='manual_move_native_test_fixture' or report['source2_compiled'] is not False or report['runtime_verified'] is not False:raise ValueError('Wrong fixture receipt')
 values=prepare_fixture(root)
 expected=[dict(source=s,target=t,derived=d,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for s,t,b,d in values]
 if report['assets']!=expected:raise ValueError('Fixture source/receipt mismatch')
 seen=set()
 for p in target.rglob('*'):
  bundle.policy.check_ancestors(root,p)
  if p.is_file():seen.add(p.relative_to(target).as_posix())
 if seen!={t for s,t,b,d in values}|{'bundle-report.json'}:raise ValueError('Unexpected files')
 for s,t,b,d in values:
  if bundle.policy.read_source(root,(target/t).relative_to(root).as_posix())!=b:raise ValueError('Changed fixture output')
 return report
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=bundle.REPOSITORY);p.add_argument('--output',type=Path);p.add_argument('--verify',type=Path);a=p.parse_args()
 if a.verify:verify_fixture(a.repository,a.verify);print('verified fixture9');return
 output=a.output or a.repository/'build/dota_coach'/('native-move-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3))
 r=build_fixture(a.repository,output);verify_fixture(a.repository,output);print(json.dumps({'output':str(output),'assets':len(r['assets'])}))
if __name__=='__main__':main()
