/* TEST-only boundary tracing. Never part of a fixed kind or production bootstrap. */
var DotaCoachPreparationResetTrace = (function () {
    "use strict";
    function start(p) {
        var closed = false, trial = null, cursor = null, tainted = false, serial = 0;
        var names = ["immediate-a", "delayed-a", "immediate-b", "delayed-b"];
        function valid() { return !closed && p.isValid(); }
        function emit(name, data) {
            data.physicalInputControlled = false;
            p.record(name, data);
        }
        function dispose() {
            if (closed) { return; }
            closed = true;
            if (p.isValid()) { p.disposeUI(); }
        }
        function fail(error) {
            if (closed) { return; }
            emit("failed", {pass: false, error: String(error), trial: trial});
            dispose();
        }
        function later(delay, fn) {
            p.schedule(delay, function () {
                if (!valid()) { return; }
                try { fn(); } catch (error) { fail(error); }
            });
        }
        function finite(n) { return typeof n === "number" && isFinite(n); }
        function sample(boundary, recordName) {
            if (!valid()) { return null; }
            var g = p.geometry();
            if (!valid()) { return null; }
            var input = p.input();
            if (!valid()) { return null; }
            if (!g || !finite(g.scroll) || !finite(g.content) || !finite(g.viewport) ||
                    g.content < 0 || g.viewport < 0) { throw new Error("Invalid geometry"); }
            if (!input || !Array.isArray(input.cursor) || input.cursor.length !== 2 ||
                    !input.cursor.every(finite) || !Array.isArray(input.buttons) ||
                    input.buttons.length !== 5 || !input.buttons.every(function (x) { return typeof x === "boolean"; }) ||
                    [input.alt, input.control, input.shift].some(function (x) { return typeof x !== "boolean"; })) {
                throw new Error("Invalid sampled input");
            }
            if ((cursor && (cursor[0] !== input.cursor[0] || cursor[1] !== input.cursor[1])) ||
                    input.buttons.some(function (x) { return x; }) || input.alt || input.control || input.shift) {
                tainted = true;
            }
            cursor = input.cursor.slice();
            var data = {pass: true, trial: trial, boundary: boundary, timeMs: p.now(),
                scroll: g.scroll, content: g.content, viewport: g.viewport,
                cursor: cursor.slice(), buttons: input.buttons.slice(), alt: input.alt,
                control: input.control, shift: input.shift,
                inputTainted: tainted, sampledInputQuiet: !tainted};
            emit(recordName || "sample", data);
            return data;
        }
        function begin(index) {
            trial = names[index]; cursor = null; tainted = false;
            var token = ++serial;
            p.prepare();
            if (!valid()) { return; }
            sample("prepared");
            function tick() {
                if (token !== serial) { return; }
                sample("tick"); later(0.1, tick);
            }
            later(0.1, tick);
            later(0.5, function () { p.scrollBottom(); if (valid()) { sample("after-bottom"); } });
            later(1.5, function () {
                sample("before-remove");
                if (!valid()) { return; }
                p.reset(); sample("after-remove");
                if (!valid()) { return; }
                function top() {
                    sample("before-top");
                    if (!valid()) { return; }
                    p.scrollTop(); if (valid()) { sample("after-top"); }
                }
                if (index % 2 === 0) { top(); } else { later(0.5, top); }
            });
            later(3.5, function () {
                serial += 1;
                if (!p.validateReset()) { throw new Error("Reset model not4/5"); }
                if (!valid()) { return; }
                var data = sample("final");
                if (!data || !valid()) { return; }
                if (data.viewport <= 0) { throw new Error("Final viewport unavailable"); }
                data.topObserved = Math.abs(data.scroll) <= 1;
                data.modelResetVerified = true;
                emit(trial, data);
                if (index < 3) { later(12, function () { begin(index + 1); }); }
                else {
                    later(12, function () {
                        p.disposeUI();
                        emit("disposed", {pass: true}); emit("cycle", {pass: true});
                        closed = true;
                    });
                }
            });
        }
        if (valid()) {
            try {
                sample("bound", "bound");
                later(12, function () { begin(0); });
            } catch (error) { fail(error); }
        }
        return {dispose: dispose};
    }
    return {start: start};
}());

