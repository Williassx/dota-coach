# C2-11-01 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Одна версия контракта работает с реальным сервером, без локального ложного подтверждения.

## Фактическое покрытие

Owned lifecycle связывает private preparation/roster/request/targets/history; optional ports не читают stale DTO. Новый server_roster_panel strict8field snapshot source присутствует.

## Непроведённые проверки и зависимости

Ранее native fixtures проверяли synthetic adapters; новая coach-scene ещё не имеет native receipt в этом срезе. Общий contract всей игры, bootstrap и реальные identity открыты.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/coach_intervention.xml](../src/panorama/layout/custom_game/coach_intervention.xml) — SHA256 f2f63a4440d7212a1c48aa800a3f6c3b5f094ab752e00582a983aa02f2911555.
- [src/panorama/layout/custom_game/coach_match_observation.xml](../src/panorama/layout/custom_game/coach_match_observation.xml) — SHA256 9e90f02b8f18af06793b0c341cef8366d480398b96076c7a7d1bcf97e89a4a94.
- [src/panorama/layout/custom_game/coach_preparation.xml](../src/panorama/layout/custom_game/coach_preparation.xml) — SHA256 acb2d2149ef220f12e40a1350e771b0829c3543362f92b59ec9a99f8a01026e1.
- [src/panorama/layout/custom_game/custom_ui_manifest.xml](../src/panorama/layout/custom_game/custom_ui_manifest.xml) — SHA256 245555a3be0f77889e1d188f7449f0123864ab78eefde5896778f8327b3987c9.
- [src/panorama/layout/custom_game/intervention_screen_manifest.xml](../src/panorama/layout/custom_game/intervention_screen_manifest.xml) — SHA256 c837986179ddae0ba2411411e1ff44fc60453c21201047b63211b201bca69be9.
- [src/panorama/layout/custom_game/match_observation_manifest.xml](../src/panorama/layout/custom_game/match_observation_manifest.xml) — SHA256 f969d96015ca70b159d92ec3bb1088725baf8a80e282c7fb1b635ec1d2268e87.
- [src/panorama/scripts/custom_game/coach_hud_binding.js](../src/panorama/scripts/custom_game/coach_hud_binding.js) — SHA256 ad0f62ba5161bf8995f60d21fd53c92acebe5ab8313f90839158e4bad9d06694.
- [src/panorama/scripts/custom_game/intervention_screen_binding.js](../src/panorama/scripts/custom_game/intervention_screen_binding.js) — SHA256 14047fd3afffe550bec16cf1a6fe5ee8dfc26f8a51725a633bf9f631c27e969e.
- [src/panorama/scripts/custom_game/intervention_selection_state.js](../src/panorama/scripts/custom_game/intervention_selection_state.js) — SHA256 832bd62056adf341ec382f514ab718e9f6e34c99ca1f210f1781d4db6d6f291d.
- [src/panorama/scripts/custom_game/match_observation_binding.js](../src/panorama/scripts/custom_game/match_observation_binding.js) — SHA256 bd0424fcebcb263da6de62765ee156b2b1d51e936d3f2fe2be3a47796370b570.
- [src/panorama/scripts/custom_game/mouse_targeting_binding.js](../src/panorama/scripts/custom_game/mouse_targeting_binding.js) — SHA256 cda43b4264cfcf1061bb68bc00ed7456ebafa48659c4897fd51d623ad49265fe.
- [src/panorama/scripts/custom_game/preparation_binding.js](../src/panorama/scripts/custom_game/preparation_binding.js) — SHA256 4cfbc58cb8b2010b452d4b9595d936f98cb2e83207725839eecead49fe09e338.
- [src/panorama/scripts/custom_game/preparation_flow_state.js](../src/panorama/scripts/custom_game/preparation_flow_state.js) — SHA256 22365b46535e852f994fe5a5727620fbb5ba766b29775312d8b868f18c654885.
- [src/panorama/scripts/custom_game/preparation_panel_port.js](../src/panorama/scripts/custom_game/preparation_panel_port.js) — SHA256 9f361986bc43108689486288d40ebf90e3cf37410790f8569d645d5a178fc9fd.
- [src/panorama/scripts/custom_game/server_roster_panel.js](../src/panorama/scripts/custom_game/server_roster_panel.js) — SHA256 26a83f962669b71867d0e4857014db2911526edb7f345b37a59fd07674724465.
- [src/panorama/styles/custom_game/coach_intervention.css](../src/panorama/styles/custom_game/coach_intervention.css) — SHA256 93bfb456276e37e7ace79393c4d6c0daca3a20d6dabcaea5c53f7af5c319e853.
- [src/panorama/styles/custom_game/coach_match_observation.css](../src/panorama/styles/custom_game/coach_match_observation.css) — SHA256 8e1a729fe43153996eb1618e81f2fcbb1415b59c2b9999bbc137fd5cd191afd5.
- [src/panorama/styles/custom_game/coach_preparation.css](../src/panorama/styles/custom_game/coach_preparation.css) — SHA256 059cb004ca423a34b60477c04cea05d20f363a059085407f81886fe4de433a73.
- [tests/hud-binding.test.cjs](../tests/hud-binding.test.cjs) — SHA256 7c354e6f09ba9571960fb2ab0927d64b695d0be3c6f98e7d14b6da59c54e96e0.
- [tests/intervention-port-binding.test.cjs](../tests/intervention-port-binding.test.cjs) — SHA256 334c044bfbbbc74bfda52a8695f5ccb1be088b4a3b4e96476357b03707e63bed.
- [tests/intervention-screen.test.cjs](../tests/intervention-screen.test.cjs) — SHA256 22199bcdb548ab2f02ee43955feb1a6a6b7fbc79132f7b4907ecbba7953a2666.
- [tests/intervention-selection.test.cjs](../tests/intervention-selection.test.cjs) — SHA256 9ce4fb93d4b5c835c8d79603c99cf5ab27dd5f96021c173121395bc1643d6e12.
- [tests/match-observation.test.cjs](../tests/match-observation.test.cjs) — SHA256 1c43c6132e01ce11b73e8dcf17384d7c44b060207815f6372453c43df0785405.
- [tests/mouse-targeting.test.cjs](../tests/mouse-targeting.test.cjs) — SHA256 94616bac49afeec588e7b4e4ae28a232276b08b9562c36741ca342662729fc53.
- [tests/panel-port.test.cjs](../tests/panel-port.test.cjs) — SHA256 305414384d5b969be83021b04e4fb1d667f83ffc53527c62cd458b352792ca53.
- [tests/preparation-binding.test.cjs](../tests/preparation-binding.test.cjs) — SHA256 61ae23f4e4c3d633a5f612e621318558a8defd359cb65d196b7039dcc0626994.
- [tests/preparation-flow.test.cjs](../tests/preparation-flow.test.cjs) — SHA256 2a488152c25ef4e0c6a4c121389867cb50e2944416252736b555022736e5e71d.
- [tests/server-roster.test.cjs](../tests/server-roster.test.cjs) — SHA256 c5506e1012a15774c0ccc7c2a0cee92da75afd151740159b44b6ffbda3304a85.
- Предыдущий отчёт: [cloud-intervention-port.md](cloud-intervention-port.md).
- Предыдущий отчёт: [cloud-intervention-screen.md](cloud-intervention-screen.md).
- Предыдущий отчёт: [cloud-intervention-selection.md](cloud-intervention-selection.md).
- Предыдущий отчёт: [cloud-match-observation.md](cloud-match-observation.md).
- Предыдущий отчёт: [cloud-mouse-targeting.md](cloud-mouse-targeting.md).
- Предыдущий отчёт: [cloud-preparation-binding.md](cloud-preparation-binding.md).
- Предыдущий отчёт: [cloud-preparation-flow.md](cloud-preparation-flow.md).
- Предыдущий отчёт: [cloud-ui-binding.md](cloud-ui-binding.md).
- Предыдущий отчёт: [native-hud-binding-2026-10-12.md](native-hud-binding-2026-10-12.md).
- Предыдущий отчёт: [native-intervention-2026-10-12.md](native-intervention-2026-10-12.md).
- Предыдущий отчёт: [native-mouse-targeting-2026-10-12.md](native-mouse-targeting-2026-10-12.md).
- Предыдущий отчёт: [native-observation-2026-10-12.md](native-observation-2026-10-12.md).
- Предыдущий отчёт: [native-preparation-2026-10-12.md](native-preparation-2026-10-12.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.

## Обновление текущего среза

Обновлены inventory hashes для нового roster/invalid-node lifecycle. Независимый C1 regrade сообщил27NodePASS. Новое native12API-phase evidence находится у [C2-11-03](../../03-end-to-end/reports/native-coach-scene-2026-10-14.md): server-confirmed TEST roster/lease/lifecycle, без physical input, private preparation submit и полной игры. Старые synthetic fixtures этим не переименованы.
