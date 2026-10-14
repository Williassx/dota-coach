# Независимая техническая проверка 36 подпунктов C1 — 14 октября 2026

Reviewer: отдельный C2 исполнитель, не автор C1 code. Разрешение: автономный technical peer review пользователя. Функциональная, human/product/legal приёмка отдельно; чекбоксы reviewer не изменял.

Проверка выполнялась чтением README, actual src/tests и existing reports;46 Python test files запущены. Четыре без __main__ дополнительно запущены через unittest discover: actual Lua execution2+1+1+5. Всё завершилось exit0; это не отрицает отдельно воспроизведённые3дефекта. Команды/outputs/хеши в [JSON](c1-technical-review-2026-10-14.json).

Исторический первоначальный verdict (исправлен последующим regrade в конце): три части требовали source fix перед reviewed handoff: C1-08-02, C1-08-03, C1-10-01. Остальные33 имеют техническое рассмотрение в указанном ограниченном scope, функциональные зависимости остаются открытыми.

## C1-01-01

Буквальный критерий: Отчёт содержит ОС, Git, пути и сборку; отсутствие локального доступа указано явно, чтение API не выдано за запуск.

Решение: **reviewed_scoped**. Read-only environment inventory plus Windows paths/build25894101 report; filesystem audit does not prove Tools/game acceptance.

Материалы: [test_inspect_environment.py](../../../../../creators/creator-1/01-foundation/01-environment-audit/tests/test_inspect_environment.py)

Тесты: test_inspect_environment.py exit0

## C1-01-02

Буквальный критерий: Реальный клиент выполняет движение и атаку; лог и наблюдение подтверждают идентичность героя.

Подготовка C1-01-02 и C2-01-02 начинается после соответствующих аудитов; затем
авторы совместно проверяют событие и подтверждение, изменяя разные серверные/UI
файлы. Завершение UI заранее не требуется для начала серверной работы.
Это проверка механизмов. Полный цикл ИИ/мышь/возврат принимается позже по
[распределению сценариев](../../../../../creators/creator-1/01-foundation/02-addon-capability/probe-design.md), а не закрывается этой карточкой.

Решение: **reviewed_scoped**. Actual native historical move/attack receipts exist; source static assertions passed; no current native launch or human input reviewed here.

Материалы: [addon_game_mode.lua](../../../../../creators/creator-1/01-foundation/02-addon-capability/src/scripts/vscripts/addon_game_mode.lua), [test_probe_sources.py](../../../../../creators/creator-1/01-foundation/02-addon-capability/tests/test_probe_sources.py)

Тесты: test_probe_sources.py exit0

## C1-01-03

Буквальный критерий: Один общий контракт имеет одну рассмотренную версию и примеры допустимых/отклонённых сообщений.

Решение: **reviewed_scoped**. Diagnostic sender equality/addressed reply tests execute Lua; diagnostic ping and limited manual v1 are not one agreed full-game contract.

Материалы: [diagnostic_ping.lua](../../../../../creators/creator-1/01-foundation/03-command-contract/src/scripts/vscripts/diagnostic_ping.lua), [ping_game_mode.lua](../../../../../creators/creator-1/01-foundation/03-command-contract/src/scripts/vscripts/ping_game_mode.lua), [test_contract_examples.py](../../../../../creators/creator-1/01-foundation/03-command-contract/tests/test_contract_examples.py), [test_diagnostic_ping.py](../../../../../creators/creator-1/01-foundation/03-command-contract/tests/test_diagnostic_ping.py)

Тесты: test_contract_examples.py exit0, test_diagnostic_ping.py exit0

## C1-02-01

Буквальный критерий: Перезапуск не дублирует события, таймеры и состояние прошлого матча.

Решение: **reviewed_scoped**. Single _G activation guard/one Think and two historical fresh-process reports; same-process reload/end-to-end session cleanup remains open.

Материалы: [addon_game_mode.lua](../../../../../creators/creator-1/02-runtime/01-session-lifecycle/src/scripts/vscripts/addon_game_mode.lua), [test_lifecycle_sources.py](../../../../../creators/creator-1/02-runtime/01-session-lifecycle/tests/test_lifecycle_sources.py)

Тесты: test_lifecycle_sources.py exit0

## C1-02-02

Буквальный критерий: Приказы старой привязки не воздействуют на нового героя; чужое назначение отклоняется.

Решение: **reviewed_scoped**. Pure binding returns copied snapshots, accepts exact live entity/revision and owner; native death/respawn/reconnect integration remains open.

