# C2-05-02 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Вмешательство относится к прежнему назначенному герою, а не переносится выделением.

## Фактическое покрытие

mouse_proposal_state удерживает captured actor при смене выделения; canSend/nativeConfirmed/sourceAuthorizationConfirmed=false. Native targeting API phases проверили TTL и stale disposal.

## Непроведённые проверки и зависимости

Настоящий physical world callback, текущий lease и authoritative target admission в этой proposal панели не проверены. TEST clock не server freshness.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/custom_ui_manifest.xml](../src/panorama/layout/custom_game/custom_ui_manifest.xml) — SHA256 8bba3c653e712ca59634683afb6661cfdb3491f034a0880f1ee5d15c639b31d8.
- [src/panorama/layout/custom_game/mouse_proposal.xml](../src/panorama/layout/custom_game/mouse_proposal.xml) — SHA256 c2da028b9c4bc2866305deb0a1ba2dddf29ef5713cb7a314f08fa6d359618938.
- [src/panorama/scripts/custom_game/mouse_proposal_panel.js](../src/panorama/scripts/custom_game/mouse_proposal_panel.js) — SHA256 01993bbe1e67339fc4d72ab3d9a047f43107faff32d49ed00e9b7844c22eb2b9.
- [src/panorama/scripts/custom_game/mouse_proposal_state.js](../src/panorama/scripts/custom_game/mouse_proposal_state.js) — SHA256 48b963d5a60f1a144f38ec4794581eef8b0e81181b3857f200d61217f88c1b57.
- [src/panorama/styles/custom_game/mouse_proposal.css](../src/panorama/styles/custom_game/mouse_proposal.css) — SHA256 3891f281daf6c7ad87597d1d524af6d15085c36a35193716f4aca57386f5ea96.
- [tests/mouse-panel.test.cjs](../tests/mouse-panel.test.cjs) — SHA256 981166c6e815b3745a74a2a238d5df6c92ec321da802eeaecb341d8df45f9910.
- [tests/mouse-proposals.test.cjs](../tests/mouse-proposals.test.cjs) — SHA256 2848f764bbd2b73a4293365ef250b4438c74ab28362d4469085fa629a71d204a.
- [tests/test_mouse_layout.py](../tests/test_mouse_layout.py) — SHA256 a87507bb15247278e4ddc0ca9fbc0c424c981abff7602222bd58142aa26bb51a.
- Предыдущий отчёт: [cloud-mouse-panel.md](cloud-mouse-panel.md).
- Предыдущий отчёт: [cloud-mouse-proposals.md](cloud-mouse-proposals.md).
- Предыдущий отчёт: [native-mouse-2026-10-11.md](native-mouse-2026-10-11.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
