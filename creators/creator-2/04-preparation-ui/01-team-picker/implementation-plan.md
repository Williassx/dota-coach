# Локальная модель выбора состава — план реализации

> **Для агента:** superpowers:executing-plans; основной агент пишет исходники,
> пять критиков рассматривают их read-only. Автономное выполнение поручено пользователем.

**Цель:** черновик из пяти разных игроков с версиями и предупреждениями происхождения.
**Архитектура:** одна чистая ES5-модель, частная UI-проекция без server/native.
**Стек:** JavaScript ES5, node:test/vm. **Спецификация:** [design.md](design.md).

## Общие ограничения

64 профиля максимум, пять выборов, exact ownfields, revision/draftRevision без wrap.
Синтетические примеры обозначены; player_model не доказывает сходство. Без auto-start.

## Фокус проверки

Getter disposal/newer update; profileVersion change; старый снимок после invalid;
копии view/draft; пустой/неполный состав без ложной server readiness.

## Задача 1 — Модель и проверяемый локальный draft

**Создать:** tests/team-picker.test.cjs, src/panorama/scripts/custom_game/team_picker_state.js.
**Вход:** update({revision,profiles}), схема в design. **Выход:** API create() из design.

- [x] Написать тесты: выбор пяти без дублей/шестого, смешанные kinds и coverage;
  version/remove/catalog reorder, invalid/duplicate revisions, неизменяемые копии,
  getter dispose/newer update/nonenumerable extra и monotonic draftRevision.
- [x] Выполнить `node --test creators/creator-2/04-preparation-ui/01-team-picker/tests/team-picker.test.cjs`:
  ожидаемый RED из-за отсутствующего source.
- [x] Реализовать create/update/choose/remove/clear/view/draft/dispose/isDisposed.
- [x] Выполнить ту же команду: все сценарии PASS без skipped/todo.
- [x] Пять критиков; подтверждённые дефекты закреплять RED→GREEN.

## Задача 2 — Результаты и воспроизводимость

**Создать:** notes/team-draft.md, reports/cloud-team-picker.md и README каталогов.
**Изменить:** README подпункта/раздела, PLAN/AGENTS, отдельную запись action log.

- [x] Повторить прежние 292 сценария; новые считать отдельно, без native claims.
- [x] Syntax/link/README/diff checks, start_skill сохранить без изменения других полей.
- [ ] Обычный fast-forward main, подтвердить remote SHA и чистое дерево.

Panel/HUD/server/storage/герои/роли не входят в эту часть. Их задачи остаются открытыми.