Материалы: [actor_binding.lua](../../../../../creators/creator-1/02-runtime/02-actor-binding/src/scripts/vscripts/actor_binding.lua), [test_actor_binding_sources.py](../../../../../creators/creator-1/02-runtime/02-actor-binding/tests/test_actor_binding_sources.py)

Тесты: test_actor_binding_sources.py exit0

## C1-02-03

Буквальный критерий: Пауза не расходует время вмешательства; записи позволяют восстановить причины переходов.

Решение: **reviewed_scoped**. Actual event_log Append/Get copies payloads and rejects regressed game clock; new wrapper links observed transitions; native pause proof is not yet supplied for new scene.

Материалы: [event_log.lua](../../../../../creators/creator-1/02-runtime/03-time-events/src/scripts/vscripts/event_log.lua), [test_event_log_sources.py](../../../../../creators/creator-1/02-runtime/03-time-events/tests/test_event_log_sources.py), [test_execution.py](../../../../../creators/creator-1/02-runtime/03-time-events/tests/test_execution.py)

Тесты: test_event_log_sources.py exit0, test_execution.py exit0

## C1-03-01

Буквальный критерий: Одинаковое разрешённое наблюдение и seed дают одинаковый выбор; скрытое состояние не влияет.

Решение: **reviewed_scoped**. Actual Lua projection/filter/seed hidden-future invariance test executed; caller-supplied visible flag is not engine authorization and BuildProjection stores caller tables.

Материалы: [observation.lua](../../../../../creators/creator-1/03-ai-baseline/01-observation/src/scripts/vscripts/observation.lua), [test_execution.py](../../../../../creators/creator-1/03-ai-baseline/01-observation/tests/test_execution.py), [test_observation_sources.py](../../../../../creators/creator-1/03-ai-baseline/01-observation/tests/test_observation_sources.py)

Тесты: test_execution.py exit0, test_observation_sources.py exit0

## C1-03-02

Буквальный критерий: Герой автономно двигается и атакует; политика не названа моделью реального человека.

Решение: **reviewed_scoped**. Actual Lua Decide patrol uses fresh allowed own point and synthetic=true, arbiter rejects AI during MANUAL; new wrapper native attack/scene outcome remains unperformed.

Материалы: [synthetic_policy.lua](../../../../../creators/creator-1/03-ai-baseline/02-synthetic-policy/src/scripts/vscripts/synthetic_policy.lua), [test_execution.py](../../../../../creators/creator-1/03-ai-baseline/02-synthetic-policy/tests/test_execution.py), [test_synthetic_policy_sources.py](../../../../../creators/creator-1/03-ai-baseline/02-synthetic-policy/tests/test_synthetic_policy_sources.py)

Тесты: test_execution.py exit0, test_synthetic_policy_sources.py exit0

## C1-03-03

Буквальный критерий: Один разрешённый источник управляет действием; повтор не исполняется дважды.

Решение: **reviewed_scoped**. Actual Resolve dedup/revision/priority and MANUAL guards run through Lua suite; streaming admission does not cancel already executed order or arbitrate a batch.

Материалы: [order_arbiter.lua](../../../../../creators/creator-1/03-ai-baseline/03-order-arbiter/src/scripts/vscripts/order_arbiter.lua), [test_arbiter_sources.py](../../../../../creators/creator-1/03-ai-baseline/03-order-arbiter/tests/test_arbiter_sources.py)

Тесты: test_arbiter_sources.py exit0

## C1-04-01

Буквальный критерий: Ручной приказ тому же герою исполняется без перебивания и последующего старого приказа ИИ.

Решение: **reviewed_scoped**. Actual controller/adapter Lua tests exercise lease5, pause/deferredStop, sender/owner and generation guards. Historical native move/cancel/arrival/expiry proven in separate prior scene only.

Материалы: [manual_mode.lua](../../../../../creators/creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/manual_mode.lua), [manual_move_controller.lua](../../../../../creators/creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/manual_move_controller.lua), [manual_move_game_mode.lua](../../../../../creators/creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/manual_move_game_mode.lua), [test_manual_mode_sources.py](../../../../../creators/creator-1/04-intervention/01-manual-actions/tests/test_manual_mode_sources.py), [test_manual_move_adapter.py](../../../../../creators/creator-1/04-intervention/01-manual-actions/tests/test_manual_move_adapter.py), [test_manual_move_controller.py](../../../../../creators/creator-1/04-intervention/01-manual-actions/tests/test_manual_move_controller.py)

