/* Native acceptance fixture only. Never included in any fixed source kind. */
(function () {
    "use strict";
    var root, phase, ui, old, rows = [], nowMs = 0, failed = false;
    function node(id) {
        var panel = root.FindChildTraverse(id);
        if (!panel || !panel.IsValid()) { throw new Error("Missing fixture node " + id); }
        return panel;
    }
    function ensure(condition, reason) { if (!condition) { throw new Error(reason); } }
    function noActions() {
        ensure(!node("OrderMove").enabled && !node("OrderAttack").enabled &&
            !node("CameraFocus").enabled, "unexpected enabled action");
    }
    function visibleCards(count) {
        for (var n = 0; n < 5; n += 1) {
            var slot = node("RosterCard" + n);
            ensure(slot.visible === (n < count), "slot visibility " + n);
            if (n < count) {
                ensure(slot.actuallayoutwidth > 0 && slot.actuallayoutheight > 0, "slot geometry " + n);
                ensure(node("RosterName" + n).text.indexOf("TEST") !== -1, "missing TEST label");
                ensure(node("RosterSource" + n).text.indexOf("Синтетический") !== -1, "missing synthetic label");
            }
        }
    }
    function record(name, assertion) {
        try {
            assertion();
            phase.text = "TEST ONLY: synthetic; no server/input | " + name + " PASS";
            $.Msg("[C2NativeBind] " + name + " pass=true");
        } catch (error) {
            failed = true;
            phase.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativeBind] " + name + " pass=false reason=" + String(error));
            if (ui) { ui.dispose(); }
        }
    }
    function after(delay, action, name, assertion) {
        $.Schedule(delay, function () {
            if (failed || !root.IsValid()) { return; }
            try { action(); } catch (error) { record(name, function () { throw error; }); return; }
            $.Schedule(1, function () { if (!failed && root.IsValid()) { record(name, assertion); } });
        });
    }
    $.Schedule(1, function () {
        root = $.GetContextPanel();
        phase = node("NativeHudFixtureStatus");
        for (var n = 0; n < 5; n += 1) {
            rows.push({ id: "TEST-" + n, playerName: "TEST " + n, heroName: null,
                role: n + 1, source: "synthetic", side: "own", availability: "alive" });
        }
        after(0, function () {
            ui = DotaCoachHudPanels.bind(root, { now: function () { return nowMs; }, maxAgeMs: 1000 });
            ensure(ui.replaceRoster(rows), "replace TEST roster rejected");
            ensure(ui.updateTargets({ revision: 1, targets: [] }), "empty targets rejected");
        }, "bound", function () { ensure(!ui.isDisposed(), "bind disposed"); visibleCards(5); noActions(); });
        after(15, function () {
            ensure(ui.updateControl({ id: "TEST-0", playerName: "TEST 0", mode: "AI",
                epoch: 1, revision: 1, side: "own", availability: "alive" }), "TEST control rejected");
            ensure(ui.selectPlayer("TEST-0"), "selection rejected");
        }, "selected", function () {
            ensure(node("RosterCard0").BHasClass("RosterSelected"), "selected class absent");
            ensure(node("OrderRecipient").text.indexOf("TEST 0") !== -1 &&
                node("CameraRecipient").text.indexOf("TEST 0") !== -1, "recipient mismatch");
            visibleCards(5); noActions();
        });
        after(30, function () { ensure(ui.replaceRoster(rows.slice(1)), "TEST removal rejected"); },
            "removed", function () {
                ensure(node("OrderRecipient").text.indexOf("TEST 0") === -1 &&
                    node("CameraRecipient").text.indexOf("TEST 0") === -1, "old recipient retained");
                ensure(node("RosterName0").text === "TEST 1", "roster did not advance");
                visibleCards(4); noActions();
            });
        after(45, function () { old = ui; ui.dispose(); }, "disposed", function () {
            ensure(old.isDisposed(), "dispose did not close handle");
            for (var i = 0; i < 4; i += 1) {
                ensure(node(["CoachRoster", "CoachOrders", "CoachCamera", "CoachTargets"][i]).visible === false,
                    "scope not hidden");
            }
        });
        after(60, function () {
            ui = DotaCoachHudPanels.bind(root, { now: function () { return nowMs; }, maxAgeMs: 1000 });
            ensure(ui.replaceRoster([{ id: "TEST-FRESH", playerName: "TEST FRESH", heroName: null,
                role: 1, source: "synthetic", side: "own", availability: "alive" }]), "fresh roster rejected");
            var reads = 0, stale = {};
            Object.defineProperty(stale, "id", { get: function () { reads += 1; return "TEST-0"; } });
            Object.defineProperty(stale, "revision", { get: function () { reads += 1; return 2; } });
            ensure(old.selectPlayer("TEST-0") === false && old.replaceRoster([stale]) === false &&
                old.updateControl(stale) === false && old.updateTargets(stale) === false &&
                old.refreshCamera() === false && reads === 0, "stale handle read or accepted input");
        }, "rebound", function () {
            ensure(!ui.isDisposed() && node("RosterName0").text === "TEST FRESH", "fresh binding changed");
            visibleCards(1); noActions();
            $.Msg("[C2NativeBind] cycle pass=true transport=absent gateway=absent identity=absent");
        });
    });
}());
