# Панель подготовки — план

> Для агента: superpowers:executing-plans/TDD; основной агент source, пять критиков read-only.

**Цель:** прочитать и выбрать local plan/talk, ясно отличая намерение от эффекта.
**Архитектура:** explicit bind, real preparationmodel reuse, fixed8+8 options/2chosen.
**Стек:** ES5/Panorama XML/CSS, Node VM/Python. **Spec:** [panel-design.md](panel-design.md).

## Ограничения и фокус

97children/root98, 19buttons; все labels plain. NoStart/Submit/bootstrap/HUD/native.
Old click/newversion, hidden destroyed node, reentrant input/render и freshbind
не должны изменить новое состояние. Emptygroup объясняется до действия.

## 1. Adapter

**Create:** tests/preparation-panel.test.cjs, src/panorama/scripts/custom_game/preparation_panel.js.
**Consumes:** DotaCoachPreparation.create(); **Produces:** bind(root) API из design.

- [x] Tests explicitselection/removal/clear/emptygroups/version/context/stale/noop/plain.
- [x] Tests owner/discovery/render/schedule/getter reentry/hidden/timer/freshbind/tworoot.
- [x] Node tests RED missingadapter → implement → GREEN; пять критиков.

## 2. Graph и результаты

**Create:** layout/custom_game/preparation_picker.xml, styles/custom_game/preparation_picker.css
в src/panorama; tests/test_preparation_layout.py, notes/preparation-panel.md,
reports/cloud-preparation-panel.md и README каталогов.
**Modify:** README/PLAN/AGENTS/journal, partial start_skill.

- [x] Graph RED missingXML → GREEN; definitions only/no manifest/HUD.
- [x] Прежние431 и новые проверки; syntax/links/README/diff.
- [x] Пять verdicts, журнал/config readback/fast-forward main/remoteSHA/clean: 1f1b5c8.

C1/native/effect/realcatalog/server/secondowner ещё открыты.
