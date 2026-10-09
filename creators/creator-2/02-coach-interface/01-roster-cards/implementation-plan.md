# C2-02-01: реализация локальных карточек

> Исполнитель — текущий агент по superpowers:executing-plans; сначала RED проверки,
> затем код и независимое рассмотрение пяти критиков. Пользователь поручил автономную работу.

**Цель:** подготовить выбор карточки для просмотра в Panorama без передачи управления.
**Спецификация:** [design.md](design.md).
**Архитектура:** чистая модель → адаптер статических панелей; демонстрационные
fixtures подключаются только отдельным bootstrap.
**Стек:** игровой ES5, XML/CSS Panorama; node:test/vm Node.js 18+ для облачных проверок.

## Ограничения

- Работать только в C2-02-01 и индексах/журнале создателя 2.
- Не определять канонический сетевой контракт, не отправлять события/приказы.
- Максимум пять записей; точные поля и enum — в дизайне.
- Сохранять статус C1-01-03 и нативной приёмки как незавершённые зависимости.
- Не менять существующий сборочный manifest и не устанавливать UI в Dota.

## Файлы и интерфейсы

- src/panorama/scripts/custom_game/roster_cards_state.js:
  DotaCoachRoster.create() → replace(rows):bool, select(id):bool,
  clearSelection():bool, view():object, dispose():void.
- src/panorama/scripts/custom_game/roster_cards.js:
  DotaCoachRosterPanels.bind(root) → replace/select/clearSelection/dispose/isDisposed;
  render модели в панели, без источников данных по умолчанию; при сбое скрыть
  частичные карточки и по возможности показать недоступность.
- src/panorama/scripts/custom_game/roster_cards_demo_data.js:
  DotaCoachRosterDemoData — два вымышленных синтетических профиля, alive и dead.
- src/panorama/scripts/custom_game/roster_cards_demo.js:
  явный запуск demo, cache ключ dotaCoachRosterDemo и watcher 0.25 секунды.
- src/panorama/layout/custom_game/roster_cards_demo.xml:
  Status, слоты 0–4 с Button и отдельными именем/героем/позицией/источником/состоянием/подсказкой.
- src/panorama/styles/custom_game/roster_cards.css.
- tests/roster-cards.test.cjs — реальные JS через vm и подменённые панели/планировщик.
- README во всех новых каталогах; reports/cloud-cards.md и отдельный action-log.

## Выполнение

- [x] Написать и выполнить RED проверки модели: id-выбор без режима, dead доступен,
  чужой/unsupported/unknown недоступны, перестановка/удаление/смена доступности,
  дубликаты/слишком большой список/неверные поля, внешняя мутация, dispose.
- [x] Реализовать модель и подтвердить GREEN.
- [x] Написать RED проверки адаптера и demo: отдельные подписи, HTML отключён,
  скрытые пустые слоты, старый callback, отказ обновления/рендеринга, повторная
  загрузка, закрытие/ошибка запуска; GameEvents и игровые API недоступны в fixture.
- [x] Реализовать адаптер/явный demo; подтвердить GREEN без пропусков.
- [x] Разобрать XML, подтвердить четыре JS ссылки в правильном порядке, CSS и пять
  комплектов панелей; прочитать образовавшиеся README и проверить локальные ссылки.
- [x] Выполнить существующие проверки среды/фундамента и новые карточки:

```sh
node --test creators/creator-2/02-coach-interface/01-roster-cards/tests/roster-cards.test.cjs
python3 -m unittest discover -s creators/creator-1/01-foundation/01-environment-audit/tests -v
python3 -m unittest discover -s creators/creator-2/01-foundation/01-workspace-audit/tests -v
python3 -m unittest discover -s creators/creator-2/01-foundation/02-panorama-capability/tests -p 'test_*.py' -v
node --test creators/creator-2/01-foundation/02-panorama-capability/tests/probe.test.cjs
```

- [x] Рассмотреть код пятью критиками, исправить подтверждённые проблемы и записать
  реальные результаты в reports и журнал.

Публикация: обычный fast-forward push в main; после push сверить удалённый SHA
с локальным HEAD и убедиться в чистом рабочем дереве. Commit доступен в Git-истории.

Нативная приёмка C2-02-01 остаётся отдельной. После общего контракта и Windows-аудита
определяются адаптер серверных данных, размещение и компиляция; эти команды сейчас не выдумываются.
