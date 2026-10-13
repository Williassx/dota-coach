# Согласованный первый игровой сценарий: временное перемещение

Пользователь13октября согласовал сценарий и прямо поручил внедрение. Ведущий69;
C2/root владеет спецификацией, общим wire контрактом и Panorama; C1 исполнитель
владеет новым server/controller, отдельный исполнитель — упаковкой. Текущий checkout.
Это один герой TEST/synthetic в addon_template/template_map, не полный матч,
персональная модель или приёмка всей карты. Существующие fixed bundles не меняются.

## Поведение

Карточка выбирает адресата без приказа. Отдельная кнопка запрашивает вмешательство.
Только server MANUAL snapshot разрешает перемещение. Левый click по миру задаёт
точку через GameUI.GetScreenWorldPosition; кнопка отмены отправляет cancel.
Более поздний выбор не переносит текущий actor. Maximum5 game seconds с выдачи
разрешения, completion по distanceXY<=80, cancel/timeout/death/replacement/end
завершают его. Пауза game clock не расходует lease и не выдаёт orders.
Server stop отменяет ручной путь; fresh synthetic AI observation выбирает новую
точку и настоящий move order. Только подтверждённая выдача AI order означает
AI resumed; death/replacement => INACTIVE, не ложное AI resumed. Respawn требует
новой generation и нового grant. Timeout UI показывает unknown и resync.

## Сервер и данные

[Общий протокол](../../../shared/contracts/manual-move-v1.md) задаёт точные поля.
Game sender разрешается по source entity/GetPlayerID/PlayerResource equality;
payload PlayerID никогда не выбирает sender. Matching native metadata удаляется
из копии, несовпадающее поле отклоняется. Server binds TEST actor to verified seat,
team/alive/current entity handle; native handle заменён => generation++. Client
не передаёт entityIndex. Session создаётся заново Activate, остальные counters
разделены: generation — binding, epoch — grant, revision — snapshot mutation.
Из bounded dedup registry max128 IDs/session/sender не вытесняются accepted IDs;
переполнение отвергает новые actions до нового session, resync остаётся доступным.
Replay same ID/same exact body возвращает current state без повторного effect;
sameID/differentbody отклоняется. Только owner addressed snapshots/replies.

## Границы реализации

Новый pure controller имеет injected game clock/observe/execute hooks; native
adapter использует GameRules:GetGameTime/IsGamePaused, ExecuteOrderFromTable,
entity equality и GridNav traversal/blocking. Position finite XYZ и bounded
distance<=2000 от героя, X/Y<=16000,Z<=2048; engine effect arrival не равен APIreturn.
Новый UI consumer строгий, dispose до чтения DTO, subscription cleanup, server
revision highwater и отдельный request outcome. Native bootstrap включает только
новые source outputs, не меняет существующие demo/production source bundles.
Engine TEST fixture может programmaticallyActivate для регрессии, но это
не physical mouse/hittest. Native physical input проверяется только доступным
реальным input каналом; отсутствие канала не подменяется synthetic clicks.

## Приёмка

Lua RED/GREEN: unauthorized/NaN/schema/stale generation/epoch/session, duplicate,
five-second lease/pause/cancel/arrival/death/replacement/clock regression,
failed stop/AI order и replacement guard. JS RED/GREEN: select no send, grant,
move/cancel correlation, stale snapshots/dispose/reload/timeouts/invalid bodies.
Bundle exact outputs/fresh path/tamper/linked input guards. Full catalog required.
Native ownPID receipt/compilehashes/actualframe/log: AI movement, grant, manual
move, expiry/cancel/arrival, resumed actualAIorder; input proof scope explicit.
Human second owner remains independent and open until actual review.
