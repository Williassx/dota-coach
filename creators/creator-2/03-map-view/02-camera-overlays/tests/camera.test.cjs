"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const folder = path.resolve(__dirname, "../src/panorama/scripts/custom_game");

function load(context, name) {
    const file = path.join(folder, name);
    assert.ok(fs.existsSync(file), "camera source missing: " + name);
    vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: name });
}
function target(id = "a", entityIndex = 101, extra = {}) {
    return { id, playerName: "Синтетический игрок " + id, entityIndex, ...extra };
}
function fixture(options = {}) {
    const calls = [];
    const forbidden = [];
    const entities = new Map([[101, { valid: true, real: true, alive: true, team: 2 }],
        [202, { valid: true, real: true, alive: true, team: 2 }]]);
    const nodes = new Map();
    function panel(id) {
        let text = "";
        const p = { valid: true, enabled: false, visible: true, html: true, events: {},
            IsValid() { return this.valid; }, FindChildTraverse(id) { return nodes.get(id); },
            SetPanelEvent(name, fn) { this.events[name] = fn; },
            ClearPanelEvent(name) { delete this.events[name]; },
            get text() { return text; }, set text(value) {
                if (options.failText === id) { throw new Error("render unavailable"); }
                text = value;
            }
        };
        nodes.set(id, p); return p;
    }
    const root = panel("CameraRoot");
    for (const id of ["CameraRecipient", "CameraAvailability", "CameraResult", "CameraFocus"]) { panel(id); }
    if (options.missing) { nodes.delete(options.missing); }
    const context = vm.createContext({
        Game: { GetLocalPlayerID() { if (options.apiThrow) throw new Error("unavailable"); return options.player ?? 0; } },
        Players: { GetTeam() { return options.team ?? 2; } },
        Entities: {
            IsValidEntity(index) { return entities.get(index)?.valid ?? false; },
            IsRealHero(index) { return entities.get(index)?.real ?? false; },
            IsAlive(index) { return entities.get(index)?.alive ?? false; },
            GetTeamNumber(index) { return entities.get(index)?.team ?? -1; },
            GetAbsOrigin() { forbidden.push("origin"); throw new Error("hidden positions forbidden"); }
        },
        GameUI: {
            MoveCameraToEntity(index) { calls.push(index); if (options.moveThrow) throw new Error("move unknown"); },
            SetCameraTarget() { forbidden.push("lock"); throw new Error("persistent camera forbidden"); },
            SetMouseCallback() { forbidden.push("mouse"); throw new Error("mouse takeover forbidden"); }
        },
        GameEvents: { SendCustomGameEventToServer() { forbidden.push("transport"); throw new Error("transport forbidden"); } }
    });
    load(context, "camera_native.js");
    return { context, calls, forbidden, entities, root, nodes, options,
        gateway() { return context.DotaCoachCameraNative.create(); },
        bind(gateway) {
            load(context, "camera_panel.js");
            return context.DotaCoachCameraPanels.bind(root, gateway);
        },
        click() { nodes.get("CameraFocus").events.onactivate(); }
    };
}

test("native startup and availability checks never move the camera", () => {
    const p = fixture();
    const gateway = p.gateway();
    assert.equal(gateway.check(101).available, true);
    assert.deepEqual(p.calls, []);
    assert.deepEqual(p.forbidden, []);
});

test("native explicit focus requests only the living real hero of the local team", () => {
    const p = fixture();
    const result = p.gateway().focus(101);
    assert.equal(result.requested, true);
    assert.equal(result.reason, null);
    assert.deepEqual(p.calls, [101]);
    assert.deepEqual(p.forbidden, []);
});

test("native rejects dead invalid nonhero opponent spectator and unknown team", () => {
    for (const options of [{ player: -1 }, { team: 1 }, { team: 0 }, { team: 3 }]) {
        const p = fixture(options);
        assert.equal(p.gateway().focus(101).requested, false);
        assert.deepEqual(p.calls, []);
    }
    for (const extra of [{ alive: false }, { real: false }, { valid: false }, { team: 3 }]) {
        const p = fixture();
        Object.assign(p.entities.get(101), extra);
        const result = p.gateway().focus(101);
        assert.equal(result.requested, false);
        assert.equal(typeof result.reason, "string");
        assert.deepEqual(p.calls, []);
    }
});

