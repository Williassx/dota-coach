/* TEST-only native acceptance. No production bootstrap, input or transport. */
(function () {
    "use strict";
    var context, root, banner, ui, old, failed = false;
    function ensure(ok, reason) { if (!ok) { throw new Error(reason); } }
    function node(id) {
        var p = context.FindChildTraverse(id);
        ensure(p && p.IsValid(), "Missing TEST node " + id); return p;
    }
    function opponents(revision, fresh) {
        var players = [];
        for (var i = 0; i < (fresh ? 1 : 5); i += 1) {
            players.push({id: "TEST-enemy" + i, playerName: fresh ? "TEST FRESH" : "TEST Enemy " + i,
                heroName: i === 0 ? null : "TEST Hero " + i});
        }
        return {revision: revision, players: players};
    }
    function order() {
        return {recipientText: "TEST Selected B", modeText: "AI",
            requestRecipientText: "TEST Captured A", actionText: "TEST Move",
            stageText: "Untrusted", reasonText: "", eligibilityText: "View only",
            canIssue: false, ticket: 1, stage: "accepted", closed: false};
    }
    function evidence() {
        var v = ui.view();
        ensure(!v.closed && v.nativeConfirmed === false &&
            v.opponents.sourceAuthorizationConfirmed === false, "TEST evidence flags changed");
        return v;
    }
    function historyReady() {
        var h = evidence().history;
        ensure(h.ready && h.events.length === 1 && h.totalStored === 1 &&
            h.hiddenStored === 0 && h.droppedEvents === 0 &&
            h.events[0].actorName === "TEST Captured A" && h.events[0].stage === "accepted" &&
            h.events[0].evidence === "presentation_snapshot" && h.events[0].nativeConfirmed === false,
            "Presentation event corrupted or duplicated");
        ensure(node("TimelineEvent0").text.indexOf("TEST Captured A") !== -1 &&
            node("TimelineEvent0").text.indexOf("TEST Selected B") === -1 &&
            node("TimelineEvent0").text.indexOf("Untrusted") === -1, "Wrong actor/stage label");
    }
    function record(name, assertion) {
        try {
            assertion();
            banner.text = "TEST ONLY: synthetic opponents/history; no C1/server/input | " + name + " PASS";
            $.Msg("[C2NativeObservation] " + name + " pass=true root_visible=" + root.visible);
        } catch (error) {
            failed = true;
            banner.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativeObservation] " + name + " pass=false reason=" + String(error));
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
    $.Schedule(1, function () {
        context = $.GetContextPanel(); root = node("CoachMatchObservation");
        banner = node("NativeObservationFixtureStatus");
        after(0, function () { ui = DotaCoachMatchObservationPanels.bind(root); }, "bound", function () {
            var v = evidence();
            ensure(root.visible && !v.opponents.ready && !v.history.ready &&
                node("OpponentName0").text === "" && node("TimelineEvent0").text === "", "Empty bind failed");
        });
        after(15, function () {
            ensure(ui.updateOpponents(opponents(1, false)), "TEST opponents rejected");
            ensure(ui.recordOrder(order()), "TEST history rejected");
        }, "ready", function () {
            var v = evidence();
            ensure(v.opponents.ready && v.opponents.players.length === 5 &&
                node("OpponentName0").text === "TEST Enemy 0" &&
                node("OpponentName4").text === "TEST Enemy 4", "TEST roster not displayed");
            historyReady();
        });
        after(30, function () {
            ensure(ui.updateOpponents(null) === false, "Invalid roster accepted");
            ensure(ui.updateOpponents(opponents(1, false)) === false, "Stale roster recovered");
        }, "opponents-invalid", function () {
            ensure(!evidence().opponents.ready && node("OpponentName0").text === "" &&
                node("OpponentName4").text === "", "Invalid roster survived");
            historyReady();
        });
        after(45, function () {
            ensure(ui.updateOpponents(opponents(2, false)), "New roster revision failed");
            ensure(ui.recordOrder(null) === false && ui.refresh(), "Invalid history gate failed");
        }, "history-invalid", function () {
            var v = evidence();
            ensure(v.opponents.ready && node("OpponentName0").text === "TEST Enemy 0" &&
                !v.history.ready && v.history.events.length === 0 && node("TimelineEvent0").text === "",
                "Independent history invalidation failed");
        });
        after(60, function () {
            ensure(ui.recordOrder(order()), "History recovery failed"); historyReady();
            old = ui; old.dispose();
        }, "disposed", function () {
            var v = old.view();
            ensure(old.isDisposed() && v.closed && v.opponents === null && v.history === null &&
                !root.visible && node("TimelineEvent0").text === "" && node("OpponentName0").text === "",
                "Dispose failed");
        });
        after(75, function () {
            ui = DotaCoachMatchObservationPanels.bind(root);
            ensure(ui.updateOpponents(opponents(1, true)), "Fresh source failed");
            var reads = 0;
            var poison = new Proxy({}, {get: function () { reads += 1; }, ownKeys: function () { reads += 1; return []; },
                getOwnPropertyDescriptor: function () { reads += 1; }});
            ensure(old.updateOpponents(poison) === false && old.recordOrder(poison) === false &&
                old.refresh() === false && reads === 0, "Stale handle inspected DTO");
        }, "rebound", function () {
            var v = evidence();
            ensure(!ui.isDisposed() && root.visible && v.opponents.ready &&
                v.opponents.players.length === 1 && !v.history.ready &&
                node("OpponentName0").text === "TEST FRESH" && node("OpponentName1").text === "Имя неизвестно",
                "Fresh source corrupted");
            $.Msg("[C2NativeObservation] cycle pass=true server=absent physical_input=not_tested");
        });
    });
}());