Тесты: test_manual_mode_sources.py exit0, test_manual_move_adapter.py exit0, test_manual_move_controller.py exit0

## C1-04-02

Буквальный критерий: После каждого выхода герой реально продолжает различимое действие ИИ; смены надписи недостаточно.

Решение: **reviewed_scoped**. Actual pure Return EnterManual/StartReturn/FinishReturn requires newer observation; historical native manual controller emits new AI movement, not proof this pure Return module is engine-wired.

Материалы: [return_manager.lua](../../../../../creators/creator-1/04-intervention/02-return-ai/src/scripts/vscripts/return_manager.lua), [test_return_sources.py](../../../../../creators/creator-1/04-intervention/02-return-ai/tests/test_return_sources.py)

Тесты: test_return_sources.py exit0

## C1-04-03

Буквальный критерий: Старое событие не завершает новое вмешательство; возрождение не повторяет старый приказ.

Решение: **reviewed_scoped**. Pure generation/action gate rejects stale completions; native pause/death/replacement/reload/late events for new coach scene await receipts.

Материалы: [generation_guards.lua](../../../../../creators/creator-1/04-intervention/03-lifecycle-guards/src/scripts/vscripts/generation_guards.lua), [test_generation_guards_sources.py](../../../../../creators/creator-1/04-intervention/03-lifecycle-guards/tests/test_generation_guards_sources.py)

Тесты: test_generation_guards_sources.py exit0

## C1-05-01

Буквальный критерий: Есть образец с происхождением либо конкретный отказ; агрегаты не названы данными микродействий.

Решение: **reviewed_scoped**. Read source fetcher/fixtures provenance/integrity tests; publicMatches aggregates lack microaction/replay coverage and do not establish individual player fidelity or licence.

Материалы: [test_fixtures_integrity.py](../../../../../creators/creator-1/05-match-data/01-source-audit/tests/test_fixtures_integrity.py)

Тесты: test_fixtures_integrity.py exit0

## C1-05-02

Буквальный критерий: Повтор не создаёт дублей; каждое поле имеет источник и версию преобразования.

Решение: **reviewed_scoped**. Actual importer dedup/quarantine/raw-normalized source/version pipeline passed nominal tests; external dataset provenance/patch and malformed-type hardening remain outside tested scope.

Материалы: [importer.py](../../../../../creators/creator-1/05-match-data/02-import/src/importer.py), [test_importer.py](../../../../../creators/creator-1/05-match-data/02-import/tests/test_importer.py)

Тесты: test_importer.py exit0

## C1-05-03

Буквальный критерий: Нормализация воспроизводится; при отсутствии событий персонализация ограничена явно.

Решение: **reviewed_scoped**. Actual replay_gate rejects explicitly flagged hidden/future events; compatible replay parser and native event provenance absent, intent retained explicitly as guess.

Материалы: [replay_gate.py](../../../../../creators/creator-1/05-match-data/03-replay-normalization/src/replay_gate.py), [test_replay_gate.py](../../../../../creators/creator-1/05-match-data/03-replay-normalization/tests/test_replay_gate.py)

Тесты: test_replay_gate.py exit0

## C1-06-01

Буквальный критерий: Профиль имеет версии и границы; характер не объявлен доказанным по агрегатам.
Разбиение и протокол оценки закреплены до вычисления/настройки признаков и модели;
преобразования обучаются на train, выбор вариантов — на validation. Итоговый test
не открывается для настройки C1-06-01/C1-06-02.

Решение: **reviewed_scoped**. validate function exists ONLY in test_profile_schema.py; synthetic fixture/protocol documentation passed. No runtime profile producer, measured model or human fidelity implementation.

Материалы: [test_profile_schema.py](../../../../../creators/creator-1/06-player-models/01-profiles/tests/test_profile_schema.py)

Тесты: test_profile_schema.py exit0

## C1-06-02

Буквальный критерий: Различия объяснимы входными признаками; правила героя и обзор не обходятся.

Решение: **reviewed_scoped**. Actual personal_policy pure TEST aggression rules passed; consuming allowed context depends on caller and never proves real player likeness or native hero/vision enforcement.

Материалы: [personal_policy.py](../../../../../creators/creator-1/06-player-models/02-personal-policy/src/personal_policy.py), [test_personal_policy.py](../../../../../creators/creator-1/06-player-models/02-personal-policy/tests/test_personal_policy.py)

Тесты: test_personal_policy.py exit0

