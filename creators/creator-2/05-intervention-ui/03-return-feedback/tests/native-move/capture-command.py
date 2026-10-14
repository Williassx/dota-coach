"""Explicit owned native manual move captures; never ordinary import/test activation."""
import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='r1')
    parser.add_argument('--addon', choices=('dota_coach_c2_move_20261013','dota_coach_c2_move_r2_20261013','dota_coach_c2_move_r3_20261013','dota_coach_c2_move_r4_20261013','dota_coach_c2_move_r5_20261013','dota_coach_c2_move_r6_20261013','dota_coach_c2_move_r7_20261013','dota_coach_c2_move_final_20261013','dota_coach_c2_move_r8_20261013','dota_coach_c2_move_final2_20261013','dota_coach_scene_r1_20261014','dota_coach_scene_r2_20261014','dota_coach_scene_r3_20261014','dota_coach_scene_ui_20261014','dota_coach_scene_ui2_20261014'), default='dota_coach_c2_move_20261013')
    parser.add_argument('--scenario', choices=('manual','coach'), default='manual')
    parser.add_argument('--ready-only', action='store_true')
    parser.add_argument('--world-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9_-]{1,32}', args.run): raise ValueError('Invalid run')
    repo = Path(__file__).resolve().parents[6]
    evidence_date='20261014' if args.scenario=='coach' else '20261013'
    prefix = repo / ('build/dota_coach/native-move-' + args.run + '-'+evidence_date)
    console = Path(str(prefix) + '-console.log')
    reports = (repo/'creators/creator-2/11-integration/03-end-to-end/reports') if args.scenario=='coach' else Path(__file__).resolve().parents[2]/'reports'
    picture_prefix='native-coach-' if args.scenario=='coach' else 'native-move-'
    picture_date='2026-10-14' if args.scenario=='coach' else '2026-10-13'
    shots = Path('C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/screenshots')
    command = (repo/'creators/creator-2/11-integration/03-end-to-end/tests/01-native-coach-scene/native-command.ps1') if args.scenario=='coach' else Path(__file__).with_name('native-command.ps1')
    query_tool = repo / 'creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/vcon-query.cjs'
    captures = []
    def check(): subprocess.run(['pwsh','-NoProfile','-File',str(command),'-Mode','Check','-Run',args.run,'-Addon',args.addon],check=True,capture_output=True,timeout=10)
    def body(): return console.read_text(encoding='utf-8',errors='replace') if console.exists() else ''
    def query(text, suffix):
        output = Path(str(prefix) + '-' + suffix + '.jsonl')
        if output.exists(): raise FileExistsError(output)
        check()
        subprocess.run(['node',str(query_tool),text,str(output),'1400'],check=True,capture_output=True,timeout=10)
        check()
        return [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines()]
    if Path(str(prefix)+'-captures.json').exists(): raise FileExistsError('Prior capture receipt is preserved')
    phases = ['ready'] if args.ready_only else ['bound','world_point'] if args.world_only else ['bound','granted','move_issued','moving','returned','cancelled_return','arrived_return','disposed']
    if args.scenario=='coach' and not args.ready_only: phases=['ready','paused','expired_return','manual_moving','cancelled_return','arrived_return','dead','rebound','stale_rejected','reloaded']
    for phase in phases:
        if (reports/(picture_prefix+args.run+'-'+phase+'-'+picture_date+'.png')).exists(): raise FileExistsError('Prior image is preserved')
    check()
    deadline = time.monotonic() + 420
    for phase in phases:
        while time.monotonic() < deadline:
            text = body()
            if 'DOTA_GAMERULES_STATE_HERO_SELECTION' in text and not Path(str(prefix)+'-hero.jsonl').exists():
                states = re.findall(r'DOTA_GAMERULES_STATE_([A-Z_]+)',text)
                if states and states[-1]=='HERO_SELECTION':
                    query('dota_pick_hero 0 npc_dota_hero_axe','hero')
            matched = re.findall((r'\[C2CoachScene\] ' if args.scenario=='coach' else r'\[C2NativeMove\] ')+re.escape(phase)+r' pass=(true|false)',text)
            if args.ready_only and '[C2ManualMove] panel_ready' in text and 'DCMOVE state mode=AI' in text: matched=['true']
            if matched: break
            time.sleep(.25)
        else: raise TimeoutError('Native phase missing: '+phase)
        rows = query('screenshot',phase+'-shot')
        row = next(row for row in reversed(rows) if 'Screenshot written to:' in row['text'])
        name = re.search(r'shot_\d+\.tga',row['text']).group(0)
        png = reports / (picture_prefix+args.run+'-'+phase+'-'+picture_date+'.png')
        if png.exists(): raise FileExistsError(png)
        with Image.open(shots/name) as frame:
            if frame.size!=(1280,720): raise ValueError('Unexpected native resolution')
            frame.convert('RGB').save(png)
        captures.append({'phase':phase,'pass':matched[-1]=='true','utc':row['utc'],'engine_tga':name,'png':str(png)})
        print(json.dumps(captures[-1]),flush=True)
        output=Path(str(prefix)+'-captures.json')
        # One owned capture receipt is updated as phases complete; images/query logs remain exclusive.
        output.write_text(json.dumps(captures,indent=2)+'\n',encoding='utf-8')
        if matched[-1]!='true': raise RuntimeError('Native assertion failed; negative capture retained')


if __name__=='__main__': main()
