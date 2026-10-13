# Diagnostic probe v1 — candidate для TEST сцены

**Статус:** кандидат C1-01-03/C2-01-02 для отдельной diagnostic fixture.
Единственный автор этой версии — исполнитель C1; рассмотрение обеими библиотеками,
native sender semantics и human second owner остаются отдельными проверками.
Это не общий контракт игровых приказов, прав ввода, идентичности игрока или lease.

## Wire envelope

Client → server, event `dota_coach_probe_request`, ровно два поля:

```json
{"protocol_version":1,"request_id":"TEST-diagnostic-1"}
```

`request_id` — непустой Lua string длиной 1..64 bytes, без начального/конечного
пробела и ASCII control bytes 0..31/127. Текущий TEST corpus использует ASCII IDs;
Unicode length semantics между JS и Lua не считаются подтверждёнными этим тестом.
`protocol_version` — finite положительное целое Lua number. Версия 1 поддерживается;
другое положительное целое отклоняется как `unsupported_version`. String/boolean,
NaN/Infinity, ноль, отрицательное или дробное значение — `invalid_request`.
Таблица с metatable, отсутствующими/лишними полями также недопустима.

Server → один проверенный native player, event `dota_coach_probe_result`, ровно
четыре поля, ответ всегда объявляет поддерживаемую версию 1:

```json
{"protocol_version":1,"request_id":"TEST-diagnostic-1","status":"ok","reason":"none"}
```

Разрешённые пары: `ok/none`, `rejected/unsupported_version`,
`rejected/invalid_request`. Если id usable, malformed envelope получает отказ с
тем же id. Если usable id нет, response отсутствует. Идентификатор не нормализуется.
Pure `diagnostic_ping.evaluate(payload)` не читает движок и не вызывает transport.
Повтор valid diagnostic id допустим: ping ничего не исполняет; это не dedup policy
игровых приказов. Client correlation/lifecycle остаётся в existing Probe model.

## Native sender boundary

TEST entrypoint `ping_game_mode.lua`, установленный как `addon_game_mode.lua`,
при `Activate` регистрирует один listener. Для каждого callback sender проверяется
сначала, до чтения payload: `EntIndexToHScript(source_index)` → entity с
`GetPlayerID()` → `PlayerResource:GetPlayer(id)` должен быть той же entity.
Source index/player id — finite nonnegative integers в диапазоне native int32.
Ошибка API, missing entity/player, invalid id или identity mismatch → no reply.
Нельзя выбирать получателя из payload `PlayerID` или делать broadcast fallback.

Если callback table содержит engine metadata `PlayerID`, она удаляется из копии
только при точном numeric совпадении с уже проверенным native player id. Mismatch
или неверный тип сохраняются как лишнее wire поле: при usable id evaluator
возвращает `rejected/invalid_request` только уже проверенному native sender.
Без usable id reply отсутствует. Остальные поля не удаляются: pure evaluator
должен отказать лишнему wire envelope. Исходный payload не изменяется.
Результат отправляется только `Send_ServerToPlayer` проверенному handle.

Trace `DCPING_SERVER` содержит лишь sourceindex, entity type/presence, player id,
native-match, metadata и result. `metadata` — только enum: `uninspected` при
активации, неизвестном sender или не-table payload; для проверенного sender и
table payload `rawget(PlayerID)` даёт `absent`, `matching_native` при точном
numeric совпадении или `mismatch`. Категория описывает поле на входе callback,
не происхождение metadata: `matching_native` сама по себе не доказывает, что
движок заменил поле клиента, а `absent` не доказывает причину удаления.
Не логируются raw payload/значение его PlayerID, аккаунт или имя пользователя.
Callback sourceindex semantics ещё требуют actual installed-build evidence;
неудача разрешения не даёт основания подменять sender присланным PlayerID.

Ни unit creation, ни orders, ни settings/microphone/ASR, ни управление игрой не
входят в этот модуль. Stubbed Lua51 assertions не являются native приёмкой.