## C1-06-03

Буквальный критерий: Метрики и ограничения опубликованы; отличие ботов само по себе не доказывает сходство.

Решение: **reviewed_scoped**. Actual evaluate pure harness/check_split run on TEST examples; run_evaluation itself does not enforce locked/disjoint splits. Published TEST rates do not establish heldout human fidelity.

Материалы: [evaluate.py](../../../../../creators/creator-1/06-player-models/03-heldout-evaluation/src/evaluate.py), [test_evaluation.py](../../../../../creators/creator-1/06-player-models/03-heldout-evaluation/tests/test_evaluation.py)

Тесты: test_evaluation.py exit0

## C1-07-01

Буквальный критерий: Нельзя скрыто назначить неподдерживаемый профиль; пять назначений однозначны.

Решение: **reviewed_scoped**. Legacy Python validator lives in tests only; new actual roster_confirmation Lua source validates five server TEST definitions, exact shape/count/compatibility/coverage and copied string slots. Native exchange new scene not yet confirmed.

Материалы: [roster_confirmation.lua](../../../../../creators/creator-1/07-coach-preparation/01-roster-roles/src/scripts/vscripts/roster_confirmation.lua), [test_roster_confirmation.py](../../../../../creators/creator-1/07-coach-preparation/01-roster-roles/tests/test_roster_confirmation.py), [test_roster_validator.py](../../../../../creators/creator-1/07-coach-preparation/01-roster-roles/tests/test_roster_validator.py)

Тесты: test_roster_confirmation.py exit0, test_roster_validator.py exit0

## C1-07-02

Буквальный критерий: Подготовка имеет заранее описанное наблюдаемое влияние.

Решение: **reviewed_scoped**. Actual pure tactics plan/declared bias tests passed; no engine effects or runtime preparation link. Context/profile compatibility with choice_fn remains interface dependency.

Материалы: [tactics.py](../../../../../creators/creator-1/07-coach-preparation/02-tactics/src/tactics.py), [test_tactics.py](../../../../../creators/creator-1/07-coach-preparation/02-tactics/tests/test_tactics.py)

Тесты: test_tactics.py exit0

## C1-07-03

Буквальный критерий: Поддержка меняет согласованные игровые параметры без ложного вывода о личности.

Решение: **reviewed_scoped**. Actual pure bounded focus/steadiness game-only params passed; not measured human morale, no server-native effect or product interpretation acceptance.

Материалы: [morale.py](../../../../../creators/creator-1/07-coach-preparation/03-morale-trust/src/morale.py), [test_morale.py](../../../../../creators/creator-1/07-coach-preparation/03-morale-trust/tests/test_morale.py)

Тесты: test_morale.py exit0

## C1-08-01

Буквальный критерий: Результат соответствует правилам клиента; неуспех имеет понятную причину.

Решение: **reviewed_scoped**. Actual pure action/shop proposal tests passed; hardcoded TEST item prices and last-hit/deny rules are not verified current Dota patch or native execution.

Материалы: [economy.py](../../../../../creators/creator-1/08-match-mechanics/01-farming-economy/src/economy.py), [test_economy.py](../../../../../creators/creator-1/08-match-mechanics/01-farming-economy/tests/test_economy.py)

Тесты: test_economy.py exit0

## C1-08-02

Буквальный критерий: Приказы не обходят ограничения героя; поддерживаемые действия перечислены.

Решение: **changes_required**. Actual hero gate tests passed existing cases, but item accepted with kind ability: concrete defect blocks technical handoff pending fix. Patch/cooldown supplied by caller not engine.

Finding {"priority": "P2", "file": "src/hero_actions.py", "line": 29, "repro": "attempt({'patch':'test','heroes':{'axe':{'abilities':['call'],'items':['blink']}}},'axe','blink','ability') returns (True,'ok')", "action": "Select pool by kind; add regression that item cannot be ability and converse."}

Материалы: [hero_actions.py](../../../../../creators/creator-1/08-match-mechanics/02-hero-actions/src/hero_actions.py), [test_hero_actions.py](../../../../../creators/creator-1/08-match-mechanics/02-hero-actions/tests/test_hero_actions.py)

Тесты: test_hero_actions.py exit0

## C1-08-03

Буквальный критерий: Командный приказ имеет адресатов, подтверждение и наблюдаемые действия.

Решение: **changes_required**. Actual pure distribution tests passed existing cases, but modulo assignment repeats one target across multiple addresses: concrete conflict defect blocks handoff pending fix. Confirmation not native action.

