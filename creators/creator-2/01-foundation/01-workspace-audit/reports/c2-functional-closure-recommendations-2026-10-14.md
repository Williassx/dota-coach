# Рекомендации по16функциональным действиям C2

14 октября 2026. Frozen baseline b267b5f. Автор C2 Task F; рекомендации не изменяют чекбоксы. Все action_index **one-based** из frozenbaseline. Ограничение общей native сцены: один TEST герой, server TEST roster, programmatic API, без physical input, второго native client и5×5. Peer technical review не human/product/legal approval.

Для действий C2-05-01/02 реализация shared manual v1 находится у владельца C2-05-03: это обозначенная общая feature path, старые локальные панели не переименованы в server-connected. Root должен сохранить эту квалификацию в closure evidence; если action трактуется как именно прежняя панель, эти4действия остаются открытыми.

## 01-foundation/01-workspace-audit — action3 (recommend_scoped)

Согласовать с создателем 1 владение исходными и создаваемыми файлами.

Критерий подпункта: Определены реальные пути; исходники отдела B не смешаны с серверными файлами A.

Основание: Task B/C assigns actual C1 Lua and C2 consumer/builder, one root shared contract author; cross review recorded by both creators. Original author libraries kept, generated addon separate.

Граница: Ownership of this limited integration agreed; not all future full-game contracts.

Доказательства: [autonomous-30pp-plan-2026-10-13.md](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/autonomous-30pp-plan-2026-10-13.md), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json), [build_coach_scene.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py)

## 01-foundation/03-interface-contract — action2 (recommend_scoped)

Передать примеры сообщений создателю 1 для C1-01-03.

Критерий подпункта: Примеры оформлены до общего согласования; этот подпункт не зависит циклически от C1-01-03.

Основание: Exact manual17field/request examples and roster8field/string slots transmitted to C1 author; actual C1 controller/wrapper+conformance tests execute those schemas.

Граница: Examples are limited manual move/read-only TEST roster; voice/attack/general match contract open.

Доказательства: [manual-move-v1.md](../../../../../creators/shared/contracts/manual-move-v1.md), [preparation-roster-v1.md](../../../../../creators/shared/contracts/preparation-roster-v1.md), [test_command_shapes.py](../../../../../creators/creator-1/11-integration/01-ui-contracts/tests/test_command_shapes.py), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json)

## 01-foundation/03-interface-contract — action3 (recommend_scoped)

Вместе проверить, что UI не устанавливает серверный режим сам.

Критерий подпункта: Примеры оформлены до общего согласования; этот подпункт не зависит циклически от C1-01-03.

Основание: C2 selection/acquire cannot create MANUAL; consumer waits correlated granted server snapshot, C1 native sender/owner/lease authorizes effect. Independently reviewed actual sources.

Граница: Programmatic source/native scenario; no physical click or all-client authorization proof.

Доказательства: [manual-move-v1.md](../../../../../creators/shared/contracts/manual-move-v1.md), [manual-move.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move.test.cjs), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 05-intervention-ui/01-request-ack — action1 (recommend_scoped)

Показать ожидание разрешения и подтверждённый MANUAL.

Критерий подпункта: До подтверждения права не присваиваются; причина отказа видна.

Основание: manual_move_panel MoveStatus displays waiting/pending and MoveMode only server snapshot; native grant/MANUAL/return phases run with actual server.

Граница: Feature realized in shared limited manual panel owned C2-05-03; old intervention_request_panel stays local, do not claim its transport replaced.

Доказательства: [manual_move_panel.js](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/scripts/custom_game/manual_move_panel.js), [manual-move-panel.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move-panel.test.cjs), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 05-intervention-ui/01-request-ack — action2 (recommend_scoped)

Разрешать ручной ввод только после ответа сервера.

Критерий подпункта: До подтверждения права не присваиваются; причина отказа видна.

Основание: canMove requires current MANUAL/alive/remaining/captured actor/generation/epoch/session and no pending; panel world callback gated before getters. C1 enforces lease independently.

Граница: Actual API/programmatic world callback; physical input/hittest untested.

