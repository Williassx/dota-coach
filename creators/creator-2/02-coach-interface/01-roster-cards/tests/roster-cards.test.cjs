"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");
function execute(context, name) {
    const file = path.join(scripts, name);
    assert.ok(fs.existsSync(file), "roster component not implemented: " + name);
    vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: name });
}
function plain(value) { return JSON.parse(JSON.stringify(value)); }
function row(id, fields = {}) {
    return { id, playerName: "Тестовый игрок " + id, heroName: "Axe", role: 3,
        source: "synthetic", side: "own", availability: "alive", ...fields };
}
function model() {
    const context = vm.createContext({});
    execute(context, "roster_cards_state.js");
    return context.DotaCoachRoster.create();
}

test("player, hero, position and synthetic origin are separate display fields", () => {
    const state = model();
    assert.equal(state.replace([row("a")]), true);
    const card = state.view().cards[0];
    assert.equal(card.playerName, "Тестовый игрок a");
    assert.equal(card.heroName, "Axe");
    assert.match(card.roleText, /3/);
    assert.match(card.sourceText, /Синтетический/);
    assert.equal(card.selected, false);
    assert.equal(card.selectable, true);
});

test("own selection changes only local card state", () => {
    const state = model();
    state.replace([row("a"), row("b")]);
    assert.equal(state.select("b"), true);
    const view = state.view();
    assert.equal(view.selectedId, "b");
    assert.equal(view.cards[0].selected, false);
    assert.equal(view.cards[1].selected, true);
    assert.equal(Object.hasOwn(view, "mode"), false);
    assert.equal(state.clearSelection(), true);
    assert.equal(state.view().selectedId, null);
});

test("own dead player remains available for inspection", () => {
    const state = model();
    state.replace([row("dead", { availability: "dead" })]);
    assert.equal(state.select("dead"), true);
    assert.match(state.view().cards[0].availabilityText, /Мёртв/);
    state.replace([row("dead", { availability: "alive" })]);
    assert.equal(state.view().selectedId, "dead");
});

test("opponent, unsupported and unknown-origin choices preserve current selection", () => {
    const state = model();
    state.replace([row("a"), row("enemy", { side: "opponent" }),
        row("unsupported", { availability: "unsupported" }), row("unknown", { source: "unknown" })]);
    state.select("a");
    for (const id of ["enemy", "unsupported", "unknown", "missing", 0, null]) {
        assert.equal(state.select(id), false);
        assert.equal(state.view().selectedId, "a");
    }
    for (const card of state.view().cards.slice(1)) {
        assert.equal(card.selectable, false);
        assert.ok(card.selectionHint.length);
    }
});

test("selection follows stable ID when rows are reordered", () => {
    const state = model();
    state.replace([row("a"), row("b")]);
    state.select("b");
    state.replace([row("b", { heroName: "Crystal Maiden", role: 5 }), row("a")]);
    assert.equal(state.view().selectedId, "b");
    assert.equal(state.view().cards[0].selected, true);
    assert.equal(state.view().cards[0].heroName, "Crystal Maiden");
});

test("removed or newly unavailable selected card loses local selection", () => {
    for (const replacement of [[], [row("a", { side: "opponent" })],
        [row("a", { availability: "unsupported" })], [row("a", { source: "unknown" })]]) {
        const state = model();
        state.replace([row("a")]);
        state.select("a");
        assert.equal(state.replace(replacement), true);
        assert.equal(state.view().selectedId, null);
    }
});

test("alive to dead update retains inspection without assigning control", () => {
    const state = model();
    state.replace([row("a")]);
    state.select("a");
    state.replace([row("a", { availability: "dead" })]);
    assert.equal(state.view().selectedId, "a");
    assert.equal(state.view().cards[0].selectable, true);
});

test("profile origins remain distinct and unassigned hero is explicit", () => {
    const state = model();
    state.replace([row("m", { source: "measured", heroName: null }),
        row("e", { source: "estimate" }), row("u", { source: "unknown" })]);
    assert.match(state.view().cards[0].sourceText, /Измеренные признаки/);
    assert.match(state.view().cards[1].sourceText, /Оценка модели/);
    assert.match(state.view().cards[2].sourceText, /неизвестен/);
    assert.match(state.view().cards[0].heroName, /не назначен/);
});

