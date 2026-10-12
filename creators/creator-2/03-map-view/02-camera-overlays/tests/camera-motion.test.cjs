"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");

function simulate(options = {}) {
    const nodes = new Map(), queue = [], messages = [], moves = [], originReads = [];
    let now = 0, alive = true, look = [1000, 1000, 128];
    function node(id) {
        const panel = {id, enabled: false, visible: true, text: "", events: {},
            actuallayoutwidth: 1920, actuallayoutheight: 1080, actualuiscale_x: 2 / 3, actualuiscale_y: 2 / 3,
            IsValid() { return true; }, FindChildTraverse(id) { return nodes.get(id); },
            ClearPanelEvent(name) { delete this.events[name]; },
            SetPanelEvent(name, callback) { this.events[name] = callback; }};
        nodes.set(id, panel); return panel;
    }
    const root = node("root");
    ["CoachCamera", "NativeCameraFixtureStatus", "CameraFocus", "CameraRecipient", "CameraAvailability", "CameraResult"].forEach(node);
    const context = vm.createContext({
        Date: {now: () => now},
        $: {GetContextPanel: () => root, Msg: text => messages.push(text),
            Schedule(delay, callback) { queue.push({at: now + delay * 1000, callback}); },
            DispatchEvent(name, panel) { assert.equal(name, "Activated"); panel.events.onactivate(); }},
        Game: {GetLocalPlayerID: () => 0},
        Players: {GetTeam: () => 2, GetPlayerHeroEntityIndex: () => 101},
        Entities: {IsValidEntity: id => id === 101, IsRealHero: () => true,
            IsAlive: () => alive, GetTeamNumber: () => 2,
            GetAbsOrigin() { originReads.push({alive, now}); return [0, 0, 128]; }},
        GameUI: {
            MoveCameraToEntity(id) {
                moves.push(id);
                if (options.deathOnFocus) { alive = false; }
                if (options.moveThrow) { throw Error("Native move failed"); }
                look = [0, 0, 128];
            },
            GetCameraLookAtPosition: () => options.badVector ? [NaN, 0, 128] : look.slice(),
            GetCameraPosition: () => [0, 0, 1000],
            GetCursorPosition: () => [-1, -1], IsMouseDown: () => false,
            WorldToScreenXYClamped: () => [.5, .5, 0],
            SetCameraTarget() { throw Error("Forbidden follow lock"); },
            SetMouseCallback() { throw Error("Forbidden input override"); }
        }
    });
    if (options.missingCursor) { delete context.GameUI.GetCursorPosition; }
    const source = path.resolve(__dirname, "../src/panorama/scripts/custom_game");
    for (const file of ["camera_native.js", "camera_panel.js"]) {
        vm.runInContext(fs.readFileSync(path.join(source, file), "utf8"), context, {filename: file});
    }
    vm.runInContext(fs.readFileSync(path.join(__dirname, "01-native-camera/camera_motion.js"), "utf8"), context);
    let steps = 0;
    while (queue.length) {
        assert.ok(++steps < 400, "Sampling did not terminate");
        queue.sort((a, b) => a.at - b.at);
        const scheduled = queue.shift(); now = scheduled.at; scheduled.callback();
    }
    return {nodes, messages, moves, originReads,
        samples: messages.filter(s => s.startsWith("[C2NativeCameraMotionSample] ")).map(s => JSON.parse(s.slice(s.indexOf(" ") + 1)))};
}

test("motion sequence samples baseline20/post80 around one actual panel handler and disposes", () => {
    const run = simulate();
    assert.equal(run.samples.length, 100);
    assert.equal(run.samples.filter(s => s.phase === "baseline" && s.calls === 0).length, 20);
    assert.equal(run.samples.filter(s => s.phase === "post" && s.calls === 1).length, 80);
    assert.deepEqual(run.moves, [101]);
    assert.equal(run.originReads.length, 100);
    assert.equal(run.samples.at(-1).elapsedMs, 19800);
    assert.deepEqual(run.samples[0].clampedProjectionRaw, [.5, .5, 0]);
    assert.equal(run.nodes.get("CameraFocus").enabled, false);
    assert.equal(run.nodes.get("CameraFocus").visible, false);
    assert.ok(run.messages.some(s => s.includes("done pass=true") && s.includes('"nearSamples":80')));
});
test("missing cursor API refuses before any origin or native request", () => {
    const run = simulate({missingCursor: true});
    assert.equal(run.samples.length, 0); assert.equal(run.originReads.length, 0);
    assert.deepEqual(run.moves, []); assert.ok(run.messages.some(s => s.includes("pass=false")));
});
test("guard rechecked after native request prevents a newly dead hero origin read", () => {
    const run = simulate({deathOnFocus: true});
    assert.deepEqual(run.moves, [101]);
    assert.equal(run.originReads.length, 20);
    assert.ok(run.originReads.every(r => r.alive));
    assert.equal(run.samples.length, 20);
    assert.ok(run.messages.some(s => s.includes("pass=false")));
});
test("malformed native vector closes diagnostics without invented success", () => {
    const run = simulate({badVector: true});
    assert.equal(run.samples.length, 0); assert.deepEqual(run.moves, []);
    assert.ok(run.messages.some(s => s.includes("Invalid native vector")));
    assert.ok(!run.messages.some(s => s.includes("done pass=true")));
});
test("native focus exception preserves failed request and stops post samples", () => {
    const run = simulate({moveThrow: true});
    assert.deepEqual(run.moves, [101]); assert.equal(run.samples.length, 20);
    assert.equal(run.originReads.length, 20);
    assert.ok(run.messages.some(s => s.includes("Native focus request missing")));
});
