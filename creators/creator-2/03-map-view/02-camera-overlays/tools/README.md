# Помощник TEST-пакета камеры

[Подпункт](../README.md) · [build_native_camera_fixture.py](build_native_camera_fixture.py).

Создаёт свежие15outputs из unchanged fixed HUD13, добавляя TEST driver/layout/manifest.
Проверяет источники до writes; source-only flagsfalse. Не компилирует и не запускает Dota.

```powershell
python creators/creator-2/03-map-view/02-camera-overlays/tools/build_native_camera_fixture.py
python creators/creator-2/03-map-view/02-camera-overlays/tools/build_native_camera_fixture.py --variant motion
```

Exact `camera` — исходный default smoke; `motion` — [motion-дизайн](../motion-design.md).
Другие значения отвергаются до чтения/записи. Target driver path прежний, его source
берётся только из двух фиксированных TEST-файлов; kind и13canonical inputs сохранены.