test("invalid fields and duplicate IDs reject the entire update", () => {
    const state = model();
    state.replace([row("a")]);
    state.select("a");
    const before = plain(state.view());
    for (const rows of [[row("x"), row("x")], [row("x", { role: 0 })],
        [row("x", { role: 1.5 })], [row("x", { source: "real" })],
        [row("x", { side: "unknown" })], [row("x", { availability: "other" })],
        [row("x", { playerName: " " })], [row("x", { heroName: 99 })],
        [row("x", { mode: "MANUAL" })], [row(" x")], [row("x".repeat(65))],
        [null], {}, null]) {
        assert.equal(state.replace(rows), false);
        assert.deepEqual(plain(state.view()), before);
    }
});

test("maximum five rows and empty replacement are handled atomically", () => {
    const state = model();
    const five = [1, 2, 3, 4, 5].map(n => row(String(n), { role: n }));
    assert.equal(state.replace(five), true);
    assert.equal(state.replace([...five, row("6")]), false);
    assert.equal(state.view().cards.length, 5);
    state.select("1");
    assert.equal(state.replace([]), true);
    assert.equal(state.view().cards.length, 0);
    assert.equal(state.view().selectedId, null);
});

test("mutating inputs or returned views cannot bypass eligibility", () => {
    const state = model();
    const input = [row("a"), row("enemy", { side: "opponent" })];
    state.replace(input);
    input[0].side = "opponent";
    input[0].playerName = "mutated";
    input[1].side = "own";
    assert.equal(state.select("a"), true);
    assert.equal(state.select("enemy"), false);
    const view = state.view();
    view.cards[1].selectable = true;
    view.cards[0].playerName = "another mutation";
    view.selectedId = "enemy";
    assert.equal(state.select("enemy"), false);
    assert.equal(state.view().selectedId, "a");
    assert.equal(state.view().cards[0].playerName, "Тестовый игрок a");
});

test("special object keys remain ordinary card IDs", () => {
    const state = model();
    assert.equal(state.replace([row("__proto__"), row("constructor")]), true);
    assert.equal(state.select("__proto__"), true);
    assert.equal(state.view().selectedId, "__proto__");
    assert.equal(state.select("constructor"), true);
});

test("disposed state ignores further updates and choices", () => {
    const state = model();
    state.replace([row("a")]);
    state.select("a");
    state.dispose();
    state.dispose();
    assert.equal(state.replace([row("b")]), false);
    assert.equal(state.select("a"), false);
    assert.equal(state.clearSelection(), false);
    assert.equal(state.view().closed, true);
    assert.equal(state.view().cards.length, 0);
    assert.equal(state.view().selectedId, null);
});

function panels(options = {}) {
    const nodes = new Map();
    const forbidden = [];
    const timers = new Map();
    const config = {};
    let serial = 0;
    const context = vm.createContext({});
    function panel(id) {
        let text = "";
        const value = { id, valid: true, enabled: true, visible: true, html: true,
            classes: new Set(), events: {},
            IsValid() { return this.valid; },
            FindChildTraverse(name) { return nodes.get(name); },
            SetHasClass(name, active) { active ? this.classes.add(name) : this.classes.delete(name); },
            SetPanelEvent(name, callback) { this.events[name] = callback; },
            ClearPanelEvent(name) { delete this.events[name]; } };
        Object.defineProperty(value, "text", { get() { return text; }, set(next) {
            if (options.failText === id) { throw new Error("display unavailable"); }
            text = next;
        } });
        nodes.set(id, value);
        return value;
    }
    const root = panel("Root");
    panel("RosterStatus");
    for (let n = 0; n < 5; n += 1) {
        panel("RosterCard" + n);
        for (const field of ["Name", "Hero", "Role", "Source", "Availability", "Hint"]) {
            panel("Roster" + field + n);
        }
    }
    if (options.missing) { nodes.delete(options.missing); }
    const deny = namespace => new Proxy({}, { get(_, method) { return () => {
        forbidden.push(namespace + "." + String(method));
        throw new Error("game control forbidden in inspection");
    }; } });
    context.GameEvents = deny("GameEvents");
    context.Players = deny("Players");
    context.Entities = deny("Entities");
    context.Game = deny("Game");
    context.GameUI = new Proxy({ CustomUIConfig: () => config }, {
        get(target, key) { return key in target ? target[key] : deny("GameUI")[key]; }
    });
    context.$ = {
        GetContextPanel: () => root,
        Schedule(delay, callback) {
            if (options.failSchedule) { throw new Error("timer unavailable"); }
            const handle = ++serial;
            timers.set(handle, { delay, callback });
            return handle;
        },
        CancelScheduled(handle) { timers.delete(handle); },
        Msg() {}
    };
    execute(context, "roster_cards_state.js");
    execute(context, "roster_cards.js");
    return { context, root, nodes, forbidden, timers, config, options,
        bind: () => context.DotaCoachRosterPanels.bind(root),
        runTimer() {
            const [id, timer] = timers.entries().next().value;
            timers.delete(id);
            timer.callback();
        },
        demo(data = true) {
            if (data) { execute(context, "roster_cards_demo_data.js"); }
            execute(context, "roster_cards_demo.js");
        } };
}

