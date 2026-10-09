# Проверки и панель камеры

[Скрипты](../README.md) · [API и lifecycle](../../../../notes/camera.md).

- [camera_native.js](camera_native.js) — create/check/focus; проверка живого героя своей команды.
- [camera_panel.js](camera_panel.js) — bind/setTarget/refresh/dispose/isDisposed.

Native не читает origin и не выдаёт приказы. Panel получает цель от будущего источника UI.
