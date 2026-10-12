/* TEST ONLY: sampled motion/input correlation. No preference, cursor or camera setters. */
(function () {
    "use strict";
    var root = $.GetContextPanel();
    var status = root.FindChildTraverse("NativeCameraFixtureStatus");
    var button = root.FindChildTraverse("CameraFocus");
    var result = root.FindChildTraverse("CameraResult");
    var native = DotaCoachCameraNative.create();
    var hero, panel, calls = 0, attempts = 0, samples = [], began, closed = false;
    function mark(name, pass, data) {
        status.text = "TEST camera motion " + name + " pass=" + pass + "; arrival separate";
        $.Msg("[C2NativeCameraMotion] " + name + " pass=" + pass + " " + JSON.stringify(data || {}));
        if (!pass) { closed = true; if (panel) { panel.dispose(); } }
    }
    function vector(value, length, field) {
        if (!Array.isArray(value) || value.length !== length || value.some(function (n) {
            return typeof n !== "number" || !isFinite(n);
        })) { throw new Error("Invalid native vector " + field + ": " + JSON.stringify(value)); }
        return value.slice();
    }
    function dimension(name) {
        var value = root[name];
        if (typeof value === "function") { value = value.call(root); }
        return typeof value === "number" && isFinite(value) ? value : null;
    }
    function tick() {
        if (closed) { return; }
        try {
            if (!native.check(hero).available) { throw new Error("Own hero guard closed before origin read"); }
            var index = samples.length;
            if (index === 20) {
                $.DispatchEvent("Activated", button, "mouse");
                if (calls !== 1 || result.text.indexOf("Запрос фокуса передан клиенту") === -1) {
                    throw new Error("Native focus request missing");
                }
            }
            if (!native.check(hero).available) { throw new Error("Own hero guard closed after native focus"); }
            var origin = vector(Entities.GetAbsOrigin(hero), 3, "ownOrigin");
            var look = vector(GameUI.GetCameraLookAtPosition(), 3, "lookAt");
            var row = {
                index: index, phase: index < 20 ? "baseline" : "post",
                elapsedMs: Date.now() - began, hero: hero, calls: calls,
                ownOrigin: origin, lookAt: look,
                cameraPosition: vector(GameUI.GetCameraPosition(), 3, "cameraPosition"),
                cursor: vector(GameUI.GetCursorPosition(), 2, "cursor"),
                mouseButtons: [0, 1, 2].map(function (n) { return GameUI.IsMouseDown(n); }),
                clampedProjectionRaw: vector(GameUI.WorldToScreenXYClamped(origin), 3, "clampedProjectionRaw"),
                distanceXY: Math.sqrt(Math.pow(look[0] - origin[0], 2) + Math.pow(look[1] - origin[1], 2))
            };
            samples.push(row);
            $.Msg("[C2NativeCameraMotionSample] " + JSON.stringify(row));
            if (index === 0) { mark("baseline", calls === 0, {hero: hero}); }
            if (index === 28) { mark("early", calls === 1, {distanceXY: row.distanceXY}); }
            if (index === 45) { mark("settled", calls === 1, {distanceXY: row.distanceXY}); }
            if (index === 80) { mark("returned", calls === 1, {distanceXY: row.distanceXY}); }
            if (index === 99) {
                var post = samples.slice(20);
                var near = post.filter(function (s) { return s.distanceXY <= 64; });
                panel.dispose(); closed = true;
                mark("done", calls === 1 && samples.length === 100, {
                    total: samples.length, baseline: 20, post: post.length, calls: calls,
                    elapsedMs: row.elapsedMs, sampledNearThreshold: 64, nearSamples: near.length,
                    minPostDistanceXY: Math.min.apply(null, post.map(function (s) { return s.distanceXY; })),
                    firstNearElapsedMs: near.length ? near[0].elapsedMs : null,
                    lastDistanceXY: row.distanceXY,
                    layoutWidth: dimension("actuallayoutwidth"), layoutHeight: dimension("actuallayoutheight"),
                    uiScaleX: dimension("actualuiscale_x"), uiScaleY: dimension("actualuiscale_y"),
                    physicalInputVerified: false, causeEstablished: false
                    ,projectionThirdComponentMeaning: "unverified"
                });
                return;
            }
            $.Schedule(0.2, tick);
        } catch (error) { mark("error", false, {message: String(error), samples: samples.length}); }
    }
    function start() {
        if (closed) { return; }
        try {
            ["GetCameraLookAtPosition", "GetCameraPosition", "GetCursorPosition", "IsMouseDown", "WorldToScreenXYClamped"].forEach(function (name) {
                if (typeof GameUI[name] !== "function") { throw new Error("Native API unavailable: " + name); }
            });
            if (typeof Players.GetPlayerHeroEntityIndex !== "function" || typeof Entities.GetAbsOrigin !== "function") {
                throw new Error("Own hero identity/origin API unavailable");
            }
            hero = Players.GetPlayerHeroEntityIndex(Game.GetLocalPlayerID());
            attempts += 1;
            if (!native.check(hero).available) {
                if (attempts >= 180) { throw new Error("Own hero guard timeout"); }
                $.Schedule(1, start); return;
            }
            $.Schedule(5, function () {
                try {
                    if (!native.check(hero).available) { throw new Error("Own hero guard closed before binding"); }
                    panel = DotaCoachCameraPanels.bind(root.FindChildTraverse("CoachCamera"), {
                        check: function (id) { return native.check(id); },
                        focus: function (id) { calls += 1; return native.focus(id); }
                    });
                    if (!panel.setTarget({id: "TEST_OWN_HERO", playerName: "TEST Axe motion", entityIndex: hero})) {
                        throw new Error("TEST target rejected");
                    }
                    began = Date.now(); tick();
                } catch (error) { mark("error", false, {message: String(error)}); }
            });
        } catch (error) { mark("error", false, {message: String(error)}); }
    }
    $.Schedule(1, start);
}());
