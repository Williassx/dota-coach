"""Read-only evidence-backed delta against a frozen creator checklist baseline."""
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
BASELINE=ROOT/'creators/creator-2/01-foundation/01-workspace-audit/notes/autonomous-30pp-baseline-2026-10-13.json'
EVIDENCE=BASELINE.with_name('autonomous-30pp-evidence-2026-10-13.json')

def local_file(root,name):
 if type(name) is not str or not name or Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('evidence_path')
 raw=root/name
 for p in (raw,*raw.parents):
  if p==root:break
  if p.is_symlink() or (p.exists() and getattr(p.stat(),'st_file_attributes',0)&0x400):raise ValueError('evidence_path')
 resolved=raw.resolve()
 if not resolved.is_relative_to(root) or not resolved.is_file():raise ValueError('evidence_path')
 return resolved

def report_delta(repository,baseline,evidence):
 root=Path(repository).resolve();errors=[];out=[];records={}
 if type(baseline) is not dict or baseline.get('schema_version')!=1 or type(baseline.get('creators')) is not list:raise ValueError('invalid_baseline')
 if type(evidence) is not list:raise ValueError('invalid_evidence')
 for proof in evidence:
  try:
   if type(proof) is not dict or type(proof.get('actions')) is not list or not proof['actions']:raise ValueError('invalid_evidence')
   author=proof.get('author_creator');reviewer=proof.get('reviewer_creator')
   if type(author) is not int or author not in (1,2) or type(reviewer) is not int or reviewer!=3-author:raise ValueError('independent_creator_review')
   if proof.get('scope') not in ('source','native','documentary','mixed'):raise ValueError('invalid_scope')
   if not proof.get('task','').startswith(f'creators/creator-{author}/'):raise ValueError('author_scope')
   local_file(root,proof['report'])
   if type(proof.get('proofs')) is not list or not proof['proofs']:raise ValueError('missing_proofs')
   for name in proof['proofs']:local_file(root,name)
   for index in proof['actions']:
    if type(index) is not int or index<1:raise ValueError('invalid_action_index')
    key=(proof['task'],index)
    if key in records:raise ValueError('duplicate_evidence')
    records[key]=proof
  except (KeyError,ValueError,OSError) as exc:errors.append({'code':str(exc),'task':proof.get('task') if type(proof) is dict else None})
 for creator in baseline['creators']:
  done=new=reopened=total=0;new_actions=[];next_actions=[]
  for task in creator['tasks']:
   try:
    text=local_file(root,task['path']).read_text(encoding='utf-8');actions=re.findall(r'^- \[([ xX])\] (.+)$',text,re.M)
    if len(actions)!=len(task['actions']):raise ValueError('action_count_changed')
    for before,(flag,label) in zip(task['actions'],actions):
     index=before['index'];after=flag.lower()=='x';done+=after;total+=1
     meaning_prefix=before['text'].split()[:6]
     if label.split()[:len(meaning_prefix)]!=meaning_prefix:errors.append({'code':'action_meaning_changed','task':task['path'],'action':index})
     if before['done'] and not after:reopened+=1
     if not before['done'] and after:
      new+=1;new_actions.append({'task':task['path'],'action':index,'label':label})
      if (task['path'],index) not in records:errors.append({'code':'missing_evidence','task':task['path'],'action':index})
     if not after:next_actions.append({'task':task['path'],'action':index,'label':label})
   except (ValueError,OSError,KeyError) as exc:errors.append({'code':str(exc),'task':task.get('path')})
  net=new-reopened;target=net>=creator['required_new'] and done>=creator['target_done']
  if total!=creator['total']:errors.append({'code':'creator_total_changed','creator':creator['creator']})
  out.append({'creator':creator['creator'],'baseline_done':creator['baseline_done'],'done':done,'total':total,'new':new,'reopened':reopened,'net_new':net,'required_new':creator['required_new'],'target_done':creator['target_done'],'target_achieved':target,'new_actions':new_actions,'remaining_actions':next_actions})
 return {'schema_version':1,'verified':not errors,'target_achieved':bool(out) and not errors and all(c['target_achieved'] for c in out),'creators':out,'errors':errors,'claim_scope':'checklist_delta_and_evidence_presence_not_game_readiness'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--baseline',type=Path,default=BASELINE);p.add_argument('--evidence',type=Path,default=EVIDENCE);p.add_argument('--require-target',action='store_true');p.add_argument('--full',action='store_true');a=p.parse_args()
 try:
  baseline=json.loads(a.baseline.read_text(encoding='utf-8'));evidence=json.loads(a.evidence.read_text(encoding='utf-8')) if a.evidence.exists() else [];r=report_delta(a.repository,baseline,evidence)
  if a.full:print(json.dumps(r,ensure_ascii=False,indent=2))
  else:print(json.dumps({**{k:r[k] for k in ('verified','target_achieved','errors')},'creators':[{k:c[k] for k in ('creator','done','total','new','reopened','net_new','required_new','target_achieved')} for c in r['creators']]},ensure_ascii=False))
  return 0 if r['verified'] and (not a.require_target or r['target_achieved']) else 1
 except (ValueError,OSError) as exc:p.exit(2,str(exc)+'\n')
if __name__=='__main__':raise SystemExit(main())
