# API сцены наблюдения матча

[Родитель](README.md) · [Дизайн](../match-observation-design.md) ·
[Упаковка](../../02-addon-packaging/notes/match-observation-package.md).

После загрузки пяти definitions в одном контексте явно вызвать
`DotaCoachMatchObservationPanels.bind(root)` для root `CoachMatchObservation`.
Пакет не выполняет это автоматически; реальный bootstrap остаётся отдельным шагом.
Внутри создаются ровно два private child bindings существующих панелей; наружу
handles/models не передаются. Прямые сторонние bindings в этих scopes не смешивать.

| Метод | Результат и смысл |
| --- | --- |
| `updateOpponents({revision,players})` | bool; передать минимальный публичный DTO одной области |
| `recordOrder(ordersView)` | bool; записать presentation snapshot одного Orders instance |
| `refresh()` | bool; проверить дерево и повторно показать обе области |
| `view()` | copied `{closed,opponents,history,nativeConfirmed:false}`; null во время незакрытой занятой операции |
| `dispose()` | закрыть оба private children, очистить status, скрыть root |
| `isDisposed()` | проверить parent/children на явном вызове, вернуть closed |

Источники независимы: нет общей revision, server epoch или transport. Ошибочный
public roster очищает только карточки, history остаётся доступной. Ошибочный
Orders view закрывает только её display gate. В группе готовность каждой области
показана отдельно; nativeConfirmed всегда false. После dispose view содержит
opponents=null/history=null. Повторные закрытые API не читают DTO/дерево.

У opponent source остаётся accepted highwater и strictly-newer recovery;
у history — captured actor, latest6/hiddenStored/droppedEvents и локальный журнал.
Один instance на источник каждой области; смена источника требует новый bind.
Входы определены в [public roster](../../../07-match-screen/02-opponent-cards/notes/public-roster.md)
и [history panel](../../../07-match-screen/03-orders-timeline/notes/panel.md).

Parent скрывается, changing child очищает текст до DTO traps, group view занят.
Все status/hosts/scopes и внутренние обязательные элементы проверяются, включая
пустые slots. Missing/hidden/replaced/invalid node закрывает всю группу. Observer
отсутствует: интегратор обязан доставлять обновления, refresh или dispose.
Parent ownership резервируется до native callbacks и сохраняется до завершения
cleanup; старый closed API не пишет в новое открытие.

Если group bind не получил оба child handles, cleanup закрывает только созданные
им bindings, восстанавливает прежнюю видимость parent и сохраняет его status.
Это защищает уже независимо работающий child от неудачной попытки объединения.
После успешного приобретения обеих областей parent полностью принадлежит группе.

Только read-only source-сцена. Нет приказов/голоса/своего состава/камеры/карты,
доказанной серверной авторизации, игрового эффекта или полной нативной приёмки.
sourceAuthorizationConfirmed=false у opponents; история — presentation snapshots.

[Native smoke](../reports/native-observation-2026-10-12.md) отдельно проверил
explicit public API/render/lifecycle в TEST addon. Bind получает inner named
CoachMatchObservation внутри anonymous canvas; это не production bootstrap/input.
