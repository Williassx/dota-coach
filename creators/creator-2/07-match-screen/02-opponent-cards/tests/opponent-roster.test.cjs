"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const file = path.join(__dirname, "../src/panorama/scripts/custom_game/opponent_roster_state.js");
const plain = x => JSON.parse(JSON.stringify(x));
const row = (id = "a", extra = {}) => ({id, playerName: "Игрок " + id, heroName: "Zeus", ...extra});
const snapshot = (revision = 1, players = [row()]) => ({revision, players});
function model() {
    assert.ok(fs.existsSync(file), "opponent roster module must exist");
    const context = vm.createContext({Game: new Proxy({}, {get() {throw Error("no game API");}})});
    vm.runInContext(fs.readFileSync(file, "utf8"), context);
    return context.DotaCoachOpponentRoster.create();
}

test("initial and closed projections contain no roster or inferred authorization", () => {
    const m = model();
    assert.deepEqual(plain(m.view()), {ready: false, revision: null, players: [], closed: false,
        evidence: "supplied_public_roster", sourceAuthorizationConfirmed: false});
    m.update(snapshot()); m.dispose(); m.dispose();
    assert.deepEqual(plain(m.view()), {ready: false, revision: null, players: [], closed: true,
        evidence: "supplied_public_roster", sourceAuthorizationConfirmed: false});
});
test("public identities have plain names and no combat or command fields", () => {
    const m = model();
    assert.equal(m.update(snapshot(0, [row("a", {playerName: "<b>A</b>"})])), true);
    assert.deepEqual(plain(m.view().players[0]), {id: "a", playerName: "<b>A</b>", heroName: "Zeus",
        playerText: "<b>A</b>", heroText: "Zeus", informationText: "Боевые данные неизвестны.", canIssue: false});
});
test("null identities remain unknown and zero is invalid", () => {
    const m = model();
    assert.equal(m.update(snapshot(1, [row("a", {playerName: null, heroName: null})])), true);
    assert.equal(m.view().players[0].playerText, "Имя неизвестно");
    assert.equal(m.view().players[0].heroText, "Герой неизвестен");
    assert.equal(m.update(snapshot(2, [row("a", {heroName: 0})])), false);
    assert.equal(m.view().ready, false);
});
test("empty roster is a ready source distinct from an unavailable source", () => {
    const m = model();
    assert.equal(m.update(snapshot(1, [])), true);
    assert.equal(m.view().ready, true);
    assert.equal(m.view().players.length, 0);
    assert.equal(m.update(null), false);
    assert.equal(m.view().ready, false);
});
test("five unique identities accepted; duplicate or sixth identity rejected", () => {
    const m = model();
    assert.equal(m.update(snapshot(1, Array.from({length: 5}, (_, i) => row(String(i))))), true);
    assert.equal(m.update(snapshot(2, [row(), row()])), false);
    assert.equal(m.update(snapshot(3, Array.from({length: 6}, (_, i) => row(String(i))))), false);
    assert.equal(m.view().revision, 1);
});
test("hidden extra fields are rejected without invoking their getters", () => {
    const m = model(); m.update(snapshot());
    const enemy = row(); let reads = 0;
    Object.defineProperty(enemy, "position", {enumerable: true, get() {reads++; throw Error("hidden");}});
    assert.equal(m.update(snapshot(2, [enemy])), false);
    assert.equal(reads, 0); assert.equal(m.view().players.length, 0);
});
test("accessors nonenumerable fields symbols and extra snapshot fields fail exact schema", () => {
    for (const mutate of [x => Object.defineProperty(x, "revision", {get() {throw Error("getter");}}),
        x => Object.defineProperty(x, "revision", {enumerable: false}),
        x => {x[Symbol("secret")] = 1;}, x => {x.health = 100;}]) {
        const m = model(), input = snapshot(); mutate(input);
        assert.equal(m.update(input), false);
    }
});
test("sparse and decorated arrays fail; capacity checked before element values", () => {
    for (const players of [Array(1), Object.assign([row()], {secret: 1}),
        Object.assign([row()], {[Symbol("secret")]: 1})]) assert.equal(model().update(snapshot(1, players)), false);
    const players = Array(6); let reads = 0;
    Object.defineProperty(players, "0", {get() {reads++; throw Error("must not read");}});
    assert.equal(model().update(snapshot(1, players)), false); assert.equal(reads, 0);
});
test("invalid ids names and revisions cannot become game identities", () => {
    for (const id of ["", " a", "a ", "a\n", "x".repeat(65), 1, null])
        assert.equal(model().update(snapshot(1, [row(id)])), false);
    for (const name of ["", "  ", "x".repeat(65), false, {}])
        assert.equal(model().update(snapshot(1, [row("a", {playerName: name})])), false);
    for (const revision of [-1, 0.5, Infinity, NaN, "1", 9007199254740992])
        assert.equal(model().update(snapshot(revision)), false);
});
test("proxy array length cannot coerce around the five-player bound", () => {
    let conversions = 0;
    const deceptive = {valueOf() {conversions++; return conversions === 1 ? 0 : 6;}};
    for (const value of [deceptive, "6", null, NaN, Infinity, -1, 1.5]) {
        const m = model(); m.update(snapshot());
        const players = new Proxy(Array.from({length: 6}, (_, i) => row(String(i))), {
            getOwnPropertyDescriptor(target, key) {
                const descriptor = Reflect.getOwnPropertyDescriptor(target, key);
                return key === "length" ? {...descriptor, value} : descriptor;
            }
        });
        assert.equal(m.update(snapshot(2, players)), false);
        assert.equal(m.view().ready, false); assert.equal(m.view().players.length, 0);
    }
    assert.equal(conversions, 0);
});
test("identical current revision accepted; equal conflict closes gate", () => {
    const m = model(); m.update(snapshot(4));
    assert.equal(m.update(snapshot(4)), true);
    assert.equal(m.update(snapshot(4, [row("b")])), false);
    assert.equal(m.view().ready, false);
    assert.equal(m.update(snapshot(4)), false);
    assert.equal(m.update(snapshot(5, [row("b")])), true);
});
test("ordered roster changes conflict at equal revision", () => {
    const m = model(); m.update(snapshot(1, [row("a"), row("b")]));
    assert.equal(m.update(snapshot(1, [row("b"), row("a")])), false);
});
test("stale or malformed source clears old data without advancing accepted highwater", () => {
    const m = model(); m.update(snapshot(10));
    assert.equal(m.update(snapshot(9)), false);
    assert.equal(m.update(snapshot(10)), false);
    assert.equal(m.update(snapshot(100, [row("a", {health: 1})])), false);
    assert.equal(m.view().revision, 10);
    assert.equal(m.update(snapshot(11)), true);
});
test("caller mutations and view mutations do not alter retained projection", () => {
    const m = model(), input = snapshot(); m.update(input);
    input.players[0].playerName = "changed";
    const view = m.view(); view.players[0].heroText = "changed"; view.players.push({});
    assert.equal(m.view().players[0].playerText, "Игрок a");
    assert.equal(m.view().players[0].heroText, "Zeus"); assert.equal(m.view().players.length, 1);
});
test("busy guard precedes traps and hides projection during validation", () => {
    const m = model(); m.update(snapshot()); let nestedReads = 0, calls = 0;
    const nested = new Proxy({}, {ownKeys() {nestedReads++; return [];}});
    const input = new Proxy(snapshot(2), {ownKeys(target) {
        calls++; assert.equal(m.view(), null); assert.equal(m.update(nested), false);
        return Reflect.ownKeys(target);
    }});
    assert.equal(m.update(input), true); assert.ok(calls >= 1); assert.equal(nestedReads, 0);
});
test("dispose during descriptor inspection prevents commit and clears old references", () => {
    const m = model(); m.update(snapshot());
    const input = new Proxy(snapshot(2), {getOwnPropertyDescriptor(target, name) {
        m.dispose(); return Reflect.getOwnPropertyDescriptor(target, name);
    }});
    assert.equal(m.update(input), false); assert.equal(m.view().closed, true);
    assert.equal(m.view().revision, null); assert.equal(m.view().players.length, 0);
});
test("closed model rejects snapshots before reading caller traps", () => {
    const m = model(); m.dispose();
    assert.equal(m.update(new Proxy({}, {ownKeys() {throw Error("unread");}})), false);
});
