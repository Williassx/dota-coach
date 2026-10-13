# Manual move v1 — согласованный ограниченный игровой протокол

Автор root/C2, пользователь согласовал поведение13октября2026. C1 реализует
producer/controller, C2 consumer. Human second-owner review open; native proof
записывается отдельно. Только TEST/synthetic один герой; voice/attack не входят.

Events: `dota_coach_manual_request` client→server,
`dota_coach_manual_state` server→verified owner. Version1. Plain exact objects;
unknown field/type/version rejected; PlayerID transport metadata exception ниже.
IDs ASCII `[A-Za-z0-9_-]{1,64}`, safe nonnegative integer counters<=2^31-1.
Session opaque server string; request ID correlation, не право.

## Запросы

- sync: `{protocol_version:1,request_id,kind:"sync"}`. Без state precondition,
  owner identified by native sender; returns current addressed state.
- acquire: `{protocol_version:1,request_id,kind:"acquire",session_id,
  actor_id,generation,epoch}`. Current AI/live binding+epoch; grants5game seconds.
- move: acquire fields with kind="move" plus `x,y,z`. Requires current MANUAL
  owned lease. Repeated new move supersedes target without extending lease.
- cancel: acquire fields with kind="cancel". Requires current MANUAL lease.

No entity index, owner or clock from client. Position numeric finite, absXY<=16000,
absZ<=2048, XY distance<=2000, GridNav traversable and unblocked before execution.
Server sender comes from source entity+GetPlayerID+PlayerResource:GetPlayer equality;
optional engine `PlayerID` stripped only if equals verified sender, otherwise
invalid_request. Unknown sender drops before DTO inspection.

## Ответ / snapshot (exact17fields)

`{protocol_version:1,session_id,actor_id,generation,epoch,revision,
mode:"AI"|"MANUAL"|"INACTIVE",alive:0|1,remaining:number,
entity_index:number,request_id:string,request_status:"none"|"accepted"|"rejected",
reason:string,transition:string,ai_order_count:number,manual_order_count:number,
server_time:number}`.

sync response request_status=accepted; unsolicited has request_id="",
request_status=none. Unknown/bad ID may drop, no invented correlation.
Native custom event r2 transported Lua true as numeric1; wire alive uses exact0/1,
consumer converts to internalboolean. Pure server snapshot retains boolean.
Counters server generated. remaining=max(0,deadline-gameTime), <=5; snapshot
gameTime not local countdown authority. revision advances each addressed emission;
consumer discards lower/equalrevision and wrongsession except awaited sync allows
new session. Native entity_index is display/camera aid, not caller authorization.

Reasons: none,invalid_request,unsupported_version,not_ready,unauthorized,
stale_session,stale_generation,stale_epoch,not_ai,not_manual,invalid_position,
dedup_limit,request_conflict,clock_regressed,engine_failed,paused.
Transitions: state,granted,move_issued,cancelled,expired,arrived,dead,replaced,
ended,ai_resumed,engine_failed. request_status=accepted means command admission;
move_issued means engine API invoked successfully, not arrival. modeAI and
ai_resumed emitted only after fresh observation and actual AI move call succeeds.
cancelled/expired/arrived transitions occur before AI resumption, allowing both
to appear in journal. dead/replaced/ended setINACTIVE; no false AI resume.

## Lifecycle

Lease maximum5game seconds, pause stops orders and countdown. At arrival<=80XY,
cancel,deadline: Stop then fresh observe then syntheticAI move. Failed effect =>
INACTIVE/engine_failed. Death before effect =>INACTIVE/dead, rebind increments
generation/epoch. Old epoch never revives. UIclose/dispose never cancels server
lease. UI timeout =>unknown+sync. New card selection never alters capturedactor.
Duplicate ID/body performs no new order; changedbody sameID rejected. Store max128
action IDs per sender/session, reject overflow without eviction. Sync exempt.
Disconnect checked native activeplayer; endmatch/controllerclose revokes manual.
General player identity/personal model/common5×5match not proven by TEST binding.

Pause policy: new acquire/move/cancel requests reject with `paused`; sync stays available. No command effects while pause state is true or unknown. Close/disconnect/clock-failure during pause queues one Stop for the same live generation/entity after confirmed unpause; replacement/original owner mismatch discards that cleanup. No AI resume after close/disconnect.

The logical deadline is exactly grant gameTime+5. The native .1-second Think observes expiration on its next tick; measured stop/return timing is reported separately, not a zero-overrun real-time guarantee.
