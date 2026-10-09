# C2-02-03: координатор ввода

> Основной агент выполняет superpowers:executing-plans; пять критиков рассматривают
> результат read-only. Автономное продолжение поручено пользователем.

**Цель:** связать локальный выбор карточки с адресатом подтверждённых приказов.
**Спецификация:** [design.md](design.md).
**Архитектура:** существующие roster/orders остаются единственными реализациями;
новый координатор связывает их API и контролирует общий жизненный цикл.
**Стек:** ES5 Panorama, node:test/vm Node.js 18+ без внешних пакетов.

## Ограничения

- Новая работа в этой папке; необходимые API расширяются в исходных модулях отдела 2.
- Сервер, общий контракт, существующие XML/CSS и manifest фундамента не менять.
- Не добавлять глобальный обработчик мыши, цели карты, MANUAL, demo или игровой транспорт.
- Режим только из снимка; allowIntents только ограничивает возможность намерения.
- Смена выбора не снимает unresolved/unknown запрос; фоновый снимок не перехватывает выбор.

## 1. Интерфейсы и проверки до кода

**Изменения:** `../01-roster-cards/src/panorama/scripts/custom_game/roster_cards_state.js`
(availableForOrders) и `roster_cards.js` (optional onSelection).
`../02-status-orders/src/panorama/scripts/custom_game/orders_state.js` и
`orders_panel.js` (updateRecipient/selectRecipient без копии валидации).
**Проверки:** `tests/input-routing.test.cjs`, реальные четыре существующих JS и координатор.

- [x] Написать RED: callback с независимой копией/null, мёртвый доступен для просмотра,
  но availableForOrders=false; callback exception закрывает карточки.
- [x] Написать RED: updateRecipient сохраняет выбранного адресата, выбор без снимка
  оставляет неизвестный режим, boolean gate не присваивает AI/MANUAL и не снимает busy.
- [x] Написать RED сценарии координатора: без gateway; выбор не отправляет; order click
  выбирает правильный id; late/background/stale; removal/death; unknown через A→B→A;
  ошибочные обновления; partial bind/render; watcher failure; dispose/root destruction.
- [x] Выполнить новую команду, подтвердить ожидаемые ошибки отсутствия методов/координатора.

## 2. Реализация

**Новый файл:** `src/panorama/scripts/custom_game/input_routing.js`.
**API:** DotaCoachInputRouting.bind(rosterRoot,ordersRoot,send?) →
replaceRoster(rows):bool, updateControl(snapshot):bool, select(id):bool,
clearSelection():bool, dispose():void, isDisposed():bool.

- [x] Расширить модели и адаптеры, сохранить прежние методы и данные input.
- [x] Реализовать создание orders→roster, callback синхронизации, обёртку send
  с проверкой обоих дочерних контроллеров и watcher 0.25s.
- [x] Подтвердить GREEN новой команды и прежних наборов карточек/приказов.

## 3. Ревью, документация и публикация

- [x] Рассмотреть код пятью критиками, воспроизвести/исправить подтверждённые дефекты.
- [x] Повторить все прежние наборы из [отчёта приказов](../02-status-orders/reports/cloud-orders.md)
  и новую команду из корня:

```sh
node --test creators/creator-2/02-coach-interface/03-control-input/tests/input-routing.test.cjs
```

- [x] Добавить README в новые папки, notes/input-routing.md, reports/cloud-routing.md;
  обновить документацию расширенных API, индекс, статусы и 00-action-log.
- [x] Проверить локальные ссылки, синтаксис ES5-исходников и git diff --check;
  сохранить воспроизводимую команду в start_skill при необходимости.

Публикация — обычный fast-forward push в main с проверкой удалённого SHA и дерева.
Нативные mouse/hittest/HUD, цели/вмешательство, общий контракт и второй владелец
остаются открытыми. Зелёная VM не закрывает приёмку клика панели внутри Dota.
