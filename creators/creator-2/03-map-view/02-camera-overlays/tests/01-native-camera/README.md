# Явная native TEST-сцена камеры

[Подпункт](../../README.md) · [Дизайн](../../native-design.md) · [Отчёт](../../reports/native-camera-2026-10-12.md).

`camera_fixture.js` подключается только derived layout; programmatic activation,
TEST id, own alive realhero. Native-command создаёт свежий addon/компилирует/запускает
собственный PID или закрывает его через quit. Capture-command выбирает TEST героя
только в наблюдаемом HERO_SELECTION и сохраняет actual screenshots. Эти команды
активируют клиент Dota и требуют установленной игры/Tools; ordinary tests их не вызывают.
Loopback [VConsole helper](vcon-query.cjs) включён здесь; bytes совпадают с helper,
фактически использованным в smoke. Node/Python/Pillow необходимы для диагностики.

```powershell
./creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/native-command.ps1 -Mode Install -Bundle <fresh-bundle>
./creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/native-command.ps1 -Mode Launch
python creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/capture-command.py --run r1
./creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/native-command.ps1 -Mode Quit
```

Повторный запуск требует нового Run/addon/bundle; ранее созданные файлы сохраняются.
Скрипты имеют дату smoke в именах receipts и намеренно не являются product bootstrap.
