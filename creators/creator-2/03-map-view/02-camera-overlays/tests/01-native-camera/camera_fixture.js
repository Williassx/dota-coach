/* TEST ONLY. Programmatic API activation; never physical mouse or identity proof. */
(function () {
    "use strict";
    var root = $.GetContextPanel();
    var scope = root.FindChildTraverse("CoachCamera");
    var status = root.FindChildTraverse("NativeCameraFixtureStatus");
    var button = root.FindChildTraverse("CameraFocus");
    var result = root.FindChildTraverse("CameraResult");
    var native = DotaCoachCameraNative.create();
    var calls = 0, hero = null, panel = null, old = null;
    var gateway = {
        check: function (id) { return native.check(id); },
        focus: function (id) { calls += 1; return native.focus(id); }
    };
    function look() { return GameUI.GetCameraLookAtPosition(); }
    function mark(name, pass, data) {
        status.text = "TEST camera " + name + " pass=" + pass + "; API activation only";
        $.Msg("[C2NativeCamera] " + name + " pass=" + pass + " " + JSON.stringify(data || {}));
        if (!pass) { throw new Error("Native camera assertion: " + name); }
    }
    function phase(name, work, next) {
        $.Schedule(12, function () {
            try { work(); if (next) { next(); } }
            catch (error) { mark("error", false, {message: String(error)}); }
        });
    }
    function start() {
        if (typeof Players.GetPlayerHeroEntityIndex !== "function" ||
                typeof GameUI.GetCameraLookAtPosition !== "function" ||
                typeof Entities.GetAbsOrigin !== "function") {
            mark("api-unavailable", false); return;
        }
        hero = Players.GetPlayerHeroEntityIndex(Game.GetLocalPlayerID());
        if (!native.check(hero).available) { $.Schedule(1, start); return; }
        $.Schedule(5, function () {
            panel = DotaCoachCameraPanels.bind(scope, gateway);
            mark("bound", !button.enabled && calls === 0, {hero: hero, look: look()});
            phase("selected", function () {
                var before = look();
                var ok = panel.setTarget({id: "TEST_OWN_HERO", playerName: "TEST Axe", entityIndex: hero});
                mark("selected", ok && button.enabled && calls === 0,
                    {calls: calls, before: before, after: look()});
            }, function () {
                phase("refreshed", function () {
                    var before = look();
                    mark("refreshed", panel.refresh() && button.enabled && calls === 0,
                        {calls: calls, before: before, after: look()});
                }, function () {
                    phase("focused", function () {
                        $.DispatchEvent("Activated", button, "mouse");
                        $.Schedule(1.5, function () {
                            var eligible = native.check(hero).available;
                            var at = look(), origin = eligible ? Entities.GetAbsOrigin(hero) : null;
                            var distance = origin ? Math.sqrt(Math.pow(at[0] - origin[0], 2) + Math.pow(at[1] - origin[1], 2)) : null;
                            mark("focused", calls === 1 && result.text.indexOf("Запрос фокуса передан клиенту") !== -1,
                                {calls: calls, eligible: eligible, look: at, ownOrigin: origin,
                                 distanceXY: distance, arrivalCausedByRequest: "unproven", result: result.text});
                            phase("rejected", function () {
                                var outcome = native.focus(-1);
                                mark("rejected", outcome.requested === false && calls === 1,
                                    {outcome: outcome, calls: calls, look: look()});
                            }, function () {
                                phase("disposed", function () {
                                    old = panel; panel.dispose();
                                    mark("disposed", old.isDisposed() && !button.enabled && !button.visible && calls === 1);
                                }, function () {
                                    phase("rebound", function () {
                                        var reads = 0;
                                        var dto = {};
                                        Object.defineProperty(dto, "id", {get: function () { reads += 1; return "stale"; }});
                                        var rejected = old.setTarget(dto) === false;
                                        panel = DotaCoachCameraPanels.bind(scope, gateway);
                                        mark("rebound", rejected && reads === 0 && !panel.isDisposed() && !button.enabled && calls === 1,
                                            {staleDtoReads: reads, calls: calls});
                                    });
                                });
                            });
                        });
                    });
                });
            });
        });
    }
    $.Schedule(1, start);
}());
