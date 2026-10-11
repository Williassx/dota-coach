"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");
const repo = path.resolve(__dirname, "../../../../..");
const plain = value => JSON.parse(JSON.stringify(value));
const actor = (id = "a", extra = {}) => ({id, playerName: "Игрок " + id, mode: "AI", epoch: 1,
    revision: 1, side: "own", availability: "alive", ...extra});

function fixture() {
    const context = vm.createContext({$: new Proxy({}, {get() {throw Error("no game API");}})});
    vm.runInContext(fs.readFileSync(path.join(repo,
        "creators/creator-2/02-coach-interface/02-status-orders/src/panorama/scripts/custom_game/orders_state.js"), "utf8"), context);
    for (const name of ["orders_timeline_state.js", "orders_timeline_panel.js"])
        vm.runInContext(fs.readFileSync(path.join(scripts, name), "utf8"), context);
    const orders = context.DotaCoachOrders.create(true);
    orders.setRecipient(actor());
    const nodes = {};
    for (const id of ["TimelineTitle", "TimelineSummary", "TimelineHint", ...Array.from({length: 6}, (_, i) => "TimelineEvent" + i)])
        nodes[id] = {visible: true, valid: true, html: true, text: "stale", IsValid() {return this.valid;}};
    const root = {visible: false, valid: true, IsValid() {return this.valid;}, FindChildTraverse(id) {return nodes[id];}};
    return {context, orders, root, nodes, bind: () => context.DotaCoachOrdersTimelinePanels.bind(root)};
}
function completion(f) {
    f.orders.begin("move");
    f.orders.report(f.orders.view().ticket, {sequence: 0, stage: "completed", reason: null});
}

test("explicit binding has no demo and labels are plain", () => {
    const f = fixture();
    assert.equal(f.root.visible, false);
    const panel = f.bind();
    assert.equal(f.root.visible, true);
    assert.equal(panel.view().ready, false);
    assert.ok(Object.values(f.nodes).every(n => n.html === false));
    assert.match(f.nodes.TimelineHint.text, /не подтверждён/);
    assert.equal(f.nodes.TimelineEvent0.text, "");
});

test("records report stages and refresh does not duplicate events", () => {
    const f = fixture(), panel = f.bind();
    f.orders.begin("move");
    assert.equal(panel.record(f.orders.view()), true);
    assert.match(f.nodes.TimelineEvent0.text, /Ожидается/);
    f.orders.report(1, {sequence: 0, stage: "accepted", reason: null});
    panel.record(f.orders.view());
    assert.match(f.nodes.TimelineEvent1.text, /выполнение не подтверждено/);
    assert.equal(panel.refresh(), true);
    assert.equal(panel.view().events.length, 2);
    assert.equal(panel.record(f.orders.view()), true);
    assert.equal(panel.view().events.length, 2);
});

test("selected card does not change historical actor", () => {
    const f = fixture(), panel = f.bind();
    f.orders.begin("move");
    panel.record(f.orders.view());
    f.orders.setRecipient(actor("b"));
    panel.record(f.orders.view());
    assert.match(f.nodes.TimelineEvent0.text, /Игрок a/);
    assert.doesNotMatch(f.nodes.TimelineEvent0.text, /Игрок b/);
    assert.equal(panel.view().events.length, 1);
});

test("latest six events count hidden saved history and true drops separately", () => {
    const f = fixture(), panel = f.bind();
    for (let i = 0; i < 70; i++) {completion(f); panel.record(f.orders.view());}
    const view = panel.view();
    assert.equal(view.events.length, 6);
    assert.equal(view.totalStored, 64);
    assert.equal(view.hiddenStored, 58);
    assert.equal(view.droppedEvents, 6);
    assert.deepEqual(plain(view.events.map(e => e.eventIndex)), [65, 66, 67, 68, 69, 70]);
    assert.match(f.nodes.TimelineSummary.text, /6 из 64/);
    assert.match(f.nodes.TimelineSummary.text, /Вытеснено: 6/);
});

test("invalid source clears display before proxy inspection and closes gate until valid source", () => {
    const f = fixture(), panel = f.bind();
    completion(f); panel.record(f.orders.view());
    let checked = false;
    const bad = new Proxy({}, {ownKeys() {
        checked = true;
        assert.equal(f.root.visible, false);
        assert.equal(f.nodes.TimelineEvent0.text, "");
        return [];
    }});
    assert.equal(panel.record(bad), false);
    assert.equal(checked, true);
    assert.equal(panel.view().ready, false);
    assert.equal(panel.view().events.length, 0);
    panel.refresh();
    assert.equal(f.nodes.TimelineEvent0.text, "");
    assert.equal(panel.record(f.orders.view()), true);
    assert.equal(panel.view().events.length, 1);
});

