# Независимое техническое рассмотрение 36 подпунктов C2 — 14 октября 2026

Проверяющий: отдельный исполнитель C1, не автор C2 исходников или авторских отчётов. Собственные C1 source fixes и TEST wrapper не получают самооценку: их рассматривает отдельный C2 исполнитель. Дополнение native проверяет C2 fixture/receipt и данные, а не заменяет независимое C2 рассмотрение серверных функций. Пользователь разрешил техническую передачу между исполнителями ИИ; это не человеческая продуктовая или правовая приёмка.

Прочитаны 36 авторских сопоставлений/README, просмотрены actual JS boundary guards и inventories XML/CSS, source consumer/packager и тестовые сценарии. Область — техническая передача/сопоставление, не полный построчный/security аудит всей библиотеки. [36 решений/файлов/хешей](c2-technical-review-2026-10-14.json).

Новые команды этого reviewer: все C2 Node test files **773 PASS**, autonomous-progress **7 PASS**, coach bundle **8 PASS**; после source исправления roster/manual required panels **27 PASS**, все 0 failed/0 skipped. Логи `build/dota_coach/c2-peer-{node,progress,coach-bundle,required-panels-regrade}-20261014.log`. Обновлённые авторские receipts сверены: **169 SHA256 /0 drift**.

## Найденные и исправленные source замечания

Два P2 были воспроизведены/переданы владельцу C2: truthy-invalid обязательный узел в server_roster_panel.js и аналогичный manual_move_panel.js. Первое actual воспроизведение `invalidRequiredRow=true,bound=true,sends=1` сохранено в `build/dota_coach/c2-peer-invalid-node-20261014.log`. После владельческого исправления прочитаны guards обязательных узлов при bind и перед callbacks; expiry закрывает owner/subscription до DTO/button reads. Независимый regrade **27 PASS**, оба source findings resolved. Ни callbacks, ни source GREEN не являются physical input proof.

## Дополнение: новый bounded native receipt R1/R2

Рассмотрены actual `native-coach-scene-2026-10-14.md/json`, C2 native fixture assertions, parsed server journal/order logs, compile source hashes и реальные PNG. Reviewer не запускал Dota. R1 negative expiry assertion сохранён: реальный arrived предшествует deadline. R2 12 API phases согласуются со снимками/счётчиками/журналом, а не только текстом PASS.

- Восстановлено 13 PNG (R2 10): bytes/SHA256/1280×720 совпадают. Full ready/dead PNG просмотрены: TEST assignments/weak coverage и INACTIVE/zero HP видны; screenshot phase не атомарно синхронизирована с API phase. Server sync button на R2 ready невидим: generated visual fix сделан после R2, его native результат этим review не утверждается.
- Exact8 roster содержит пять distinct TEST ids/string slots и weak-coverage для slot2; это server fixed assignments, не клиентский preparation submit/start и не реальный состав5×5. Consumer snapshots нормализовали alive в bool; это не raw17 wire type evidence.
- Два native report reply во время паузы имеют одинаковый game_time32.43333435058594, Time interval2.1999969482421875s; client wall2202ms. Remaining4.799999237 и AI/manual6/1 между paused/unpaused неизменны. Native Time не объявлен калиброванными часами.
- Parsed journal monotonic seq/gameTime; grant32.233333587646→expired37.266670227051 =5.033336639405 game seconds; expired seq23→AI resume seq25. В этот game time записаны order kinds21(Stop)→1(move). Это порядок успешных pcall ExecuteOrderFromTable, не доказательство принятия/завершения каждого приказа движком. Независимые origin observations дополняют его: manual motion306.449XY и дальнейшее движение. Точность5.000s не заявляется.
- Cancel/arrived имеют собственные transition→AI resume и новый kind1 log; death INACTIVE/alivefalse, respawn generation1→2, late move rejected/stale_generation при manual counter3 неизменном; rebind activeAI/staleProxyDTOreads0. Это локальная перезагрузка binding, не серверный live reload.
- Parsed journal — подмножество snapshot entries с пропусками seq для других записей; полного payload/order-link replay receipt нет. Native source_inputs R2 совпадают с current inputs (0 drift), но generated layout поменян после R2. Normal UI2 на момент review только compile, launch не подтверждён. Own PID6264/5708 gone указаны в source receipt; это проверка сохранённого receipt, не независимый live OS poll.

Автоматические consistency assertions: `build/dota_coach/c2-native-peer-verification-20261014.json`. Вопросы карты/visibility, real profiles/heldout fidelity, microphone-ASR, physical input/hittest, normal launch после visual fix, full5×5/result/performance/rights/human acceptance открыты. Никакие C2 flags reviewer не изменял.

## Решения по 36 подпунктам

