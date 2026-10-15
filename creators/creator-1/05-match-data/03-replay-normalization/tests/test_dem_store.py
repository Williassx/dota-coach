import dataclasses
import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import test_dem_inputs as fixtures
from dem_types import DemImportError
from dem_inputs import validate_inputs, BASE, sha256
from dem_store import run_import, verify_cache, promote_no_replace, validate_streams


STATE={'seq':0,'demo_tick':2,'server_tick':466,'binding_epoch':1,'clock_epoch':1,
       'actor':{'account32':70388657,'steam64':'76561198030654385','full_handle':100,'index':4,'serial':2,'class':'TEST_Hero','reference_path':'TEST'},
       'resources':{'hp':40,'max_hp':100,'mana':20.5,'max_mana':100.0},
       'clock':{'game_seconds':None,'start':0.0,'pause_start':0,'pause_total':0,'paused':False,'tick_interval_seconds':1/30},
       'phase_raw':5,'knowledge_scope':'spectator_research','unknown_reasons':['clock_unknown']}


class StoreTests(unittest.TestCase):
    def setUp(self):
        fixtures.InputTests.setUp(self)
        self.ctx=validate_inputs(self.spec)

    def command(self, mode):
        def build(ctx, stage):
            code='''import pathlib,json,sys,time,os
p=pathlib.Path(sys.argv[1]); mode=sys.argv[2]
state=json.loads(sys.argv[3])
if mode=='timeout':time.sleep(5)
if mode=='hold':time.sleep(0.4)
if mode=='environment':print(json.dumps({k:k in os.environ for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']}))
if mode=='stderr':sys.stderr.write('x'*2000000);sys.stderr.flush();time.sleep(2)
for name,data in [('states',[state]),('events',[]),('gaps',[])]:
 (p/(name+'.jsonl')).write_text(''.join(json.dumps(r)+'\\n' for r in data))
if mode=='truncated':(p/'states.jsonl').write_text('{')
if mode=='oversize':(p/'states.jsonl').write_text('x'*100000)
if mode!='noeof':
 (p/'emitter-summary.json').write_text(json.dumps({'eof':True,'match_id':'9042986015','account_id':70388657,'states':1,'events':0,'gaps':0,'real_ticks':1,'synthetic_ticks':1,'unassigned':0,'last_tick':2,'verified_actor_events':False}))
if mode=='tamper':pathlib.Path(sys.argv[4]).write_bytes(b'changed')
if mode=='nested':
 q=pathlib.Path(sys.argv[5])/'classes/com/google/gson';q.mkdir(parents=True);(q/'Gson.class').write_bytes(b'TEST_NESTED')
if mode=='nonzero':sys.exit(3)
'''
            return [sys.executable,'-c',code,str(stage),mode,json.dumps(STATE),str(self.dem),str(self.root/'runtime')]
        return build

    def invoke(self, mode='ok'):
        with patch('dem_store.prepare_runtime'),patch('dem_store.emitter_command',self.command(mode)):
            return run_import(self.ctx)

    def test_cache_tamper_refused(self):
        result=self.invoke();self.assertEqual(result.status,'imported')
        self.assertEqual(verify_cache(self.spec.output,self.ctx).status,'cache_hit')
        with patch('dem_store.prepare_runtime'),patch('dem_store.emitter_command',side_effect=AssertionError('cache launched child')):
            self.assertEqual(run_import(self.ctx).status,'cache_hit')
        (self.spec.output/'states.jsonl').write_text('{}')
        with self.assertRaises(DemImportError):verify_cache(self.spec.output,self.ctx)

    def test_eof_and_exit_both_required_and_no_completed_output(self):
        for mode in ['noeof','nonzero','truncated','oversize']:
            with self.subTest(mode=mode):
                with self.assertRaises(DemImportError): self.invoke(mode)
                self.assertFalse(self.spec.output.exists())

    def test_timeout_stderr_and_output_limits(self):
        self.ctx.limits=dataclasses.replace(self.ctx.limits,timeout_seconds=1,max_stderr_bytes=1000)
        for mode in ['timeout','stderr']:
            with self.assertRaises(DemImportError) as caught:self.invoke(mode)
            self.assertEqual(caught.exception.code,6)
            self.assertFalse(self.spec.output.exists())

    def test_receipt_and_diagnostics_in_output_budget(self):
        self.ctx.limits=dataclasses.replace(self.ctx.limits,max_output_bytes=2500)
        with self.assertRaises(DemImportError) as caught:self.invoke()
        self.assertEqual(caught.exception.code,6)
        self.assertFalse(self.spec.output.exists())

    def test_failed_stage_cannot_be_reused_as_completed_cache(self):
        self.ctx.limits=dataclasses.replace(self.ctx.limits,max_output_bytes=2500)
        with self.assertRaises(DemImportError):self.invoke()
        failed=next(self.root.glob('.out.failed-*'))
        self.assertFalse((failed/'receipt.json').exists())
        with self.assertRaises(DemImportError):verify_cache(failed,self.ctx)

    def test_publication_failure_removes_completed_receipt(self):
        with patch('dem_store.promote_no_replace',side_effect=DemImportError(5,'TEST_publication_failure')):
            with self.assertRaises(DemImportError):self.invoke()
        failed=next(self.root.glob('.out.failed-*'))
        self.assertFalse((failed/'receipt.json').exists())
        self.assertFalse(self.spec.output.exists())
        with self.assertRaises(DemImportError):verify_cache(failed,self.ctx)

    def test_cache_enforces_current_byte_budget(self):
        self.invoke();self.ctx.limits=dataclasses.replace(self.ctx.limits,max_output_bytes=1)
        with self.assertRaises(DemImportError) as caught:verify_cache(self.spec.output,self.ctx)
        self.assertEqual(caught.exception.code,6)

    def test_cache_receipt_counts_and_provenance_checked(self):
        self.invoke();p=self.spec.output/'receipt.json';r=json.loads(p.read_text());r['counts']['states']=999
        p.write_text(json.dumps(r))
        with self.assertRaises(DemImportError):verify_cache(self.spec.output,self.ctx)

    def test_cache_inconsistent_eof_summary_rejected(self):
        self.invoke();p=self.spec.output/'receipt.json';r=json.loads(p.read_text());r['parser_summary']['eof']=False
        p.write_text(json.dumps(r))
        with self.assertRaises(DemImportError):verify_cache(self.spec.output,self.ctx)

    def test_changed_input_rejected_before_publish(self):
        with self.assertRaises(DemImportError):self.invoke('tamper')
        self.assertFalse(self.spec.output.exists())

    def test_two_writers_and_external_empty_destination_preserved(self):
        lock=self.spec.output.parent/('.'+self.spec.output.name+'.lock')
        lock.write_text('other-owner')
        with self.assertRaises(DemImportError):self.invoke()
        self.assertEqual(lock.read_text(),'other-owner')
        lock.unlink()
        staging=self.root/'staging';staging.mkdir();self.spec.output.mkdir()
        with self.assertRaises(DemImportError):promote_no_replace(staging,self.spec.output)
        self.assertTrue(staging.exists());self.assertEqual(list(self.spec.output.iterdir()),[])

    def test_two_concurrent_imports_only_one_writer(self):
        results=[];errors=[]
        def writer():
            try:results.append(run_import(self.ctx))
            except Exception as e:errors.append(e)
        with patch('dem_store.prepare_runtime'),patch('dem_store.emitter_command',self.command('hold')):
            t=threading.Thread(target=writer);t.start()
            deadline=time.monotonic()+3
            lock=self.spec.output.parent/('.'+self.spec.output.name+'.lock')
            while not lock.exists() and time.monotonic()<deadline:time.sleep(.01)
            with self.assertRaises(DemImportError):run_import(self.ctx)
            t.join(timeout=5)
        self.assertFalse(t.is_alive());self.assertFalse(errors);self.assertEqual(len(results),1)
        self.assertTrue((self.spec.output/'receipt.json').exists())

    @unittest.skipUnless(os.name=='nt','Windows junction acceptance')
    def test_staging_escape_refuses_cleanup(self):
        import _winapi
        from dem_inputs import checked_path
        target=self.root/'target';target.mkdir();sentinel=target/'sentinel';sentinel.write_text('preserve')
        junction=self.root/'junction';_winapi.CreateJunction(str(target),str(junction))
        self.addCleanup(lambda: os.rmdir(junction) if junction.exists() else None)
        with self.assertRaises(DemImportError):checked_path(junction)
        self.assertEqual(sentinel.read_text(),'preserve')

    def test_wrong_actor_and_nonfinite_state_rejected(self):
        stage=self.root/'validate';stage.mkdir()
        for name in ['events','gaps']:(stage/(name+'.jsonl')).write_text('')
        for bad in [dict(STATE,actor=dict(STATE['actor'],account32=1)),dict(STATE,resources={'hp':float('nan')})]:
            (stage/'states.jsonl').write_text(json.dumps(bad)+'\n')
            with self.assertRaises(DemImportError):validate_streams(stage,self.ctx)

    def test_native_calibration_scoped_to_input_actor_and_fields(self):
        from dem_store import calibration_reference
        self.assertEqual(calibration_reference(self.ctx)['status'],'unverified')
        self.ctx.hashes['input']='3d647fb889e058534e85a759e405b9afad6a68878cfa20dae016c39c38234330'
        ref=calibration_reference(self.ctx)
        self.assertEqual(len(ref['points']),3)
        stage=self.root/'calibration';stage.mkdir()
        for name in ['events','gaps']:(stage/(name+'.jsonl')).write_text('')
        row=dict(STATE,demo_tick=21212)
        (stage/'states.jsonl').write_text(json.dumps(row)+'\n')
        with self.assertRaises(DemImportError):validate_streams(stage,self.ctx)

    def test_java_environment_injection_not_inherited(self):
        keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']
        with patch.dict(os.environ,{k:'TEST_DO_NOT_PROPAGATE' for k in keys}):self.invoke('environment')
        diagnostics=next(self.root.glob('.out.diagnostics-*'))
        flags=json.loads((diagnostics/'stdout.log').read_text())
        self.assertEqual(flags,{k:False for k in keys})

    def runtime_fixture(self):
        runtime=self.root/'runtime';classes=runtime/'classes';classes.mkdir(parents=True)
        (classes/'TelemetryEmitter.class').write_bytes(b'TEST_COMPILED')
        receipt={'schema':'dem-compile-v1','lock_sha256':self.ctx.hashes['lock'],
                 'sources':{p.name:sha256(p) for p in (BASE/'src').glob('*.java')},
                 'classes':{'TelemetryEmitter.class':sha256(classes/'TelemetryEmitter.class')}}
        (runtime/'compile-receipt.json').write_text(json.dumps(receipt))
        return runtime

    def test_nested_classpath_shadow_rejected(self):
        from dem_store import prepare_runtime
        runtime=self.runtime_fixture();p=runtime/'classes/com/google/gson';p.mkdir(parents=True);(p/'Gson.class').write_bytes(b'TEST_SHADOW')
        with patch('dem_store.BUILD',runtime):
            with self.assertRaises(DemImportError):prepare_runtime(self.ctx)

    def test_classpath_membership_rechecked_before_publication(self):
        runtime=self.runtime_fixture()
        with patch('dem_store.BUILD',runtime),patch('dem_store.emitter_command',self.command('nested')):
            with self.assertRaises(DemImportError):run_import(self.ctx)
        self.assertFalse(self.spec.output.exists())

    def test_full_required_state_clock_dto_rejected_before_publish(self):
        changes=[{'server_tick':'invalid'},{'binding_epoch':-1},{'clock_epoch':False},{'phase_raw':None},
                 {'clock':dict(STATE['clock'],start='invalid')},{'clock':dict(STATE['clock'],paused='invalid')},
                 {'clock':dict(STATE['clock'],pause_total=-99)},{'clock':dict(STATE['clock'],game_seconds=99)},
                 {'clock':dict(STATE['clock'],tick_interval_seconds=0)},{'clock':{'game_seconds':None}}]
        original=dict(STATE)
        for i,change in enumerate(changes):
            with self.subTest(change=change):
                self.ctx.spec=dataclasses.replace(self.ctx.spec,output=self.root/f'bad-clock-{i}')
                with patch.dict(STATE,dict(original,**change),clear=True):
                    with self.assertRaises(DemImportError):self.invoke()
                self.assertFalse(self.ctx.spec.output.exists())

    def test_epoch_regression_rejected(self):
        stage=self.root/'epochs';stage.mkdir()
        for name in ['events','gaps']:(stage/(name+'.jsonl')).write_text('')
        rows=[STATE,dict(STATE,seq=1,demo_tick=3,server_tick=467,binding_epoch=0,clock_epoch=0)]
        (stage/'states.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        with self.assertRaises(DemImportError):validate_streams(stage,self.ctx)


if __name__=='__main__':unittest.main()
