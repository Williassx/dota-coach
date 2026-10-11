# Локальные предложения действий мышью

[Родитель](README.md). Пользователь описал движение, автоатаку, добивание вражеских
крипов и deny союзных. Пока нет C1 permission/lease и native mouse/identity/geometry;
независимый этап готовит только bounded local proposal, без отправки/исполнения.

Выбран private draft вместо native hooks или нового server contract.
`DotaCoachMouseProposals.create()`:
`captureActor({id,playerName,epoch})`, `proposeMove({x,y,z})`,
`proposeTarget(targetsView)` → bool; `reset()`, `dispose()`; `view()` copied либо
null пока busy. Нет handlers/timers/transport, игрового времени или подтверждения.

Actor exact own enumerable data fields, строки ≤64, epoch safe int0..MAX.
Id без крайних пробелов/control. Первое явное capture фиксирует адресата.
Пока actor существует, повторное capture отвергается до чтения DTO: смена выделения
не переносит действие. Для другого адресата требуется явный reset и новое capture;
reset не является отменой серверного вмешательства. Имя/epoch копируются, ID —
виртуальный игрок, не native entity/проверенное право. Invalid first capture не
создаёт actor; предложение без captured actor отвергается до DTO reads.

Move point exact x/y/z, primitive finite numbers, локальные предварительные caps:
x/y ∈[-32768,32768], z∈[-8192,8192]. Это ограничение входа, не геометрия/патч Dota.
Target input — exact existing Targets.view `{status,message,target}`;
только status=ready и target exact `{id,label,team,kind,alive,entityIndex}`.
Не-ready проверяется до target descriptors/значений; дополнительный hidden field
отклоняется без чтения его значения. Message plain string ≤256 (включая пустую),
id/label ≤64, team ally|enemy, kind hero|creep, alive=true, index int0..2147483647.
Модель не определяет native identity или freshness; caller должен получать fresh
Targets.view того же источника. Передавать hidden сведения сюда нельзя, C1 policy
остаётся ответственна за разрешённое наблюдение.

Enemy hero→attack, enemy creep→last_hit, allied creep→deny. Allied hero не даёт
боевого предложения. Наличие живого крипа не доказывает порог добивания/deny:
игровые правила/health/permission проверяются сервером отдельно.
Каждый accepted клик заменяет предыдущий draft, сохраняя actor. Invalid input
очищает proposal до DTO traps; actor сохраняется. Serial монотонный локальный
счётчик accepted proposals, не server ticket/dedup; reset не откатывает serial.

`view()` exact `{actor,proposal,closed,evidence,canSend,nativeConfirmed,sourceAuthorizationConfirmed}`.
Evidence=local_click_proposal, три flags false. Proposal содержит serial/action,
copied actor, point либо null, target либо null. Target output только id/label/
team/kind, entityIndex не выдаётся за транспортную identity. Нет canIssue,
остатка lease, способности или утверждения «выполнено».
Busy guard до caller traps; вложенные операции не читают DTO, dispose при чтении
отменяет commit. Reset во время чтения отвергается. Closed view пустой,
closed методы входов не читают. Один instance на источник/сцену, новый при смене.

Native мышь/клик, привязка к карте/UI, transport/lease/AI return, текущая source
visibility/identity и второй владелец остаются открытыми. Только pure модель.