test("returned projection is copied", () => {
    const f = fixture(), panel = f.bind();
    completion(f); panel.record(f.orders.view());
    const view = panel.view();
    view.events[0].actorName = "Подмена";
    assert.equal(panel.view().events[0].actorName, "Игрок a");
});

test("missing hidden invalid and replaced required labels fail closed", () => {
    for (const issue of ["missing", "hidden", "invalid", "replaced"]) {
        const f = fixture(), panel = f.bind();
        const node = f.nodes.TimelineEvent5;
        if (issue === "missing") delete f.nodes.TimelineEvent5;
        if (issue === "hidden") node.visible = false;
        if (issue === "invalid") node.valid = false;
        if (issue === "replaced") f.nodes.TimelineEvent5 = {...node};
        assert.equal(panel.refresh(), false);
        assert.equal(panel.isDisposed(), true);
        assert.equal(f.root.visible, false);
    }
});

test("isDisposed inspects the tree without requiring record or refresh", () => {
    const f = fixture(), panel = f.bind();
    delete f.nodes.TimelineEvent5;
    assert.equal(panel.isDisposed(), true);
    assert.equal(f.root.visible, false);
    assert.equal(f.nodes.TimelineEvent0.text, "");
});

test("root ownership is reserved before discovery and duplicate binding preserves active root", () => {
    const f = fixture();
    const find = f.root.FindChildTraverse;
    f.root.FindChildTraverse = function(id) {assert.throws(() => f.bind(), /already bound/); return find.call(this, id);};
    const panel = f.bind();
    assert.throws(() => f.bind(), /already bound/);
    assert.equal(panel.isDisposed(), false);
    assert.equal(f.root.visible, true);
});

test("partial bind failure cleans and releases ownership for repair", () => {
    const f = fixture(), missing = f.nodes.TimelineEvent5;
    delete f.nodes.TimelineEvent5;
    assert.throws(() => f.bind());
    assert.equal(f.root.visible, false);
    f.nodes.TimelineEvent5 = missing;
    const panel = f.bind();
    assert.equal(panel.isDisposed(), false);
});

test("busy preflight rejects nested calls before native and DTO reads", () => {
    const f = fixture(), panel = f.bind();
    const find = f.root.FindChildTraverse;
    let inside = false, reads = 0;
    const unread = new Proxy({}, {ownKeys() {reads++; return [];}});
    f.root.FindChildTraverse = function(id) {
        if (!inside) {
            inside = true;
            assert.equal(panel.record(unread), false);
            assert.equal(panel.refresh(), false);
            assert.equal(panel.view(), null);
            assert.equal(panel.isDisposed(), false);
            inside = false;
        }
        return find.call(this, id);
    };
    completion(f);
    assert.equal(panel.record(f.orders.view()), true);
    assert.equal(reads, 0);
});

test("dispose during source inspection aborts paint and releases root", () => {
    const f = fixture(), panel = f.bind();
    completion(f);
    const row = plain(f.orders.view());
    const input = new Proxy(row, {ownKeys(target) {panel.dispose(); return Reflect.ownKeys(target);}});
    assert.equal(panel.record(input), false);
    assert.equal(panel.isDisposed(), true);
    assert.equal(f.nodes.TimelineEvent0.text, "");
    assert.equal(f.root.visible, false);
    const fresh = f.bind();
    assert.equal(fresh.isDisposed(), false);
});

test("old closed binding never reads source or overwrites fresh binding", () => {
    const f = fixture(), old = f.bind();
    old.dispose();
    const fresh = f.bind();
    completion(f); fresh.record(f.orders.view());
    const text = f.nodes.TimelineEvent0.text;
    const input = new Proxy({}, {ownKeys() {throw Error("must not inspect");}});
    assert.equal(old.record(input), false);
    assert.equal(old.refresh(), false);
    old.dispose();
    assert.equal(f.nodes.TimelineEvent0.text, text);
    assert.equal(f.root.visible, true);
});

test("closed source and externally hidden root close binding", () => {
    for (const close of ["source", "root"]) {
        const f = fixture(), panel = f.bind();
        if (close === "source") {f.orders.dispose(); panel.record(f.orders.view());}
        else {f.root.visible = false; panel.refresh();}
        assert.equal(panel.isDisposed(), true);
        assert.equal(f.root.visible, false);
        assert.equal(f.nodes.TimelineEvent0.text, "");
    }
});

test("names and reasons display literally as plain text", () => {
    const f = fixture(), panel = f.bind();
    f.orders.setRecipient(actor("a", {playerName: "<b>Имя</b>", revision: 2}));
    f.orders.begin("move");
    f.orders.report(1, {sequence: 0, stage: "rejected", reason: "<script>Причина</script>"});
    panel.record(f.orders.view());
    assert.match(f.nodes.TimelineEvent0.text, /<b>Имя<\/b>/);
    assert.match(f.nodes.TimelineEvent0.text, /<script>Причина<\/script>/);
    assert.equal(f.nodes.TimelineEvent0.html, false);
});