test("Panorama renders explicit data as plain text and hides empty slots", () => {
    const p = panels();
    const ui = p.bind();
    assert.equal(p.nodes.get("RosterCard0").visible, false);
    assert.equal(ui.replace([row("a", { playerName: "<b>Игрок</b>" }), row("dead", { availability: "dead" })]), true);
    assert.equal(p.nodes.get("RosterName0").text, "<b>Игрок</b>");
    assert.equal(p.nodes.get("RosterName0").html, false);
    assert.match(p.nodes.get("RosterHero0").text, /Axe/);
    assert.match(p.nodes.get("RosterSource0").text, /Синтетический/);
    assert.equal(p.nodes.get("RosterCard1").enabled, true);
    assert.equal(p.nodes.get("RosterCard2").visible, false);
    assert.equal(p.nodes.get("RosterCard4").visible, false);
    assert.deepEqual(p.forbidden, []);
});

test("Panorama click highlights one card without any game action", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a"), row("b")]);
    p.nodes.get("RosterCard1").events.onactivate();
    assert.equal(p.nodes.get("RosterCard1").classes.has("RosterSelected"), true);
    assert.equal(p.nodes.get("RosterCard0").classes.has("RosterSelected"), false);
    assert.match(p.nodes.get("RosterStatus").text, /Просмотр: Тестовый игрок b/);
    ui.clearSelection();
    assert.equal(p.nodes.get("RosterCard1").classes.has("RosterSelected"), false);
    assert.deepEqual(p.forbidden, []);
});

test("Panorama stale click follows ID after reorder and cannot select removed player", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a"), row("b")]);
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    ui.replace([row("b"), row("a")]);
    oldClick();
    assert.equal(p.nodes.get("RosterCard1").classes.has("RosterSelected"), true);
    ui.replace([row("b")]);
    ui.select("b");
    oldClick();
    assert.equal(p.nodes.get("RosterCard0").classes.has("RosterSelected"), true);
    assert.match(p.nodes.get("RosterStatus").text, /недоступ/);
    assert.deepEqual(p.forbidden, []);
});

test("Panorama update removes eligibility and rejects old callback", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a")]);
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    oldClick();
    ui.replace([row("a", { side: "opponent" })]);
    oldClick();
    assert.equal(p.nodes.get("RosterCard0").enabled, false);
    assert.equal(p.nodes.get("RosterCard0").classes.has("RosterSelected"), false);
    assert.match(p.nodes.get("RosterHint0").text, /Другая команда/);
    assert.deepEqual(p.forbidden, []);
});

test("Panorama invalid update reports previous data without partial replacement", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a")]);
    ui.select("a");
    assert.equal(ui.replace([row("b"), row("b")]), false);
    assert.equal(p.nodes.get("RosterName0").text, "Тестовый игрок a");
    assert.equal(p.nodes.get("RosterCard0").classes.has("RosterSelected"), true);
    assert.match(p.nodes.get("RosterStatus").text, /предыдущие данные/);
});

test("Panorama render failure closes handlers and old callbacks", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a")]);
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    p.options.failText = "RosterName0";
    assert.equal(ui.replace([row("b")]), false);
    for (let n = 0; n < 5; n += 1) {
        assert.equal(p.nodes.get("RosterCard" + n).enabled, false);
        assert.equal(p.nodes.get("RosterCard" + n).events.onactivate, undefined);
    }
    assert.doesNotThrow(oldClick);
    assert.equal(ui.select("a"), false);
    assert.deepEqual(p.forbidden, []);
});

