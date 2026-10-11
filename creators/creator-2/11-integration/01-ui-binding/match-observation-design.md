# Общая сцена наблюдения матча

[Родитель](README.md). Следующий шаг эскиза пользователя: публичные соперники
сверху, история приказов справа, прозрачный центр для будущей сцены Dota.
Это source-композиция двух уже проверенных областей, без новой карты или механик.

Выбран explicit owned binding вместо общего нового DTO или независимых bootstrap:
один родитель управляет lifecycle двух существующих панелей, источники остаются
независимыми. API `DotaCoachMatchObservationPanels.bind(root)`:
`updateOpponents(snapshot)`, `recordOrder(snapshot)`, `refresh()` → bool;
`view()` → copied `{closed,opponents,history,nativeConfirmed:false}` либо null
во время незакрытой занятой операции; `dispose()`, `isDisposed()`.

Private child bindings используют канонические OpponentPanels и TimelinePanels.
Новых моделей нет. По одному источнику/instance в каждой области; смена источника
требует dispose и нового bind. Не вводим фиктивную общую revision или server epoch.
Invalid одной области очищает её через existing panel, другая остаётся доступной;
готовность показывается отдельно. Parent скрыт и status очищен до DTO reads.
Пока операция busy, вложенные методы отвергаются до native/DTO reads.

Shell: CoachMatchObservation root (initially hidden), MatchObservationStatus,
MatchOpponentHost, MatchHistoryHost. В hosts композиция вставляет по одному root:
OpponentRosterRoot/OrdersTimelineRoot. Каждый обязательный node проверяется на
missing/hidden/replaced/invalid на явном API, включая isDisposed. Владение parent
резервируется до любых native callbacks; повторный bind не меняет живую сцену.
Dispose закрывает группу до cleanup, закрывает оба private children, очищает
status/скрывает root и освобождает parent только после окончания операции.
Partial bind error освобождает лишь созданные child handles. До приобретения обеих
панелей parent visibility сохраняется для rollback; при отказе независимый child
и прежний status не изменяются, parent visibility восстанавливается.
После успешного приобретения действует обычное закрытие всей группы. Старый closed API
не читает входов и не изменяет новый binding. Watcher/timer/transport/handlers нет.

Отдельный пакет использует shell XML/CSS/manifest и binding из C2-11-01 плюс
канонические XML/CSS/два JS каждой области. Выбран composer вместо копирования
разметки: два raw-source fingerprints, повторная композиция в verifier.
Fixed kind `panorama_source_match_observation`: 10 output assets, 2 XML inputs,
5 definitions, 3 CSS, 9 links, 38 ID (4 shell +24 opponents +10 history).
Layout inputs строго фиксированы, root IDs не переименовываются; они различны.
После insert весь topology проверяется; scripts definitions-only, explicit bind.

Панель сообщает смысл наблюдений, ограничения находятся в metadata/docs.
Нет игрового эффекта, native права, серверной авторизации, выбора/управления,
собственных игроков/голоса/камеры. sourceAuthorizationConfirmed=false у opponents,
история — presentation snapshots. Общий игровой HUD, C1 и Windows приёмка открыты.
