# C2-05-03 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Новый пользователь понимает, кто управляет героем; неуспех не подписан успехом.

## Фактическое покрытие

manual_move_state принимает strict17-field wire, ждёт correlated server grant; native report r8/final2 содержит фактический move/cancel/arrival/expiry и новый synthetic AI order.

## Непроведённые проверки и зависимости

Понимание нового пользователя не исследовано; physical input/hittest открыты. Старый native report не доказывает новую coach scene или native pause/death/replacement/reload.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/manual_move.xml](../src/panorama/layout/custom_game/manual_move.xml) — SHA256 df10d10bfcc164153c0698ac8f7a7e066adf91983bde4824e834b20baefea450.
- [src/panorama/scripts/custom_game/manual_move_panel.js](../src/panorama/scripts/custom_game/manual_move_panel.js) — SHA256 d06c6551586ea04042fd971b7f6996a081912ec8f6494617e61f66cbcfb55554.
- [src/panorama/scripts/custom_game/manual_move_state.js](../src/panorama/scripts/custom_game/manual_move_state.js) — SHA256 514824f2d52de820d3889ff3f4cf017e1b3647094b126a4502d0cd47350a9a01.
- [src/panorama/styles/custom_game/manual_move.css](../src/panorama/styles/custom_game/manual_move.css) — SHA256 36eb15d1eb61713aec7d6fb2cf5e16548b106c91bbbd13a13b30b5232bcfe594.
- [tests/manual-move-panel.test.cjs](../tests/manual-move-panel.test.cjs) — SHA256 63ad205d877bfe056d3ce60499a250220aed63fe40e7cdcc0f453fba9dae9cbc.
- [tests/manual-move.test.cjs](../tests/manual-move.test.cjs) — SHA256 d15f919c609b5fc15afc94a1788fbb5502ff33f1769f46305808660e1b5c0270.
- [tests/native-move/capture-command.py](../tests/native-move/capture-command.py) — SHA256 7ca74198346f7903d2d978a5eba792eef77d8b46d3735f6a10d6fda4b086d16c.
- [tests/native-move/native-command.ps1](../tests/native-move/native-command.ps1) — SHA256 0b38896c06a30b85600f5a2e73872636ecc747ba3dec732cee1a430587bd53b6.
- [tests/test_manual_move_bundle.py](../tests/test_manual_move_bundle.py) — SHA256 9d2c97b2f704e7bea7222cc2a9732c7b3f9b1b53dcf60260854a19276a31e8a7.
- [tests/test_native_move_fixture.py](../tests/test_native_move_fixture.py) — SHA256 9723c166bd6f2e70fa7c7b45ba4a6e1fe65204a0d45333477cf9c7dfcf4baa43.
- [tools/build_manual_move_bundle.py](../tools/build_manual_move_bundle.py) — SHA256 1a3db96b44e63be0e06cd48ae99c4d1cc60ca7d8c1f9820e2330552c0148fb5f.
- [tools/build_native_move_fixture.py](../tools/build_native_move_fixture.py) — SHA256 a87d24a1e276dc239caf53236eabf0fa30e9ade26be478fc90ea8941619e95a8.
- [tools/launch_manual_move.ps1](../tools/launch_manual_move.ps1) — SHA256 1fa093753b6f37ef75f4899361b7b7660e8eaf1a140b5231f66bd8270a3c747e.
- Предыдущий отчёт: [dependency-audit.md](dependency-audit.md).
- Предыдущий отчёт: [native-manual-move-2026-10-13.md](native-manual-move-2026-10-13.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
