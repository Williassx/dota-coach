# Координатор выбора и приказов

[Скрипты](../README.md) · [Спецификация](../../../../design.md)

- [input_routing.js](input_routing.js) — `DotaCoachInputRouting.bind(rosterRoot, ordersRoot, send?)`.

Методы: replaceRoster(rows), updateControl(snapshot), select(id), clearSelection(),
dispose(), isDisposed(). Данные карточек и контрольных снимков различаются;
выбор не создаёт режим, эпоху или команду.

Зависимости: DotaCoachRoster, DotaCoachRosterPanels, DotaCoachOrders,
DotaCoachOrderPanels из исходных подпунктов. Загрузить каждую модель перед её
адаптером, все четыре — перед координатором; каждый файл ровно один раз.
Конкретный XML/bootstrap ещё не подключён. На тех же root не запускать отдельные demo.
