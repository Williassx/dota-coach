/* Panorama adapter. Native rendering/lifecycle must still be checked in Dota. */
(function () {
    "use strict";
    var panel = $.GetContextPanel();
    var button = panel.FindChildTraverse("ProbeButton");
    var status = panel.FindChildTraverse("ProbeStatus");
    var client = null;
    var cache = null;
    var controller = null;
    var watcher = null;
    var closed = false;

    function log(event, id) {
        $.Msg("[DotaCoachProbe]", event, id || "");
    }

    function render(state, reason) {
        if (!panel.IsValid() || !button || !button.IsValid() || !status || !status.IsValid()) {
            return;
        }
        var labels = {
            idle: "Нажмите «Проверить связь».",
            pending: "Ожидаем ответ сервера…",
            ok: "Сервер ответил. Связь подтверждена.",
            rejected: "Запрос отклонён сервером.",
            timeout: "Ответ не получен. Повторите проверку.",
            error: "Не удалось отправить запрос. Повторите проверку.",
            unavailable: "Проверка связи недоступна."
        };
        if (state === "rejected") {
            labels.rejected += reason === "unsupported_version" ?
                " Версия обмена не поддерживается." : " Проверьте формат запроса.";
        }
        status.text = labels[state] || labels.unavailable;
        button.enabled = state !== "pending" && state !== "unavailable";
    }

    function dispose() {
        if (closed) { return; }
        closed = true;
        if (watcher !== null) {
            try { $.CancelScheduled(watcher); }
            catch (error) { log("watcher_cancel_failed"); }
            watcher = null;
        }
        if (client) { client.dispose(); }
        if (button && button.IsValid()) { button.ClearPanelEvent("onactivate"); }
        if (cache && cache.controller === controller) { cache.controller = null; }
    }

    function showUnavailable() {
        try { render("unavailable", "none"); }
        catch (error) { log("unavailable_label_failed"); }
    }

    function watch() {
        watcher = null;
        if (closed) { return; }
        if (!panel.IsValid()) {
            dispose();
            return;
        }
        try { watcher = $.Schedule(0.25, watch); }
        catch (error) {
            dispose();
            showUnavailable();
            log("watcher_unavailable");
        }
    }

    try {
        var config = GameUI.CustomUIConfig();
        cache = config.dotaCoachProbe;
        if (!cache) {
            cache = {
                boot: Date.now().toString(36) + "-" + Math.floor(Math.random() * 4294967296).toString(36),
                sequence: 0,
                controller: null
            };
            config.dotaCoachProbe = cache;
        }
        if (cache.controller) { cache.controller.dispose(); }
        if (!button || !status || !panel.IsValid()) { throw new Error("Probe panels unavailable"); }

        client = DotaCoachProbe.create({
            subscribe: function (callback) {
                return GameEvents.Subscribe("dota_coach_probe_result", function (message) {
                    if (closed) { return; }
                    if (!panel.IsValid()) { dispose(); return; }
                    callback(message);
                });
            },
            unsubscribe: function (handle) { GameEvents.Unsubscribe(handle); },
            send: function (message) { GameEvents.SendCustomGameEventToServer("dota_coach_probe_request", message); },
            schedule: function (delay, callback) { return $.Schedule(delay, callback); },
            cancelTimer: function (handle) { $.CancelScheduled(handle); },
            nextRequestID: function () {
                cache.sequence += 1;
                return "probe-" + cache.boot + "-" + cache.sequence;
            },
            render: render,
            log: log,
            onUnavailable: function () { dispose(); showUnavailable(); }
        });
        controller = { dispose: dispose };
        cache.controller = controller;
        button.SetPanelEvent("onactivate", function () {
            if (!panel.IsValid()) { dispose(); return; }
            client.request();
        });
        watcher = $.Schedule(0.25, watch);
        log("panel_ready");
    } catch (error) {
        dispose();
        showUnavailable();
        log("panel_unavailable");
    }
}());