Доказательства: [manual_move_state.js](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/scripts/custom_game/manual_move_state.js), [manual-move.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move.test.cjs), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json)

## 05-intervention-ui/01-request-ack — action3 (recommend_scoped)

Проверить чужого/мёртвого героя и отказ.

Критерий подпункта: До подтверждения права не присваиваются; причина отказа видна.

Основание: Actual Lua unauthorized sender test returns without DTO reads/emission; stale_actor/session/generation rejected; dead state blocks acquire/move. Native r2 death/respawn/stale_generation proves dead/rebind state.

Граница: Foreign case is executed Lua/source, not independent second native client. One TEST actor; no real profile identity acceptance.

Доказательства: [test_manual_move_controller.py](../../../../../creators/creator-1/04-intervention/01-manual-actions/tests/test_manual_move_controller.py), [manual-move.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move.test.cjs), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json)

## 05-intervention-ui/02-mouse-targeting — action4 (recommend_scoped)

Показать текущее действие и остаток времени.

Критерий подпункта: Вмешательство относится к прежнему назначенному герою, а не переносится выделением.

Основание: MoveMode displays server remaining.toFixed(1); MoveResult maps move_issued/arrived/cancelled/expired, admitted move is distinct arrival. Native pause remaining unchanged then expiry.

Граница: Display provided by shared manual panel; proposal-only model remains canSend=false/unknown lease. No real mouse capture proof.

Доказательства: [manual_move_panel.js](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/scripts/custom_game/manual_move_panel.js), [manual-move-panel.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move-panel.test.cjs), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 05-intervention-ui/03-return-feedback — action3 (recommend_scoped)

Проверить смерть, паузу и запоздалое состояние.

Критерий подпункта: Новый пользователь понимает, кто управляет героем; неуспех не подписан успехом.

Основание: Native r2 pause2.202 wall/game delta0/unchanged remaining and counters, then expiry5.033 game secs; death INACTIVE/alivefalse, respawn gen1->2, oldgen move rejected. Staleoldhandle Proxyreads0.

Граница: Only one owned TEST scene and named lifecycle cases; disconnected replacement/reload adversarial multiplayer not generally accepted.

Доказательства: [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md), [manual-move.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move.test.cjs), [test_manual_move_controller.py](../../../../../creators/creator-1/04-intervention/01-manual-actions/tests/test_manual_move_controller.py)

## 11-integration/01-ui-binding — action5 (recommend_scoped)

Сверить каналы событий с общим контрактом.

Критерий подпункта: Одна версия контракта работает с реальным сервером, без локального ложного подтверждения.

Основание: C1 RegisterListener manual_request/roster_request and addressed manual_state/roster_state match C2 Send/Subscribe with exact v1 fields; native r2 receives both.

Граница: Two limited versioned channels, not all private preparation/orders/voice/public visibility ports.

Доказательства: [manual-move-v1.md](../../../../../creators/shared/contracts/manual-move-v1.md), [preparation-roster-v1.md](../../../../../creators/shared/contracts/preparation-roster-v1.md), [coach_scene_game_mode.lua](../../../../../creators/creator-1/11-integration/01-ui-contracts/src/scripts/vscripts/coach_scene_game_mode.lua), [manual_move_panel.js](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/src/panorama/scripts/custom_game/manual_move_panel.js), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 11-integration/01-ui-binding — action6 (recommend_scoped)

Проверить поздний снимок, смену героя и старое подключение.

Критерий подпункта: Одна версия контракта работает с реальным сервером, без локального ложного подтверждения.

Основание: Manual stale/equal revision, wrongsession, generation/epoch/gameclock rollback and owned dispose/rebind guarded in actual Node/Lua tests; native generation1->2 and oldhandle DTOreads0.

Граница: No claim that every private panel/server adapter is integrated; old disposed UI cannot cancel new binding, server lease independent.

Доказательства: [manual-move.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move.test.cjs), [manual-move-panel.test.cjs](../../../../../creators/creator-2/05-intervention-ui/03-return-feedback/tests/manual-move-panel.test.cjs), [server-roster.test.cjs](../../../../../creators/creator-2/11-integration/01-ui-binding/tests/server-roster.test.cjs), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json)