Finding {"priority": "P2", "file": "src/team_orders.py", "line": 26, "repro": "distribute('attack',['a','b'],['x'],{'a':['x'],'b':['x']}) returns ok with target x twice", "action": "Reject insufficient unique targets/resource conflicts; regression roles>targets."}

Материалы: [team_orders.py](../../../../../creators/creator-1/08-match-mechanics/03-team-coordination/src/team_orders.py), [test_team_orders.py](../../../../../creators/creator-1/08-match-mechanics/03-team-coordination/tests/test_team_orders.py)

Тесты: test_team_orders.py exit0

## C1-09-01

Буквальный критерий: Все акторы, карта и правила принадлежат согласованному запуску и патчу.

Решение: **reviewed_scoped**. Actual pure version bind checks two lists of five; caller patch/content/version not independently engine-verified, full roster identities/map/version coherence absent.

Материалы: [match_config.py](../../../../../creators/creator-1/09-full-match/01-match-configuration/src/match_config.py), [test_match_config.py](../../../../../creators/creator-1/09-full-match/01-match-configuration/tests/test_match_config.py)

Тесты: test_match_config.py exit0

## C1-09-02

Буквальный критерий: Обе стороны действуют автономно; соперник не читает скрытую информацию.

Решение: **reviewed_scoped**. Actual pure opponent choices reject explicitly hidden/future flags; no independent native side/vision source, two autonomous engine teams not built.

Материалы: [opponent.py](../../../../../creators/creator-1/09-full-match/02-opponent-policy/src/opponent.py), [test_opponent.py](../../../../../creators/creator-1/09-full-match/02-opponent-policy/tests/test_opponent.py)

Тесты: test_opponent.py exit0

## C1-09-03

Буквальный критерий: Результат однозначен; ограниченный журнал не назван полным повтором Dota.

Решение: **reviewed_scoped**. Actual pure limited result bundle/restore passed supplied endings; no real full-match winner/replay engine source. Bundles store supplied mutable nested records and remain local.

Материалы: [result_bundle.py](../../../../../creators/creator-1/09-full-match/03-result-replay/src/result_bundle.py), [test_result_bundle.py](../../../../../creators/creator-1/09-full-match/03-result-replay/tests/test_result_bundle.py)

Тесты: test_result_bundle.py exit0

## C1-10-01

Буквальный критерий: Совместимые данные восстанавливаются, остальные отклоняются без порчи текущих.

Решение: **changes_required**. Actual save/load nominal compatibility tests passed; returned nested payload aliases original, contradicts fresh-structures guarantee and blocks handoff pending fix. No disk/runtime persistence.

Finding {"priority": "P2", "file": "src/save_compat.py", "line": 29, "repro": "x={'nested':[]}; restored=load_state(save_state(x))[0]; restored['payload']['nested'].append('mutation') mutates x", "action": "Deep-copy nested payload at save/load boundary; regress mutations in all directions."}

Материалы: [save_compat.py](../../../../../creators/creator-1/10-reliability/01-saves-versions/src/save_compat.py), [test_save_compat.py](../../../../../creators/creator-1/10-reliability/01-saves-versions/tests/test_save_compat.py)

Тесты: test_save_compat.py exit0

## C1-10-02

Буквальный критерий: Отчёт позволяет повторить сбой и не содержит токенов или полного окружения.

Решение: **reviewed_scoped**. Actual diagnostic allowlist/forbidden-hint gate tests passed; minimal pure reports not telemetry system; string-hint screening cannot prove all possible secret values absent.

Материалы: [diag_report.py](../../../../../creators/creator-1/10-reliability/02-diagnostics/src/diag_report.py), [test_diag_report.py](../../../../../creators/creator-1/10-reliability/02-diagnostics/tests/test_diag_report.py)

Тесты: test_diag_report.py exit0

## C1-10-03

Буквальный критерий: Есть сравнимые измерения; облачная оценка не выдана за производительность Dota.

Решение: **reviewed_scoped**. Documentation/marker tests only, no profiler/runtime measurements; cloud figures not native frame/tick benchmark or bottleneck proof.

Материалы: [test_performance_note.py](../../../../../creators/creator-1/10-reliability/03-performance/tests/test_performance_note.py)

Тесты: test_performance_note.py exit0

## C1-11-01

Буквальный критерий: Интерфейс отражает сервер; старый ответ не возвращает прежний режим.

