# Подключение общей модели запроса

[Подпункт](../README.md) · [Дизайн](../intervention-port-design.md).

Интегратор явно загружает Orders, Roster, Requests, InterventionSelection,
PanelPorts и InterventionRequestPanels из единственных исходников библиотеки.
Standalone пакет из шести ресурсов сохраняется; общего recipe/экрана ещё нет.

```js
var flow = DotaCoachInterventionSelection.create(typeof send === "function");
var ui = DotaCoachInterventionRequestPanels.bind(root, send, flow.requestPort());
flow.replaceRoster(rows);
flow.updateControl(frame);
flow.selectPlayer(playerId);
ui.refresh();
```

root/send/rows/frame/playerId предоставляет интегратор. Это схема, не bootstrap.
ui.update/ui.select меняют тот же flow и обновляют панель. После внешних изменений
flow вызывайте ui.refresh. Изменение без refresh: первое нажатие только обновляет
экран, запрос требует нового действия. Подпись также атомарно проверяется внутри
requestPort.begin. Адаптеры портов — доверенный код; не подменяйте begin на flow.begin.

Один стабильный порт принадлежит одной панели. ui.dispose или потеря обязательного
узла закрывает весь flow, включая карточки. Следующий bind получает новый flow.
Disposal не отменяет серверный запрос и не возвращает ИИ. ACK/observed MANUAL не
выдают права ввода. Native/сервер/lease/мышь/возврат ИИ остаются открытыми.
