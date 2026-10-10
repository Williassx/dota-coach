# План просмотра допустимых целей

> Используем superpowers:executing-plans, TDD и пять read-only критиков.
> Пользователь разрешил непрерывное автономное продолжение.

**Цель:** убрать скрытую/устаревшую цель из UI и объяснить невозможный выбор.
**Спецификация:** [design.md](design.md).
**Стек:** ES5, Node18+ node:test/vm, Panorama XML/CSS.

## 1. Проверки до реализации

**Создать:** tests/targets.test.cjs.
**Новые файлы:** src/panorama/scripts/custom_game/targets_state.js, targets_panel.js.

- [x] RED: full snapshot/visible ally/enemy hero/creep/dead; explicit selection.
- [x] RED: hidden/gone/unknown/removal без чтения подписи/координат, без auto-reselect.
- [x] RED: freshness/old revision/options/invalid bounds/copy/plain text/reentrancy.
- [x] RED: root ownership/rollback/render failure/watch/dispose/native APIs forbidden.
- [x] Запустить тесты до source и подтвердить ожидаемые failures.

## 2. Реализация

- [x] Model create/update/select/view/dispose с точным schema, clock и revision.
- [x] Панель с caller options, одним отменяемым watcher и plain-text fields.
- [x] GREEN, разметка/стиль без bootstrap/demo/транспорта.

```sh
node --test creators/creator-2/03-map-view/03-visibility-targets/tests/targets.test.cjs
```

## 3. Ревью и публикация

- [x] Пять независимых направлений; подтверждённые ошибки RED→GREEN.
- [x] Повторить baseline211, проверить source/XML/resources/README/Markdown links.
- [x] Документация/статусы/индексы/отдельный журнал; сохранить только команду start_skill.
- [ ] Обычный fast-forward main, совпадение SHA и чистое дерево.

Не закрывать зависимость C1-03-01, общий контракт, native видимость, карту или мышь.
Не менять сервер, существующие модули или foundation manifest.