Решение: **reviewed_scoped**. Actual Lua coach wrapper requires observation/policy/arbiter/event_log/manual native sources; once-only hooks and sender-first roster guarded. Current mock Lua tests passed; new native compile/run not yet claimed.

Материалы: [coach_scene_game_mode.lua](../../../../../creators/creator-1/11-integration/01-ui-contracts/src/scripts/vscripts/coach_scene_game_mode.lua), [test_coach_scene.py](../../../../../creators/creator-1/11-integration/01-ui-contracts/tests/test_coach_scene.py), [test_command_shapes.py](../../../../../creators/creator-1/11-integration/01-ui-contracts/tests/test_command_shapes.py), [test_lua_execution.py](../../../../../creators/creator-1/11-integration/01-ui-contracts/tests/test_lua_execution.py), [test_ui_contracts.py](../../../../../creators/creator-1/11-integration/01-ui-contracts/tests/test_ui_contracts.py)

Тесты: test_coach_scene.py exit0, test_command_shapes.py exit0, test_lua_execution.py exit0, test_ui_contracts.py exit0

## C1-11-02

Буквальный критерий: Настоящая речь меняет поведение, ошибки не создают произвольный приказ.

Решение: **reviewed_scoped**. Actual voice_gate structured exact schema/source coach/origin voice, MANUAL fail-closed and nonmutating preliminary gate passed; no ASR/audio/native orders.

Материалы: [voice_gate.py](../../../../../creators/creator-1/11-integration/02-voice-commands/src/voice_gate.py), [test_voice_gate.py](../../../../../creators/creator-1/11-integration/02-voice-commands/tests/test_voice_gate.py)

Тесты: test_voice_gate.py exit0

## C1-11-03

Буквальный критерий: Полная цепочка выполнена в Dota; ограничения модели и клиента записаны.

Решение: **reviewed_scoped**. Acceptance-split doc tests preserve incomplete full-chain scope; no actual5x5/preparation/voice/manual/postmatch joint acceptance.

Материалы: [test_acceptance_split.py](../../../../../creators/creator-1/11-integration/03-joint-acceptance/tests/test_acceptance_split.py)

Тесты: test_acceptance_split.py exit0

## C1-12-01

Буквальный критерий: Ни доступность файла, ни кастомка не объявлены лицензией на отдельную игру.

Решение: **reviewed_scoped**. Rights register/doc guards preserve unverified licence and primary-source access limits; technical review is not legal opinion or Valve permission.

Материалы: [test_rights_register.py](../../../../../creators/creator-1/12-release/01-source-rights/tests/test_rights_register.py)

Тесты: test_rights_register.py exit0

## C1-12-02

Буквальный критерий: Пакет конкретен и не утверждает одобрение; отправка отдельно авторизуется.

Решение: **reviewed_scoped**. Unsent proposal/demo guards distinguish concept and implementation; ready complete demo packet/Valve approval not established.

Материалы: [test_demo_guards.py](../../../../../creators/creator-1/12-release/02-valve-demo/tests/test_demo_guards.py)

Тесты: test_demo_guards.py exit0

## C1-12-03

Буквальный критерий: Выпуск имеет техническую проверку и применимые права; перенос вне Dota отдельно разрешён.

Решение: **reviewed_scoped**. Release guards/docs retain missing applicable rights/install acceptance; source tests are not publication, Workshop approval or independent-product permission.

Материалы: [test_release_guards.py](../../../../../creators/creator-1/12-release/03-release-package/tests/test_release_guards.py)

Тесты: test_release_guards.py exit0




## Независимый повтор после исправлений

Все3исходных дефекта независимо повторены на actual изменённых src: теперь отрицательные входы отклоняются, вложенные copies независимы. Новые owner tests5+6+6=17PASS/0skips. Итог36reviewed_scoped/0changes_required; ранние findings выше сохранены как история, актуальные resolved решения/хеши в JSON. Native/product/legal acceptance не повышена этим source исправлением.

- C1-08-02 wrong kinds refused; correct pools regression PASS OK
- C1-08-03 all4 orders shortage rejected atomically OK
- C1-10-01 save/load nested independent copies PASS OK

## Текущий C1 реестр материалов

Независимо сверены 164 entries текущего material register: hash/size mismatches=0. Все entries runtime_asset=false, rights_status=not_assessed, external_distribution_confirmed=false. Чтение официальных SSA/requirements автором отдельно от licence approval; сеть9октября не отказ Valve. Техническая инвентаризация пригодна для рассмотрения, права выпуска остаются открытыми.
