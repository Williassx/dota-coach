"""Internal exact source/proof excerpt. No engine material, install or upload."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

REPO=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('review_coach_scene',REPO/'creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py')
scene=importlib.util.module_from_spec(spec);spec.loader.exec_module(scene)
REPORTS='creators/creator-2/11-integration/03-end-to-end/reports/'
DOCS=[
 'creators/creator-2/12-release/02-valve-presentation/notes/prototype-packet-2026-10-14.md',
 'creators/creator-2/12-release/03-release-guide/notes/prototype-local-guide-2026-10-14.md',
 'creators/creator-1/12-release/02-valve-demo/notes/rights-requests-2026-10-14.md',
 'creators/creator-1/12-release/03-release-package/reports/technical-packet-2026-10-14.md',
 'docs/legal/plan.md','docs/legal/initial-review.md',
 REPORTS+'native-coach-scene-2026-10-14.md',REPORTS+'native-coach-scene-2026-10-14.json',
 REPORTS+'native-coach-ui3-ready-2026-10-14.png',
 'creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py',
 'creators/creator-2/11-integration/02-addon-packaging/tests/test_coach_scene_bundle.py',
 'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py',
 'creators/creator-1/12-release/03-release-package/tools/build_review_packet.py',
]
PHASES=('ready','manual_moving','paused','expired_return','cancelled_return','arrived_return','dead','rebound','stale_rejected','reloaded')
def allowed():
 return sorted(set(scene.INPUTS)|{scene.FIXTURE_LUA,scene.FIXTURE_JS}|set(DOCS)|{REPORTS+'native-coach-r2-'+phase+'-2026-10-14.png' for phase in PHASES})
def prepare():
 # Validate both source graphs before archiving original inputs, never copied build outputs.
 scene.prepare(REPO);scene.prepare(REPO,True)
 result=[]
 for name in allowed():
  path=Path(name)
  if path.suffix.lower() not in ('.lua','.js','.xml','.css','.py','.md','.json','.png') or any(part.lower() in ('build','.freebuff','models','audio','maps','template','engine') for part in path.parts):raise ValueError('Forbidden member')
  if path.suffix.lower()=='.png':
   # Proof images have a separate bound; UI policy/default limit is unchanged.
   actual=REPO.joinpath(*scene.policy.portable_path(name).parts)
   scene.policy.check_ancestors(REPO,actual)
   if not actual.is_file():raise ValueError('Proof must be a regular file')
   with actual.open('rb') as stream:raw=stream.read(8*1024*1024+1)
   if len(raw)>8*1024*1024 or not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid/oversized PNG proof')
  else:raw=scene.policy.read_source(REPO,name)
  result.append((name,raw))
 return result
def verify(output):
 output=Path(output).absolute();boundary=REPO/'build/dota_coach'
 if not output.is_relative_to(boundary) or output==boundary:raise ValueError('Review output boundary')
 scene.policy.check_ancestors(REPO,output)
 report=json.loads(scene.policy.read_source(REPO,(output/'packet-manifest.json').relative_to(REPO).as_posix()))
 values=prepare();expected=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),purpose='native-proof' if n.startswith(REPORTS) else 'project-source-or-document',rights='not_assessed') for n,b in values]
 if report.get('members')!=expected or report.get('public_release') is not False or report.get('sent') is not False:raise ValueError('Manifest mismatch')
 archive=output/'review-packet.zip';scene.policy.check_ancestors(REPO,archive)
 if sorted(p.name for p in output.iterdir())!=['packet-manifest.json','review-packet.zip']:raise ValueError('Unexpected packet files')
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=report.get('archive_sha256'):raise ValueError('Archive hash mismatch')
 with zipfile.ZipFile(archive) as zipped:
  if zipped.namelist()!=[n for n,b in values] or zipped.testzip() is not None:raise ValueError('Archive membership/CRC mismatch')
  for name,raw in values:
   if zipped.read(name)!=raw:raise ValueError('Archived bytes mismatch')
 return report
def build(output):
 output=scene.policy.output_path(REPO,Path(output));values=prepare()
 output.parent.mkdir(parents=True,exist_ok=True);output.mkdir()
 archive=output/'review-packet.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as zipped:
  for name,raw in values:
   info=zipfile.ZipInfo(name,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;zipped.writestr(info,raw)
 report=dict(schema_version=1,scope='early limited internal prototype review excerpt',sent=False,public_release=False,
  engine_assets_included=False,rights='not_assessed',normal_source_outputs=15,test_source_outputs=18,
  archive=str(archive.relative_to(REPO)).replace('\\','/'),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),archive_bytes=archive.stat().st_size,
  members=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),purpose='native-proof' if n.startswith(REPORTS) else 'project-source-or-document',rights='not_assessed') for n,b in values])
 (output/'packet-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 verify(output);return report
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);parser.add_argument('--verify',type=Path);args=parser.parse_args()
 if bool(args.output)==bool(args.verify):parser.error('Choose --output or --verify')
 report=verify(args.verify) if args.verify else build(args.output)
 print(json.dumps(dict(verified=True,archive=report['archive'],members=len(report['members']),sha256=report['archive_sha256'])))
