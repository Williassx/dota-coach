"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const parts = path.resolve(__dirname, "../..");

function run(context, section, file) {
    const source = path.join(parts, section, "src/panorama/scripts/custom_game", file);
    assert.ok(fs.existsSync(source), "routing component missing: " + file);
    vm.runInContext(fs.readFileSync(source, "utf8"), context, { filename: file });
}
function card(id, extra = {}) {
    return { id, playerName: "Тестовый игрок " + id, heroName: "Axe", role: 3,
        source: "synthetic", side: "own", availability: "alive", ...extra };
}
function control(id, extra = {}) {
    return { id, playerName: "Тестовый игрок " + id, mode: "AI", epoch: 1,
        revision: 1, side: "own", availability: "alive", ...extra };
}
function result(sequence, stage, reason = null) { return { sequence, stage, reason }; }
function fixture(options = {}) {
    const nodes = new Map();
    const timers = new Map();
    const forbidden = [];
    let serial = 0;
    function panel(id) {
        let text = "";
        const p = { id, valid: true, enabled: false, visible: true, html: true,
            events: {}, classes: new Set(), IsValid() { return this.valid; },
            FindChildTraverse(name) { return nodes.get(name); },
            SetHasClass(name, active) { active ? this.classes.add(name) : this.classes.delete(name); },
            SetPanelEvent(name, callback) { this.events[name] = callback; },
            ClearPanelEvent(name) { delete this.events[name]; },
            get text() { return text; },
            set text(value) { if (options.failText === id) { throw new Error("label unavailable"); } text = value; }
        };
        nodes.set(id, p);
        return p;
    }
    const rosterRoot = panel("RosterRoot");
    const ordersRoot = panel("OrdersRoot");
    panel("RosterStatus");
    for (let n = 0; n < 5; n++) {
        panel("RosterCard" + n);
        for (const field of ["Name", "Hero", "Role", "Source", "Availability", "Hint"]) {
            panel("Roster" + field + n);
        }
    }
    for (const field of ["Recipient", "Mode", "RequestRecipient", "Action", "Result", "Reason", "Eligibility", "Move", "Attack"]) {
        panel("Order" + field);
    }
    if (options.missing) { nodes.delete(options.missing); }
    function deny(name) {
        return new Proxy({}, { get(_, key) { return () => {
            forbidden.push(name + "." + String(key)); throw new Error("game input forbidden");
        }; } });
    }
    const context = vm.createContext({ $: {
        Schedule(delay, callback) {
            if (options.failSchedule) { throw new Error("schedule unavailable"); }
            const handle = ++serial;
            timers.set(handle, { delay, callback });
            return handle;
        },
        CancelScheduled(handle) { timers.delete(handle); }
    } });
    for (const name of ["GameEvents", "GameUI", "Game", "Players", "Entities"]) { context[name] = deny(name); }
    run(context, "01-roster-cards", "roster_cards_state.js");
    run(context, "01-roster-cards", "roster_cards.js");
    run(context, "02-status-orders", "orders_state.js");
    run(context, "02-status-orders", "orders_panel.js");
    return { context, nodes, timers, forbidden, options, rosterRoot, ordersRoot,
        bind(send) {
            run(context, "03-control-input", "input_routing.js");
            return context.DotaCoachInputRouting.bind(rosterRoot, ordersRoot, send);
        },
        tick(delay) {
            const entry = [...timers].find(([, timer]) => timer.delay === delay);
            assert.ok(entry, "timer with delay " + delay);
            timers.delete(entry[0]); entry[1].callback();
        }
    };
}

test("roster exposes order eligibility separately from inspection eligibility", () => {
    const p = fixture();
    const state = p.context.DotaCoachRoster.create();
    state.replace([card("alive"), card("dead", { availability: "dead" })]);
    assert.equal(state.view().cards[0].availableForOrders, true);
    assert.equal(state.view().cards[1].availableForOrders, false);
    assert.equal(state.view().cards[1].selectable, true);
});

test("roster publishes a copied selection and null on clearing or removal", () => {
    const p = fixture();
    const received = [];
    const ui = p.context.DotaCoachRosterPanels.bind(p.rosterRoot, selected => received.push(selected));
    ui.replace([card("a")]);
    ui.select("a");
    assert.equal(received.at(-1)?.id, "a");
    received.at(-1).playerName = "Подмена";
    ui.select("a");
    assert.equal(received.at(-1).playerName, "Тестовый игрок a");
    ui.clearSelection();
    assert.equal(received.at(-1), null);
    ui.select("a");
    ui.replace([]);
    assert.equal(received.at(-1), null);
});

