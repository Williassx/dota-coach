"""Opt-in real DEM acceptance. Local files only, no Dota/network launch."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
DEM_SHA='3d647fb889e058534e85a759e405b9afad6a68878cfa20dae016c39c38234330'

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1048576),b''):h.update(c)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['dem','lock','config','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    assert digest(a.dem)==DEM_SHA,'wrong golden DEM'
    a.output.mkdir(exist_ok=False)
    runs=[]
    def run(name,output,extra=(),input_path=None,expected=0):
        cmd=[sys.executable,str(BASE/'src/import_dem.py'),'--input',str(input_path or a.dem),
             '--match-id','9042986015','--account-id','70388657','--lock',str(a.lock),'--config',str(a.config),'--output',str(output)]
        for key,value in extra:
            cmd[cmd.index(key)+1]=str(value)
        start=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=360)
        record={'name':name,'code':r.returncode,'seconds':time.monotonic()-start,'stdout':r.stdout.decode('utf-8'),'stderr':r.stderr.decode('utf-8')}
        (a.output/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        assert r.returncode==expected,record
        result=json.loads(r.stdout)
        assert result['completed']==(expected==0),record
        runs.append(record);print(json.dumps({'name':name,'code':r.returncode,'seconds':round(record['seconds'],3)}),flush=True)
        return result
    first=run('first',a.output/'first')
    second=run('second',a.output/'second')
    assert first['data_hashes']==second['data_hashes'],'nondeterministic output'
    before={p.name:digest(p) for p in (a.output/'first').iterdir()}
    hit=run('cache',a.output/'first');assert hit['status']=='cache_hit'
    assert before=={p.name:digest(p) for p in (a.output/'first').iterdir()},'cache rewrote output'
    run('wrong-match',a.output/'bad-match',[('--match-id',1)],expected=3)
    run('wrong-account',a.output/'bad-account',[('--account-id',1)],expected=3)
    broken=a.output/'truncated.dem'
    with a.dem.open('rb') as f:broken.write_bytes(f.read(1024))
    truncated=run('truncated',a.output/'bad-truncated',input_path=broken,expected=2)
    assert not (a.output/'bad-truncated').exists()
    receipt=json.loads((a.output/'first/receipt.json').read_text(encoding='utf-8'))
    summary=receipt['parser_summary']
    assert (summary['real_ticks'],summary['states'],summary['synthetic_ticks'],summary['unassigned'])==(34051,32178,34050,1873)
    assert summary['events']==11341
    states={}
    with (a.output/'first/states.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            assert r['actor']['account32']==70388657 and r['actor']['full_handle']==14926170
            assert r['raw_player_id']==14
            if r['demo_tick'] in [21212,41706,45846]:states[r['demo_tick']]=r
    expected={21212:(71,956,62,651,492),41706:(1215,1308,734,1376,1175),45846:(782,1528,1335,1376,1313)}
    for tick,(hp,maxhp,mana,maxmana,clock) in expected.items():
        r=states[tick]
        for key,v in zip(['hp','max_hp','mana','max_mana'],[hp,maxhp,mana,maxmana]):assert abs(r['resources'][key]-v)<=1
        assert int(r['clock']['game_seconds'])==clock
    deaths=[]
    for line in (a.output/'first/events.jsonl').open(encoding='utf-8'):
        r=json.loads(line);assert r['actor_link']=='candidate_name_only'
        if r['type']=='DOTA_COMBATLOG_DEATH' and r['target']=='npc_dota_hero_storm_spirit' and not r['is_target_illusion']:deaths.append(r['demo_tick'])
    assert deaths==[21232,34406,41758,45886]
    result={'schema':'dem-golden-check-v1','verified_scoped':True,'dem_sha256':DEM_SHA,'data_hashes':first['data_hashes'],
            'counts':first['counts'],'parser_summary':summary,'calibration':receipt['calibration'],
            'episode_index':receipt['episode_index'],'run_seconds':{r['name']:r['seconds'] for r in runs},
            'same_fresh_data_hashes':True,'cache_preserved_all_bytes':True,'target_death_candidate_ticks':deaths,
            'model_trained':False,'player_fidelity_verified':False,'native_verified':False}
    (a.output/'golden-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('golden scoped checks PASS',flush=True)

if __name__=='__main__':main()
