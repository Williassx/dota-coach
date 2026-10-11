"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const file = path.join(__dirname, "../src/panorama/scripts/custom_game/mouse_proposal_state.js");
const plain = x => JSON.parse(JSON.stringify(x));
const actor = (id = "a") => ({id, playerName: "Player " + id, epoch: 1});
const point = () => ({x: 100, y: -200, z: 0});
const observation = (extra = {}) => ({status: "ready", message: "Visible target", target:
    {id: "target-a", label: "Target A", team: "enemy", kind: "hero", alive: true, entityIndex: 10, ...extra}});
function model(captured = true) {
    assert.ok(fs.existsSync(file), "mouse proposal module must exist");
    const native = new Proxy({}, {get() {throw Error("no native API");}});
    const context = vm.createContext({$: native, Game: native, Entities: native});
    vm.runInContext(fs.readFileSync(file, "utf8"), context);
    const m = context.DotaCoachMouseProposals.create();
    if (captured) assert.equal(m.captureActor(actor()), true);
    return m;
}
test("initial and closed state has no actor proposal or input authority", () => {
    const m = model(false);
    assert.deepEqual(plain(m.view()), {actor: null, proposal: null, closed: false, evidence: "local_click_proposal",
        canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false});
    m.captureActor(actor()); m.proposeMove(point()); m.dispose(); m.dispose();
    assert.deepEqual(plain(m.view()), {actor: null, proposal: null, closed: true, evidence: "local_click_proposal",
        canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false});
});
test("explicit actor capture remains fixed despite another selected player's snapshot", () => {
    const m = model(); m.proposeMove(point());
    assert.equal(m.captureActor(actor("b")), false); assert.equal(m.view().actor.id, "a");
    assert.equal(m.view().proposal.actor.id, "a");
});
test("active capture and missing actor reject input before caller traps", () => {
    const unread = new Proxy({}, {ownKeys() {throw Error("unread");}});
    assert.equal(model().captureActor(unread), false);
    const m = model(false); assert.equal(m.proposeMove(unread), false); assert.equal(m.proposeTarget(unread), false);
});
test("move proposal stores bounded copied point and captured actor", () => {
    const m = model(), input = point(); assert.equal(m.proposeMove(input), true); input.x = 999;
    assert.deepEqual(plain(m.view().proposal), {serial: 1, action: "move", actor: actor(), point: point(), target: null});
});
test("second click replaces proposal while preserving actor and increasing local serial", () => {
    const m = model(); m.proposeMove(point()); m.proposeTarget(observation());
    assert.equal(m.view().proposal.serial, 2); assert.equal(m.view().proposal.action, "attack");
    assert.equal(m.view().proposal.actor.id, "a"); assert.equal(m.view().proposal.point, null);
});
test("explicit reset requires recapture and does not rewind accepted proposal serial", () => {
    const m = model(); m.proposeMove(point()); assert.equal(m.reset(), true);
    assert.equal(m.view().actor, null); assert.equal(m.view().proposal, null);
    assert.equal(m.proposeMove(point()), false); assert.equal(m.captureActor(actor("b")), true);
    m.proposeMove(point()); assert.equal(m.view().proposal.actor.id, "b"); assert.equal(m.view().proposal.serial, 2);
});
test("enemy hero enemy creep and allied creep map to three distinct local actions", () => {
    for (const [team, kind, action] of [["enemy", "hero", "attack"], ["enemy", "creep", "last_hit"], ["ally", "creep", "deny"]]) {
        const m = model(); assert.equal(m.proposeTarget(observation({team, kind})), true);
        const proposal = m.view().proposal; assert.equal(proposal.action, action);
        assert.deepEqual(plain(proposal.target), {id: "target-a", label: "Target A", team, kind});
        assert.equal(proposal.point, null); assert.equal(m.view().canSend, false);
    }
});
test("allied hero dead target and invalid entity index cannot form attack proposals", () => {
    for (const extra of [{team: "ally"}, {alive: false}, {entityIndex: -1}, {entityIndex: "10"}, {kind: "building"}]) {
        const m = model(); m.proposeMove(point()); assert.equal(m.proposeTarget(observation(extra)), false);
        assert.equal(m.view().proposal, null); assert.equal(m.view().actor.id, "a");
    }
});
test("non-ready observation never inspects hidden target fields", () => {
    for (const status of ["dead", "stale", "unavailable", "invalid", "empty", "disposed"]) {
        let reads = 0; const target = new Proxy({}, {ownKeys() {reads++; throw Error("hidden");}});
        const m = model(); assert.equal(m.proposeTarget({status, message: "", target}), false);
        assert.equal(reads, 0); assert.equal(m.view().proposal, null);
    }
});
test("extra target combat getter is rejected without being read", () => {
    const m = model(), input = observation(); let reads = 0;
    Object.defineProperty(input.target, "health", {enumerable: true, get() {reads++; throw Error("hidden");}});
    assert.equal(m.proposeTarget(input), false); assert.equal(reads, 0);
});
test("point numbers must be primitive finite within provisional local bounds", () => {
    let conversions = 0; const object = {valueOf() {conversions++; return 1;}};
    for (const input of [{x: 32769, y: 0, z: 0}, {x: 0, y: -32769, z: 0}, {x: 0, y: 0, z: 8193},
        {x: NaN, y: 0, z: 0}, {x: Infinity, y: 0, z: 0}, {x: "1", y: 0, z: 0}, {x: object, y: 0, z: 0}]) {
        const m = model(); m.proposeMove(point()); assert.equal(m.proposeMove(input), false);
        assert.equal(m.view().proposal, null);
    }
    assert.equal(conversions, 0);
    assert.equal(model().proposeMove({x: -32768, y: 32768, z: -8192}), true);
});
test("exact data DTO rejects accessors symbols hidden fields and invalid actor identity", () => {
    for (const mutate of [x => {x.extra = 1;}, x => {x[Symbol("extra")] = 1;},
        x => Object.defineProperty(x, "id", {get() {throw Error("accessor");}}),
        x => Object.defineProperty(x, "id", {enumerable: false}), x => {x.id = " a";},
        x => {x.epoch = -1;}, x => {x.playerName = "";}]) {
        const input = actor(); mutate(input); assert.equal(model(false).captureActor(input), false);
    }
    assert.equal(model().proposeMove({...point(), target: "extra"}), false);
    assert.equal(model().proposeTarget({...observation(), extra: 1}), false);
});
test("projection mutations cannot change captured actor or proposal target", () => {
    const input = actor(), m = model(false); m.captureActor(input); input.playerName = "changed";
    m.proposeTarget(observation()); const view = m.view(); view.actor.id = "b";
    view.proposal.actor.playerName = "changed"; view.proposal.target.label = "changed";
    assert.equal(m.view().actor.id, "a"); assert.equal(m.view().proposal.actor.playerName, "Player a");
    assert.equal(m.view().proposal.target.label, "Target A");
});
test("new proposal clears old value before traps; busy nested calls cannot inspect input", () => {
    const m = model(); m.proposeMove(point()); let inspected = false, reads = 0;
    const unread = new Proxy({}, {ownKeys() {reads++; return [];}});
    const input = new Proxy(point(), {ownKeys(target) {
        inspected = true; assert.equal(m.view(), null); assert.equal(m.proposeMove(unread), false);
        assert.equal(m.proposeTarget(unread), false); assert.equal(m.captureActor(unread), false);
        assert.equal(m.reset(), false); return Reflect.ownKeys(target);
    }});
    assert.equal(m.proposeMove(input), true); assert.equal(inspected, true); assert.equal(reads, 0);
});
test("dispose during caller inspection prevents new proposal or actor commit", () => {
    for (const method of ["captureActor", "proposeMove", "proposeTarget"]) {
        const m = model(method !== "captureActor");
        const data = method === "captureActor" ? actor() : method === "proposeMove" ? point() : observation();
        const input = new Proxy(data, {ownKeys(target) {m.dispose(); return Reflect.ownKeys(target);}});
        assert.equal(m[method](input), false); assert.equal(m.view().closed, true);
        assert.equal(m.view().actor, null); assert.equal(m.view().proposal, null);
    }
});
test("closed APIs reject inputs and reset without caller reads", () => {
    const m = model(); m.dispose(); const input = new Proxy({}, {ownKeys() {throw Error("unread");}});
    assert.equal(m.captureActor(input), false); assert.equal(m.proposeMove(input), false);
    assert.equal(m.proposeTarget(input), false); assert.equal(m.reset(), false);
});
test("real Targets projection produces a proposal then expiry removes the next proposal", () => {
    const context = vm.createContext({});
    const targetsFile = path.resolve(__dirname, "../../../03-map-view/03-visibility-targets/src/panorama/scripts/custom_game/targets_state.js");
    vm.runInContext(fs.readFileSync(targetsFile, "utf8"), context);
    vm.runInContext(fs.readFileSync(file, "utf8"), context);
    let time = 0;
    const targets = context.DotaCoachTargets.create({now: () => time, maxAgeMs: 1000});
    const m = context.DotaCoachMouseProposals.create(); m.captureActor(actor());
    assert.equal(targets.update({revision: 1, targets: [{...observation().target, visibility: "visible"}]}), true);
    assert.equal(targets.select("target-a"), true);
    assert.equal(m.proposeTarget(targets.view()), true); assert.equal(m.view().proposal.action, "attack");
    time = 1000;
    assert.equal(m.proposeTarget(targets.view()), false); assert.equal(m.view().proposal, null);
    assert.equal(m.view().actor.id, "a"); assert.equal(m.view().canSend, false);
});
