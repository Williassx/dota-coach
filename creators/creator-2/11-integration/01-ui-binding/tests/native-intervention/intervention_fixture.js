/* TEST-only local send/report. No physical input, server or input authority. */
(function () {
    "use strict";
    var context, root, banner, ui, old, reply, firstReply, sent = [], failed = false;
    var requestedAt = 0, timeoutObserved = false;
    function ensure(ok, reason) { if (!ok) { throw new Error(reason); } }
    function node(id) {
        var p = context.FindChildTraverse(id);
        ensure(p && p.IsValid(), "Missing TEST node " + id); return p;
    }
    function card(id) {
        return {id: id, playerName: "TEST " + id, heroName: null, role: 3,
            source: "synthetic", side: "own", availability: "alive"};
    }
    function control(id) {
        return {id: id, playerName: "TEST " + id, mode: "AI", epoch: 1,
            revision: 1, side: "own", availability: "alive"};
    }
    function send(intent, report) { sent.push(intent); reply = report; }
    function ready() {
        ensure(ui.replaceRoster([card("a"), card("b"), card("c"), card("d"), card("e")]), "TEST roster rejected");
        ensure(ui.updateControl(control("a")) && ui.updateControl(control("b")), "TEST control rejected");
        ensure(ui.selectPlayer("a"), "TEST selection rejected");
    }
    function record(name, assertion) {
        try {
            assertion();
            var manual = node("ManualRequestRoot"), window = manual.GetChild(0);
            if (root.visible) {
                ensure(window && window.IsValid() && manual.actuallayoutwidth > 0 &&
                    manual.actuallayoutheight > 0 && window.actuallayoutwidth > 0 &&
                    window.actuallayoutheight > 0, "Manual pane has empty native geometry");
            }
            banner.text = "TEST ONLY: synthetic roster/local send; no server/input | " + name + " PASS";
            $.Msg("[C2NativeIntervention] " + name + " pass=true root_visible=" + root.visible +
                " manual_w=" + manual.actuallayoutwidth + " manual_h=" + manual.actuallayoutheight +
                " window_w=" + window.actuallayoutwidth + " window_h=" + window.actuallayoutheight);
        } catch (error) {
            failed = true;
            banner.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativeIntervention] " + name + " pass=false reason=" + String(error));
            if (ui) { ui.dispose(); }
        }
    }
    function after(delay, action, name, assertion) {
        $.Schedule(delay, function () {
            if (failed || !context.IsValid()) { return; }
            try { action(); } catch (error) { record(name, function () { throw error; }); return; }
            $.Schedule(1, function () { if (!failed && context.IsValid()) { record(name, assertion); } });
        });
    }
    function observeTimeout() {
        if (failed || !context.IsValid() || ui.isDisposed()) { return; }
        var v = ui.view();
        if (v && v.manual.status === "unknown") {
            timeoutObserved = true;
            $.Msg("[C2NativeIntervention] timeout_observed elapsed_ms=" + (Date.now() - requestedAt));
            return;
        }
        $.Schedule(0.25, observeTimeout);
    }
    $.Schedule(1, function () {
        context = $.GetContextPanel(); root = node("CoachInterventionScreen");
        banner = node("NativeInterventionFixtureStatus");
        after(0, function () { ui = DotaCoachInterventionScreenPanels.bind(root, send); }, "bound", function () {
            var v = ui.view();
            ensure(v && !ui.isDisposed() && !v.canRequest && v.manual.request === null &&
                node("ManualRequestButton").enabled === false, "Empty bind gate failed");
        });
        after(15, ready, "ready", function () {
            var v = ui.view();
            ensure(v.canRequest && !v.manual.manualModeReported && v.roster.selectedId === "a" &&
                sent.length === 0 && node("RosterName0").text === "TEST a" &&
                node("RosterName4").text === "TEST e" && node("ManualRequestButton").enabled,
                "Ready source or selection unexpectedly sent request");
        });
        after(30, function () {
            requestedAt = Date.now(); ensure(ui.request(), "Local request rejected");
        }, "pending", function () {
            var v = ui.view();
            ensure(sent.length === 1 && Object.keys(sent[0]).sort().join(",") === "action,epoch,recipientId,ticket" &&
                sent[0].ticket === 1 && sent[0].recipientId === "a" && sent[0].epoch === 1 &&
                sent[0].action === "request_manual" && !v.canRequest &&
                v.manual.status === "pending" && v.manual.request.sourceRevision === 1 &&
                v.manual.request.sequence === -1, "Pending captured request corrupted");
        });
        // ACK must precede the real five-second timer; capture pending before this action.
        after(34, function () {
            ensure(ui.selectPlayer("b"), "Card switch rejected");
            firstReply = reply;
            ensure(reply({sequence: 0, stage: "accepted", reason: null}), "Local ACK rejected");
        }, "accepted", function () {
            var v = ui.view();
            ensure(v.roster.selectedId === "b" && v.manual.selected.id === "b" &&
                v.manual.request.recipientId === "a" && v.manual.status === "accepted" &&
                v.manual.request.sequence === 0 && !v.manual.manualModeReported && !v.canRequest &&
                ui.request() === false && sent.length === 1 &&
                node("ManualRequestRecipient").text.indexOf("[b]") !== -1 &&
                node("ManualRequestActor").text.indexOf("[a]") !== -1, "ACK changed captured actor or input gate");
        });
        after(50, function () {
            ui.dispose(); sent = [];
            ui = DotaCoachInterventionScreenPanels.bind(root, send); ready();
            requestedAt = Date.now(); ensure(ui.request(), "Fresh timeout request rejected");
            $.Schedule(4.5, observeTimeout);
        }, "timeout-pending", function () {
            var v = ui.view();
            ensure(sent.length === 1 && v.manual.status === "pending" &&
                v.manual.request.recipientId === "a", "Fresh pending gate failed");
        });
        after(65, function () {}, "timeout-unknown", function () {
            var v = ui.view();
            ensure(timeoutObserved && Date.now() - requestedAt >= 5000 && v.manual.status === "unknown" &&
                !v.canRequest && !v.manual.manualModeReported && v.manual.request.recipientId === "a" &&
                ui.request() === false && sent.length === 1 &&
                node("ManualRequestState").text.indexOf("неизвест") !== -1 &&
                node("ManualRequestMessage").text.indexOf("неизвест") !== -1 &&
                node("CoachInterventionStatus").text.indexOf("неизвест") !== -1,
                "Actual ACK timer did not update source and watcher summary");
        });
        after(80, function () { old = ui; old.dispose(); }, "disposed", function () {
            ensure(old.isDisposed() && old.view() === null && !root.visible &&
                node("RosterName0").text === "" && node("ManualRequestActor").text === "", "Dispose failed");
        });
        after(95, function () {
            ui = DotaCoachInterventionScreenPanels.bind(root, send); ready();
            var reads = 0;
            var poison = new Proxy({}, {get: function () { reads += 1; }, ownKeys: function () { reads += 1; return []; },
                getOwnPropertyDescriptor: function () { reads += 1; }});
            ensure(old.replaceRoster(poison) === false && old.updateControl(poison) === false &&
                reply(poison) === false && firstReply(poison) === false &&
                old.request() === false && old.selectPlayer("b") === false && old.refresh() === false &&
                reads === 0, "Closed APIs/replies inspected DTO");
        }, "rebound", function () {
            var v = ui.view();
            ensure(v && !ui.isDisposed() && root.visible && v.roster.selectedId === "a" &&
                v.manual.request === null && v.canRequest && sent.length === 1, "Fresh flow corrupted");
            $.Msg("[C2NativeIntervention] cycle pass=true server=absent physical_input=not_tested");
        });
    });
}());
