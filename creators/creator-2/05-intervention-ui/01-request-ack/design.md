# Локальная проекция запроса ручного вмешательства

**Дата UTC:** 2026-10-10. **Основа:** d5066a2. Пользователь поручил работать самостоятельно.

## Намерение и граница задачи

Тренер выбирает игрока, запрашивает временное ручное управление и видит ожидание/
отказ/наблюдённый режим. Подтверждение получения запроса не означает передачу героя.
C2-05-01 сейчас реализует pure presentation state, без native input, transport,
серверных полномочий, lease/clock/возвратаИИ или изменения общего контракта.
Мышь/действия/отмена/время относятся к следующим частям и C1-04. Полная приёмка открыта.

## Использование существующего source state

Добавить в DotaCoachOrders только read API snapshot(id?): independent copy семи
полей существующего validated snapshot, без выбора/изменения/callback. Без аргумента
возвращает текущего recipient; неизвестный/invalid id или closed →null.
Новая DotaCoachInterventionRequests.create(transportReady) владеет private instance
существующего Orders. Его store/validation/10actors/epoch+revision highwater не
копируются. Component хранит свой selectedid независимо от внутреннего выбора Orders,
который setRecipient переводит на updatedactor. Component не вызывает Orders.begin/report, не использует action move
для запроса MANUAL. Отдельно ведёт выбранный id и один pending request.

## API и данные

update(frame):bool → existing source.setRecipient(frame), затем source.snapshot()
без повторного чтения DTO. select(id|null):bool выбирает только knownactor; выбор
не выдаёт запрос. begin(): copied {ticket,recipientId,epoch,action:"request_manual"}|null.
Новый action — локальное предложение для futuretransport, не утверждённый wire contract.
report(ticket,{sequence,stage,reason}):bool; exact fields, sequence safeint и строго
возрастает; stage accepted/rejected/cancelled; rejected/cancelled требуют boundedreason160.
accepted не terminal и не меняет source mode. expire(ticket) pending→unknown,
результат неизвестен и retry блокирован. notSent(ticket) только stage pending без serverACK→not-sent terminal.
Caller обязан доказать, что транспорт не отправил запрос: timeout/ambiguousexception
не дают этого права; после accepted/unknown переход запрещён.
view()/dispose()/isDisposed(); real action/submit/cancel API отсутствует.

view возвращает копии selected snapshot/request plus plain message, canRequest,
manualModeReported, lifecycle/connection note. Никакого canManualInput/permission token:
локальная проекция не авторизует мышь. canRequest только local eligibility: connected
stricttrue, выбран knownownaliveAI, source не blocked, нет unresolvedrequest.
manualModeReported только observedcurrent snapshot modeMANUAL; не identity/lease proof.
Snapshot MANUAL для pending actor той же epoch завершает request как mode-observed
лишь при revision строго выше capturebegin revision. Такой snapshot может прийти
раньше accepted report; поздний accepted тогда не возвращает pending. Смена epoch
того же actor прекращает correlation с отдельным сообщением о непроверенном старом
исходе. Смена карточки не переносит прежний request; update другого actor не закрывает его.

Invalid/rejectedsource update fail-closes local display/gate для всех cached actors;
сами snapshots/highwater остаются у existing Orders. Для восстановления eligibility
нужен accepted frame нужного actor: per-actor fresh set после invalid полностью
очищается; validA не делает cachedB fresh. update(null) fail-closes, несмотря на
setRecipient(null)=true, поскольку copiedsnapshot отсутствует. Это deliberate conservative UI policy; старый
orders UI не меняет поведения. Повтор exactsame source frame допустим existing store.

## Reentry и ограничения

Generation до каждого external DTO read. Busy скрывает selected/request и отклоняет
nested update/select/begin/report до чтения input; dispose побеждает. После вызова
source store читать только его copiedsnapshot и проверять current token. Текст/числа
проверяются по типу; no coercion. Report exactkeys/ownfields guard после Object.keys
и каждого getter, commits atomic. Один request/counter safeint, source≤10actors;
публичные copies не дают mutability. Definitions inert/no native/timer/storage/network.

## Проверки

ExistingOrders readAPI: independent sevenfield copies, no selection/highwater mutation,
unknown/closed/querybounds. NewVM: request→accepted безMANUAL; fresh snapshot→observed,
old/equal revision/mode/epoch, foreign/dead/inactive/unconnected, captured actor при
смене выбора, invalidsource blocking/recovery, timeoutunknown/late report, notsent,
privatecopies/busy/getters/dispose/no source reread/no native. Пять read-only критиков;
прежние542 повторить, journal/config/fast-forwardmain. C1/shared/native/secondowner открыты.

transportReady означает static adapterConfigured, а не online/serverauthproof.
Пересоздание при reconnect не заменяет authoritative reconciliation; unknown в одной
epoch остаётся unresolved до report/observedmode/epochchange. Dispose UI не отменяет
серверный запрос, localticket не глобальный wireid; mapping требуется futuretransport.
Сообщение unknown называет capturedactor и говорит «исход неизвестен; повтор недоступен».
