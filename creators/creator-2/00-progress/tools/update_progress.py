"""Generate Creator 2 progress from its canonical action checklists."""
import argparse
import io
import json
import os
from pathlib import Path
import re
import tempfile

CREATOR = Path(__file__).resolve().parents[2]


def collect(root):
    sections = sorted(p for p in root.iterdir()
                      if p.is_dir() and re.match(r'^(0[1-9]|1[0-2])-', p.name))
    if [p.name[:2] for p in sections] != [f'{n:02d}' for n in range(1, 13)]:
        raise ValueError('Expected exactly sections 01 through 12')
    result = []
    for section in sections:
        title = (section / 'README.md').read_text(encoding='utf-8').splitlines()[0]
        title = title.split('—', 1)[-1].lstrip('# ').strip()
        title = re.sub(r'^Создатель 2:\s*', '', title)
        parts = sorted(p for p in section.iterdir() if p.is_dir() and re.match(r'^\d\d-', p.name))
        if [p.name[:2] for p in parts] != ['01', '02', '03']:
            raise ValueError(f'{section.name}: expected subsections 01, 02, 03')
        tasks = []
        for part in parts:
            source = part / 'README.md'
            text = source.read_text(encoding='utf-8')
            match = re.search(r'^## Действия\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
            checks = re.findall(r'^- \[([ xX])\] ', match.group(1) if match else '', re.M)
            if not checks:
                raise ValueError(f'{source}: action checklist missing')
            tasks.append({'path': source.relative_to(root).as_posix(),
                          'done': sum(c.lower() == 'x' for c in checks), 'total': len(checks)})
        done, total = sum(t['done'] for t in tasks), sum(t['total'] for t in tasks)
        result.append({'number': int(section.name[:2]), 'title': title,
                       'path': (section / 'README.md').relative_to(root).as_posix(),
                       'done': done, 'total': total, 'percent': round(done / total * 100, 1),
                       'subsections': tasks})
    done, total = sum(s['done'] for s in result), sum(s['total'] for s in result)
    return {'schema_version': 1, 'metric': 'checked_actions_over_all_actions',
            'done': done, 'total': total, 'percent': round(done / total * 100, 1), 'sections': result}


def figure(data):
    os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'dota-coach-progress-mpl'))
    os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir()) / 'dota-coach-progress-cache'))
    Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    plt.rcParams['svg.hashsalt'] = 'dota-coach-creator2-progress-v1'
    fig, ax = plt.subplots(figsize=(12, 7))
    labels = [f"{s['number']:02d}. {s['title']}" for s in data['sections']]
    values = [s['percent'] for s in data['sections']]
    ax.barh(labels, values, color='#2b83ba', height=0.65)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel('Отмеченные действия, %')
    ax.set_title(f"Создатель 2 · разделы 01–12 · всего {data['percent']:.1f}%", pad=16)
    ax.xaxis.grid(True, alpha=0.25)
    ax.set_axisbelow(True)
    for n, s in enumerate(data['sections']):
        ax.text(min(s['percent'] + 1.5, 97), n, f"{s['percent']:.1f}% ({s['done']}/{s['total']})",
                va='center', ha='right' if s['percent'] >= 95 else 'left', fontsize=9)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    fig.text(0.02, 0.02, 'Источник: чек-листы README. Процент не означает готовность игры в Dota.', fontsize=9)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    return fig


def render(data):
    fig = figure(data)
    svg = io.BytesIO()
    fig.savefig(svg, format='svg', metadata={'Date': None, 'Creator': 'Dota Coach progress generator'})
    from matplotlib import pyplot as plt
    plt.close(fig)
    md = ['# Прогресс создателя 2', '', '[План](PLAN.md) · [Как считается](00-progress/README.md)', '',
          f"**Всего: {data['percent']:.1f}% — {data['done']} из {data['total']} действий.**", '',
          '![Разделы 01–12, шкала 0–100%](progress.svg)', '',
          '| Раздел | Выполнено | Прогресс |', '|---|---:|---:|']
    md += [f"| [{s['number']:02d}. {s['title']}]({s['path']}) | {s['done']}/{s['total']} | {s['percent']:.1f}% |"
           for s in data['sections']]
    md += ['', 'Это доля отмеченных действий, не оценка времени или готовности кастомки.',
           'Готовые исходники не закрывают нативную проверку и приёмку второго создателя.', '',
           'Обновление: `python3 creators/creator-2/00-progress/tools/update_progress.py`.', '']
    return {'PROGRESS.md': '\n'.join(md).encode('utf-8'), 'progress.svg': ('\n'.join(line.rstrip() for line in svg.getvalue().decode('utf-8').splitlines()) + '\n').encode('utf-8'),
            'progress.json': (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check outputs without writing')
    args = parser.parse_args()
    try:
        data = collect(CREATOR)
        outputs = render(data)
        stale = [name for name, raw in outputs.items()
                 if not (CREATOR / name).is_file() or (CREATOR / name).read_bytes() != raw]
        if args.check and stale:
            parser.exit(1, 'Stale progress outputs: ' + ', '.join(stale) + '\n')
        if not args.check:
            for name, raw in outputs.items():
                (CREATOR / name).write_bytes(raw)
        print(f"{'Checked' if args.check else 'Updated'} 12 sections: {data['done']}/{data['total']} actions ({data['percent']:.1f}%)")
    except (ValueError, OSError, ImportError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
