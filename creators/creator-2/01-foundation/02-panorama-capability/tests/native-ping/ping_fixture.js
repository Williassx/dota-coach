/* TEST only: actual diagnostic events, never game orders or permission. */
(function () {
    "use strict";
    var root = $.GetContextPanel(), status = root.FindChildTraverse("ProbeStatus");
    var button = root.FindChildTraverse("ProbeButton"), badge = root.FindChildTraverse("NativePingFixtureStatus");
    var data = {phase: "waiting", records: [], sends: [], replies: [], disposedReads: null,
        physicalInputTested: false, gameCommandsSent: 0, serverAuthorityConfirmed: false};
    GameUI.CustomUIConfig().dotaCoachNativePingFixture = data;
    var serial = 0, client = null, owner = null, requestedVariant = "valid", waitAttempts = 0;
    function record(phase, pass, details) {
        var row = {phase: phase, pass: pass, details: details || null, clientState: data.clientState,
            clientReason: data.clientReason, utcMs: Date.now()};
        data.phase = phase; data.records.push(row);
        badge.text = "TEST ONLY — diagnostic " + phase + " " + (pass ? "PASS" : "FAILED") + ". No game orders.";
        $.Msg("[C2NativePing] " + phase + " pass=" + pass + " " + JSON.stringify(row));
        return pass;
    }
    function bind() {
        var closed = false, callback = null;
        var model = DotaCoachProbe.create({
            subscribe: function (receive) {
                callback = function (message) {
                    if (closed) { return; }
                    data.replies.push({protocol_version: message.protocol_version, request_id: message.request_id,
                        status: message.status, reason: message.reason});
                    receive(message);
                };
                return GameEvents.Subscribe("dota_coach_probe_result", callback);
            },
            unsubscribe: function (handle) { GameEvents.Unsubscribe(handle); },
            schedule: function (delay, fn) { return $.Schedule(delay, fn); },
            cancelTimer: function (handle) { $.CancelScheduled(handle); },
            nextRequestID: function () { serial += 1; return "native-ping-" + Date.now().toString(36) + "-" + serial; },
            send: function (payload) {
                var wire = {protocol_version: payload.protocol_version, request_id: payload.request_id};
                if (requestedVariant === "unsupported") { wire.protocol_version = 2; }
                if (requestedVariant === "extra") { wire.unexpected = true; }
                if (requestedVariant === "spoofed-player-id") { wire.PlayerID = 99999; }
                data.sends.push({variant: requestedVariant, wire: JSON.parse(JSON.stringify(wire))});
                GameEvents.SendCustomGameEventToServer("dota_coach_probe_request", wire);
            },
            render: function (state, reason) {
                data.clientState = state; data.clientReason = reason;
                var text = {idle: "TEST: diagnostic ready.", pending: "Ожидаем ответ сервера…",
                    ok: "Сервер ответил. Связь подтверждена.", rejected: "Запрос отклонён: ",
                    timeout: "Ответ не получен.", error: "Отправка не удалась.", unavailable: "Проверка связи недоступна."};
                status.text = (text[state] || "TEST unavailable") + (state === "rejected" ? reason : "");
                button.enabled = state !== "pending" && state !== "unavailable";
            },
            log: function (event, id) { $.Msg("[C2NativePingState] " + event + " " + (id || "")); }
        });
        button.SetPanelEvent("onactivate", function () { if (!closed) { requestedVariant = "valid"; model.request(); } });
        return {request: model.request, oldDelivery: function (message) { if (callback) { callback(message); } },
            dispose: function () { if (closed) { return; } closed = true; model.dispose(); button.ClearPanelEvent("onactivate"); }};
    }
    function phase(variant, predicate, next) {
        requestedVariant = variant;
        var beforeReplies = data.replies.length;
        if (!client.request()) { record(variant, false, "request-refused"); return; }
        $.Schedule(3, function () {
            var reply = data.replies.length > beforeReplies ? data.replies[data.replies.length - 1] : null;
            if (!record(variant, !!reply && predicate(reply), reply)) { return; }
            $.Schedule(10, next);
        });
    }
    function disposePhase() {
        var old = owner; old.dispose(); var state = data.clientState, reads = 0;
        var stale = {}; Object.defineProperty(stale, "protocol_version", {get: function () { reads += 1; return 1; }});
        old.oldDelivery(stale); data.disposedReads = reads;
        record("disposed", reads === 0 && state === "unavailable" && data.clientState === state,
            {staleReads: reads, gameCommandsSent: 0, sentWires: data.sends, replies: data.replies});
    }
    function validAgain() { phase("valid-again", function (r) { return r.status === "ok" && r.reason === "none"; }, disposePhase); }
    function spoof() {
        phase("spoofed-player-id", function (r) {
            return r.protocol_version === 1 && ((r.status === "ok" && r.reason === "none") ||
                (r.status === "rejected" && r.reason === "invalid_request"));
        }, validAgain);
    }
    function extra() { phase("extra", function (r) { return r.status === "rejected" && r.reason === "invalid_request"; }, spoof); }
    function unsupported() { phase("unsupported", function (r) { return r.status === "rejected" && r.reason === "unsupported_version"; }, extra); }
    function start() {
        if (Players.GetLocalPlayer() < 0) {
            waitAttempts += 1;
            if (waitAttempts >= 1800) { record("bound", false, "local-player-timeout"); return; }
            $.Schedule(0.25, start); return;
        }
        client = bind(); owner = client;
        record("bound", data.clientState === "idle", {localPlayer: Players.GetLocalPlayer()});
        $.Schedule(10, function () { phase("valid", function (r) { return r.status === "ok" && r.reason === "none"; }, unsupported); });
    }
    $.Schedule(0.5, start);
}());
