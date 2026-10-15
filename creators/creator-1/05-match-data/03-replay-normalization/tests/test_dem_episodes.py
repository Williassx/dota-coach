import dataclasses
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from dem_types import Limits, DemImportError
from dem_episodes import build_episodes


def state(seq,tick,life=0,epoch=1):
    return {'seq':seq,'demo_tick':tick,'binding_epoch':epoch,'clock_epoch':1,
            'clock':{'game_seconds':None},'raw_life_state':life,'raw_state64':'0',
            'knowledge_scope':'spectator_research'}


class EpisodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.out=Path(self.tmp.name)

    def test_overlap_and_duplicate_windows_no_duplicate_records(self):
        windows=[{'id':'A','start_demo_tick':2,'end_demo_tick':6},{'id':'B','start_demo_tick':4,'end_demo_tick':8}]
        result=build_episodes(iter([state(i,t) for i,t in enumerate([0,2,4,6,8])]),iter([]),iter([]),windows,self.out,Limits())
        records=[json.loads(s) for s in (self.out/'windows.jsonl').read_text().splitlines()]
        self.assertEqual(len(records),4);self.assertEqual(result.window_record_count,4)
        self.assertEqual(len(records),len({(r['stream'],r['seq']) for r in records}))
        self.assertEqual(records[1]['window_ids'],['A','B'])

    def test_unknown_clock_uses_demo_ticks(self):
        build_episodes(iter([state(0,100)]),iter([]),iter([]),[{'id':'unknown','start_demo_tick':100,'end_demo_tick':100}],self.out,Limits())
        r=json.loads((self.out/'windows.jsonl').read_text())
        self.assertIsNone(r['record']['clock']['game_seconds']);self.assertEqual(r['record']['demo_tick'],100)

    def test_death_gap_and_epoch_not_interpolated(self):
        states=[state(0,0),state(1,2,life=2),state(2,20,life=0,epoch=2)]
        gaps=[{'seq':0,'start_demo_tick':4,'end_demo_tick':18,'binding_epoch':1,'reason':'deleted'}]
        build_episodes(iter(states),iter([]),iter(gaps),[],self.out,Limits())
        entries=json.loads((self.out/'episodes.json').read_text())['entries']
        self.assertTrue(any(r['kind']=='gap_samples' for r in entries))
        self.assertTrue(any(r['kind']=='raw_state_change' and r['demo_tick']==2 for r in entries))
        self.assertFalse((self.out/'windows.jsonl').exists())
        self.assertNotIn('alive',json.dumps(entries))

    def test_candidate_event_not_promoted_to_action(self):
        events=[{'seq':0,'demo_tick':10,'type':'DOTA_COMBATLOG_MODIFIER_ADD','actor_link':'candidate_name_only','target':'TEST_Hero'}]
        build_episodes(iter([]),iter(events),iter([]),[],self.out,Limits())
        entries=json.loads((self.out/'episodes.json').read_text())['entries']
        self.assertEqual(entries[0]['actor_link'],'candidate_name_only')
        self.assertNotIn('observed_action',json.dumps(entries));self.assertNotIn('stunned',json.dumps(entries))

    def test_index_limit_aborts(self):
        with self.assertRaises(DemImportError) as caught:
            build_episodes(iter([state(0,0),state(1,1000,life=2)]),iter([]),iter([]),[],self.out,dataclasses.replace(Limits(),max_index_entries=1))
        self.assertEqual(caught.exception.code,6)

    def test_streaming_does_not_materialize_all_states(self):
        out=self.out
        class SinglePass:
            def __iter__(self):
                for i in range(10000):
                    if i==1000:
                        assert (out/'windows.jsonl').stat().st_size>0, 'input consumed eagerly before streaming write'
                    yield state(i,i*2)
            def __len__(self):raise AssertionError('no list(all states)')
        r=build_episodes(iter(SinglePass()),iter([]),iter([]),[{'id':'all','start_demo_tick':0,'end_demo_tick':20000}],self.out,Limits())
        self.assertLess(r.index_count,100)
        self.assertEqual(r.window_record_count,10000)


if __name__=='__main__':unittest.main()
