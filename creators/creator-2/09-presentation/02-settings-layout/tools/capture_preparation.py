"""Explicit TEST capture; does not launch Dota or change persistent preferences."""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path


def main():
    from PIL import Image
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, choices=('1600x900', '1024x768'))
    parser.add_argument('--date', default='20261012')
    parser.add_argument('--attempt', default='')
    parser.add_argument('--variant', choices=('baseline', 'reset'), default='baseline')
    parser.add_argument('--addon', default='dota_coach_c2_preparation_r1_20261012',
                        choices=('dota_coach_c2_preparation_r1_20261012',
                                 'dota_coach_c2_preparation_scale_r2_20261013',
                                 'dota_coach_c2_preparation_reset_trace_20261013'))
    args = parser.parse_args()
    capture_date = datetime.datetime.strptime(args.date, '%Y%m%d').strftime('%Y-%m-%d')
    if len(args.date) != 8 or (args.attempt and not re.fullmatch(r'[a-z0-9_-]{1,24}', args.attempt)):
        raise ValueError('Invalid date/attempt')
    if (args.variant == 'reset') != (args.addon == 'dota_coach_c2_preparation_reset_trace_20261013'):
        raise ValueError('Diagnostic variant/addon mismatch')
    repo = Path(__file__).resolve().parents[5]
    run_id = args.run + ('-' + args.attempt if args.attempt else '')
    prefix = repo / ('build/dota_coach/preparation-scale-' + run_id + '-' + args.date)
    receipt = json.loads(Path(str(prefix) + '-owned.json').read_text(encoding='utf-8-sig'))
    log = Path(str(prefix) + '-console.log')
    addon = args.addon
    if (receipt['addon'] != addon or Path(receipt['log']) != log or
            receipt.get('diagnostic_variant', 'baseline') != args.variant):
        raise ValueError('Wrong owned TEST receipt')
    reports = Path(__file__).resolve().parents[1] / 'reports'
    reports.mkdir(exist_ok=True)
    phases = (('bound', 'immediate-a', 'delayed-a', 'immediate-b', 'delayed-b', 'disposed')
              if args.variant == 'reset' else ('bound', 'team', 'complete', 'reset', 'disposed', 'rebound'))
    marker = '[C2NativePreparationReset]' if args.variant == 'reset' else '[C2NativePreparation]'
    outputs = [reports / ('preparation-' + run_id + '-' + p + '-' + capture_date + '.png') for p in phases]
    manifest = Path(str(prefix) + '-captures.json')
    if manifest.exists() or any(p.exists() for p in outputs):
        raise FileExistsError('Fresh capture outputs required')
    helper = repo / 'creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/vcon-query.cjs'
    shots = Path('C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/screenshots')
    records = []
    deadline = time.monotonic() + 420

    def body():
        return log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''

    def query(command, suffix):
        output = Path(str(prefix) + '-' + suffix + '.jsonl')
        if output.exists():
            raise FileExistsError(output)
        # Check exact own process identity immediately before sending a console command.
        guard = (f"$p=Get-Process -Id {int(receipt['pid'])} -ErrorAction Stop; "
                 f"if ($p.ProcessName -ne 'dota2' -or $p.StartTime.ToUniversalTime().Ticks -ne "
                 f"{int(receipt['start_utc_ticks'])}) {{throw 'Owned PID identity changed'}}")
        subprocess.run(['pwsh', '-NoProfile', '-Command', guard], check=True,
                       capture_output=True, timeout=10)
        subprocess.run(['node', str(helper), command, str(output), '1200'], check=True,
                       capture_output=True, timeout=10)
        return [json.loads(x) for x in output.read_text(encoding='utf-8').splitlines()]

    hero_deadline = time.monotonic() + 180
    while time.monotonic() < hero_deadline:
        states = re.findall(r'DOTA_GAMERULES_STATE_([A-Z_]+)', body())
        state = states[-1] if states else None
        if state == 'HERO_SELECTION':
            for command, name in (('sv_cheats 1', 'cheats'), ('dota_pick_hero 0 npc_dota_hero_axe', 'hero')):
                if re.findall(r'DOTA_GAMERULES_STATE_([A-Z_]+)', body())[-1] != 'HERO_SELECTION':
                    raise RuntimeError('Hero selection window changed')
                query(command, name)
            print('phase_scoped_hero_commands_sent=true', flush=True)
            break
        if state in ('STRATEGY_TIME', 'TEAM_SHOWCASE', 'PRE_GAME', 'GAME_IN_PROGRESS'):
            raise RuntimeError('Hero selection missed')
        time.sleep(.25)
    else:
        raise TimeoutError('Fresh hero selection missing')
    for phase, png in zip(phases, outputs):
        while time.monotonic() < deadline:
            lines = [x for x in body().splitlines() if marker in x]
            if any('pass=false' in x for x in lines):
                raise RuntimeError('Native assertion failed')
            if any(marker + ' ' + phase + ' pass=true' in x for x in lines):
                break
            time.sleep(.25)
        else:
            raise TimeoutError('Missing native phase: ' + phase)
        time.sleep(2)
        rows = query('screenshot', phase + '-shot')
        row = next(x for x in reversed(rows) if 'Screenshot written to:' in x['text'])
        name = re.search(r'shot_\d+\.tga', row['text']).group(0)
        with Image.open(shots / name) as frame:
            dimensions = list(frame.size)
            frame.convert('RGB').save(png)
        records.append({'phase': phase, 'utc': row['utc'], 'engine_tga': name,
                        'png': png.name, 'dimensions': dimensions,
                        'sha256': hashlib.sha256(png.read_bytes()).hexdigest()})
        manifest.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(records[-1]), flush=True)
        if dimensions != [int(x) for x in args.run.split('x')]:
            raise RuntimeError('Actual dimensions differ from requested flags; preserve failed capture')
    if marker + ' cycle pass=true' not in body():
        raise RuntimeError('Native cycle incomplete')


if __name__ == '__main__':
    main()
