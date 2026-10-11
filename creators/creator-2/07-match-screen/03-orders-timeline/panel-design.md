# Панель последних записей справа

Продолжение [pure истории](design.md). Ведущий — основной исполнитель отдела 2.
Один explicit `DotaCoachOrdersTimelinePanels.bind(root)` создаёт одну частную историю.
Caller передаёт `Orders.view()` через `record`, `refresh` только обновляет отображение;
нет polling, timers, handlers, transport или автоматической загрузки тестовых данных.

Отдельный inert XML/CSS содержит title, summary, hint и шесть plain Label строк.
Показываются последние шесть событий в хронологическом порядке. Summary различает
непоказанные сохранённые события и вытеснения из bounded64 истории. Новый source/invalid
снимок сначала очищает старое изображение. Invalid input закрывает display gate,
частная история остаётся до следующего valid input или dispose. Source closed закрывает
binding. `view` возвращает только копию текущей отображаемой проекции, без доступа
к частному model API. Нет управления героем/сброса history/передачи приказов.

Root ownership резервируется до native discovery. Все nodes обязательны; замена,
отсутствие, скрытие или invalid root закрывают binding при следующем вызове API.
Busy/generation guards предшествуют native calls/DTO reads и защищают от reentry.
Root временно скрывается перед записью; dispose очищает plain labels и освобождает
ownership после cleanup. Закрытый binding не пишет в новое владение тем же root.
Без watcher root проверяется по явным вызовам; источник сам отвечает за доставку
снимков и своевременный dispose, полный server stream не гарантируется.

XML loading проверяет definitions/dependencies, а VM — binding/labels. Это не
нативный hittest/appearance; source package и общий HUD остаются будущими этапами.
