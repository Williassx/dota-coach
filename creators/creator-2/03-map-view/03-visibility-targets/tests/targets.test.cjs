"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");

function fixture() {
    let time = 0, serial = 0;
    const timers = new Map(), forbidden = [];
    let failSchedule = false;
    const nodes = new Map();
    function panel(id) {
        return { id, valid: true, html: true, text: "", fail: false,
            IsValid() { return this.valid; } };
    }
    for (const id of ["TargetTitle", "TargetDetails", "TargetStatus"]) {
        const n = panel(id); let value = "";
        Object.defineProperty(n, "text", { configurable: true, get() { return value; }, set(v) {
            if (n.fail) { throw new Error("render"); } value = v;
        } }); nodes.set(id, n);
    }
    const root = panel("root"); root.FindChildTraverse = id => nodes.get(id);
    function forbiddenCall(name) { return () => { forbidden.push(name); throw new Error(name); }; }
    const context = vm.createContext({
        $: { Schedule(seconds, callback) {
            assert.equal(seconds, 0.1); if (failSchedule) { throw new Error("schedule"); }
            const id = ++serial; timers.set(id, callback); return id;
        }, CancelScheduled(id) { timers.delete(id); } },
        Entities: new Proxy({}, { get(_, key) { return forbiddenCall("Entities." + String(key)); } }),
        GameEvents: new Proxy({}, { get(_, key) { return forbiddenCall("GameEvents." + String(key)); } }),
        GameUI: new Proxy({}, { get(_, key) { return forbiddenCall("GameUI." + String(key)); } })
    });
    function load(name) { vm.runInContext(fs.readFileSync(path.join(scripts, name), "utf8"), context); }
    load("targets_state.js"); load("targets_panel.js");
    return { context, root, nodes, timers, forbidden,
        now: () => time, time: value => { time = value; },
        scheduleFailure: () => { failSchedule = true; },
        model(options) { return context.DotaCoachTargets.create(options || { now: () => time, maxAgeMs: 1000 }); },
        bind(options) { return context.DotaCoachTargetPanels.bind(root, options || { now: () => time, maxAgeMs: 1000 }); },
        tick() { const entry = timers.entries().next().value; assert.ok(entry); timers.delete(entry[0]); entry[1](); }
    };
}
function visible(id = "a", extra = {}) {
    return { id, visibility: "visible", label: "Синтетическая цель " + id,
        team: "enemy", kind: "hero", alive: true, entityIndex: 101, ...extra };
}
function snapshot(revision = 1, targets = [visible()]) { return { revision, targets }; }
function plain(value) { return JSON.parse(JSON.stringify(value)); }

