/* Test-only native acceptance. Never a fixed-kind production bootstrap. */
(function () {
    "use strict";
    var context, root, banner, stack, ui, old, failed = false, profiles = [];
    function ensure(ok, reason) { if (!ok) { throw new Error(reason); } }
    function node(id) {
        var p = context.FindChildTraverse(id);
        ensure(p && p.IsValid(), "Missing TEST node " + id); return p;
    }
    function navigationLabels() {
        ["TeamPagePrevious", "TeamPageNext", "TeamClear", "HeroRolePrevious", "HeroRoleNext",
            "HeroRoleClear", "PreparationClear"].forEach(function (id) {
                var label = node(id).GetChild(0);
                ensure(label && label.IsValid() && label.text.length > 0 &&
                    label.actuallayoutwidth > 0 && label.actuallayoutheight > 0, "blank navigation " + id);
            });
    }
    function record(name, assertion) {
        try {
            assertion();
            banner.text = "TEST ONLY: synthetic draft; no C1/server/input | " + name + " PASS";
            $.Msg("[C2NativePreparation] " + name + " pass=true scroll=" + stack.scrolloffset_y +
                " content=" + stack.contentheight + " height=" + stack.actuallayoutheight);
        } catch (error) {
            failed = true;
            banner.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativePreparation] " + name + " pass=false reason=" + String(error));
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
        context = $.GetContextPanel(); root = node("CoachPreparationRoot");
        banner = node("NativePreparationFixtureStatus");
        stack = node("CoachPreparationTeamHost").GetParent();
        for (var i = 0; i < 5; i += 1) {
            profiles.push({id: "TEST-p" + i, profileVersion: "v1", playerName: "TEST " + i,
                kind: "synthetic", sourceLabel: "TEST источник", coverage: "unknown"});
        }
        after(0, function () { ui = DotaCoachPreparationBindings.bind(root); }, "bound", function () {
            ensure(!ui.isDisposed() && ui.draft() === null && root.visible, "empty binding failed");
            ensure(node("CoachPreparationStatus").html === false && stack.actuallayoutheight > 0,
                "status or viewport invalid");
            navigationLabels();
        });
        after(15, function () {
            ensure(ui.updateTeam({revision: 0, profiles: profiles}), "catalog rejected");
            for (var i = 0; i < 5; i += 1) { ensure(ui.choosePlayer("TEST-p" + i), "TEST player rejected"); }
            stack.ScrollToTop();
        }, "team", function () {
            var t = ui.contexts().team;
            ensure(t.players.length === 5 && t.complete && t.serverConfirmed === false, "wrong local team");
            ensure(ui.draft() === null && node("TeamPickerCount").text.indexOf("5/5") !== -1, "premature draft");
            ensure(node("TeamSelectedName0").text.indexOf("TEST") !== -1, "missing TEST name");
        });
        after(30, function () {
            var team = ui.contexts().team;
            var proposals = team.players.map(function (p, n) {
                return {id: p.id, profileVersion: p.profileVersion, playerName: "TEST " + n,
                    kind: "synthetic", sourceLabel: "TEST предложения", choices: [
                        {heroId: "TEST-h" + n, heroName: "TEST герой " + n, role: n + 1, coverage: "unknown"}]};
            });
            ensure(ui.updateHeroes({revision: 0, team: team, proposals: proposals}), "hero proposals rejected");
            for (var i = 0; i < 5; i += 1) {
                ensure(ui.assignHero("TEST-p" + i, "TEST-h" + i, i + 1), "hero assignment rejected");
            }
            ensure(ui.updatePreparation({revision: 0, lineup: ui.contexts().heroes,
                plans: [{id: "TEST-plan", optionVersion: "v1", label: "TEST план", intent: "TEST намерение"}],
                talks: [{id: "TEST-talk", optionVersion: "v1", label: "TEST разговор", intent: "TEST намерение"}]}),
                "preparation options rejected");
            ensure(ui.choosePlan("TEST-plan") && ui.chooseTalk("TEST-talk"), "local choices rejected");
            // Wait for the new composite content to be measured by native layout.
            $.Schedule(0.5, function () { if (!failed && root.IsValid()) { stack.ScrollToBottom(); } });
        }, "complete", function () {
            var d = ui.draft();
            ensure(d && d.complete && d.serverConfirmed === false && d.lineup.assignments.length === 5 &&
                d.plan.id === "TEST-plan" && d.talk.id === "TEST-talk", "wrong complete local draft");
            ensure(node("PreparationCount").text.indexOf("2/2") !== -1, "choice count missing");
            ensure(isFinite(stack.scrolloffset_y) && Math.abs(stack.scrolloffset_y) > 1, "API scroll did not move");
        });
        after(45, function () { ensure(ui.removePlayer("TEST-p4"), "team removal rejected"); stack.ScrollToTop(); },
            "reset", function () {
                var c = ui.contexts();
                ensure(c.team.players.length === 4 && c.heroes === null && c.preparation === null && ui.draft() === null,
                    "downstream context retained");
                ensure(node("PreparationLineup").text === "" && node("HeroRolePlayerName0").text === "", "stale labels");
            });
        after(60, function () { old = ui; old.dispose(); }, "disposed", function () {
            ensure(old.isDisposed() && old.contexts() === null && old.draft() === null && !root.visible,
                "dispose did not close group");
        });
        after(75, function () {
            ui = DotaCoachPreparationBindings.bind(root);
            ensure(ui.updateTeam({revision: 0, profiles: profiles.slice(0, 1)}), "fresh catalog rejected");
            var reads = 0;
            var poison = new Proxy({}, {get: function () { reads += 1; }, ownKeys: function () { reads += 1; return []; },
                getOwnPropertyDescriptor: function () { reads += 1; }});
            ensure(old.updateTeam(poison) === false && old.updateHeroes(poison) === false &&
                old.updatePreparation(poison) === false && old.choosePlayer("TEST-p0") === false && reads === 0,
                "stale API read or accepted DTO");
            stack.ScrollToTop();
        }, "rebound", function () {
            ensure(!ui.isDisposed() && ui.contexts().team.players.length === 0 && ui.draft() === null &&
                node("TeamCandidateName0").text.indexOf("TEST") !== -1, "fresh binding corrupted");
            $.Msg("[C2NativePreparation] cycle pass=true server=absent physical_input=not_tested");
        });
    });
}());
