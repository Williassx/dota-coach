# Панель героев и позиций — план

> Для агента: superpowers:executing-plans/TDD; пять read-only критиков.

**Цель:** локально показать предложения activeplayer и назначить без ложного server proof.
**Архитектура:** fixed5players/5choices/5assignments, realmodel reuse и отдельный source screen.
**Стек:** ES5/Panorama XML/CSS, Node VM/Python. **Spec:** [panel-design.md](panel-design.md).

## Ограничения/фокус

До32choices игрока/7pages; все Labels plain; no automaticfocus/assign/start/HUD.
Проверить неверный profileVersion/oldhandlers/ABA/conflict/emptychoices/freshbind/labelfailure.

## 1. Adapter

**Создать:** tests/hero-role-panel.test.cjs, src/panorama/scripts/custom_game/hero_role_panel.js.
**Использовать:** DotaCoachHeroRoles.create() API. **Выдать:** bind(root) API из panel-design.

- [x] Focus/pages/assignment/conflict/clear/version/empty/invalid/plain tests.
- [x] Owner/partialfailure/lifecycle/getters/stalehandlers/freshbind tests.
- [x] `node --test creators/creator-2/04-preparation-ui/02-hero-role-picker/tests/hero-role-panel.test.cjs`: RED missingadapter.
- [x] Adapter implementation → GREEN; пять критиков и RED регрессии для дефектов.

## 2. Source layout и результаты

**Создать:** XML/CSS, tests/test_hero_role_layout.py, notes/hero-role-panel.md,
reports/cloud-hero-role-panel.md и README каталогов.
**Изменить:** текущие индексы/PLAN/AGENTS/action log, start_skill частично.

- [x] Sourcegraph RED→GREEN, no native proof/no manifest/HUD incorporation.
- [x] Прежние374 и новые сценарии; syntax/links/README/diff.
- [x] Пять критиков, journal/config readback, fast-forward main, remote SHA/clean tree: 045fb99.

UI data/source/native/server acceptance and equal second-owner review remain open.