test("native malformed index and absent APIs return an explicit block", () => {
    const p = fixture();
    for (const id of [-1, "101", 1.5, NaN, Infinity, 2147483648]) {
        assert.equal(p.gateway().focus(id).requested, false);
    }
    delete p.context.GameUI.MoveCameraToEntity;
    assert.equal(p.gateway().focus(101).requested, false);
    assert.deepEqual(p.calls, []);
});

test("native rechecks death after an earlier successful availability check", () => {
    const p = fixture();
    const gateway = p.gateway();
    assert.equal(gateway.check(101).available, true);
    p.entities.get(101).alive = false;
    assert.equal(gateway.focus(101).requested, false);
    assert.deepEqual(p.calls, []);
});

test("native API or camera throw does not claim an arrived camera", () => {
    const p = fixture({ apiThrow: true });
    assert.equal(p.gateway().focus(101).requested, false);
    assert.deepEqual(p.calls, []);
    const q = fixture({ moveThrow: true });
    assert.equal(q.gateway().focus(101).requested, false);
    assert.match(q.gateway().focus(101).reason, /неизвестно|подтвержд/);
});

test("panel without gateway or target never enables focus", () => {
    const p = fixture();
    const ui = p.bind();
    assert.equal(p.nodes.get("CameraFocus").enabled, false);
    ui.setTarget(target());
    assert.equal(p.nodes.get("CameraFocus").enabled, false);
    assert.deepEqual(p.calls, []);
    const q = fixture();
    q.bind(q.gateway());
    assert.equal(q.nodes.get("CameraFocus").enabled, false);
});

test("selection and refresh make no motion; explicit click requests focus", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    assert.equal(ui.setTarget(target()), true);
    ui.refresh();
    assert.deepEqual(p.calls, []);
    p.click();
    assert.deepEqual(p.calls, [101]);
    assert.match(p.nodes.get("CameraResult").text, /передан|запрошен/);
    assert.match(p.nodes.get("CameraResult").text, /не подтверждено|не подтвержден/);
    assert.deepEqual(p.forbidden, []);
});

test("selected recipient remains separate from the previous focus request", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    ui.setTarget(target("a", 101)); p.click();
    ui.setTarget(target("b", 202));
    assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
    assert.match(p.nodes.get("CameraResult").text, /игрок a/);
    assert.deepEqual(p.calls, [101]);
    ui.setTarget(null);
    assert.match(p.nodes.get("CameraResult").text, /игрок a/);
    assert.equal(p.nodes.get("CameraFocus").enabled, false);
});

test("fresh death blocks an old enabled button before its next refresh", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    ui.setTarget(target());
    p.entities.get(101).alive = false;
    p.click();
    assert.deepEqual(p.calls, []);
    assert.equal(p.nodes.get("CameraFocus").enabled, false);
    assert.match(p.nodes.get("CameraAvailability").text, /мёртв|жив/);
});

test("old focus callbacks cannot become new clicks after selection and refresh", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    ui.setTarget(target("a", 101));
    const old = p.nodes.get("CameraFocus").events.onactivate;
    ui.setTarget(target("b", 202)); ui.setTarget(target("a", 101));
    old();
    const after = p.nodes.get("CameraFocus").events.onactivate;
    ui.refresh(); after();
    assert.deepEqual(p.calls, []);
});

test("target is copied, invalid target preserves selection and labels are plain text", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    const row = target("a", 101, { playerName: "<b>Игрок</b>" });
    ui.setTarget(row); row.entityIndex = 202;
    assert.equal(ui.setTarget(target("bad", "101")), false);
    assert.equal(ui.setTarget({ ...target(), extra: true }), false);
    p.click();
    assert.deepEqual(p.calls, [101]);
    assert.match(p.nodes.get("CameraRecipient").text, /<b>Игрок<\/b>/);
    for (const id of ["CameraRecipient", "CameraAvailability", "CameraResult"]) {
        assert.equal(p.nodes.get(id).html, false);
    }
});

