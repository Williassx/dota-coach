/* TEST API only: synthetic identity/targets and controlled clock; no input/transport. */
(function () {
    "use strict";
    var context, root, banner, ui, old, failed = false, ms = 0;
    function ensure(ok, reason) { if (!ok) { throw new Error(reason); } }
    function node(id) {
        var p = context.FindChildTraverse(id);
        ensure(p && p.IsValid(), "Missing TEST node " + id); return p;
    }
    function actor(id) { return {id: id, playerName: "TEST " + id, epoch: 1}; }
    function target(id, team, kind) {
        return {id: id, visibility: "visible", label: "<b>TEST " + id + "</b>",
            team: team, kind: kind, alive: true, entityIndex: 10};
    }
    function bind() { return DotaCoachMouseTargetingPanels.bind(root, {
        now: function () { return ms; }, maxAgeMs: 1000}); }
    function authority(v) {
        ensure(v && !v.closed, "Open view required");
        [v, v.mouse].forEach(function (s) {
            ensure(s.canSend === false && s.nativeConfirmed === false &&
                s.sourceAuthorizationConfirmed === false, "Authority flags changed");
        });
    }
    function record(name, assertion) {
        try {
            assertion();
            if (root.visible) {
                ensure(root.actuallayoutwidth > 0 && root.actuallayoutheight > 0,
                    "Native mouse pane geometry empty");
                ["MouseActor", "MouseLease", "MouseHint"].forEach(function (id) {
                    ensure(node(id).actuallayoutwidth > 0 && node(id).actuallayoutheight > 0,
                        "Native label geometry empty " + id);
                });
                authority(ui.view());
            }
            banner.text = "TEST ONLY: actor/targets; controlled clock; no input/server | " + name + " PASS";
            $.Msg("[C2NativeMouseTargeting] " + name + " pass=true clock_ms=" + ms +
                " root_visible=" + root.visible + " width=" + root.actuallayoutwidth +
                " height=" + root.actuallayoutheight + " actor=" + node("MouseActor").text +
                " action=" + node("MouseAction").text + " target=" + node("MouseTarget").text);
        } catch (error) {
            failed = true; banner.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativeMouseTargeting] " + name + " pass=false reason=" + String(error));
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
        context = $.GetContextPanel(); root = node("MouseProposalRoot");
        banner = node("NativeMouseTargetingFixtureStatus");
        after(0, function () { ui = bind(); }, "bound", function () {
            var v = ui.view();
            ensure(v.observation.status === "empty" && v.mouse.actor === null &&
                v.mouse.proposal === null && node("MouseLease").text.indexOf("неизвестно") !== -1,
                "Empty bind mismatch");
        });
        after(15, function () {
            ensure(ui.captureActor(actor("A")) && ui.updateTargets({revision: 1,
                targets: [target("t", "enemy", "hero")]}) && ui.selectTarget("t") &&
                ui.proposeTarget(), "Attack setup rejected");
        }, "attack", function () {
            var p = ui.view().mouse.proposal;
            ensure(p.action === "attack" && p.serial === 1 && p.actor.id === "A" &&
                p.target.id === "t" && node("MouseAction").text === "Атака героя" &&
                node("MouseTarget").text === "<b>TEST t</b>" && node("MouseTarget").html === false,
                "Attack/literal label mismatch");
        });
        after(30, function () {
            ensure(ui.updateTargets({revision: 2, targets: [target("t", "enemy", "creep"),
                target("u", "ally", "creep")]}) && ui.view().mouse.proposal === null &&
                ui.selectTarget("t") && ui.proposeTarget(), "Last hit rejected");
            ensure(ui.view().mouse.proposal.action === "last_hit" &&
                node("MouseAction").text === "Добивание вражеского крипа", "Last hit caption mismatch");
            ensure(ui.selectTarget("u") && ui.view().mouse.proposal === null &&
                ui.captureActor(actor("B")) === false && ui.proposeTarget(), "Captured switch failed");
        }, "captured-switch", function () {
            var p = ui.view().mouse.proposal;
            ensure(p.action === "deny" && p.serial === 3 && p.actor.id === "A" && p.target.id === "u" &&
                node("MouseActor").text === "TEST A" && node("MouseAction").text === "Денай союзного крипа",
                "Switch changed actor or silently reissued action");
        });
        after(45, function () {
            ms = 999; ensure(ui.view().mouse.proposal !== null, "TTL expired early");
            ms = 1000; ensure(ui.refresh(), "Expiry refresh failed");
        }, "expiry", function () {
            var v = ui.view();
            ensure(v.observation.status === "stale" && v.mouse.proposal === null &&
                v.mouse.actor.id === "A" && node("MouseAction").text === "" &&
                node("MouseTarget").text === "" && !ui.proposeTarget(), "TTL boundary mismatch");
        });
        after(60, function () {
            ensure(ui.reset() && ui.captureActor(actor("A")), "Move reset rejected");
            ms = 2000;
            ensure(ui.updateTargets({revision: 3, targets: [{id: "t", visibility: "hidden"}]}) &&
                ui.proposeMove({x: 100, y: 200, z: 0}) && ui.selectTarget(null), "Move setup rejected");
            ms = 3000; ensure(ui.refresh(), "Move stale refresh rejected");
        }, "move", function () {
            var v = ui.view(), p = v.mouse.proposal;
            ensure(v.observation.status === "stale" && p.action === "move" && p.actor.id === "A" &&
                p.point.x === 100 && p.point.y === 200 && p.point.z === 0 &&
                node("MouseAction").text === "Движение" && node("MouseTarget").text === "Точка выбрана.",
                "Move lost to hidden/stale target source");
        });
        after(75, function () {
            ensure(ui.reset() && ui.captureActor(actor("A")), "Recovery reset failed"); ms = 4000;
            ensure(ui.updateTargets({revision: 4, targets: [target("t", "enemy", "hero")]}) &&
                ui.selectTarget("t") && ui.proposeTarget(), "Recovery initial source failed");
            ensure(ui.updateTargets({revision: 5, targets: [{id: "t", visibility: "visible"}]}) === false &&
                ui.view().observation.status === "invalid" && ui.view().mouse.proposal === null &&
                ui.view().mouse.actor.id === "A", "Invalid source retained target");
            ensure(ui.updateTargets({revision: 6, targets: [target("t", "enemy", "hero")]}) &&
                ui.selectTarget("t") && ui.proposeTarget(), "Newer recovery failed");
        }, "recovery", function () {
            ensure(ui.view().observation.status === "ready" && ui.view().mouse.proposal.action === "attack" &&
                node("MouseTarget").html === false, "Recovered proposal mismatch");
        });
        after(90, function () { old = ui; old.dispose(); }, "disposed", function () {
            var v = old.view();
            ensure(old.isDisposed() && v.closed && v.mouse === null && v.observation === null &&
                !root.visible && node("MouseActor").text === "" && node("MouseAction").text === "", "Dispose failed");
        });
        after(105, function () {
            ui = bind(); ensure(ui.captureActor(actor("B")), "Fresh actor rejected");
            var reads = 0, poison = new Proxy({}, {get: function () { reads += 1; },
                ownKeys: function () { reads += 1; return []; }, getOwnPropertyDescriptor: function () { reads += 1; }});
            ensure(old.captureActor(poison) === false && old.updateTargets(poison) === false &&
                old.proposeMove(poison) === false && old.selectTarget(poison) === false &&
                old.proposeTarget() === false && old.reset() === false && old.refresh() === false &&
                reads === 0, "Closed API inspected input");
        }, "rebound", function () {
            var v = ui.view();
            ensure(!ui.isDisposed() && root.visible && v.mouse.actor.id === "B" &&
                v.mouse.proposal === null && v.observation.status === "empty" &&
                node("MouseActor").text === "TEST B", "Fresh bind corrupted");
            $.Msg("[C2NativeMouseTargeting] cycle pass=true physical_input=not_tested clock=controlled server=absent");
        });
    });
}());
