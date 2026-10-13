# C2 рассмотрел предложение C1: переходник пока не определён

Основание — новое поручение пользователя подключить переданные файлы C1 и затем
продолжить C2. C1 коммиты и ограниченные исправления опубликованы в `0edbd9f`;
C2 grammar diagnostic — в `108b6dd`. Ведущий146, автор этой заметки — C2/root.
Это рассмотрение существующих форм, не новая общая версия контракта.
[Срез исходников/полей](c1-gap-review-2026-10-13.json),
[C1 предложение](../../../../creator-1/01-foundation/03-command-contract/notes/contract-review.md),
[C2 требования](ui-contract-input.md), [общая область](../../../../shared/contracts/README.md).

## Что фактически имеется

| Область | C2 сейчас | C1 сейчас | До общей интеграции |
|---|---|---|---|
| Диагностический ping | protocol_version/request_id и адресный probe_result | отдельная native probe сцена; общего event handler нет | отдельно согласовать имена/версию и sender/result correlation |
| Игровой приказ | local ticket/recipientId/epoch/action, capture при begin | предложение orderId/orderType/actorEntity/position или targetEntity/revision | определить wire envelope; local ticket не становится orderId/правом автоматически |
| Идентичность | stable id/name/side/availability для представления | logical projectId→seat/entity/owner binding и pure guards | trusted session/entity generation, ownership, team/alive observation; unit name+index не доказывают identity реального игрока |
| Режим и свежесть | snapshot id/playerName/mode/epoch/revision/side/availability; равные revision с другими полями отклоняются | Manual.Request/Confirm/Leave, binding revision и guards generation; общего snapshot producer нет | определить источники каждого поля, отдельные пространства revision/epoch/generation и resync после reload |
| Принятие/исход | report sequence/stage/reason; accepted≠MANUAL, mode-observed≠permission | arbiter admission, event seq/order links/mode tags; outcome emitter нет | versioned addressed event, actor/request/epoch binding, reject/complete/cancel/AI-return причинность |
| Голос | final utteranceId/text/rosterRevision; proposal farm/retreat/regroup/hold + recipientIds | exact structured farm/retreat/gather/attack + string target; source coach/origin voice | mapping нельзя угадывать: hold отсутствует, regroup≠gather без решения; recipients не engine targets |
| Возврат/lease | ACK timeout показывает unknown; local UI не отменяет серверное действие | pure return EnterManual/StartReturn/FinishReturn; свежая числовая revision нужна, engine reevaluation не доказана | серверный lease/clock/pause/death/disconnect/reload и actual AI action после возврата |
| Допустимое наблюдение | private projection имеет sourceAuthorizationConfirmed/nativeConfirmed=false | pure visible flag filtering, caller предоставит clock/visibility/identity | trusted observation source и hidden-state invariance; frontend filter не authorization |

## Ограниченные совпадения

Непустой строковый correlation id и nonnegative safe integer revision пригодны
для дальнейшего обсуждения. Они не устанавливают единую область revision или
источник authority. Исправленный voice producer действительно проходит pure
арбитр с source=coach; origin=voice — metadata, не authenticated sender.
Это checked C1 producer→arbiter, не проверенная цепь C2 ASR→C1→Dota.

C1 contract examples содержат локальный validate в test-файле. Это примеры формы,
не runtime endpoint. Проверки bool/nan/malformed/full envelope и ownership для
этого примера ещё требуют будущего schema решения; не использовать его как
production authorization validator. EventLog seq — порядок локального журнала;
он не объявлен sequence каждого конкретного ответа C2. Его clock передаёт caller,
паузы/lease/реальная game time этим кодом не подтверждаются.

## Следующий согласуемый подпроект

1. Автор общей версии C1 фиксирует отдельно diagnostic ping и игровой envelope,
   C2 рассматривает потребительские поля. Не расширять fixed source bundles до этого.
2. Оба владельца устанавливают trusted session/actor identity и источники snapshot,
   scope epoch/revision/sequence, дедупликацию и resync. Не выдавать UI данные за право.
3. Определяют lease/game clock/отмену/возврат и outcome emitter; подтверждают реальные
   native APIs/ownership. `Confirm(true)` caller не становится server evidence.
4. Только затем один переходник преобразует versioned wire DTO в existing private
   UI проекции; C1 guards и engine adapter остаются единственным authoritative path.
   Unknown version/actor/permission/mapping должны закрывать отправку.
5. Приёмка содержит stale/duplicate/foreign sender/death/replacement/reload и
   настоящую передачу/возврат того же героя. Source VM и эта таблица её не закрывают.

До рассмотрения C1 общий contracts каталог и runtime UI не изменены. Checkbox
совместной передачи/приёмки не отмечены, C2progress54/213 сохранён. Эта записка
добавляет конкретный результат рассмотрения, а не искусственно снимает зависимость.