test("missing panels and initial rendering failure leave no active handler", () => {
    for (const options of [{ missing: "CameraResult" }, { failText: "CameraRecipient" }]) {
        const p = fixture(options);
        assert.throws(() => p.bind(p.gateway()));
        assert.equal(p.nodes.get("CameraFocus").events.onactivate, undefined);
    }
});

test("render failure disposes the adapter and stale clicks cannot move the camera", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    ui.setTarget(target());
    const old = p.nodes.get("CameraFocus").events.onactivate;
    p.options.failText = "CameraAvailability";
    assert.equal(ui.refresh(), false);
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.nodes.get("CameraFocus").visible, false);
    old(); assert.deepEqual(p.calls, []);
});

test("malformed check or focus result closes the panel without inventing success", () => {
    for (const kind of ["check", "focus"]) {
        const p = fixture();
        const gateway = p.gateway();
        if (kind === "check") { gateway.check = () => ({ available: "true", reason: null }); }
        else { gateway.focus = () => ({ requested: "true", reason: null }); }
        const ui = p.bind(gateway);
        ui.setTarget(target());
        if (kind === "focus") { p.click(); }
        assert.equal(ui.isDisposed(), true);
        assert.deepEqual(p.calls, []);
    }
});

test("gateway focus exception records unknown camera position without closing selection", () => {
    const p = fixture();
    const gateway = p.gateway();
    gateway.focus = () => { throw new Error("client call uncertain"); };
    const ui = p.bind(gateway);
    ui.setTarget(target()); p.click();
    assert.match(p.nodes.get("CameraResult").text, /неизвестно|подтвержд/);
    assert.equal(ui.isDisposed(), false);
});

test("root destruction and disposal ignore old clicks and later updates", () => {
    for (const method of ["dispose", "destroy"]) {
        const p = fixture();
        const ui = p.bind(p.gateway());
        ui.setTarget(target());
        const old = p.nodes.get("CameraFocus").events.onactivate;
        if (method === "dispose") { ui.dispose(); } else { p.root.valid = false; }
        old();
        assert.equal(ui.isDisposed(), true);
        assert.equal(ui.setTarget(target("b", 202)), false);
        assert.equal(ui.refresh(), false);
        assert.deepEqual(p.calls, []);
    }
});

test("one live adapter owns a root until disposal", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    assert.throws(() => p.context.DotaCoachCameraPanels.bind(p.root, p.gateway()));
    ui.dispose();
    const fresh = p.context.DotaCoachCameraPanels.bind(p.root, p.gateway());
    assert.equal(fresh.isDisposed(), false);
});

test("target getter disposal cannot restore panels or overwrite a new binding", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    let fresh;
    const row = target();
    Object.defineProperty(row, "playerName", { enumerable: true, get() {
        ui.dispose();
        fresh = p.context.DotaCoachCameraPanels.bind(p.root, p.gateway());
        fresh.setTarget(target("b", 202));
        return "Прежний игрок";
    } });
    assert.equal(ui.setTarget(row), false);
    assert.equal(fresh.isDisposed(), false);
    assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
    p.click(); assert.deepEqual(p.calls, [202]);
});

test("check-result getter disposal cannot paint over a fresh controller", () => {
    const p = fixture();
    const gateway = p.gateway();
    const ui = p.bind(gateway);
    let fresh;
    gateway.check = () => ({ get available() {
        ui.dispose(); fresh = p.context.DotaCoachCameraPanels.bind(p.root, p.gateway());
        fresh.setTarget(target("b", 202)); return true;
    }, reason: null });
    assert.equal(ui.setTarget(target()), false);
    assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
    assert.equal(fresh.isDisposed(), false);
});

