"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");
const row = (id = "a", extra = {}) => ({id, playerName: "Игрок " + id, heroName: "Zeus", ...extra});
const snapshot = (revision = 1, players = [row()]) => ({revision, players});
function fixture() {
    const deny = new Proxy({}, {get() {throw Error("no game API");}});
    const context = vm.createContext({$: deny, Game: deny});
    for (const name of ["opponent_roster_state.js", "opponent_roster_panel.js"]) {
        const file = path.join(scripts, name);
        assert.ok(fs.existsSync(file), name + " must exist");
        vm.runInContext(fs.readFileSync(file, "utf8"), context);
    }
    const labels = ["OpponentRosterStatus", "OpponentRosterHint"];
    const containers = ["OpponentCards"];
    for (let i = 0; i < 5; i++) {
        containers.push("OpponentCard" + i);
        labels.push("OpponentName" + i, "OpponentHero" + i, "OpponentInformation" + i);
    }
    const nodes = {};
    for (const id of labels.concat(containers)) nodes[id] = {visible: true, valid: true,
        html: true, text: "old", IsValid() {return this.valid;}};
    const root = {visible: false, valid: true, IsValid() {return this.valid;}, FindChildTraverse(id) {return nodes[id];}};
    return {context, root, nodes, labels, bind: () => context.DotaCoachOpponentPanels.bind(root)};
}
test("explicit binding renders unavailable source with plain empty identities", () => {
    const f = fixture(); assert.equal(f.root.visible, false);
    const p = f.bind(); assert.equal(f.root.visible, true); assert.equal(p.view().ready, false);
    assert.match(f.nodes.OpponentRosterStatus.text, /недоступен/);
    assert.equal(f.nodes.OpponentName0.text, "");
    assert.ok(f.labels.every(id => f.nodes[id].html === false));
});
test("five slots display public identities literally and missing identities as unknown", () => {
    const f = fixture(), p = f.bind();
    assert.equal(p.update(snapshot(1, [row("a", {playerName: "<b>A</b>", heroName: null})])), true);
    assert.equal(f.nodes.OpponentName0.text, "<b>A</b>");
    assert.equal(f.nodes.OpponentHero0.text, "Герой неизвестен");
    assert.equal(f.nodes.OpponentName4.text, "Имя неизвестно");
    assert.equal(f.nodes.OpponentInformation4.text, "Боевые данные неизвестны.");
    assert.equal(p.view().sourceAuthorizationConfirmed, false);
});
test("valid empty roster remains ready and differs from invalid input", () => {
    const f = fixture(), p = f.bind();
    assert.equal(p.update(snapshot(1, [])), true); assert.equal(p.view().ready, true);
    assert.match(f.nodes.OpponentRosterStatus.text, /0 из 5/);
    assert.equal(p.update(null), false); assert.equal(p.view().ready, false);
    assert.equal(f.nodes.OpponentName4.text, "");
});
test("new ordered roster replaces old names and public projection is copied", () => {
    const f = fixture(), p = f.bind(); p.update(snapshot(1, [row("a"), row("b")]));
    p.update(snapshot(2, [row("b"), row("a")]));
    assert.equal(f.nodes.OpponentName0.text, "Игрок b");
    const view = p.view(); view.players[0].playerName = "changed";
    assert.equal(p.view().players[0].playerName, "Игрок b");
});
test("visible old data is cleared before DTO traps and refresh cannot revive it", () => {
    const f = fixture(), p = f.bind(); p.update(snapshot()); let inspected = false;
    const input = new Proxy({}, {ownKeys() {
        inspected = true; assert.equal(f.root.visible, false);
        assert.ok(f.labels.every(id => f.nodes[id].text === ""));
        assert.equal(p.view(), null); return [];
    }});
    assert.equal(p.update(input), false); assert.equal(inspected, true);
    assert.equal(p.refresh(), true); assert.equal(p.view().ready, false);
    assert.equal(p.update(snapshot(1)), false); assert.equal(p.update(snapshot(2)), true);
});
test("equal revision conflicts and stale sources do not display previous enemies", () => {
    const f = fixture(), p = f.bind(); p.update(snapshot(3));
    assert.equal(p.update(snapshot(3, [row("b")])), false);
    assert.equal(f.nodes.OpponentName0.text, "");
    assert.equal(p.update(snapshot(2)), false); assert.equal(p.update(snapshot(4)), true);
});
test("all labels and containers including unused slots are required", () => {
    for (const id of ["OpponentName4", "OpponentInformation4", "OpponentCards", "OpponentCard4"]) {
        for (const issue of ["missing", "hidden", "invalid", "replaced"]) {
            const f = fixture(), p = f.bind(); p.update(snapshot());
            if (issue === "missing") delete f.nodes[id];
            if (issue === "hidden") f.nodes[id].visible = false;
            if (issue === "invalid") f.nodes[id].valid = false;
            if (issue === "replaced") f.nodes[id] = {...f.nodes[id]};
            assert.equal(p.refresh(), false); assert.equal(p.isDisposed(), true);
            assert.equal(f.root.visible, false); assert.equal(f.nodes.OpponentName0.text, "");
        }
    }
});
test("isDisposed checks native tree and root visibility on explicit call", () => {
    for (const issue of ["hiddenRoot", "missingChild", "invalidRoot"]) {
        const f = fixture(), p = f.bind();
        if (issue === "hiddenRoot") f.root.visible = false;
        if (issue === "missingChild") delete f.nodes.OpponentCard4;
        if (issue === "invalidRoot") f.root.valid = false;
        assert.equal(p.isDisposed(), true); assert.equal(p.view().closed, true);
    }
});
test("ownership is reserved before native discovery; duplicate bind preserves active panel", () => {
    const f = fixture(), find = f.root.FindChildTraverse;
    f.root.FindChildTraverse = function (id) {assert.throws(() => f.bind(), /already bound/); return find.call(this, id);};
    const p = f.bind(); assert.throws(() => f.bind(), /already bound/);
    assert.equal(p.isDisposed(), false); assert.equal(f.root.visible, true);
});
test("partial binding failure clears labels and releases root for repair", () => {
    const f = fixture(), saved = f.nodes.OpponentCard4; delete f.nodes.OpponentCard4;
    assert.throws(() => f.bind()); assert.equal(f.root.visible, false);
    assert.equal(f.nodes.OpponentName0.text, "");
    f.nodes.OpponentCard4 = saved; assert.equal(f.bind().isDisposed(), false);
});
test("busy native callbacks reject nested updates before DTO inspection", () => {
    const f = fixture(), p = f.bind(), find = f.root.FindChildTraverse;
    let reads = 0;
    const unread = new Proxy({}, {ownKeys() {reads++; return [];}});
    f.root.FindChildTraverse = function (id) {
        assert.equal(p.update(unread), false); assert.equal(p.refresh(), false);
        assert.equal(p.view(), null); assert.equal(p.isDisposed(), false);
        return find.call(this, id);
    };
    assert.equal(p.update(snapshot()), true); assert.equal(reads, 0);
});
test("dispose during source inspection aborts painting; old API cannot touch new binding", () => {
    const f = fixture(), p = f.bind(); p.update(snapshot());
    const input = new Proxy(snapshot(2), {ownKeys(target) {p.dispose(); return Reflect.ownKeys(target);}});
    assert.equal(p.update(input), false); assert.equal(p.isDisposed(), true);
    assert.equal(f.root.visible, false); assert.equal(f.nodes.OpponentName0.text, "");
    const fresh = f.bind(); fresh.update(snapshot(1, [row("b")]));
    assert.equal(p.update(new Proxy({}, {ownKeys() {throw Error("unread");}})), false);
    p.dispose(); p.refresh(); p.view(); p.isDisposed();
    assert.equal(f.nodes.OpponentName0.text, "Игрок b"); assert.equal(fresh.isDisposed(), false);
});
test("dispose during native text setter stops writes and retains ownership until cleanup", () => {
    const f = fixture(), p = f.bind(); let text = "", triggered = false;
    Object.defineProperty(f.nodes.OpponentName0, "text", {get() {return text;}, set(value) {
        text = value;
        if (value === "Игрок a" && !triggered) {
            triggered = true; p.dispose(); assert.throws(() => f.bind(), /already bound/);
        }
    }});
    assert.equal(p.update(snapshot()), false); assert.equal(triggered, true);
    assert.equal(f.root.visible, false); assert.equal(text, "");
    assert.equal(f.bind().isDisposed(), false);
});