(function () {
    "use strict";
    $.Schedule(1, function () {
        var context = $.GetContextPanel(), root = context.FindChildTraverse("CoachPreparationRoot");
        var banner = context.FindChildTraverse("NativePreparationFixtureStatus");
        var stack = context.FindChildTraverse("CoachPreparationTeamHost").GetParent(), ui = null;
        function ensure(ok, message) { if (!ok) { throw new Error(message); } }
        function prepare() {
            if (ui) { ui.dispose(); }
            ui = DotaCoachPreparationBindings.bind(root);
            var profiles = [];
            for (var n = 0; n < 5; n += 1) {
                profiles.push({id: "TEST-p" + n, profileVersion: "v1", playerName: "TEST " + n,
                    kind: "synthetic", sourceLabel: "TEST источник", coverage: "unknown"});
            }
            ensure(ui.updateTeam({revision: 0, profiles: profiles}), "team source rejected");
            profiles.forEach(function (p) { ensure(ui.choosePlayer(p.id), "choose rejected"); });
            var team = ui.contexts().team;
            var proposals = team.players.map(function (p, n) {
                return {id: p.id, profileVersion: p.profileVersion, playerName: "TEST " + n,
                    kind: "synthetic", sourceLabel: "TEST предложения", choices: [
                        {heroId: "TEST-h" + n, heroName: "TEST герой " + n, role: n + 1, coverage: "unknown"}]};
            });
            ensure(ui.updateHeroes({revision: 0, team: team, proposals: proposals}), "hero source rejected");
            profiles.forEach(function (p, n) { ensure(ui.assignHero(p.id, "TEST-h" + n, n + 1), "assign rejected"); });
            ensure(ui.updatePreparation({revision: 0, lineup: ui.contexts().heroes,
                plans: [{id: "TEST-plan", optionVersion: "v1", label: "TEST план", intent: "TEST намерение"}],
                talks: [{id: "TEST-talk", optionVersion: "v1", label: "TEST разговор", intent: "TEST намерение"}]}),
                "preparation source rejected");
            ensure(ui.choosePlan("TEST-plan") && ui.chooseTalk("TEST-talk"), "choices rejected");
            ensure(ui.draft().complete && ui.draft().serverConfirmed === false, "not local complete");
        }
        ui = DotaCoachPreparationBindings.bind(root);
        DotaCoachPreparationResetTrace.start({
            isValid: function () { return context.IsValid() && root.IsValid() && stack.IsValid(); },
            schedule: function (delay, fn) { $.Schedule(delay, fn); }, now: function () { return Date.now(); },
            geometry: function () { return {scroll: stack.scrolloffset_y, content: stack.contentheight,
                viewport: stack.actuallayoutheight}; },
            input: function () {
                return {cursor: GameUI.GetCursorPosition(), buttons: [0, 1, 2, 3, 4].map(function (n) {
                    return GameUI.IsMouseDown(n);
                }), alt: GameUI.IsAltDown(), control: GameUI.IsControlDown(), shift: GameUI.IsShiftDown()};
            },
            prepare: prepare,
            reset: function () { ensure(ui.removePlayer("TEST-p4"), "remove rejected"); },
            scrollBottom: function () { stack.ScrollToBottom(); }, scrollTop: function () { stack.ScrollToTop(); },
            validateReset: function () {
                var c = ui.contexts();
                return c && c.team.players.length === 4 && c.heroes === null &&
                    c.preparation === null && ui.draft() === null;
            },
            disposeUI: function () { if (ui) { ui.dispose(); } },
            record: function (name, data) {
                if (name !== "sample") {
                    banner.text = "TEST ONLY reset trace; physical input unverified | " + name +
                        (data.pass === false ? " FAIL" : " PASS") +
                        (typeof data.topObserved === "boolean" ? " top=" + data.topObserved : "");
                }
                $.Msg("[C2NativePreparationReset] " + name + " pass=" + (data.pass !== false) +
                    " data=" + JSON.stringify(data));
            }
        });
    });
}());
