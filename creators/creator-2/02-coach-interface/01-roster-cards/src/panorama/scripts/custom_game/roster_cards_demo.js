/* This entry is loaded only by the demonstration layout. No server-data fallback. */
(function () {
    "use strict";
    var root = $.GetContextPanel();
    var client = null;
    var cache = null;
    var controller = null;
    var watcher = null;
    var closed = false;

    function dispose() {
        if (closed) { return; }
        closed = true;
        if (watcher !== null) {
            try { $.CancelScheduled(watcher); } catch (error) { /* Already unavailable. */ }
            watcher = null;
        }
        if (client) { client.dispose(); }
        if (cache && cache.dotaCoachRosterDemo === controller) { cache.dotaCoachRosterDemo = null; }
    }

    function unavailable() {
        try {
            var status = root.FindChildTraverse("RosterStatus");
            if (root.IsValid() && status && status.IsValid()) {
                status.html = false;
                status.text = "Демонстрация недоступна.";
            }
        } catch (error) { /* The entire context may be gone. */ }
    }

    function watch() {
        watcher = null;
        if (closed) { return; }
        if (!root.IsValid() || client.isDisposed()) { dispose(); return; }
        try { watcher = $.Schedule(0.25, watch); }
        catch (error) { dispose(); unavailable(); }
    }

    try {
        cache = GameUI.CustomUIConfig();
        if (cache.dotaCoachRosterDemo) { cache.dotaCoachRosterDemo.dispose(); }
        client = DotaCoachRosterPanels.bind(root);
        controller = { dispose: dispose };
        cache.dotaCoachRosterDemo = controller;
        if (!client.replace(DotaCoachRosterDemoData)) { throw new Error("Invalid demonstration roster"); }
        watcher = $.Schedule(0.25, watch);
    } catch (error) {
        dispose();
        unavailable();
    }
}());
