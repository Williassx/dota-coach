# Черновик героев и позиций — план реализации

> Для агента: superpowers:executing-plans, TDD; основной агент пишет единственный
> source, пять критиков read-only. Автономное продолжение поручено пользователем.

**Цель:** локально выбрать предложения героя/позиции для пяти виртуальных id.
**Архитектура:** атомарный private frame с team draft и proposals, без server/native.
**Стек:** ES5, node:test/vm. **Спецификация:** [design.md](design.md).

## Ограничения и фокус

Ровно пять team ids/профилей, до32choices на каждый, role1..5. Уникальные локальные
heroes/roles, одна атомарная замена на игрока; complete не означает готовность сервера.
Фокус: неверная profileVersion; missingproposal; старый frame послеinvalid; getters
newer/invalid/dispose; независимые копии и причины снятия выбора.

## 1. Модель и проверяемый draft

**Создать:** tests/hero-role.test.cjs, src/panorama/scripts/custom_game/hero_role_state.js.
**Вход:** update({revision,team,proposals}), assign(id,heroId,role). **Выход:** API из design.

- [x] Тесты complete/unique/conflict/atomicreplace/remove/clear/sourcewarnings.
- [x] Тесты exactschema/teamversion/emptychoices/invalid/highwater/getters/copies/bounds.
- [x] `node --test creators/creator-2/04-preparation-ui/02-hero-role-picker/tests/hero-role.test.cjs`: RED missing source.
- [x] Реализовать create/update/assign/remove/clear/view/draft/dispose/isDisposed.
- [x] GREEN; пять критиков, concrete defects RED→GREEN.

## 2. Воспроизводимость и фиксация

**Создать:** notes/hero-role-draft.md, reports/cloud-hero-role.md, README каталогов.
**Изменить:** текущие индексы/PLAN/AGENTS и отдельную action log запись.

- [x] Прежние346 сценариев и новые проверки, syntax/link/README/diff.
- [x] Start_skill partial save/readback без изменения других полей; activation отдельно.
- [ ] Обычный fast-forward main, remote SHA и чистое дерево.

UI/постоянноеstorage/server/native и подтверждённое владение героем не входят.
