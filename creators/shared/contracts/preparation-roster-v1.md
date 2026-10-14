# Preparation roster v1 — ограниченное подтверждение TEST состава

Автор root/C2; C1 producer/validator, C2 strict consumer, техническая проверка
другим исполнителем обязательна. Сценарий пользователь разрешил в автономном плане
13октября2026. Только read-only roster пяти synthetic TEST профилей; не start5×5,
не подтверждение сходства людей, не submit частного client preparation draft.

Events: dota_coach_roster_request client→server; dota_coach_roster_state server→
verified native sender. Sender source entity/GetPlayerID/PlayerResource equality
через manual native resolver; ID из payload не выбирает получателя. Matching
native PlayerID strip из копии; mismatch/extra field invalid_request.

Request exact {protocol_version:1,request_id}. request_id ASCII[A-Za-z0-9_-]1..64.
Response exact8 fields {protocol_version:1,request_id,session_id,revision,status,
reason,synthetic:1,assignments}. session_id opaque serverASCII1..64; revision positive
integer<=2147483647. status confirmed|rejected; reasons none|invalid_request|
unsupported_version|not_ready. rejected assignments={} и reason!=none;
confirmed reason=none, exactly5 assignments object slots string1..5, никакойarray.

Каждый entry exact5 {id,hero,role,coverage,warning}: id TEST profileASCII1..64;
hero npc_dota_hero_[a-z0-9_]+; unique id/hero; roles integers1..5 unique;
coverage finite0..1 serverdefinition; warning '' либо weak-coverage,
weak-coverage iff coverage<0.5. synthetic1 применим ко всем записям.

C1 confirm() получает только server-owned TEST definitions и фиксированные
assignments, валидирует count/id/hero/role/compatibility/coverage. Native request
не передаёт profiles/assignments; подтверждение не строится из client success flag.
Addressed snapshot с request correlation, новый replyrevision, no broadcast.

C2 read-only create/bind/dispose: exact schema and types, no forbidden getters
после dispose, clone consumed data, matching pending request before sessionchange,
strict revision highwater. Timeout=>unknown/requery толькопоявномуsync, no false
confirmed state. confirmed snapshot означает server roster validation в этой
TEST сцене, не permission manual move/start/native5×5/profile fidelity.
