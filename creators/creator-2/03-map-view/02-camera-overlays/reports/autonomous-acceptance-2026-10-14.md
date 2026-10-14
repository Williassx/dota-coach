# C2-03-02 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Выбранная цель совпадает с объектом карты; обозначения не раскрывают скрытые данные.

## Фактическое покрытие

camera_native вызывает запрос фокуса допустимого живого своего героя. Native-camera requested подтверждён; motion trace содержит 100 samples.

## Непроведённые проверки и зависимости

distanceXY4520.37 через1.5s не arrival; baseline уже near18/20, post near2/80 при active input. Причина возврата камеры и identity→entity не установлены, маркеры открыты.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/camera_focus.xml](../src/panorama/layout/custom_game/camera_focus.xml) — SHA256 4198c0419dd18a8842639ae8eb4bb2d7cef912547ff6f1c42312188bf3261c92.
- [src/panorama/scripts/custom_game/camera_native.js](../src/panorama/scripts/custom_game/camera_native.js) — SHA256 d34d2fbb58422c8e6b392deebbdeefa8ed41880a8648b5c086b1a5b62ca03068.
- [src/panorama/scripts/custom_game/camera_panel.js](../src/panorama/scripts/custom_game/camera_panel.js) — SHA256 1681bf081222664c876c017af6f81949233dc9c8acea4af8ed262ce505d249d0.
- [src/panorama/styles/custom_game/camera_focus.css](../src/panorama/styles/custom_game/camera_focus.css) — SHA256 982ef24cbea4a5a15f06e0a2cf741683199173e2930fdeb1b479c86e3f18d9fa.
- [tests/camera-motion.test.cjs](../tests/camera-motion.test.cjs) — SHA256 9564ff13596ae4b467008b1437c5ea743a0f4c39f6f4b4c5c3e1e1cfb7e625f3.
- [tests/camera.test.cjs](../tests/camera.test.cjs) — SHA256 60e6df184684c5954157578b7a5d238521f9a8f51bbe61548348ba28f2319d09.
- [tests/test_native_camera_fixture.py](../tests/test_native_camera_fixture.py) — SHA256 70955eb5c23e667887b4ac264926781e057d025e3781a13a24939ea10ba39a61.
- [tests/01-native-camera/capture-command.py](../tests/01-native-camera/capture-command.py) — SHA256 988fa0630e646cc5d9672181587b02d86ae1b8b71fc07fc47f752039a110bfac.
- [tests/01-native-camera/vcon-query.cjs](../tests/01-native-camera/vcon-query.cjs) — SHA256 28c3bcb7f90f1353b899bad085432d1a7ed8f8cfcf4410390e51e2d739aa36c0.
- Предыдущий отчёт: [cloud-camera.md](cloud-camera.md).
- Предыдущий отчёт: [native-camera-2026-10-12.md](native-camera-2026-10-12.md).
- Предыдущий отчёт: [native-camera-motion-2026-10-12.md](native-camera-motion-2026-10-12.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