test("selection callback exception disables the roster", () => {
    const p = fixture();
    let fail = false;
    const ui = p.context.DotaCoachRosterPanels.bind(p.rosterRoot, () => {
        if (fail) { throw new Error("consumer unavailable"); }
    });
    ui.replace([card("a")]);
    fail = true;
    assert.equal(ui.select("a"), false);
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
});

test("selection without a snapshot does not invent a mode or permission", () => {
    const p = fixture();
    const state = p.context.DotaCoachOrders.create(true);
    assert.equal(typeof state.selectRecipient, "function");
    assert.equal(state.selectRecipient("a", "Игрок А", true), true);
    assert.equal(state.view().recipientText, "Игрок А");
    assert.match(state.view().modeText, /не получен/);
    assert.equal(state.begin("move"), null);
    assert.equal(state.updateRecipient(control("a")), true);
    assert.equal(state.view().canIssue, true);
    assert.equal(state.selectRecipient("a", "Игрок А", false), true);
    assert.equal(state.view().canIssue, false);
    assert.equal(state.selectRecipient("a", "Игрок А", "true"), false);
});

test("background control update preserves selection and clears only the relevant old epoch", () => {
    const p = fixture();
    const state = p.context.DotaCoachOrders.create(true);
    assert.equal(typeof state.updateRecipient, "function");
    state.setRecipient(control("b"));
    const intent = state.begin("move");
    state.setRecipient(control("a"));
    assert.equal(state.updateRecipient(control("b", { epoch: 2, revision: 0 })), true);
    assert.equal(state.view().recipientText, "Тестовый игрок a");
    assert.equal(state.view().ticket, null);
    assert.equal(state.report(intent.ticket, result(1, "completed")), false);
});

test("router card selection emits no command and an explicit order targets that player", () => {
    const p = fixture();
    const sent = [];
    const ui = p.bind((intent, report) => { sent.push({ intent, report }); });
    ui.replaceRoster([card("a"), card("b")]);
    ui.updateControl(control("a"));
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    p.nodes.get("RosterCard0").events.onactivate();
    assert.equal(sent.length, 0);
    assert.match(p.nodes.get("OrderRecipient").text, /игрок a/);
    p.nodes.get("OrderMove").events.onactivate();
    assert.equal(sent.length, 1);
    assert.equal(sent[0].intent.recipientId, "a");
    assert.equal(sent[0].intent.action, "move");
    assert.deepEqual(p.forbidden, []);
});

test("router without gateway leaves confirmed AI controls disabled", () => {
    const p = fixture();
    const ui = p.bind();
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
    assert.deepEqual(p.forbidden, []);
});

test("background snapshots cannot steal the selected card's recipient", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a"), card("b")]);
    ui.select("a");
    ui.updateControl(control("b"));
    assert.match(p.nodes.get("OrderRecipient").text, /игрок a/);
    assert.match(p.nodes.get("OrderMode").text, /не получен/);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    ui.updateControl(control("a", { mode: "MANUAL" }));
    assert.match(p.nodes.get("OrderMode").text, /Вручную/);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
});

test("dead card remains inspectable but blocks orders despite an older alive control", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    assert.equal(p.nodes.get("OrderMove").enabled, true);
    ui.replaceRoster([card("a", { availability: "dead" })]);
    assert.equal(p.nodes.get("RosterCard0").classes.has("RosterSelected"), true);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.match(p.nodes.get("OrderEligibility").text, /просмотр/);
});

test("removed or unsupported selection clears recipient without resolving a sent command", () => {
    const p = fixture();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.replaceRoster([card("a"), card("b")]);
    ui.updateControl(control("a"));
    ui.updateControl(control("b"));
    ui.select("a");
    p.nodes.get("OrderMove").events.onactivate();
    ui.replaceRoster([card("b")]);
    assert.match(p.nodes.get("OrderRecipient").text, /не выбран/);
    assert.match(p.nodes.get("OrderRequestRecipient").text, /игрок a/);
    ui.select("b");
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    reply(result(1, "completed"));
    assert.equal(p.nodes.get("OrderMove").enabled, true);
    ui.replaceRoster([card("b", { availability: "unsupported" })]);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
});