test("no data and explicit null selection show no target or native action", () => {
    const p = fixture(), m = p.model();
    assert.equal(m.view().status, "empty"); assert.equal(m.view().target, null);
    assert.equal(m.select(null), true); assert.deepEqual(p.forbidden, []);
});
test("visible ally enemy hero and creep require explicit selection", () => {
    for (const team of ["ally", "enemy"]) for (const kind of ["hero", "creep"]) {
        const p = fixture(), m = p.model();
        assert.equal(m.update(snapshot(1, [visible("a", { team, kind })])), true);
        assert.equal(m.view().target, null); assert.equal(m.select("a"), true);
        assert.equal(m.view().status, "ready"); assert.equal(m.view().target.team, team);
        assert.equal(m.view().target.kind, kind); assert.deepEqual(p.forbidden, []);
    }
});
test("visible dead target retains observation without claiming an action", () => {
    const p = fixture(), m = p.model(); m.update(snapshot()); m.select("a");
    m.update(snapshot(2, [visible("a", { alive: false })]));
    assert.equal(m.view().status, "dead"); assert.equal(m.view().target.alive, false);
    assert.doesNotMatch(m.view().message, /атак.*доступ|выполнен/);
});
test("hidden gone unknown and removal clear selected data and preserve generic reason", () => {
    for (const visibility of ["hidden", "gone", "unknown", "removed"]) {
        const p = fixture(), m = p.model(); m.update(snapshot()); m.select("a");
        m.update(snapshot(2, visibility === "removed" ? [] : [{ id: "a", visibility }]));
        const view = m.view(); assert.equal(view.status, "unavailable"); assert.equal(view.target, null);
        assert.doesNotMatch(JSON.stringify(view), /Синтетическая|entityIndex|101/);
        assert.match(view.message, visibility === "hidden" ? /не видна/ : visibility === "unknown" ? /неизвестна/ : /не наблюдается/);
        m.update(snapshot(3)); assert.equal(m.view().target, null);
        assert.equal(m.view().status, "unavailable"); assert.equal(m.select("a"), true);
    }
});
test("unseen ids cannot disclose a hidden tombstone through selection", () => {
    const p = fixture(), m = p.model(); m.update(snapshot(1, [{ id: "never-seen", visibility: "hidden" }]));
    assert.equal(m.select("never-seen"), false);
    assert.equal(m.view().target, null); assert.doesNotMatch(m.view().message, /скры|не видна/);
});
test("nonvisible fields are rejected without reading hidden labels or entity indices", () => {
    const p = fixture(), m = p.model(); let reads = 0;
    const row = { id: "a", visibility: "hidden", get label() { reads++; throw new Error("hidden"); },
        get entityIndex() { reads++; throw new Error("hidden"); } };
    m.update(snapshot()); m.select("a"); assert.equal(m.update(snapshot(2, [row])), false);
    assert.equal(reads, 0); assert.equal(m.view().status, "invalid"); assert.equal(m.view().target, null);
});
test("freshness expires exactly at its local receipt bound and cannot auto-restore", () => {
    const p = fixture(), m = p.model(); p.time(100); m.update(snapshot()); m.select("a");
    p.time(1099); assert.equal(m.view().status, "ready");
    p.time(1100); assert.equal(m.view().status, "stale"); assert.equal(m.view().target, null);
    m.update(snapshot(2)); assert.equal(m.view().target, null); assert.equal(m.select("a"), true);
});
test("old duplicate revisions never refresh receipt time or replace a visible label", () => {
    const p = fixture(), m = p.model(); m.update(snapshot(2)); m.select("a"); p.time(900);
    for (const rev of [1, 2]) assert.equal(m.update(snapshot(rev, [visible("a", { label: "wrong" })])), false);
    assert.notEqual(m.view().target.label, "wrong"); p.time(1000); assert.equal(m.view().status, "stale");
    assert.equal(m.update(snapshot(2)), false); assert.equal(m.view().target, null);
});
test("full snapshot copies and returned views cannot mutate subsequent UI", () => {
    const p = fixture(), m = p.model(); const input = snapshot(); m.update(input); m.select("a");
    input.targets[0].label = "changed"; input.targets.length = 0;
    const out = m.view(); out.target.label = "also changed";
    assert.equal(m.view().target.label, "Синтетическая цель a");
    assert.deepEqual(Object.keys(plain(m.view().target)).sort(), ["alive", "entityIndex", "id", "kind", "label", "team"]);
});
test("invalid snapshots clear prior data and exact schemas reject coordinates", () => {
    const invalid = [null, { revision: 2, targets: [], extra: true }, snapshot(-1), snapshot(1.5),
        snapshot(9007199254740992), snapshot(2, "bad"), snapshot(2, [visible("a", { x: 7 })]),
        snapshot(2, [visible("a", { alive: 1 })]), snapshot(2, [visible("a", { entityIndex: -1 })]),
        snapshot(2, [visible("a", { team: "unknown" })]), snapshot(2, [visible("a", { kind: "tower" })]),
        snapshot(2, [visible("a", { id: " padded " })]), snapshot(2, [visible("a", { label: " " })]),
        snapshot(2, [visible("a", { visibility: "bogus" })]), snapshot(2, [visible(), visible()])];
    for (const input of invalid) {
        const p = fixture(), m = p.model(); m.update(snapshot()); m.select("a");
        assert.equal(m.update(input), false); assert.equal(m.view().status, "invalid"); assert.equal(m.view().target, null);
    }
});
test("input target count and field lengths stay bounded", () => {
    for (const input of [snapshot(2, Array.from({ length: 33 }, (_, n) => visible(String(n)))),
        snapshot(2, [visible("x".repeat(65))]), snapshot(2, [visible("a", { label: "x".repeat(65) })])]) {
        const p = fixture(), m = p.model(); assert.equal(m.update(input), false);
    }
    const p = fixture(), m = p.model();
    assert.equal(m.update(snapshot(1, Array.from({ length: 32 }, (_, n) => visible(String(n))))), true);
});
test("array growth while copying cannot pass the bounded observation limit", () => {
    const p = fixture(), m = p.model(); const rows = [visible()];
    Object.defineProperty(rows[0], "label", { get() { rows.length = 33; return "grow"; } });
    assert.equal(m.update(snapshot(1, rows)), false); assert.equal(m.view().target, null);
});
test("clock exception nonnumber rollback and recovery clear previous data", () => {
    for (const bad of [NaN, Infinity, -1, "0", 9]) {
        const p = fixture(), m = p.model(); p.time(10); m.update(snapshot()); m.select("a"); p.time(bad);
        assert.equal(m.view().status, "invalid"); assert.equal(m.view().target, null);
        p.time(20); assert.equal(m.update(snapshot(2)), true); assert.equal(m.view().target, null);
    }
    const p = fixture(); let throws = false;
    const m = p.model({ now() { if (throws) throw new Error("clock"); return 0; }, maxAgeMs: 1000 });
    m.update(snapshot()); m.select("a"); throws = true; assert.equal(m.view().target, null);
});
test("explicit clock and bounded maxAge options are required", () => {
    const p = fixture();
    for (const options of [null, {}, { now: 0, maxAgeMs: 1 }, { now: p.now, maxAgeMs: 0 },
        { now: p.now, maxAgeMs: 60001 }, { now: p.now, maxAgeMs: 1.5 }]) {
        assert.throws(() => p.context.DotaCoachTargets.create(options));
    }
});
test("disposed model cannot accept input or read data back", () => {
    const p = fixture(), m = p.model(); m.update(snapshot()); m.select("a"); m.dispose(); m.dispose();
    assert.equal(m.isDisposed(), true); assert.equal(m.update(snapshot(2)), false); assert.equal(m.select("a"), false);
    assert.equal(m.view().status, "disposed"); assert.equal(m.view().target, null);
});
test("input getter disposal and reentrant update cannot restore older observations", () => {
    for (const mode of ["dispose", "update"]) {
        const p = fixture(), m = p.model(); const row = visible();
        Object.defineProperty(row, "label", { get() {
            if (mode === "dispose") m.dispose(); else m.update(snapshot(5, [visible("b")]));
            return "old";
        } });
        assert.equal(m.update(snapshot(1, [row])), false);
        if (mode === "dispose") assert.equal(m.view().status, "disposed");
        else { assert.equal(m.select("b"), true); assert.equal(m.view().target.id, "b"); }
    }
});
test("stale malformed getter result cannot erase a reentrant newer observation", () => {
    const p = fixture(), m = p.model(); const row = visible();
    Object.defineProperty(row, "label", { get() { m.update(snapshot(5, [visible("b")])); return null; } });
    assert.equal(m.update(snapshot(1, [row])), false); assert.equal(m.select("b"), true);
    assert.equal(m.view().target.id, "b");
});
test("clock getter disposal cannot restore model selection", () => {
    const p = fixture(); let close = false, m;
    m = p.model({ now() { if (close) m.dispose(); return 0; }, maxAgeMs: 1000 });
    m.update(snapshot()); close = true; assert.equal(m.select("a"), false);
    assert.equal(m.view().status, "disposed");
});
test("panel uses plain text and clears labels immediately on disappearance", () => {
    const p = fixture(), ui = p.bind(); assert.equal(p.timers.size, 1);
    ui.update(snapshot(1, [visible("a", { label: "<b>name</b>", team: "ally", kind: "creep" })])); ui.select("a");
    assert.equal(p.nodes.get("TargetTitle").text, "<b>name</b>");
    assert.match(p.nodes.get("TargetDetails").text, /Союзный крип/);
    assert.ok([...p.nodes.values()].every(n => n.html === false));
    ui.update(snapshot(2, [{ id: "a", visibility: "gone" }]));
    assert.doesNotMatch(p.nodes.get("TargetTitle").text, /name/);
    assert.equal(p.nodes.get("TargetDetails").text, ""); assert.match(p.nodes.get("TargetStatus").text, /не наблюдается/);
    assert.deepEqual(p.forbidden, []);
});
test("watcher expires labels without another user action and remains singular", () => {
    const p = fixture(), ui = p.bind(); ui.update(snapshot()); ui.select("a");
    p.time(1000); p.tick(); assert.equal(p.timers.size, 1);
    assert.doesNotMatch(p.nodes.get("TargetTitle").text, /Синтетическая/);
    assert.equal(p.nodes.get("TargetDetails").text, ""); assert.match(p.nodes.get("TargetStatus").text, /устарел/);
});
test("dispose root destruction and stale watcher cannot repaint or reschedule", () => {
    for (const mode of ["dispose", "root"]) {
        const p = fixture(), ui = p.bind(); const old = [...p.timers.values()][0];
        if (mode === "dispose") ui.dispose(); else p.root.valid = false;
        old(); assert.equal(ui.isDisposed(), true); assert.equal(p.timers.size, 0);
        assert.equal(ui.update(snapshot()), false); assert.equal(ui.select("a"), false);
    }
});
test("exclusive panel ownership is released only after disposal", () => {
    const p = fixture(), ui = p.bind(); assert.throws(() => p.bind()); assert.equal(p.timers.size, 1);
    ui.dispose(); const fresh = p.bind(); assert.equal(fresh.isDisposed(), false); assert.equal(p.timers.size, 1);
});
test("partial bind rendering and initial schedule failures leave no watcher", () => {
    for (const mode of ["missing", "render", "schedule"]) {
        const p = fixture();
        if (mode === "missing") p.nodes.delete("TargetStatus");
        if (mode === "render") p.nodes.get("TargetTitle").fail = true;
        if (mode === "schedule") p.scheduleFailure();
        assert.throws(() => p.bind()); assert.equal(p.timers.size, 0);
    }
});
test("later render and reschedule failures dispose and clear the existing watcher", () => {
    for (const mode of ["render", "schedule"]) {
        const p = fixture(), ui = p.bind();
        if (mode === "render") { p.nodes.get("TargetTitle").fail = true; assert.equal(ui.update(snapshot()), false); }
        else { p.scheduleFailure(); p.tick(); }
        assert.equal(ui.isDisposed(), true); assert.equal(p.timers.size, 0);
    }
});
test("old panel input getter cannot paint over a newly rebound controller", () => {
    const p = fixture(), ui = p.bind(); let fresh; const row = visible();
    Object.defineProperty(row, "label", { get() {
        ui.dispose(); fresh = p.bind(); fresh.update(snapshot(2, [visible("b")])); fresh.select("b"); return "old";
    } });
    assert.equal(ui.update(snapshot(1, [row])), false);
    assert.equal(fresh.isDisposed(), false); assert.equal(p.nodes.get("TargetTitle").text, "Синтетическая цель b");
    assert.equal(p.timers.size, 1);
});

