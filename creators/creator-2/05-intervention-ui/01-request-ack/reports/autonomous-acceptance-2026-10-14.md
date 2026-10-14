# C2-05-01 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

До подтверждения права не присваиваются; причина отказа видна.

## Фактическое покрытие

intervention_request_state связывает captured actor и pending request, reuse Orders snapshot; панель показывает unknown/отказ, ACK отдельно от MANUAL.

## Непроведённые проверки и зависимости

Пятсекундный ACK timeout не lease. Этот local adapter не выдаёт server authority; manual move работает в другой ограниченной сцене, общий HUD не подключён.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/custom_ui_manifest.xml](../src/panorama/layout/custom_game/custom_ui_manifest.xml) — SHA256 13fb12fb2dc02142a64b212f9869269c4dc9c452ca75adf1ebb79d3625e608c9.
- [src/panorama/layout/custom_game/intervention_request.xml](../src/panorama/layout/custom_game/intervention_request.xml) — SHA256 fdb814b4176b5c47021dfd1f255f77a235964c494ca5831d01590e7d7d7b908e.
- [src/panorama/scripts/custom_game/intervention_request_panel.js](../src/panorama/scripts/custom_game/intervention_request_panel.js) — SHA256 dde7e38ba4b5b5c5651a3ff57b6f64d7ba5019839e64733a965c6c24f9559379.
- [src/panorama/scripts/custom_game/intervention_request_state.js](../src/panorama/scripts/custom_game/intervention_request_state.js) — SHA256 93c8f6fc920aa0bb493dde503299bafa56d1f20dd1da0ffd3f510a4db9e4cb07.
- [src/panorama/styles/custom_game/intervention_request.css](../src/panorama/styles/custom_game/intervention_request.css) — SHA256 23cd96ac7bfb0cdb6fb39d5ba9c483ba089e9c012d98bbbb6930eefe32ad1432.
- [tests/intervention-panel.test.cjs](../tests/intervention-panel.test.cjs) — SHA256 9e1c511fc15b15baedc9a3dbcae99566ab367f09975d841736154be9ad061463.
- [tests/intervention-request.test.cjs](../tests/intervention-request.test.cjs) — SHA256 3152c63d85dc2806b3678e621fbf19bfa000ef2f7f26119b95eb48163f7d8ee9.
- [tests/test_intervention_layout.py](../tests/test_intervention_layout.py) — SHA256 61107dcb8eb5235f054448d529214b11577dc793207b95c2df97bba0b95189ca.
- Предыдущий отчёт: [cloud-request-panel.md](cloud-request-panel.md).
- Предыдущий отчёт: [cloud-request.md](cloud-request.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
