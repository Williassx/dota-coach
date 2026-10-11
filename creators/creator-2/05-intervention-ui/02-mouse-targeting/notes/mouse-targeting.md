# Предложения действия по клику

[Родитель](README.md) · [Спецификация](../design.md).

Загрузить mouse_proposal_state.js и создать `DotaCoachMouseProposals.create()`.
Модель без зависимостей, автоматически не создаётся и мышь не перехватывает.

| Метод | Локальный смысл |
| --- | --- |
| `captureActor({id,playerName,epoch})` | впервые зафиксировать виртуального адресата |
| `proposeMove({x,y,z})` | заменить draft на движение к числовой точке |
| `proposeTarget(targetsView)` | заменить draft на attack / last_hit / deny |
| `view()` | независимая копия actor/proposal, null пока занято |
| `reset()` | убрать actor/draft, не откатывая serial; требуется новое capture |
| `dispose()` | закрыть модель и удалить сохранённые сведения |

Пока actor captured, новые capture не читают DTO и возвращают false. Поэтому
смена выделенной карточки не переносит draft. Каждый accepted propose увеличивает
serial и заменяет предыдущую точку/цель. Invalid propose очищает draft, сохраняя
actor. Reset — только локальная операция, не серверная отмена вмешательства.

Point exact own x/y/z: finite primitive numbers; local caps x/y±32768, z±8192.
Это предварительная проверка входа, не проверенная карта Dota. Target input —
точный [Targets.view](../../../03-map-view/03-visibility-targets/notes/targets.md)
того же источника, полученный caller непосредственно перед предложением.
Status только ready, alive=true. Enemy hero → attack; enemy creep → last_hit;
ally creep → deny; ally hero и dead/unknown/stale не принимаются.
Не-ready проверяется до чтения target descriptors; лишние поля не фильтруются,
а отвергаются без чтения их значений. В output entityIndex не переносится.

Draft не отслеживает TTL после создания и не устанавливает freshness/authorization:
caller обязан обновлять наблюдение, а сервер заново проверять допустимость цели,
identity, lease, смерть/паузу и игровые условия добивания. Только наличие крипа
не подтверждает право на last hit/deny. UI/transport и все эти проверки открыты.

View содержит actor/proposal/closed, evidence=local_click_proposal и неизменные
canSend=false, nativeConfirmed=false, sourceAuthorizationConfirmed=false.
Нет native entity, серверного ticket или оставшегося времени вмешательства.
Предложение не означает, что команда разрешена, отправлена или выполнена.
Observed MANUAL/ACK не заменяют отдельное доказанное право ручного ввода.

Без handlers/timers/game API/storage/transport; busy guard до traps, nested methods
отвергаются без чтения DTO. Dispose во время инспекции отменяет commit; closed view
пустой, closed входы не читаются. Один instance на источник/сцену.