## 11-integration/01-ui-binding — action7 (recommend_scoped)

Передать результаты создателю 1 для общей интеграции.

Критерий подпункта: Одна версия контракта работает с реальным сервером, без локального ложного подтверждения.

Основание: Actual C1 author/runtime consumes C2 v1 contracts; independent C1 peer reviewed36C2 parts, root existing checkout shared sources native bundle contains both authors.

Граница: Technical integration handoff under user AI peer override, no human/product approval.

Доказательства: [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json), [preparation-roster-v1.md](../../../../../creators/shared/contracts/preparation-roster-v1.md), [manual-move-v1.md](../../../../../creators/shared/contracts/manual-move-v1.md), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 11-integration/02-addon-packaging — action8 (recommend_scoped)

После локального аудита согласовать manifest исходников и конечные game/content пути.

Критерий подпункта: Сборка использует единственные исходники и не перезаписывает установку без отдельного действия.

Основание: Normal15/TEST18 exact recipe source map uses original author files, derived canonical UI and explicit game/content destinations; independent C1 review and native compile r2.

Граница: Existing fixed kinds remain unchanged; scoped coach scene manifest only, not entire future game.

Доказательства: [build_coach_scene.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py), [test_coach_scene_bundle.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tests/test_coach_scene_bundle.py), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 11-integration/02-addon-packaging — action9 (recommend_scoped)

Собирать отдельный создаваемый каталог, сохраняя оригиналы в папках авторов.

Критерий подпункта: Сборка использует единственные исходники и не перезаписывает установку без отдельного действия.

Основание: Builder creates guarded fresh output, refuses existing/escape paths and preserves authored sources. Separate TEST installation own addon/PIDs recorded in native report.

Граница: Generated output separate from creator libraries; raw build outputs are not edited source or distributable licence evidence.

Доказательства: [build_coach_scene.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py), [test_coach_scene_bundle.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tests/test_coach_scene_bundle.py), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 11-integration/02-addon-packaging — action13 (recommend_scoped)

Проверить полноту и отсутствие дублей серверных/UI исходников.

Критерий подпункта: Сборка использует единственные исходники и не перезаписывает установку без отдельного действия.

Основание: Exact normal15/TEST18 outputs and hashes/derived XML graph checked; missing/extra/tamper, rehashed layout and source escape rejected; source map uses single C1/C2 implementations.

Граница: Completeness relative to fixed recipe; not full Dota game/native all assets, known Windows symlink skips retain strictfalse.

Доказательства: [build_coach_scene.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py), [test_coach_scene_bundle.py](../../../../../creators/creator-2/11-integration/02-addon-packaging/tests/test_coach_scene_bundle.py), [c2-technical-review-2026-10-14.json](../../../../../creators/creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json), [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 12-release/02-valve-presentation — action2 (hold_packet)

Отделить работающий результат от следующих обещаний.

Критерий подпункта: Презентация показывает реальное управление и ограничения модели; пакет не отправлен автоматически.

Основание: New native report separates one TEST hero/server TEST roster from realprofiles/voice/physical/5x5; release demo packet still being authored.

Граница: Can close only after actual presentation/packet carries same implemented/future distinctions and independent review.

Доказательства: [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)

## 12-release/02-valve-presentation — action3 (hold_packet)

Передать пакет создателю 1 без самостоятельной отправки.

Критерий подпункта: Презентация показывает реальное управление и ограничения модели; пакет не отправлен автоматически.

Основание: Shared native evidence available to C1, but concrete completed demo packet/path+hash and C1 receipt not yet read by this reviewer.

Граница: Unsent packet transfer not inferred from source repository visibility; requires actual packet and peer receipt, no external send.

Доказательства: [native-coach-scene-2026-10-14.md](../../../../../creators/creator-2/11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md), [c1-technical-review-2026-10-14.json](../../../../../creators/creator-2/01-foundation/01-workspace-audit/notes/c1-technical-review-2026-10-14.json)
