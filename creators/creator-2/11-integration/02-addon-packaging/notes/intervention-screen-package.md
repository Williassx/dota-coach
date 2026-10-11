# Source-сцена карточек и запроса

[Подпункт](../README.md) · [Recipe](../intervention-screen-manifest.json).

Из корня репозитория проверена следующая команда с новым автоматическим output:

```bash
python3 - <<'PY'
import json, subprocess
base = 'creators/creator-2/01-foundation/02-panorama-capability/tools/'
manifest = 'creators/creator-2/11-integration/02-addon-packaging/intervention-screen-manifest.json'
result = subprocess.run(['python3', base + 'build_probe_bundle.py', '--manifest', manifest], check=True, capture_output=True, text=True)
output = json.loads(result.stdout)['output']
subprocess.run(['python3', base + 'verify_probe_bundle.py', '--manifest', manifest, '--bundle', output], check=True)
PY
```

Пятый kind `panorama_source_intervention_screen`: 13 outputs, 12 resource links,
одна source Hud-сцена. Composer извлекает только roster/manual scopes из двух
единственных XML, переименовывает roster root и вставляет их в canonical parent.
Восемь определений загружаются в одном контексте; никаких автоматических bind/send.
Явное подключение описано [в C2-11-01](../../../11-integration/01-ui-binding/notes/intervention-screen.md).

Verifier повторно собирает layout из текущих исходников, проверяет raw input
fingerprints и байты всех outputs. Старые виды пакетов сохранены. Это альтернативный
manifest: копирование поверх другого пакета заменило бы его декларацию Hud.
Source-сборка не устанавливает аддон и не компилирует Source 2. Игровой transport,
полномочия, lease, ручной ввод и возврат ИИ остаются зависимостями C1/native.
