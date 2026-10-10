# Локальная цепь подготовки — план

> Для агента: superpowers:executing-plans/TDD; source пишет основной агент, пять read-only критиков.

**Goal:** контекст предыдущего шага ограничивает следующий и снимает устаревший выбор.
**Architecture:** private3models + source reset preserving highwater, copied-draft comparisons.
**Stack:** ES5/Node VM. **Spec:** [preparation-flow-design.md](preparation-flow-design.md).

## Constraints/Review Focus

No panel/native/server/start/catalog invention. All nested mutations whilebusy false,
не читать вложенный DTO; draft скрыт. Сохранить highwater через reset. Context includes
всеcounters/id/version/assignments; duplicates/noop/oldframes не сбрасывают готовое.

## 1. Reset моделей

**Modify:** C2-04-02/src/panorama/scripts/custom_game/hero_role_state.js и tests/hero-role.test.cjs;
C2-04-03/src/panorama/scripts/custom_game/preparation_state.js и tests/preparation.test.cjs.
**Interface:** reset():bool снимает source/выборы, сохраняет highwater, counter onlyactualremoval.

- [x] Tests reset/draftnull/lateframe/noauto/noop/disposed/generation getter RED.
- [x] Implement reset → GREEN; preserve existing tests/source copies.

## 2. Coordinator и фиксация

**Create:** tests/preparation-flow.test.cjs, src/panorama/scripts/custom_game/preparation_flow_state.js,
notes/preparation-flow.md/reports/cloud-preparation-flow.md.
**Consumes:** threeactualmodels includingreset. **Produces:** create API из design.

- [x] Happychain/contextgates/reset/invalid/stale/busy/dispose/copies tests RED.
- [x] Implement → GREEN; пять критиков/reproducibledefects RED→GREEN.
- [x] Прежние458 +новые, syntax/README/links/diff, journal/configreadback.
- [x] Commit/fast-forward main, remoteSHA/clean. Partial statuses and native/server open.

Review уточнил API contexts(): copied intermediate drafts без guessed counters,
19flowGREEN, busy/dispose скрывают результат.

Опубликован 9f26bdf; remoteSHA и чистота checkout проверены.