test("old malformed body is not read and cannot invalidate a newer observation", () => {
    const p = fixture(), m = p.model(); m.update(snapshot(10)); m.select("a"); let reads = 0;
    for (const revision of [9, 10]) {
        assert.equal(m.update({ revision, get targets() { reads++; throw new Error("old body"); } }), false);
    }
    assert.equal(reads, 0); assert.equal(m.view().status, "ready");
});
test("new invalid body consumes revision and old observations cannot restore data", () => {
    const p = fixture(), m = p.model(); m.update(snapshot(10)); m.select("a");
    assert.equal(m.update(snapshot(20, [visible("a", { label: null })])), false);
    for (const revision of [9, 10, 19, 20]) assert.equal(m.update(snapshot(revision)), false);
    assert.equal(m.view().target, null); assert.equal(m.update(snapshot(21)), true);
});
test("expiry is synchronous for select and old update before a watcher can run", () => {
    for (const method of ["select", "update"]) {
        const p = fixture(), m = p.model({ now: p.now, maxAgeMs: 50 }); m.update(snapshot()); m.select("a");
        p.time(51); assert.equal(method === "select" ? m.select("a") : m.update(snapshot()), false);
        assert.equal(m.view().status, "stale"); assert.equal(m.view().target, null);
    }
});
test("throw after reentrant update does not erase newer data", () => {
    const p = fixture(), m = p.model(); const row = visible();
    Object.defineProperty(row, "label", { get() { m.update(snapshot(5, [visible("b")])); throw new Error("old"); } });
    assert.equal(m.update(snapshot(1, [row])), false); assert.equal(m.select("b"), true);
    assert.equal(m.view().target.id, "b");
});
test("old clock callback cannot paint or cancel a fresh binding timer", () => {
    const p = fixture(); let rebound = false, ui, fresh;
    ui = p.bind({ now() {
        if (rebound) { rebound = false; ui.dispose(); fresh = p.bind(); fresh.update(snapshot(2, [visible("b")])); fresh.select("b"); }
        return 0;
    }, maxAgeMs: 1000 });
    ui.update(snapshot()); ui.select("a"); rebound = true; p.tick();
    assert.equal(ui.isDisposed(), true); assert.equal(fresh.isDisposed(), false);
    assert.equal(p.nodes.get("TargetTitle").text, "Синтетическая цель b"); assert.equal(p.timers.size, 1);
});

