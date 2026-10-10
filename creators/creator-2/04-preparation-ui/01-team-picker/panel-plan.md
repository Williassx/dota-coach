# Панель выбора — план реализации

> Для агента: superpowers:executing-plans, TDD; пять критиков read-only.

**Цель:** выбрать локально пять разных записей через фиксированную пагинированную панель.
**Архитектура:** переиспользовать team_picker_state.js; отдельный panel adapter без bootstrap.
**Стек:** ES5, Panorama XML/CSS, node:test/vm. **Спецификация:** [panel-design.md](panel-design.md).

## Ограничения и фокус

Пять кандидатов на страницу, пять выбранных, максимум 64 profiles. Plain text, никаких
native действий/server confirmation. Проверить stale page handler, invalid clearing,
вложенный fresh bind, label failure, destroyed root и сохранение версии выбранных.

## 1. Adapter и RED→GREEN

**Создать:** tests/team-picker-panel.test.cjs и src/panorama/scripts/custom_game/team_picker_panel.js.
**Использовать:** DotaCoachTeamPicker.create(), API из design.md.
**Выдать:** DotaCoachTeamPickerPanels.bind(root), методы из panel-design.md.

- [x] Тесты выбора/удаления/лимита/пагинации/version/invalid/копий draft.
- [x] Тесты owner/partial failure/cleanup/destroyed required panels/reentry/plain text.
- [x] `node --test creators/creator-2/04-preparation-ui/01-team-picker/tests/team-picker-panel.test.cjs`: RED missing source.
- [x] Реализовать adapter; та же команда GREEN, пять критиков, regression RED→GREEN.

## 2. Отдельный source-экран и результаты

**Создать:** src XML/CSS, notes/team-panel.md, reports/cloud-team-panel.md, README новых каталогов.
**Изменить:** индексы текущих каталогов/подпункта/PLAN/AGENTS, отдельный action log.

- [x] XML exact ids/plain labels/resources/no bootstrap; не включать в match HUD.
- [x] Повторить 320 прежних сценариев и новые проверки; syntax/links/README/diff.
- [x] Start_skill partial update/readback, документировать ограничения native/activation.
- [ ] Commit, fast-forward main, remote SHA и clean tree.
