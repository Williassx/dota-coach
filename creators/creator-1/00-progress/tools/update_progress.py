"""Generate Creator 1 progress from its canonical action checklists.

Standard library only; SVG is rendered by this script (no matplotlib),
following the section-checklist metric the project uses for creator 2.
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

CREATOR = Path(__file__).resolve().parents[2]


def collect(root: Path) -> dict:
    sections = sorted(p for p in root.iterdir()
                      if p.is_dir() and re.match(r'^(0[1-9]|1[0-2])-', p.name))
    if [p.name[:2] for p in sections] != [f'{n:02d}' for n in range(1, 13)]:
        raise ValueError('Expected exactly sections 01 through 12')
    result = []
    for section in sections:
        title = (section / 'README.md').read_text(encoding='utf-8').splitlines()[0]
        title = title.split('—', 1)[-1].lstrip('# ').strip()
        title = re.sub(r'^Создатель 1:\s*', '', title)
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
            'done': done, 'total': total, 'percent': round(done / total * 100, 1),
            'sections': result}


def render_svg(data: dict) -> str:
    width, height = 864, 504
    title_top = 30
    bottom = 40
    bar_h = 20
    rows = len(data['sections'])
    top = title_top + 14
    usable = height - top - bottom
    step = usable / rows
    out = ['<?xml version="1.0" encoding="utf-8" standalone="no"?>',
           '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d" version="1.1">' % (width, height, width, height),
           '  <rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>'
           % (width, height),
           '  <text x="12" y="24" font-family="sans-serif" font-size="15" '
           'fill="#23495e">%s</text>' % escape(
               'Создатель 1 · разделы 01–12 · всего %.1f%%' % data['percent']),
           '  <text x="12" y="%d" font-family="sans-serif" font-size="9" fill="#666">%s</text>'
           % (height - 14, escape(
               'Источник: чек-листы README. Процент не означает готовность игры в Dota.'))]
    for i, s in enumerate(data['sections']):
        y = round(top + i * step + (step - bar_h) / 2, 2)
        label = '%02d. %s' % (s['number'], s['title'])
        done_val = s['percent'] / 100.0 * (width - 240)
        out.append('  <text x="12" y="%.2f" font-family="sans-serif" font-size="11" '
                   'fill="#333">%s</text>' % (y + bar_h - 5, escape(label)))
        out.append('  <rect x="240" y="%.2f" width="%.2f" height="%d" fill="#2b83ba"/>'
                   % (y, done_val, bar_h))
        out.append('  <text x="%d" y="%.2f" font-family="sans-serif" font-size="10" '
                   'fill="#444">%s</text>'
                   % (250 + done_val, y + bar_h - 6,
                      escape('%.1f%% (%d/%d)' % (s['percent'], s['done'], s['total']))))
        out.append('  <rect x="240" y="%.2f" width="%d" height="%d" fill="none" '
                   'stroke="#d8d8d8"/>' % (y, width - 250, bar_h))
    out.append('</svg>')
    return '\n'.join(out) + '\n'


def render_md(data: dict) -> str:
    lines = ['# Прогресс создателя 1', '',
             '[План](PLAN.md) · [Как считается](00-progress/README.md)', '',
             '**Всего: %.1f%% — %d из %d действий.**' % (data['percent'], data['done'], data['total']),
             '',
             '![Разделы 01–12, шкала 0–100%%](progress.svg)', '',
             '| Раздел | Выполнено | Прогресс |', '|---|---:|---:|']
    for s in data['sections']:
        lines.append('| [%02d. %s](%s) | %d/%d | %.1f%% |'
                     % (s['number'], s['title'], s['path'], s['done'], s['total'], s['percent']))
    lines += ['', 'Это доля отмеченных действий, не оценка времени или готовности кастомки.',
              'Готовые исходники не закрывают нативную проверку и приёмку второго создателя.', '',
              'Обновление: `python creators/creator-1/00-progress/tools/update_progress.py`.', '']
    return '\n'.join(lines)


def main() -> int:
    data = collect(CREATOR)
    (CREATOR / 'progress.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (CREATOR / 'PROGRESS.md').write_text(render_md(data), encoding='utf-8')
    (CREATOR / 'progress.svg').write_text(render_svg(data), encoding='utf-8')
    print('Updated creator-1 progress: %d/%d actions (%.1f%%)'
          % (data['done'], data['total'], data['percent']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
