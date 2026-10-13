/* TEST observer around the unchanged original auto adapter. Programmatic activation, not mouse/hittest. */
(function () {
    "use strict";
    var root = $.GetContextPanel(), button = root.FindChildTraverse("ProbeButton");
    var status = root.FindChildTraverse("ProbeStatus"), badge = root.FindChildTraverse("NativePingFixtureStatus");
    var data = {records: [], physicalInputTested: false, gameCommandsSent: 0, originalAdapter: true};
    GameUI.CustomUIConfig().dotaCoachNativePingAdapter = data;
    function record(phase, pass, details) {
        var row = {phase: phase, pass: pass, details: details || null, adapterStatus: status.text, utcMs: Date.now()};
        data.records.push(row); badge.text = "TEST original adapter — " + phase + " " + (pass ? "PASS" : "FAILED");
        $.Msg("[C2NativePing] " + phase + " pass=" + pass + " " + JSON.stringify(row));
        return pass;
    }
    function config() { return GameUI.CustomUIConfig().dotaCoachProbe; }
    function activate(phase, next) {
        var before = config().sequence;
        try { $.DispatchEvent("Activated", button, "mouse"); }
        catch (error) { record(phase, false, "native-dispatch-failed"); return; }
        $.Schedule(3, function () {
            if (!record(phase, config().sequence === before + 1 && status.text === "Сервер ответил. Связь подтверждена.",
                {sequence: config().sequence, buttonEnabled: button.enabled, physicalInputTested: false})) { return; }
            $.Schedule(10, next);
        });
    }
    function dispose() {
        config().controller.dispose();
        record("disposed", config().controller === null && button.enabled === false && status.text === "Проверка связи недоступна.");
    }
    $.Schedule(0.5, function () {
        if (!record("bound", !!config() && !!config().controller && button.enabled, {originalAdapter: true})) { return; }
        $.Schedule(10, function () { activate("activated", function () { activate("repeated", dispose); }); });
    });
}());