test("Panorama missing panels and initial display failure leave no live handlers", () => {
    for (const options of [{ missing: "RosterName4" }, { failText: "RosterStatus" }]) {
        const p = panels(options);
        assert.throws(p.bind);
        for (let n = 0; n < 5; n += 1) {
            assert.equal(p.nodes.get("RosterCard" + n).events.onactivate, undefined);
        }
    }
});

test("Panorama disposal ignores stale clicks and further data", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a")]);
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    ui.dispose();
    const before = p.nodes.get("RosterStatus").text;
    oldClick();
    assert.equal(ui.replace([row("b")]), false);
    assert.equal(p.nodes.get("RosterStatus").text, before);
    assert.equal(p.timers.size, 0);
    assert.deepEqual(p.forbidden, []);
});

test("demo data is explicit, synthetic and separate from model default", () => {
    const p = panels();
    p.demo();
    assert.match(p.nodes.get("RosterName0").text, /Тестовый игрок/);
    assert.match(p.nodes.get("RosterSource0").text, /Синтетический/);
    assert.match(p.nodes.get("RosterSource1").text, /Синтетический/);
    assert.match(p.nodes.get("RosterAvailability1").text, /Мёртв/);
    assert.equal(p.nodes.get("RosterCard1").enabled, true);
    assert.equal(p.timers.size, 1);
    assert.deepEqual(p.forbidden, []);
    const empty = panels();
    empty.demo(false);
    assert.match(empty.nodes.get("RosterStatus").text, /недоступна/);
    assert.equal(empty.timers.size, 0);
});

test("demo reload disposes old controller and keeps only one watcher", () => {
    const p = panels();
    p.demo();
    const old = p.config.dotaCoachRosterDemo;
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    p.demo();
    assert.notEqual(p.config.dotaCoachRosterDemo, old);
    assert.equal(p.timers.size, 1);
    const before = p.nodes.get("RosterStatus").text;
    oldClick();
    assert.equal(p.nodes.get("RosterStatus").text, before);
    assert.deepEqual(p.forbidden, []);
});

test("demo context destruction releases watcher and buttons", () => {
    const p = panels();
    p.demo();
    p.root.valid = false;
    p.runTimer();
    assert.equal(p.timers.size, 0);
    assert.equal(p.config.dotaCoachRosterDemo, null);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
});

test("demo scheduling failure rolls back cache and handlers", () => {
    const p = panels({ failSchedule: true });
    p.demo();
    assert.equal(p.config.dotaCoachRosterDemo, null);
    assert.equal(p.timers.size, 0);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
    assert.match(p.nodes.get("RosterStatus").text, /недоступна/);
});

test("array growth during row copying cannot bypass the five-player bound", () => {
    const state = model();
    state.replace([row("old")]);
    state.select("old");
    const before = plain(state.view());
    const input = [row("a"), row("b"), row("c"), row("d"), row("e")];
    Object.defineProperty(input[0], "playerName", {
        enumerable: true,
        get() { input.push(row("sixth")); return "Тестовый игрок a"; }
    });
    assert.equal(state.replace(input), false);
    assert.deepEqual(plain(state.view()), before);
});

test("Panorama partial rendering failure hides mixed data and reports unavailable", () => {
    const p = panels();
    const ui = p.bind();
    ui.replace([row("a")]);
    ui.select("a");
    p.options.failText = "RosterRole0";
    assert.equal(ui.replace([row("b", { heroName: "Crystal Maiden", role: 5 })]), false);
    assert.match(p.nodes.get("RosterStatus").text, /недоступен/);
    for (let n = 0; n < 5; n += 1) {
        assert.equal(p.nodes.get("RosterCard" + n).visible, false);
        assert.equal(p.nodes.get("RosterCard" + n).enabled, false);
        assert.equal(p.nodes.get("RosterCard" + n).events.onactivate, undefined);
    }
});

test("demo releases watcher and cache after an adapter rendering failure", () => {
    const p = panels();
    p.demo();
    const oldClick = p.nodes.get("RosterCard0").events.onactivate;
    p.options.failText = "RosterName0";
    oldClick();
    p.runTimer();
    assert.equal(p.timers.size, 0);
    assert.equal(p.config.dotaCoachRosterDemo, null);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
    assert.match(p.nodes.get("RosterStatus").text, /недоступен/);
    assert.doesNotThrow(oldClick);
    assert.deepEqual(p.forbidden, []);
});
