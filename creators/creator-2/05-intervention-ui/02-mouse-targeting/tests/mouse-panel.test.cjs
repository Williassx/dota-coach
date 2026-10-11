"use strict";
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path");
const test = require("node:test"), vm = require("node:vm");
const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");
const actor = (id = "a") => ({id, playerName: "Player " + id, epoch: 1});
const point = () => ({x: 100, y: 200, z: 0});
const target = (team = "enemy", kind = "hero") => ({status: "ready", message: "", target:
    {id: "target", label: "<b>Target</b>", team, kind, alive: true, entityIndex: 10}});
function fixture() {
    const deny = new Proxy({}, {get() {throw Error("no native API");}});
    const context = vm.createContext({$: deny, Game: deny});
    for (const name of ["mouse_proposal_state.js", "mouse_proposal_panel.js"]) {
        const file = path.join(scripts, name); assert.ok(fs.existsSync(file), name + " must exist");
        vm.runInContext(fs.readFileSync(file, "utf8"), context);
    }
    const names = ["MouseActor", "MouseAction", "MouseTarget", "MouseState", "MouseLease", "MouseHint"], nodes = {};
    for (const name of names) nodes[name] = {visible: true, valid: true, html: true, text: "old", IsValid() {return this.valid;}};
    const root = {visible: false, valid: true, IsValid() {return this.valid;}, FindChildTraverse(id) {return nodes[id];}};
    return {context, root, nodes, names, bind: () => context.DotaCoachMouseProposalPanels.bind(root)};
}
test("explicit empty panel shows unknown lease without execution or authority", () => {
    const f = fixture(); assert.equal(f.root.visible, false); const p = f.bind();
    assert.equal(f.root.visible, true); assert.equal(p.view().canSend, false);
    assert.match(f.nodes.MouseActor.text, /не назначен/); assert.match(f.nodes.MouseLease.text, /неизвестно/);
    assert.ok(f.names.every(id => f.nodes[id].html === false));
});
test("fixed actor remains while move and all three target actions render", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor());
    assert.equal(p.proposeMove(point()), true); assert.match(f.nodes.MouseAction.text, /Движение/);
    assert.match(f.nodes.MouseTarget.text, /Точка выбрана/);
    for (const [team, kind, caption] of [["enemy", "hero", /Атака/], ["enemy", "creep", /Добивание/], ["ally", "creep", /Денай/]]) {
        assert.equal(p.proposeTarget(target(team, kind)), true); assert.match(f.nodes.MouseAction.text, caption);
        assert.equal(f.nodes.MouseTarget.text, "<b>Target</b>"); assert.equal(f.nodes.MouseTarget.html, false);
    }
    assert.equal(p.captureActor(actor("b")), false); assert.equal(p.view().actor.id, "a");
    assert.equal(f.nodes.MouseActor.text, "Player a"); assert.match(f.nodes.MouseHint.text, /не выполнено/);
});
test("invalid proposal clears action target but retains captured actor", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor()); p.proposeMove(point());
    assert.equal(p.proposeTarget(null), false); assert.equal(f.nodes.MouseAction.text, "");
    assert.equal(f.nodes.MouseTarget.text, ""); assert.equal(f.nodes.MouseActor.text, "Player a");
    assert.equal(p.refresh(), true); assert.equal(p.view().proposal, null);
});
test("reset permits new actor without rewinding model's local proposal serial", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor()); p.proposeMove(point());
    assert.equal(p.reset(), true); assert.equal(p.view().actor, null);
    p.captureActor(actor("b")); p.proposeMove(point());
    assert.equal(p.view().proposal.actor.id, "b"); assert.equal(p.view().proposal.serial, 2);
});
test("all labels cleared and root hidden before DTO inspection", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor()); p.proposeMove(point()); let read = false;
    const input = new Proxy({}, {ownKeys() {
        read = true; assert.equal(f.root.visible, false); assert.ok(f.names.every(id => f.nodes[id].text === ""));
        assert.equal(p.view(), null); return [];
    }});
    assert.equal(p.proposeTarget(input), false); assert.equal(read, true);
    assert.equal(f.nodes.MouseAction.text, "");
});
test("view copies private actor and proposal", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor()); p.proposeMove(point());
    const v = p.view(); v.actor.playerName = "changed"; v.proposal.point.x = 0;
    assert.equal(p.view().actor.playerName, "Player a"); assert.equal(p.view().proposal.point.x, 100);
});
test("missing hidden replaced invalid required label closes and clears panel", () => {
    for (const issue of ["missing", "hidden", "replaced", "invalid"]) {
        const f = fixture(), p = f.bind(); p.captureActor(actor());
        if (issue === "missing") delete f.nodes.MouseLease;
        if (issue === "hidden") f.nodes.MouseLease.visible = false;
        if (issue === "replaced") f.nodes.MouseLease = {...f.nodes.MouseLease};
        if (issue === "invalid") f.nodes.MouseLease.valid = false;
        assert.equal(p.refresh(), false); assert.equal(p.isDisposed(), true);
        assert.equal(f.root.visible, false); assert.equal(f.nodes.MouseActor.text, "");
    }
});
test("isDisposed inspects external root visibility and tree", () => {
    for (const mutate of [f => {f.root.visible = false;}, f => {delete f.nodes.MouseHint;}, f => {f.root.valid = false;}]) {
        const f = fixture(), p = f.bind(); mutate(f); assert.equal(p.isDisposed(), true);
        assert.equal(p.view().closed, true); assert.equal(p.view().actor, null);
    }
});
test("root ownership reserved before native validity; duplicate bind preserves live panel", () => {
    const f = fixture(); f.root.IsValid = function () {assert.throws(() => f.bind(), /already bound/); return this.valid;};
    const p = f.bind(); assert.throws(() => f.bind(), /already bound/); assert.equal(p.isDisposed(), false);
});
test("partial discovery and alias failures release only new owner for repair", () => {
    for (const issue of ["missing", "alias"]) {
        const f = fixture(), saved = f.nodes.MouseLease;
        if (issue === "missing") delete f.nodes.MouseLease; else f.nodes.MouseLease = f.nodes.MouseActor;
        assert.throws(() => f.bind()); assert.equal(f.root.visible, false);
        f.nodes.MouseLease = saved; assert.equal(f.bind().isDisposed(), false);
    }
});
test("busy native callback rejects all nested methods before caller reads", () => {
    const f = fixture(), p = f.bind(), find = f.root.FindChildTraverse; let reads = 0;
    const unread = new Proxy({}, {ownKeys() {reads++; return [];}});
    f.root.FindChildTraverse = function (id) {
        assert.equal(p.captureActor(unread), false); assert.equal(p.proposeMove(unread), false);
        assert.equal(p.proposeTarget(unread), false); assert.equal(p.reset(), false); assert.equal(p.refresh(), false);
        assert.equal(p.view(), null); assert.equal(p.isDisposed(), false); return find.call(this, id);
    };
    assert.equal(p.captureActor(actor()), true); assert.equal(reads, 0);
});
test("dispose during DTO inspection aborts paint and old API cannot touch new binding", () => {
    const f = fixture(), p = f.bind(); p.captureActor(actor());
    const input = new Proxy(point(), {ownKeys(row) {p.dispose(); return Reflect.ownKeys(row);}});
    assert.equal(p.proposeMove(input), false); assert.equal(f.root.visible, false);
    const fresh = f.bind(); fresh.captureActor(actor("b"));
    const unread = new Proxy({}, {ownKeys() {throw Error("unread");}});
    assert.equal(p.captureActor(unread), false); assert.equal(p.proposeTarget(unread), false);
    assert.equal(p.proposeMove(unread), false); p.reset(); p.dispose(); p.refresh(); p.view(); p.isDisposed();
    assert.equal(f.nodes.MouseActor.text, "Player b"); assert.equal(fresh.isDisposed(), false);
});
test("dispose in native setter retains root ownership until last cleanup", () => {
    const f = fixture(), p = f.bind(); let text = "", fired = false;
    Object.defineProperty(f.nodes.MouseActor, "text", {get() {return text;}, set(value) {
        text = value;
        if (value === "Player a" && !fired) {fired = true; p.dispose(); assert.throws(() => f.bind(), /already bound/);}
    }});
    assert.equal(p.captureActor(actor()), false); assert.equal(text, ""); assert.equal(f.root.visible, false);
    assert.equal(f.bind().isDisposed(), false);
});
