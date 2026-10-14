import importlib.util
import tempfile
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/'tools/autonomous_progress.py'
class AutonomousProgressTests(unittest.TestCase):
 def load(self):
  self.assertTrue(PATH.exists(),'actual read-only progress checker missing')
  spec=importlib.util.spec_from_file_location('autonomous_progress_test',PATH);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def fixture(self,root,done=False,old=False):
  p=root/'creators/creator-1/01-test/01-example/README.md';p.parent.mkdir(parents=True);p.write_text('- ['+('x' if done else ' ')+'] Implement guarded action.\n',encoding='utf-8')
  return {'schema_version':1,'creators':[{'creator':1,'baseline_done':int(old),'total':1,'required_new':1,'target_done':int(old)+1,'tasks':[{'path':p.relative_to(root).as_posix(),'actions':[{'index':1,'done':old,'text':'Implement guarded action.','key':'old'}]}]}]}
 def proof(self,root,reviewer=2):
  report=root/'creators/creator-2/01-review/report.md';report.parent.mkdir(parents=True);report.write_text('Independent technical review of actual source; PASS; native open.',encoding='utf-8')
  return [{'task':'creators/creator-1/01-test/01-example/README.md','actions':[1],'author_creator':1,'reviewer_creator':reviewer,'report':report.relative_to(root).as_posix(),'scope':'source','proofs':[report.relative_to(root).as_posix()]}]
 def test_new_done_requires_evidence(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);r=m.report_delta(root,b,[]);self.assertFalse(r['verified']);self.assertIn('missing_evidence',str(r['errors']))
 def test_old_done_is_never_new(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True,True);r=m.report_delta(root,b,[]);self.assertEqual(r['creators'][0]['new'],0);self.assertFalse(r['target_achieved'])
 def test_verified_new_action_reaches_target(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);r=m.report_delta(root,b,self.proof(root));self.assertTrue(r['verified']);self.assertTrue(r['target_achieved']);self.assertEqual(r['creators'][0]['new'],1)
 def test_reopened_done_reduces_net_delta(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,False,True);r=m.report_delta(root,b,[]);self.assertEqual(r['creators'][0]['reopened'],1);self.assertEqual(r['creators'][0]['net_new'],-1)
 def test_same_creator_cannot_review_own_action(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);r=m.report_delta(root,b,self.proof(root,1));self.assertFalse(r['verified']);self.assertIn('independent_creator_review',str(r['errors']))
 def test_missing_report_and_changed_denominator_rejected(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);p=self.proof(root);(root/p[0]['report']).unlink();r=m.report_delta(root,b,p);self.assertFalse(r['verified']);self.assertIn('evidence_path',str(r['errors']))
   (root/b['creators'][0]['tasks'][0]['path']).write_text('- [x] Implement guarded action.\n- [x] Sneak in a new action.\n',encoding='utf-8');r=m.report_delta(root,b,[]);self.assertFalse(r['verified']);self.assertIn('action_count_changed',str(r['errors']))
 def test_evidence_outside_repo_rejected(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);p=self.proof(root);p[0]['report']='../outside.md';r=m.report_delta(root,b,p);self.assertFalse(r['verified'])
 def test_short_original_action_accepts_appended_evidence_but_not_changed_words(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);b=self.fixture(root,True);p=root/b['creators'][0]['tasks'][0]['path'];proof=self.proof(root)
   p.write_text('- [x] Implement guarded action. Evidence independently reviewed.\n',encoding='utf-8')
   self.assertTrue(m.report_delta(root,b,proof)['verified'])
   p.write_text('- [x] Implement unguarded action. Evidence independently reviewed.\n',encoding='utf-8')
   self.assertIn('action_meaning_changed',str(m.report_delta(root,b,proof)['errors']))
if __name__=='__main__':unittest.main()
