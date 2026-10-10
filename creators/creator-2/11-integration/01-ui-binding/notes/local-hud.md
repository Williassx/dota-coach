# Явная локальная привязка HUD

[Подпункт](../README.md) · [Дизайн](../design.md).

`DotaCoachHudPanels.bind(root, options)` вызывается будущим интегратором явно.
Загрузка script сама ничего не запускает. Root содержит CoachRoster, CoachOrders,
CoachCamera, CoachTargets и CoachHudStatus. Не привязывать эти области одновременно
вручную и через координатор.

Options: обязательные `now` (монотонные локальные ms), `maxAgeMs` (целое 1–60000);
необязательные `send(intent, report)`, `cameraGateway` с check/focus,
`resolveCameraEntity(stableId)` → entity integer или неизвестное значение.
Поля options копируются один раз; неизвестные поля отклоняются. Нет default native
clock, транспорта, entity discovery или данных. Gateway методы сохраняют receiver.

Методы: replaceRoster, updateControl, selectPlayer, clearSelection, updateTargets,
selectTarget, refreshCamera, dispose, isDisposed. Схемы данных остаются схемами
[карточек](../../../02-coach-interface/01-roster-cards/README.md),
[приказов](../../../02-coach-interface/02-status-orders/README.md) и
[целей](../../../03-map-view/03-visibility-targets/notes/targets.md).
Boolean означает локальное принятие обновления, не выполнение в игре.

Выбор обновляет адресата приказов, затем снимает прежний handler камеры до resolver.
Без mapping камера сохраняет имя, но отключена. Resolver exceptions/неверные индексы
не закрывают остальные области. Refresh повторяет mapping без перемещения камеры.
Только существующая кнопка запрашивает фокус, только отдельные тестовые кнопки
приказов вызывают send при допустимом локальном состоянии. Наблюдение цели не
становится приказом. Mapping не доказывает identity или серверные полномочия.

Lifecycle guard проверяет все области перед transport/report и camera check/focus.
Watcher проверяет только жизненный цикл. Initial null observer разрешён в binding
phase; при его ошибке router откатывает собственный запуск. Родитель удерживает
владение root до конца частичного rollback, закрывает только созданные им handles.
Dispose скрывает свои области и очищает таймеры; чужие привязки не закрывает.
Закрытие UI не является отменой уже переданного серверного запроса.

Команда из корня репозитория:

```sh
node --test creators/creator-2/11-integration/01-ui-binding/tests/hud-binding.test.cjs
```

Native HUD/clock/visibility/identity, серверная интеграция, восстановление запросов
после reload и проверка второго владельца остаются открытыми.