test("reentrant focus selection does not attribute the old request to a new player", () => {
    const p = fixture();
    const gateway = p.gateway();
    let ui;
    gateway.focus = () => {
        ui.setTarget(target("b", 202)); return { requested: true, reason: null };
    };
    ui = p.bind(gateway); ui.setTarget(target()); p.click();
    assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
    assert.doesNotMatch(p.nodes.get("CameraResult").text, /игрок b.*передан|игрок b.*запрошен/);
});

test("native values are strict integers booleans and either playable team", () => {
    for (const player of [1.5, NaN, Infinity, "0", 64]) {
        const p = fixture({ player });
        assert.equal(p.gateway().check(101).available, false);
    }
    for (const field of ["valid", "real", "alive"]) {
        const p = fixture(); p.entities.get(101)[field] = "true";
        assert.equal(p.gateway().check(101).available, false);
    }
    const p = fixture({ team: 3 }); p.entities.get(101).team = 3;
    assert.equal(p.gateway().focus(101).requested, true);
    assert.deepEqual(p.calls, [101]);
});

test("check reentrancy that refreshes or changes selection invalidates the old click", () => {
    for (const mode of ["refresh", "select"]) {
        const p = fixture();
        const gateway = p.gateway();
        const ui = p.bind(gateway); ui.setTarget(target());
        let once = true;
        gateway.check = () => {
            if (once) {
                once = false;
                if (mode === "refresh") { ui.refresh(); } else { ui.setTarget(target("b", 202)); }
            }
            return { available: true, reason: null };
        };
        p.click();
        assert.deepEqual(p.calls, []);
    }
});

test("a focus-result getter cannot overwrite a rebound controller", () => {
    const p = fixture();
    const gateway = p.gateway();
    const ui = p.bind(gateway); ui.setTarget(target());
    let fresh;
    gateway.focus = () => ({ get requested() {
        ui.dispose(); fresh = p.context.DotaCoachCameraPanels.bind(p.root, p.gateway());
        fresh.setTarget(target("b", 202)); return true;
    }, reason: null });
    p.click();
    assert.equal(fresh.isDisposed(), false);
    assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
    assert.equal(p.nodes.get("CameraResult").text, "Фокус ещё не запрошен.");
});

test("refusal reasons must be readable bounded text", () => {
    for (const reason of [null, "", " ", "x".repeat(161)]) {
        const p = fixture();
        const gateway = p.gateway();
        gateway.check = () => ({ available: false, reason });
        const ui = p.bind(gateway);
        ui.setTarget(target());
        assert.equal(ui.isDisposed(), true);
    }
});

test("malformed stale gateway results cannot close a newer selection", () => {
    for (const method of ["check", "focus"]) {
        const p = fixture();
        const gateway = p.gateway();
        const original = gateway[method];
        const ui = p.bind(gateway); ui.setTarget(target());
        let once = true;
        gateway[method] = index => {
            if (!once) { return original(index); }
            once = false;
            const field = method === "check" ? "available" : "requested";
            return { get [field]() { ui.setTarget(target("b", 202)); return "bad"; }, reason: null };
        };
        p.click();
        assert.equal(ui.isDisposed(), false, method);
        assert.match(p.nodes.get("CameraRecipient").text, /игрок b/);
        assert.equal(p.nodes.get("CameraFocus").enabled, true);
    }
});

test("equal player names do not attribute a previous focus request to a new stable id", () => {
    const p = fixture();
    const ui = p.bind(p.gateway());
    ui.setTarget(target("a", 101, { playerName: "Alex" })); p.click();
    ui.setTarget(target("b", 202, { playerName: "Alex" }));
    assert.match(p.nodes.get("CameraRecipient").text, /Alex/);
    assert.match(p.nodes.get("CameraResult").text, /Предыдущ|предыдущ|ранее выбран/);
    assert.deepEqual(p.calls, [101]);
    ui.setTarget(target("a", 101, { playerName: "Alex" }));
    assert.doesNotMatch(p.nodes.get("CameraResult").text, /Предыдущ|предыдущ|ранее выбран/);
});
