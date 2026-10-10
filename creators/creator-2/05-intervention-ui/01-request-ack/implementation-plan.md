# План локального запроса ручного вмешательства

> Для исполнителя: superpowers:executing-plans/TDD; один source редактор, пять read-only критиков.

**Goal:** UI отличает pending/accepted/observed mode без локальной передачи героя.
**Architecture:** reuse Orders snapshot store; новый private request state, без sharedwirecontract.
**Stack:** ES5/NodeVM. **Spec:** [design.md](design.md).

## Constraints/review focus

Snapshot store один источник; only read API в existing Orders, прежние панели не меняются.
accepted ≠ MANUAL; cacheinvalid disables gate; actorselection не переносит request.
Busy/getter/dispose/staleepoch должны сохранять atomic state; no native/lease/action claim.

## 1. Snapshot read API

**Modify:** C2-02-02 orders_state.js и tests/orders.test.cjs.
- [x] RED snapshot copies/unknown/closed/no selection or revision mutation.
- [x] Implement snapshot(id?) only; GREEN existing35 +new.

## 2. Pure request state

**Create:** src/panorama/scripts/custom_game/intervention_request_state.js,
tests/intervention-request.test.cjs, notes/local-request.md, reports/cloud-request.md;
newdirectories README/parentlinks. Interface create(strictbool): update/select/begin/
report/expire/notSent/view/dispose/isDisposed из design. Uses DotaCoachOrders.create(true).

- [x] VM requestflow/actor/highwater/busy/DTO/privatecopy tests RED.
- [x] Minimal implementation GREEN; no panel/transport/sharedcontract/native added.
- [x] Пять read-only verdicts; concretefixes RED→GREEN; previous542/regression/syntax.
- [x] Docs/library/journal/links/start_skill/readback, fast-forwardmain/remoteSHA/clean.

Опубликовано: 36845f6; remote main и чистое дерево были проверены.
