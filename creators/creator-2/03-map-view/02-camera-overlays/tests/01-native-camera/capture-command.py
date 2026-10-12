"""Explicit native diagnostics: selects own TEST hero and captures actual engine frames."""
import argparse, datetime, json, re, subprocess, time
from pathlib import Path
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='r1')
    parser.add_argument('--variant', choices=('camera', 'motion'), default='camera')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9_-]+', args.run): raise ValueError('Invalid run id')
    repo = Path(__file__).resolve().parents[6]
    prefix = repo / ('build/dota_coach/native-camera-' + args.run + '-20261012')
    log = Path(str(prefix) + '-console.log')
    reportdir = Path(__file__).resolve().parents[2] / 'reports'
    shots = Path('C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/screenshots')
    phases = (['baseline', 'early', 'settled', 'returned'] if args.variant == 'motion' else
              ['bound', 'selected', 'refreshed', 'focused', 'rejected', 'disposed', 'rebound'])
    marker = '[C2NativeCameraMotion]' if args.variant == 'motion' else '[C2NativeCamera]'
    records = []
    deadline = time.monotonic() + 420
    def body(): return log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
    def query(command, suffix, wait=1200):
        output = Path(str(prefix) + '-' + suffix + '.jsonl')
        if output.exists(): raise FileExistsError(output)
        proc = subprocess.run(['node', str(Path(__file__).with_name('vcon-query.cjs')), command, str(output), str(wait)], capture_output=True, text=True)
        if proc.returncode: raise RuntimeError(proc.stdout + proc.stderr)
        return [json.loads(line) for line in output.read_text(encoding='utf-8').splitlines()]
    hero_deadline = time.monotonic() + 180
    while time.monotonic() < hero_deadline:
        states = re.findall(r'DOTA_GAMERULES_STATE_([A-Z_]+)', body())
        state = states[-1] if states else None
        if state == 'HERO_SELECTION':
            for command, suffix in [('sv_cheats 1', 'cheats'), ('dota_pick_hero 0 npc_dota_hero_axe', 'hero')]:
                if re.findall(r'DOTA_GAMERULES_STATE_([A-Z_]+)', body())[-1] != 'HERO_SELECTION': raise RuntimeError('Hero-selection window changed')
                query(command, suffix, 1000)
            print('phase_scoped_hero_commands_sent=true', flush=True)
            if args.variant == 'motion': query('find dota_camera', 'camera-settings')
            break
        if state in ('STRATEGY_TIME', 'TEAM_SHOWCASE', 'PRE_GAME', 'GAME_IN_PROGRESS'): raise RuntimeError('Hero selection missed')
        time.sleep(.25)
    else: raise TimeoutError('Fresh hero-selection state missing')
    for phase in phases:
        while time.monotonic() < deadline:
            lines = [line for line in body().splitlines() if marker in line]
            if any('pass=false' in line for line in lines): raise RuntimeError('Native assertion failed; inspect log')
            if any(marker + ' ' + phase + ' pass=true' in line for line in lines): break
            time.sleep(.25)
        else: raise TimeoutError('Native phase missing: ' + phase)
        time.sleep(2)
        rows = query('screenshot', phase + '-shot')
        row = next(row for row in reversed(rows) if 'Screenshot written to:' in row['text'])
        name = re.search(r'shot_\d+\.tga', row['text']).group(0)
        png = reportdir / ('native-camera-' + args.run + '-' + phase + '-2026-10-12.png')
        if png.exists(): raise FileExistsError(png)
        with Image.open(shots / name) as frame: frame.convert('RGB').save(png)
        records.append({'phase': phase, 'utc': row['utc'], 'engine_tga': name, 'png': str(png)})
        print(json.dumps(records[-1]), flush=True)
    Path(str(prefix) + '-captures.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    if args.variant == 'motion':
        while time.monotonic() < deadline:
            lines = [line for line in body().splitlines() if marker in line]
            if any('pass=false' in line for line in lines): raise RuntimeError('Native motion assertion failed')
            if any(marker + ' done pass=true' in line for line in lines): break
            time.sleep(.25)
        else: raise TimeoutError('Native motion sample sequence incomplete')

if __name__ == '__main__': main()
