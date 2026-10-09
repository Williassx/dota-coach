# Логика приказов

[Скрипты](../README.md) · [Спецификация](../../../../design.md)

- [orders_state.js](orders_state.js) — подтверждённый режим и отдельный жизненный цикл приказа.
- [orders_panel.js](orders_panel.js) — панели и таймер первого ответа.
- [orders_demo_data.js](orders_demo_data.js) — один вымышленный профиль.
- [orders_demo.js](orders_demo.js) — имитация ответов и очистка demo.

bind(root, send) не имеет транспорта по умолчанию. send(intent, report) — внутренний
переходник; ticket связывает callbacks только внутри экземпляра UI. Сетевые ID,
авторизация, цели и команды Dota принадлежат будущему общему/серверному контракту.
Модули карточек не копируются: их подключение выполняется при интеграции.

Для [C2-02-03](../../../../../03-control-input/README.md) модель/панель получили
updateRecipient(snapshot), который сохраняет выбор/gate, и
selectRecipient(id, playerName, allowIntents), который не создаёт mode/epoch.
allowIntents строго boolean и только ограничивает canIssue. Без снимка видны имя
выбранного и неизвестный режим. null снимает выбор, сохраняя unresolved запрос.
Прежний setRecipient(snapshot) продолжает одновременно обновлять и выбирать.
Панель владеет root исключительно до dispose; отдельное demo на том же root
не запускается одновременно с координатором.
