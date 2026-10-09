# C2-02-02: реализация панели приказов

> Исполнитель использует superpowers:executing-plans; автор исходников один,
> пять критиков рассматривают независимо. Автономная работа поручена пользователем.

**Цель:** отображать подтверждённый режим и ход двух приказов через подключаемый переходник.
**Спецификация:** [design.md](design.md).
**Архитектура:** чистая модель → адаптер Panorama → явно переданный send/report.
**Стек:** ES5, XML/CSS Panorama, Node.js 18+ node:test/vm без внешних пакетов.

## Ограничения и фокус проверки

- Все новые исходники внутри этого подпункта; общие контракты и сервер не менять.
- Не подключать GameEvents/приказы Dota, не назначать MANUAL, не копировать карточки.
- Один незавершённый запрос на контроллер; cache максимум десяти адресатов.
- Snapshot/report точной формы из дизайна; epoch/revision/sequence безопасные целые.
- UI deadline первого ответа 2 секунды; после ответа игровую длительность UI не задаёт.
- A→B→A: сохранить блокировку unknown и отклонить старую epoch/старый click.
- Синхронный report→throw: сохранить подтверждённый статус.
- Callback таймера после отмены: не менять завершённый/новый запрос.
- Частичный рендер: скрыть команды и освободить все обработчики/таймеры.
- Missing gateway: отсутствие команды, фикстуры только из отдельного demo входа.

## 1. Модель

**Файл:** `src/panorama/scripts/custom_game/orders_state.js`.
**API:** `DotaCoachOrders.create(transportReady)` → setRecipient(snapshot):bool,
begin(action):intent|null, report(ticket,update):bool, expire(ticket):bool,
notSent(ticket):bool, view():object, dispose():void.
view содержит recipientText, modeText, requestRecipientText, actionText, stageText,
reasonText, eligibilityText,
canIssue, ticket, stage, closed. Каждая копия независима от состояния.

- [x] Написать tests/orders.test.cjs: неизвестный режим; разрешённый AI; MANUAL/INACTIVE,
  dead/opponent/unsupported/no gateway; pending→accepted→executing→completed;
  rejected/cancelled и причина; поздний report после unknown; global lock A→B→A;
  смена epoch и версии; неверные формы и внешние изменения; dispose.
- [x] Запустить `node --test .../tests/orders.test.cjs`, подтвердить RED из-за отсутствия модели.
- [x] Реализовать модель; повторить ту же команду до GREEN без пропусков.

## 2. Адаптер и демонстрация

**Файлы:** `src/panorama/scripts/custom_game/orders_panel.js`, `orders_demo_data.js`,
`orders_demo.js`; `src/panorama/layout/custom_game/orders_demo.xml`;
`src/panorama/styles/custom_game/orders.css`.
**API:** `DotaCoachOrderPanels.bind(root, send)` → setRecipient(snapshot):bool,
dispose():void, isDisposed():bool. send(intent,report) — injected function, без default.
**Панели:** OrderRecipient, OrderMode, OrderRequestRecipient, OrderAction, OrderResult,
OrderReason, OrderEligibility,
OrderMove, OrderAttack. Labels html=false; callbacks снабжены поколением.
**Demo:** один synthetic адресат AI; локально имитируются accepted/executing/completed
с sequence 1/2/3. Надпись явно говорит об имитации и отсутствии приказов в Dota.

- [x] Добавить RED тесты UI: одиночная отправка/двойной клик, synchronous report,
  report→throw, timeout/late report, timer failure до send, stale click/response/timer,
  частичный рендер, отсутствие переходника, dispose, demo reload/destruction/failure.
- [x] Реализовать адаптер и явное demo; подтвердить GREEN всей командой.
- [x] Разобрать XML, сверить 5 ресурсных ссылок, порядок 4 JS и 9 необходимых панелей.
- [x] Создать README в новых каталогах с родительскими ссылками.

## 3. Проверка и публикация

- [x] Получить финальное рассмотрение пяти критиков; воспроизвести подтверждённые
  дефекты RED, исправить и подтвердить GREEN.
- [x] Выполнить прежние команды проверок из [отчёта карточек](../01-roster-cards/reports/cloud-cards.md)
  и новую команду из корня репозитория:

```sh
node --test creators/creator-2/02-coach-interface/02-status-orders/tests/orders.test.cjs
```

- [x] Проверить локальные Markdown ссылки, синтаксис игровых JS и git diff --check.
- [x] Сохранить результаты в reports/cloud-orders.md, обновить README подпункта,
  индексы, отдельный журнал и необходимые инструкции среды.

Публикация — обычный fast-forward push в main с проверкой удалённого SHA.
Нативная приёмка, общий контракт, реальные цели/приказы/герой и второй владелец
остаются открытыми; сборочный manifest фундамента не изменяется.
