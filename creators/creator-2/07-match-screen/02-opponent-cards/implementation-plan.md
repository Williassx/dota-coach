# Public opponent cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.
> Пользователь выбрал самостоятельную работу основного исполнителя; подагенты не нужны.

**Goal:** Модель минимального публичного состава и отдельная source-панель пяти соперников.
**Architecture:** Own-descriptor DTO → private versioned projection → plain Labels.
Серверный контракт и право доступа не определяются клиентом.
**Tech Stack:** Panorama-compatible JavaScript, Node VM, Python stdlib XML checks.
**Spec:** [design.md](design.md).

## Global Constraints

- Не менять файлы создателя1, общий контракт или existing HUD/source recipes.
- Единственные исходники в src/panorama, новый каталог имеет README/parent link.
- Max5 rows, имена≤64, local safe revision; sourceAuthorizationConfirmed=false.
- Нет боевых полей/Game API/handlers/timers/transport, null не превращается в0.
- Invalid/stale очищает projection; восстановление только при более новом revision.

## Review Focus

- Extra hidden fields с getters: отклонить без чтения значений, очистить старую проекцию.
- Equal/stale revision после отказа: не восстановить старый состав.
- Sparse/extra-property array: не читать произвольную коллекцию.
- Proxy reentry/dispose: не commit после закрытия или вложенного изменения.
- Missing off-slot label/старый binding: закрыть отображение и сохранить новое владение.

### Task 1: Pure projection

**Files:** `src/panorama/scripts/custom_game/opponent_roster_state.js`,
`tests/opponent-roster.test.cjs`.
**Interfaces:** create→update(snapshot):bool, view():copy|null, dispose().

- [x] Написать тесты null/zero/empty roster, exact schema/bounds/duplicates/sparse,
  extra getter/no-read, monotonic/equal/recovery, copied view, busy/dispose.
- [x] Запустить `node --test --test-reporter=tap creators/creator-2/07-match-screen/02-opponent-cards/tests/opponent-roster.test.cjs`; получить RED отсутствующего модуля.
- [x] Реализовать private модель согласно exact spec, без зависимостей и Game API.
- [x] Получить GREEN тем же вызовом и записать actual counts.

### Task 2: Source panel

**Files:** `src/panorama/scripts/custom_game/opponent_roster_panel.js`,
`src/panorama/layout/custom_game/opponent_roster.xml`,
`src/panorama/styles/custom_game/opponent_roster.css`,
`tests/opponent-panel.test.cjs`, `tests/test_opponent_layout.py`.
**Interfaces:** bind(root)→update(snapshot):bool/refresh():bool/view():copy|null/
dispose()/isDisposed():bool, одна модель Task1.

- [x] Написать tests explicit bind/plain5 slots/invalid clear-beforeDTO/empty vs unknown,
  ownership/partial repair/required nodes/reentry/dispose vs fresh root + exact inert XML.
- [x] Получить RED через Node suite и Python unittest discover этой tests папки.
- [x] Реализовать exact17 Labels +7 Panels (root/strip/five cards), два JS definitions/CSS; busy до native/DTO,
  lifecycle check также в isDisposed; без авто-bind/handlers/watchers.
- [x] Получить GREEN, не выдавая его за нативный клиентский запуск.

### Task 3: Verification and publication

**Files:** canonical suite-catalog.json C2-11-03, README/notes/reports этой части,
PLAN/UTC journal/progress и общий agent-usage ledger.

- [x] Добавить оба Node набора и Python набор в единый каталог.
- [x] Выполнить полный `python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py`.
- [x] Самостоятельно проверить production diff; один final critic после завершения.
  При подтверждённом quota ждать изменения условий, не запускать больше агентов.
- [x] Обновить actual milestones/график, отчёт/журнал/учёт и необходимые reusable настройки.
- [x] Проверить links/JSON, progress --check, Git diff/cached diff и подготовить
  guarded normal push main. Remote SHA/clean checkout фиксируются в выводе задачи;
  Native/C1/second-owner пункты остаются открытыми.
