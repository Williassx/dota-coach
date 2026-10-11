# Подключение двух областей вмешательства

[Подпункт](../README.md) · [Дизайн](../intervention-screen-design.md).

Явно загрузите Roster, Orders, Requests, PanelPorts, InterventionSelection,
RosterPanels, RequestPanels и ScreenPanels из canonical файлов библиотеки.
Дерево содержит distinct CoachInterventionRoster/ManualRequestRoot и plain
CoachInterventionStatus, а child scopes — required IDs соответствующих панелей.

```js
var ui = DotaCoachInterventionScreenPanels.bind(root, send);
ui.replaceRoster(rows);
ui.updateControl(frame);
ui.selectPlayer(playerId);
```

root/send/rows/frame/playerId предоставляет интегратор. bind создаёт один private
flow и два owned порта. Child API наружу не выдаются, view — новая копия или null
при busy/closed. Click карточки обновляет область запроса без отправки; request()
или click кнопки создаёт намерение для injected send. DTO читаются после suspend
обеих областей. refresh обновляет UI по уже полученным данным, не запрашивает сервер.

Watcher обновляет общую сводку каждые0.25сек, чтобы timeout не оставлял старую
подпись. Это UI polling, не lease/игровой clock. Actual ACK timer остаётся пять секунд.
dispose/потеря required node закрывает flow/children и watcher/ACK timer; серверная
операция этим не отменяется. Новый bind получает новый private flow. Частичный
отказ не скрывает через parent независимо занятую child scope.

ACK/observed MANUAL не дают права ввода и не доказывают возврат ИИ. Это source
binding существующего дерева, не native приёмка. Layout/recipe — следующий шаг.
