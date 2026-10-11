# Нативная проверка mouse-targeting 7/6

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute this plan task-by-task. Основной исполнитель работает самостоятельно; один итоговый критик после завершённого результата.

**Goal:** проверить существующий explicit binding и границы мыши в установленной Dota без добавления sender, lease или новых механик.

**Architecture:** fixed panorama_source_mouse_targeting содержит 7 ресурсов/6 ссылок. Безымянный XML host содержит существующий MouseProposalRoot с шестью Labels; интегратор явно связывает внутренний компонент с private Targets/MouseProposals. Source-пакет остаётся inert, runtime bootstrap и серверное право не подразумеваются.

**Tech Stack:** Dota build25845666, Source 2 resourcecompiler, Panorama XML/CSS/ES5, Python3.12.14, Node24.19.0.

**Spec:** [panel-design.md](panel-design.md), [binding API](../../11-integration/01-ui-binding/notes/mouse-targeting.md), [fixed recipe](../../11-integration/02-addon-packaging/mouse-targeting-manifest.json).

## Global Constraints

- Standalone mouse-proposal остаётся5/4, mouse-targeting —7/6; probe/HUD policy и общий контракт не изменять.
- Root component MouseProposalRoot содержит ровно MouseActor/MouseAction/MouseTarget/MouseState/MouseLease/MouseHint: 7 ID, 6 plain empty Labels, visible=false до explicit bind.
- Нет auto-bind/handlers/transport/lease. canSend/nativeConfirmed/sourceAuthorizationConfirmed остаются false; ACK/MANUAL не доказывают право ввода.
- Source view ready не подтверждает авторизацию, entityIndex не подтверждает identity; реальные наблюдения и право даёт C1.
- Существующие аддоны и immutable generated output сохранять. Source files остаются canonical в библиотеках C2.

## Review Focus

- Интегратор передал внешний context panel: bind должен получить именно внутренний MouseProposalRoot.
- Native clock остановился/пошёл назад/сменился после reload: проверить invalid/expiry, не выдавать frame clock за серверный lease.
- XML host перекрыл карту: hittest=false в файле не заменяет реальный клик вне панели.
- Цель скрылась/устарела или сменился адресат: draft не переносится и не подтверждает допустимость приказа.
- Старый handle пережил закрытие/смену сцены: он не читает новые DTO и не пишет в новый binding.

## Task 1: исправление native XML root и компиляция

**Files:** canonical mouse_proposal.xml/CSS; tests/test_mouse_layout.py; mouse_proposal_layout.py и два bundle tests в C2-11-02. Не менять JS или mapping recipes.

**Interfaces:** безымянный MouseProposalHost с hittest=false/hittestchildren=true и одним ребёнком MouseProposalRoot. Existing bind(root) и bind(root,{now,maxAgeMs}) не меняются.

- [x] Воспроизвести compile failure `Found root panel with 'id' attribute` на исходном 7/6.
- [x] RED: anonymous host проверка layout; reject identified root/changed host input policy в обоих fixed kinds.
- [x] Обернуть прежний component, сохранить его visible=false/6 Labels; exact validator принимает только эту topology. Shared parser/probe defaults не расширять.
- [x] GREEN: три layout и две новые policy проверки; свежие handoff 7/6 и5/4 source_verified=true.
- [x] Native compile свежего generated 7/6 в новом addon: exit0, семь непустых outputs, SHA-256 проверены. [Факты и команды](reports/native-mouse-2026-10-11.md).
- [x] Полный source runner выполнен; verified=false, шесть упавших Windows suites записаны в отчёте. Этот шаг означает проверку, не зелёную регрессию.

## Task 2: native binding существующей группы

**Files:** существующий mouse_targeting_binding.js не переписывать; результаты будущего прогона — reports/native-mouse-binding.md. Нужен отдельный рассмотренный runtime integrator, не изменения fixed source bundle.

**Consumes:** DotaCoachMouseTargetingPanels.bind(root,{now,maxAgeMs}), component `$.GetContextPanel().FindChildTraverse("MouseProposalRoot")`; exact API captureActor/updateTargets/selectTarget/proposeMove/proposeTarget/refresh/view/reset/dispose/isDisposed.
**Produces:** native evidence явного bind/dispose; отсутствие evidence оставляет задачу открытой.

- [ ] Восстановить штатный Windows input/capture канал: свежий пустой контроль захватывается, его наблюдаемый элемент принимает ввод. На 11 октября WGC timeout воспроизводится и в Блокноте; guessed clicks не выполнять.
- [ ] Подготовить отдельную native сцену с этим альтернативным manifest, без наложения probe/HUD manifests. UI bundle уже скомпилирован, карта/сцена этого аддона ещё не созданы.
- [ ] Проверить реальную JS семантику `$.FrameTime()` из native справки: finite seconds since Panorama initialization; после перевода в ms значения не убывают. Это кандидат now, не подтверждённый clock. Проверить ожидание/паузу/reload; при несоответствии не bind.
- [ ] Передать проверенный now и maxAgeMs=1000 (тестовая конфигурация из existing source tests) явному bind внутреннего root. Не запускать synthetic actor автоматически и не выдавать тестовые DTO за C1 наблюдения.
- [ ] Проверить отображение/clear/refresh/dispose на явно обозначенных local test fixtures; все три evidence flags false, «Время вмешательства неизвестно», никаких серверных событий.
- [ ] Снять native evidence при missing/hidden/replaced дочернем Label и при смене scene: группа закрыта, root скрыт, живые Labels очищены. Старый API не читает входы, новый explicit bind не получает записи старого.

## Task 3: hittest и реальные цели

**Files:** отчёт reports/native-mouse-binding.md; native mouse hook или новый bridge в этом плане не реализуются.

**Consumes:** восстановленный физический ввод, реально загруженная карта, C1 разрешённые observations/identity. Native справка подтверждает имена GetCursorPosition/GetScreenWorldPosition/FindScreenEntities/SetMouseCallback; их наличие не подтверждает результаты.
**Produces:** сценарии физического попадания клика и local proposal; игровых полномочий не добавляет.

- [ ] Нажать внутри/вне панели и на стандартный HUD, проверить сохранение штатного ввода вне неё и границу widget. Сохранить фактические screen coordinates/масштаб без вывода World position из изображения.
- [ ] Проверить native world result, включая null/out-of-world; proposeMove получает только finite x/y/z в существующих local caps. Caps не означают геометрию Dota.
- [ ] Сверить native entity с C1 stable identity и разрешённым текущим наблюдением. До такого источника не соединять FindScreenEntities с updateTargets и не устанавливать глобальный mouse callback.
- [ ] Проверить второй клик, смену selected card без переноса captured actor, hidden/stale/gone цель и expiry на явном refresh/view. Для настоящих игровых last_hit/deny/lease/AI return нужен отдельный серверный этап.
- [ ] Обновить native отчёт/чекбоксы только по полностью пройденным сценариям; передать результат человеческому второму владельцу. AI critic не заменяет его.
