# API source-панели истории

Сначала загрузить definitions `orders_timeline_state.js` и `orders_timeline_panel.js`
в один context. `DotaCoachOrdersTimelinePanels.bind(root)` вызывается интегратором
явно; root содержит nodes из [XML](../src/panorama/layout/custom_game/orders_timeline.xml).
Нет bootstrap/демо/таймеров/событий UI/Game API.
[Отдельный source-пакет](../../../11-integration/02-addon-packaging/notes/orders-timeline-package.md)
добавлен; нативная установка не выполнена.

- `record(orders.view())` → bool. Один Orders на весь lifecycle; recorded/unchanged
  открывают display gate. Invalid snapshot возвращает false и очищает отображение;
  private история сохраняется, следующая valid запись может открыть её снова.
  Закрытый источник закрывает binding. Корневые guards/очистка выполняются до DTO.
- `refresh()` → bool; только перерисовка. Не захватывает новые снимки и не восстанавливает
  invalid gate. Не создавать второй экземпляр истории параллельно этому binding.
- `view()` → копия ready/events/totalStored/hiddenStored/droppedEvents/closed;
  во время native/DTO preflight — null. Это отображаемая проекция, не private model API.
- `dispose()`/`isDisposed()`: явное закрытие и просмотр lifecycle. Dispose удаляет имена,
  очищает Labels/скрывает root и освобождает ownership после cleanup. Старый binding
  не читает DTO и не пишет в повторно привязанный root.
  isDisposed также проверяет дерево; при reentry во время операции возвращает только
  текущий closed flag, не вызывает native discovery повторно.

Показаны последние шесть событий от старых к новым. hiddenStored — сохранённые64,
которые не вошли в последние6, droppedEvents — удалённые сверх capacity64. Оба
счётчика видны. Все Labels html=false; собственные stage captions отличают сообщения
источника от подтверждённого эффекта. Нет клика/приказа/очистки correlation history.

Root/node invalidity, hide/replace/missing проверяются на каждом явном вызове API.
Watcher отсутствует: caller обязан вовремя передавать снимки и вызывать dispose.
Скролл, appearance/hittest, source package, общий HUD/сервер и другой владелец открыты.