| Подпункт | Рассмотренная часть и открытая граница |
|---|---|
| C2-01-01 | Bounded file audit keeps runtime_verified false and separate C1 helper provenance; path inventory is not full foundation acceptance. |
| C2-01-02 | Probe pending/correlation/dispose semantics align with addressed diagnostic exchange; historical native receipt is programmatic activation. |
| C2-01-03 | Proposed fields/examples and C1 gap review remain explicit proposals; no general approved wire protocol exists. |
| C2-02-01 | Roster separates playerName/heroName/source and local selection; synthetic tags are explicit, actual identity and physical input remain open. |
| C2-02-02 | Orders retain pending capture and distinguish accepted/executing/completed/unknown; actual move+attack through this adapter remains absent. |
| C2-02-03 | Input routing coordinates existing ports with guarded callback lifecycle; no native map-click exclusion is established. |
| C2-03-01 | Map audit keeps actual_loaded_map/patch/geometry unknown; build association cannot establish loaded geometry. |
| C2-03-02 | Native gateway checks live own-team real hero before requesting focus; requested does not prove camera arrival or stable player identity. |
| C2-03-03 | Target projection uses local freshness/revision guards; caller visibility is not trusted server privacy or admission. |
| C2-04-01 | Team count5 and unique virtual ids make a local draft; serverConfirmed false prevents private draft pretending to be submitted. |
| C2-04-02 | Hero-role draft preserves coverage/proposal kind and preliminary conflict policy; no real player hero mastery or server support claimed. |
| C2-04-03 | Preparation choices reset with upstream context; a declared intent is not actual tactic/morale effect or understood UX. |
| C2-05-01 | Request ACK/timeout and captured actor are distinct from observed mode; the ACK timer supplies no lease authority. |
| C2-05-02 | Mouse proposal pins captured actor and retains canSend/nativeConfirmed/sourceAuthorizationConfirmed false; native API fixture is not hittest. |
| C2-05-03 | Actual strict17 consumer/manual scene supports bounded server observations; newcomer understanding and production mouse scope remain unproved. |
| C2-06-01 | Capture/decoder scripts are explicit diagnostics; quiet recording and three synthetic samples do not establish real speech acceptance. |
| C2-06-02 | Text parser resolves ambiguity without random recipients; actual tested supplied text is independent of microphone/ASR accuracy. |
| C2-06-03 | Voice panel previews parser output and expires stale DTO access; native text preview is not voice/button execution equivalence. |
| C2-07-01 | An inert own-cards HUD template exists, but it imports single existing implementations and does not supply match-state authority itself. |
| C2-07-02 | Opponent roster declares supplied_public_roster and sourceAuthorizationConfirmed false; privacy depends on trusted server producer. |
| C2-07-03 | Timeline is copied presentation history, not the authoritative full event journal or full match screen layout. |
| C2-08-01 | No event-replay runtime exists; comparison correctly retains replay/state reconstruction as open. |
| C2-08-02 | No profile-evidence runtime exists; measured/estimate labels in other cards do not prove heldout fidelity. |
| C2-08-03 | No post-match runtime/result source exists; causal victory explanations cannot be accepted. |
| C2-09-01 | Dated source/media register explicitly excludes engine/transitive inputs and keeps rights_not_assessed; hashes are not licenses. |
| C2-09-02 | Reset/scaling receipts are bounded observations with uncontrolled input and historical build distinction; click-target scaling is unverified. |
| C2-09-03 | No dedicated accessibility runtime exists; label styling alone cannot establish hotkeys/fallback input or unclipped meaning. |
| C2-10-01 | Handoff tooling sets source2_compiled/runtime_verified false and does not silently install; novice clean install remains open. |
| C2-10-02 | No user-task playtest report exists; API fixture testing cannot establish newcomer usability. |
| C2-10-03 | Existing native layout fixes remain in source owners; no user-observed task/retest evidence closes usability acceptance. |
| C2-11-01 | Private lifecycle bindings have independent regression evidence; required-node liveness findings fixed and independently regraded 27 Node PASS; general contract/native coach scene still open. |
| C2-11-02 | Exact coach recipe uses single sources and isolated TEST18/normal15 outputs; fresh eight-test run passes; source receipt is not compile/install. |
| C2-11-03 | Canonical runner separates incomplete/skips from errors and strict verifiedfalse; a full coach preparation/voice/match chain remains absent. |
| C2-12-01 | Rights-related comparison correctly avoids a Valve permission claim; no local product rights display acceptance or current legal conclusion. |
| C2-12-02 | Historical real manual-scene frames are bounded evidence, not a completed Valve packet; no external send occurred in this review. |
| C2-12-03 | Release guide remains incomplete and cannot inherit native TEST launch evidence as a clean-user installation guarantee. |

Все 36 технических передач рассмотрены с explicit functional_complete=false: пустые runtime папки получают документарный review. Bounded native supplement применим к своим C2-05-03/C2-11 частям и не закрывает общий продуктовый критерий.

Урок: общий Node GREEN не покрывал invalid-panel lifecycle; независимый reviewer воспроизвёл реальный модуль, автор исправил source, reviewer повторил checks. Native labels сравниваются со снимками/counters/parsed journal/issuance logs и origin, а screenshots с hash и неатомарным временем. Token usage/cost: null.

## Дополнение normal UI3 после visual fix

Просмотрен actual `native-coach-ui3-ready-2026-10-14.png`: кнопка «Обновить серверный состав», пять TEST assignments и weak coverage видны; AI/server-linked статус показан. SHA256/1280×720 совпадают с root receipt. Exact normal bundle15 повторно проверен actual verify_bundle, TEST driver отсутствует; current source_inputs/assets равны отдельному ui2 compile receipt7 outputs. UI3 — run name, normal installed addon называется ui2. Всего14 PNG. Проверены текущие launcher/delegating helper/build hashes (JSON), без утверждения, что эти hashes замерены в момент native launch. Это повторная визуальная проверка после исправления, не physical input/hittest.

Owned6264/5708/22208/9516 gone указаны в receipt; reviewer не делал live OS poll. Steam13704 currently running в root receipt; старый12964 absent, причина unknown. Идентичность прежнего Steam PID не объявляется сохранённой. Incomplete UI2 capture сохранён как negative. Ранее указанный pending post-R2 visual fix теперь resolved в этой ограниченной visual/recipe области.

## Source regrade: короткая формулировка действия

Прочитан actual progress checker и новый eighth test; fresh8PASS лог `build/dota_coach/c2-peer-progress-short-regrade-20261014.log`. Исправление сравнивает все старые слова короткой формулировки и сохраняет прежний prefix6 rule для длинной: добавление proof-link больше не ложное action_meaning_changed, изменение исходных слов по-прежнему отклоняется. Это исправление учёта, не расширение gameplay acceptance.
