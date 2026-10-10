# Локальное состояние запроса MANUAL

[Подпункт](../README.md) · [Дизайн](../design.md).

Загрузите existing orders_state.js перед intervention_request_state.js. Определения
инертны; DotaCoachInterventionRequests.create(adapterConfigured) создаёт один private
Orders store и свою корреляцию. Strict true означает настроенный futureadapter,
а не online/серверное разрешение. Здесь нет транспорта, таймеров или нативных действий.

update(frame) принимает прежние7snapshot fields через existing store. UI-selectedid
независим от внутреннего выбора Orders; update сам не выбирает карточку. select(id|null)
выбирает только knownactor. Неверный source очищает per-actor eligibility для всех;
acceptedA восстанавливает толькоA. Fresh означает принятый snapshot, не TTL/clockproof.

begin() создаёт копию localticket/recipientId/epoch/action=request_manual. Это предложение
для будущего wirecontract, не серверная команда. report(ticket,{sequence,stage,reason})
принимает exact ownfields без extra hidden/symbol, sequence возрастает, accepted/
rejected/cancelled; для отказа/отмены нужна причина. Принятие запроса не меняет mode.
MANUAL snapshot sameactor/epoch и revision>capture переводит request в mode-observed;
наблюдение не доказывает причину перехода, личность игрока, права ввода или lease.

expire(ticket) толькоpending→unknown. Retry недоступен, поздний ответ может уточнить
исход. Unknown/accepted остаются unresolved без authoritative report/mode/epochchange.
notSent(ticket) толькоpending безACK: caller должен знать, что transport не отправлял
запрос. Timeout/неопределённое исключение не дают права на notSent. Серверная отмена
здесь только report; cancellation action и возврат ИИ не реализованы.

view возвращает copied selected/request, localcanRequest и manualModeReported, plain
message. canManualInput/permissiontoken отсутствуют. Сообщение называет capturedname
иID, различает одинаковые имена при смене выбора. Busy скрывает обе копии, nestedcalls
не читают DTO; dispose закрывает источник и не отменяет серверный запрос.

Orders.snapshot(id?) — copied read семи полей; только отсутствие аргумента означает
currentrecipient. Explicit undefined/invalid/unknown/closed→null. Чтение не выбирает
игрока и не потребляет actor revisions. Localticket уникален только в одной instance;
будущий transport обязан маршрутизировать lateACK в originatinginstance/session.

Панель/нативный mouseinput, C1-04/sharedcontract/authority/lease/clock/возвратИИ,
реальныйtransport и проверка второго владельца остаются открытыми.