test("unknown request remains locked across card switches and clear selection", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a"), card("b")]);
    ui.updateControl(control("a"));
    ui.updateControl(control("b"));
    ui.select("a");
    p.nodes.get("OrderAttack").events.onactivate();
    p.tick(2);
    ui.select("b");
    ui.clearSelection();
    ui.select("a");
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.match(p.nodes.get("OrderResult").text, /неизвестен/);
});

test("old order callback cannot follow a changed card selection", () => {
    const p = fixture();
    let sent = 0;
    const ui = p.bind(() => { sent++; });
    ui.replaceRoster([card("a"), card("b")]);
    ui.updateControl(control("a"));
    ui.updateControl(control("b"));
    ui.select("a");
    const old = p.nodes.get("OrderMove").events.onactivate;
    ui.select("b");
    ui.select("a");
    old();
    assert.equal(sent, 0);
});

test("invalid roster and stale control updates preserve current recipient and mode", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a", { revision: 3, mode: "MANUAL" }));
    ui.select("a");
    assert.equal(ui.replaceRoster([card("b"), card("b")]), false);
    assert.equal(ui.updateControl(control("a", { revision: 2 })), false);
    assert.match(p.nodes.get("OrderRecipient").text, /игрок a/);
    assert.match(p.nodes.get("OrderMode").text, /Вручную/);
});

test("partial bind and watcher failure release both sets of handlers", () => {
    for (const options of [{ missing: "RosterName4" }, { failSchedule: true }]) {
        const p = fixture(options);
        assert.throws(() => p.bind(() => {}));
        assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
        assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
        assert.equal(p.timers.size, 0);
    }
});

test("closed roster prevents gateway invocation even before the watcher tick", () => {
    const p = fixture();
    let sent = 0;
    const ui = p.bind(() => { sent++; });
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    const orderClick = p.nodes.get("OrderMove").events.onactivate;
    p.options.failText = "RosterName0";
    p.nodes.get("RosterCard0").events.onactivate();
    orderClick();
    assert.equal(sent, 0);
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.timers.size, 0);
});

test("order rendering failure closes the remaining roster on the next watcher tick", () => {
    const p = fixture();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    p.nodes.get("OrderMove").events.onactivate();
    p.options.failText = "OrderMode";
    reply(result(1, "completed"));
    p.tick(0.25);
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
    assert.equal(p.timers.size, 0);
});

test("destroying either context cancels pending timers and disposes both children", () => {
    for (const target of ["rosterRoot", "ordersRoot"]) {
        const p = fixture();
        const ui = p.bind(() => {});
        ui.replaceRoster([card("a")]);
        ui.updateControl(control("a"));
        ui.select("a");
        p.nodes.get("OrderMove").events.onactivate();
        p[target].valid = false;
        p.tick(0.25);
        assert.equal(ui.isDisposed(), true);
        assert.equal(p.timers.size, 0);
        assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
        assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
    }
});

test("disposal ignores old clicks, replies and watcher callbacks", () => {
    const p = fixture();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    const cardClick = p.nodes.get("RosterCard0").events.onactivate;
    p.nodes.get("OrderMove").events.onactivate();
    const watcher = [...p.timers.values()].find(t => t.delay === 0.25).callback;
    ui.dispose();
    cardClick(); reply(result(1, "completed")); watcher();
    assert.equal(ui.replaceRoster([card("b")]), false);
    assert.equal(ui.updateControl(control("b")), false);
    assert.equal(ui.select("b"), false);
    assert.equal(ui.clearSelection(), false);
    assert.equal(p.timers.size, 0);
    assert.deepEqual(p.forbidden, []);
});

test("fresh AI snapshots cannot override the dead card inspection gate", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a", { availability: "dead" })]);
    ui.select("a");
    ui.updateControl(control("a"));
    ui.updateControl(control("a", { revision: 2 }));
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.match(p.nodes.get("OrderEligibility").text, /просмотр/);
});

test("a callback that disposes its roster makes selection return false", () => {
    const p = fixture();
    let ui;
    let stop = false;
    ui = p.context.DotaCoachRosterPanels.bind(p.rosterRoot, () => {
        if (stop) { ui.dispose(); }
    });
    ui.replace([card("a")]);
    stop = true;
    assert.equal(ui.select("a"), false);
    assert.equal(p.nodes.get("RosterCard0").events.onactivate, undefined);
});

