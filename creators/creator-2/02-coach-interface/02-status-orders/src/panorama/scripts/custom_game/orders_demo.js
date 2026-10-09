/* Explicit simulation entry. Reports below never execute orders in Dota. */
(function () {
    "use strict";
    var root = $.GetContextPanel();
    var client = null;
    var cache = null;
    var controller = null;
    var scheduled = [];
    var closed = false;

    function dispose() {
        if (closed) { return; }
        closed = true;
        for (var n = 0; n < scheduled.length; n += 1) {
            try { $.CancelScheduled(scheduled[n]); } catch (error) { /* Context may be gone. */ }
        }
        scheduled = [];
        if (client) { client.dispose(); }
        if (cache && cache.dotaCoachOrdersDemo === controller) { cache.dotaCoachOrdersDemo = null; }
    }
    function unavailable() {
        try {
            var result = root.FindChildTraverse("OrderResult");
            if (root.IsValid() && result && result.IsValid()) {
                result.html = false;
                result.text = "Демонстрация приказов недоступна.";
            }
        } catch (error) { /* Context may be gone. */ }
    }
    function schedule(delay, callback) {
        var handle = $.Schedule(delay, function () {
            var index = scheduled.indexOf(handle);
            if (index !== -1) { scheduled.splice(index, 1); }
            if (closed) { return; }
            if (!root.IsValid() || (client && client.isDisposed())) { dispose(); return; }
            try { callback(); }
            catch (error) { dispose(); unavailable(); }
        });
        scheduled.push(handle);
    }
    function simulatedSend(intent, report) {
        var stages = ["accepted", "executing", "completed"];
        function phase(index) {
            schedule(0.1, function () {
                report({ sequence: index + 1, stage: stages[index], reason: null });
                if (client.isDisposed()) { dispose(); return; }
                if (index + 1 < stages.length) { phase(index + 1); }
            });
        }
        phase(0);
    }
    function watch() { schedule(0.25, watch); }
    try {
        cache = GameUI.CustomUIConfig();
        if (cache.dotaCoachOrdersDemo) { cache.dotaCoachOrdersDemo.dispose(); }
        client = DotaCoachOrderPanels.bind(root, simulatedSend);
        controller = { dispose: dispose };
        cache.dotaCoachOrdersDemo = controller;
        if (!client.setRecipient(DotaCoachOrdersDemoData)) { throw new Error("Invalid orders fixture"); }
        watch();
    } catch (error) {
        dispose();
        unavailable();
    }
}());
