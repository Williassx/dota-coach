# Общая привязка подготовки — план

> Для агента: superpowers:executing-plans/TDD; основной source редактор, пять read-only критиков.

**Goal:** existing panel clicks управляют одной privateflow и сразу очищают dependencies.
**Architecture:** owned modelports +3facades/groupguard/explicit refresh. **Stack:** ES5/NodeVM.
**Spec:** [preparation-binding-design.md](preparation-binding-design.md).

## Constraints/Review Focus

Backcompatible standalonebind; no nativecreate/bootstrap/newlayout/server/HUD.
Projection methodsdataonly, ownershiponeport, descriptors/reentry/failure safe.
Groupbusy beforeDTO hideslabels/handlers; hiddenpane failure blocks allactions;
latehandle cleanup beforeownerrelease. Partialcontext copies, no guessedcounters.

## 1. Ports и adapter refresh

**Create:** src/panorama/scripts/custom_game/preparation_panel_port.js, tests/panel-port.test.cjs.
**Modify:** team_picker_panel.js, hero_role_panel.js, preparation_panel.js optionalport+refresh/suspend,
соответствующие tests; flow contexts().preparation и tests.

- [x] Port/injection/refresh/context tests RED→GREEN; existing standalone suites.
- [x] Validate ownfunctionsreceiver/duplicateownership/throws/data-only/getter guard.

## 2. Group binding

**Create:** src/panorama/scripts/custom_game/preparation_binding.js, tests/preparation-binding.test.cjs,
notes/preparation-binding.md, reports/cloud-preparation-binding.md.
**Interface:** bind(root) methods и scopes из design; actualadapters/flow reuse.

- [x] Actualclickchain/reset/failure/reentry/busy/latehandlers/partialowner tests RED→GREEN.
- [x] Пять criticverdicts/concretefix RED→GREEN, previous481+new tests, syntax/README/links/diff.
- [ ] Journal/configreadback/fast-forward main/remoteSHA/clean; native/server/secondowner open.