test("live adapters exclusively own their roots and release ownership on dispose", () => {
    const p = fixture();
    const roster = p.context.DotaCoachRosterPanels.bind(p.rosterRoot);
    const orders = p.context.DotaCoachOrderPanels.bind(p.ordersRoot);
    assert.throws(() => p.context.DotaCoachRosterPanels.bind(p.rosterRoot));
    assert.throws(() => p.context.DotaCoachOrderPanels.bind(p.ordersRoot));
    roster.dispose(); orders.dispose();
    const ui = p.bind();
    assert.equal(ui.isDisposed(), false);
    ui.dispose();
});

test("a reply after roster destruction closes both children before the watcher", () => {
    const p = fixture();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a"));
    ui.select("a");
    p.nodes.get("OrderMove").events.onactivate();
    const resultText = p.nodes.get("OrderResult").text;
    p.rosterRoot.valid = false;
    reply(result(1, "completed"));
    assert.equal(p.nodes.get("OrderResult").text, resultText);
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.timers.size, 0);
});

test("roster copying cannot commit after an input getter disposes the model", () => {
    for (const trigger of ["playerName", "final-length"]) {
        const p = fixture();
        const state = p.context.DotaCoachRoster.create();
        const row = card("a");
        let rows = [row];
        if (trigger === "playerName") {
            Object.defineProperty(row, "playerName", { enumerable: true, get() {
                state.dispose(); return "Закрытый игрок";
            } });
        } else {
            let reads = 0;
            rows = new Proxy(rows, { get(target, key, receiver) {
                if (key === "length" && ++reads === 3) { state.dispose(); }
                return Reflect.get(target, key, receiver);
            } });
        }
        assert.equal(state.replace(rows), false, trigger);
        assert.equal(state.view().closed, true);
        assert.equal(state.view().cards.length, 0);
    }
});

test("input getters cannot make disposed adapters render or restore handlers", () => {
    for (const method of ["replaceRoster", "updateControl"]) {
        const p = fixture();
        const ui = p.bind(() => {});
        ui.replaceRoster([card("a")]);
        ui.updateControl(control("a"));
        ui.select("a");
        const row = method === "replaceRoster" ? card("a") : control("a", { revision: 2 });
        Object.defineProperty(row, "playerName", { enumerable: true, get() {
            ui.dispose(); return "Закрытый игрок";
        } });
        assert.equal(ui[method](method === "replaceRoster" ? [row] : row), false);
        for (const id of ["RosterCard0", "OrderMove", "OrderAttack"]) {
            assert.equal(p.nodes.get(id).visible, false, method + ": " + id);
            assert.equal(p.nodes.get(id).enabled, false, method + ": " + id);
            assert.equal(p.nodes.get(id).events.onactivate, undefined, method + ": " + id);
        }
        assert.equal(p.timers.size, 0);
    }
});

test("an old update cannot overwrite a fresh controller rebound from an input getter", () => {
    for (const method of ["replaceRoster", "updateControl"]) {
        const p = fixture();
        const old = p.bind(() => {});
        let fresh;
        const row = method === "replaceRoster" ? card("old") : control("old");
        Object.defineProperty(row, "playerName", { enumerable: true, get() {
            old.dispose();
            fresh = p.bind(() => {});
            fresh.replaceRoster([card("new")]);
            fresh.updateControl(control("new"));
            fresh.select("new");
            return "Прежний игрок";
        } });
        assert.equal(old[method](method === "replaceRoster" ? [row] : row), false);
        assert.equal(fresh.isDisposed(), false);
        assert.match(p.nodes.get("RosterName0").text, /игрок new/);
        assert.match(p.nodes.get("OrderRecipient").text, /игрок new/);
        assert.equal(p.nodes.get("OrderMove").enabled, true);
        assert.equal(typeof p.nodes.get("OrderMove").events.onactivate, "function");
        assert.equal(p.timers.size, 1);
        fresh.dispose();
    }
});

test("a returning stable roster id reuses its last known control snapshot without inventing a new one", () => {
    const p = fixture();
    const ui = p.bind(() => {});
    ui.replaceRoster([card("a")]);
    ui.updateControl(control("a", { mode: "MANUAL", revision: 3 }));
    ui.select("a");
    ui.replaceRoster([]);
    ui.replaceRoster([card("a")]);
    ui.select("a");
    assert.match(p.nodes.get("OrderMode").text, /Вручную/);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.equal(ui.updateControl(control("a", { revision: 2 })), false);
    assert.match(p.nodes.get("OrderMode").text, /Вручную/);
    ui.updateControl(control("a", { mode: "AI", revision: 4 }));
    assert.equal(p.nodes.get("OrderMove").enabled, true);
});