test("option getters cannot establish a second live owner during binding", () => {
    const p = fixture();
    assert.throws(() => p.bind({ get now() { p.bind(); return p.now; }, maxAgeMs: 1000 }));
    assert.equal(p.timers.size, 0);
    const fresh = p.bind(); assert.equal(fresh.isDisposed(), false); assert.equal(p.timers.size, 1);
});

test("disposal clears the last visible target from a still-live panel", () => {
    const p = fixture(), ui = p.bind(); ui.update(snapshot()); ui.select("a"); ui.dispose();
    assert.doesNotMatch([...p.nodes.values()].map(n => n.text).join(" "), /Синтетическая|Цель видна|· жив/);
    assert.equal(p.nodes.get("TargetDetails").text, ""); assert.equal(p.timers.size, 0);
});
test("changed visibility is rejected before reading remaining visible fields", () => {
    const p = fixture(), m = p.model(); let reads = 0, labels = 0, indices = 0;
    const row = visible();
    Object.defineProperty(row, "visibility", { get() { reads++; return reads === 1 ? "visible" : "hidden"; } });
    Object.defineProperty(row, "label", { get() { labels++; return "hidden name"; } });
    Object.defineProperty(row, "entityIndex", { get() { indices++; return 123; } });
    assert.equal(m.update(snapshot(1, [row])), false); assert.equal(labels, 0); assert.equal(indices, 0);
    assert.equal(m.view().target, null);
});
test("nonenumerable own extras cannot bypass exact projection schemas", () => {
    for (const place of ["snapshot", "row", "options"]) {
        const p = fixture(), m = p.model(); let reads = 0;
        const input = snapshot(); const options = { now: p.now, maxAgeMs: 1000 };
        const value = place === "snapshot" ? input : place === "row" ? input.targets[0] : options;
        Object.defineProperty(value, "x", { get() { reads++; return 100; } });
        if (place === "options") assert.throws(() => p.context.DotaCoachTargets.create(options));
        else assert.equal(m.update(input), false);
        assert.equal(reads, 0);
    }
});
test("rendering reentry cannot overwrite a newer selection or fresh binding", () => {
    for (const mode of ["select", "rebind"]) {
        const p = fixture(), ui = p.bind(); let fresh = ui, once = true;
        ui.update(snapshot(1, [visible(), visible("b", { team: "ally" })]));
        const title = p.nodes.get("TargetTitle"), descriptor = Object.getOwnPropertyDescriptor(title, "text");
        Object.defineProperty(title, "text", { configurable: true, get: descriptor.get, set(value) {
            descriptor.set.call(this, value);
            if (once && value === "Синтетическая цель a") {
                once = false;
                if (mode === "rebind") { ui.dispose(); fresh = p.bind(); fresh.update(snapshot(2, [visible("b", { team: "ally" })])); }
                fresh.select("b");
            }
        } });
        assert.equal(ui.select("a"), false); assert.equal(fresh.isDisposed(), false);
        assert.equal(title.text, "Синтетическая цель b");
        assert.match(p.nodes.get("TargetDetails").text, /Союзный/); assert.equal(p.timers.size, 1);
    }
});

test("a newer selection during watcher rendering retains automatic expiry", () => {
    const p = fixture(), ui = p.bind();
    ui.update(snapshot(1, [visible(), visible("b", { team: "ally" })])); ui.select("a");
    const title = p.nodes.get("TargetTitle"), descriptor = Object.getOwnPropertyDescriptor(title, "text");
    let once = true;
    Object.defineProperty(title, "text", { configurable: true, get: descriptor.get, set(value) {
        descriptor.set.call(this, value);
        if (once) { once = false; ui.select("b"); }
    } });
    p.tick(); assert.equal(ui.isDisposed(), false); assert.equal(p.timers.size, 1);
    assert.equal(title.text, "Синтетическая цель b"); p.time(1000); p.tick();
    assert.doesNotMatch(title.text, /Синтетическая/); assert.match(p.nodes.get("TargetStatus").text, /устарел/);
});
