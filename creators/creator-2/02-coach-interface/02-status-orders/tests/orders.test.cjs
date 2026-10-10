"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");

function execute(context, name) {
    const file = path.join(scripts, name);
    assert.ok(fs.existsSync(file), "orders component not implemented: " + name);
    vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: name });
}
function plain(value) { return JSON.parse(JSON.stringify(value)); }
function snapshot(id = "a", extra = {}) {
    return { id, playerName: "Тестовый игрок " + id, mode: "AI", epoch: 1,
        revision: 1, side: "own", availability: "alive", ...extra };
}
function update(sequence, stage, reason = null) { return { sequence, stage, reason }; }
function model(ready = true) {
    const context = vm.createContext({});
    execute(context, "orders_state.js");
    return context.DotaCoachOrders.create(ready);
}

test("mode remains unknown before a recipient snapshot", () => {
    const state = model();
    assert.match(state.view().modeText, /не получен/);
    assert.equal(state.view().canIssue, false);
    assert.equal(state.begin("move"), null);
});

test("only an own alive supported recipient in confirmed AI can receive an intent", () => {
    for (const extra of [{ mode: "MANUAL" }, { mode: "INACTIVE" },
        { side: "opponent" }, { availability: "dead" }, { availability: "unsupported" }]) {
        const state = model();
        assert.equal(state.setRecipient(snapshot("a", extra)), true);
        assert.equal(state.view().canIssue, false);
        assert.equal(state.begin("move"), null);
    }
    const offline = model(false);
    offline.setRecipient(snapshot());
    assert.equal(offline.begin("attack"), null);
    assert.match(offline.view().eligibilityText, /переходник/);
});

test("begin emits a copied local intent and prevents a second command", () => {
    const state = model();
    state.setRecipient(snapshot());
    assert.equal(state.begin("other"), null);
    const intent = state.begin("move");
    assert.deepEqual(plain(intent), { ticket: 1, recipientId: "a", epoch: 1, action: "move" });
    intent.recipientId = "b";
    intent.ticket = 9;
    assert.equal(state.view().ticket, 1);
    assert.equal(state.view().canIssue, false);
    assert.equal(state.begin("attack"), null);
    assert.match(state.view().modeText, /ИИ/);
    assert.match(state.view().stageText, /ответ/);
});

test("accepted and executing are distinct from a terminal completion", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("attack");
    assert.equal(state.report(ticket, update(1, "accepted")), true);
    assert.equal(state.view().stage, "accepted");
    assert.equal(state.view().canIssue, false);
    assert.equal(state.report(ticket, update(2, "executing")), true);
    assert.equal(state.view().stage, "executing");
    assert.equal(state.report(ticket, update(3, "completed")), true);
    assert.equal(state.view().canIssue, true);
    assert.match(state.view().stageText, /Выполнен/);
    assert.equal(state.report(ticket, update(4, "rejected", "Поздний отказ")), false);
    assert.equal(state.begin("move").ticket, ticket + 1);
});

test("server may report a terminal result without intermediate events", () => {
    for (const stage of ["completed", "rejected", "cancelled"]) {
        const state = model();
        state.setRecipient(snapshot());
        const { ticket } = state.begin("move");
        assert.equal(state.report(ticket, update(0, stage, stage === "completed" ? null : "Тестовая причина")), true);
        assert.equal(state.view().stage, stage);
        assert.equal(state.view().canIssue, true);
        if (stage !== "completed") { assert.equal(state.view().reasonText, "Тестовая причина"); }
    }
});

test("wrong tickets, duplicate sequences and regressing stages preserve result", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    state.report(ticket, update(2, "executing"));
    const before = plain(state.view());
    for (const [id, data] of [[99, update(3, "completed")], [ticket, update(2, "completed")],
        [ticket, update(1, "rejected", "Причина")], [ticket, update(3, "accepted")]]) {
        assert.equal(state.report(id, data), false);
        assert.deepEqual(plain(state.view()), before);
    }
});

test("timeout keeps unknown busy and a late matching report can resolve it", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    assert.equal(state.expire(ticket), true);
    assert.equal(state.view().stage, "unknown");
    assert.equal(state.begin("move"), null);
    assert.equal(state.expire(ticket), false);
    assert.equal(state.report(ticket, update(1, "completed")), true);
    assert.equal(state.view().canIssue, true);
});

test("an unanswered command survives recipient switches and deselection", () => {
    const state = model();
    state.setRecipient(snapshot("a"));
    const { ticket } = state.begin("move");
    state.expire(ticket);
    state.setRecipient(snapshot("b"));
    assert.match(state.view().recipientText, /игрок b/);
    assert.match(state.view().requestRecipientText, /игрок a/);
    assert.equal(state.begin("attack"), null);
    state.setRecipient(null);
    assert.equal(state.view().ticket, ticket);
    state.setRecipient(snapshot("a"));
    assert.equal(state.begin("move"), null);
    state.setRecipient(snapshot("b"));
    assert.equal(state.report(ticket, update(1, "completed")), true);
    assert.equal(state.view().canIssue, true);
});

test("only a newer epoch of the request recipient releases its tracking", () => {
    const state = model();
    state.setRecipient(snapshot("a"));
    const { ticket } = state.begin("move");
    state.setRecipient(snapshot("b", { epoch: 99 }));
    assert.equal(state.view().ticket, ticket);
    state.setRecipient(snapshot("a", { epoch: 2, revision: 0 }));
    assert.equal(state.view().ticket, null);
    assert.match(state.view().reasonText, /не подтверждено/);
    assert.equal(state.report(ticket, update(1, "completed")), false);
});

test("cached snapshot versions prevent rollback after A to B to A", () => {
    const state = model();
    state.setRecipient(snapshot("a", { epoch: 2, revision: 8, mode: "MANUAL" }));
    state.setRecipient(snapshot("b"));
    assert.equal(state.setRecipient(snapshot("a", { epoch: 1, revision: 100 })), false);
    assert.equal(state.setRecipient(snapshot("a", { epoch: 2, revision: 7 })), false);
    assert.equal(state.setRecipient(snapshot("a", { epoch: 2, revision: 8 })), false);
    assert.equal(state.setRecipient(snapshot("a", { epoch: 2, revision: 8, mode: "MANUAL" })), true);
    assert.match(state.view().modeText, /Вручную/);
    assert.equal(state.view().canIssue, false);
});

test("mode updates stay independent of order results", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    state.setRecipient(snapshot("a", { revision: 2, mode: "MANUAL" }));
    assert.equal(state.report(ticket, update(1, "completed")), true);
    assert.match(state.view().modeText, /Вручную/);
    assert.equal(state.view().canIssue, false);
});

test("malformed snapshots and reports reject atomically", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    const before = plain(state.view());
    for (const data of [snapshot(" "), snapshot("a", { revision: 1.5 }),
        snapshot("a", { epoch: -1 }), snapshot("a", { mode: "unknown" }),
        snapshot("a", { revision: Number.MAX_SAFE_INTEGER + 1 }),
        snapshot("a", { playerName: "" }), snapshot("a", { extra: true }), []]) {
        assert.equal(state.setRecipient(data), false);
        assert.deepEqual(plain(state.view()), before);
    }
    for (const data of [update(-1, "accepted"), update(1, "other"), update(1, "rejected"),
        update(1, "cancelled", ""), update(1, "completed", "x".repeat(161)),
        { ...update(1, "accepted"), mode: "MANUAL" }, null]) {
        assert.equal(state.report(ticket, data), false);
        assert.deepEqual(plain(state.view()), before);
    }
});

test("local not-sent failure permits retry without claiming server rejection", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    assert.equal(state.notSent(ticket), true);
    assert.equal(state.view().stage, "not-sent");
    assert.equal(state.view().canIssue, true);
    assert.match(state.view().stageText, /Не отправлен/);
    assert.equal(state.report(ticket, update(1, "completed")), false);
});

test("expire and not-sent cannot overwrite a synchronous valid response", () => {
    for (const stage of ["accepted", "completed"]) {
        const state = model();
        state.setRecipient(snapshot());
        const { ticket } = state.begin("move");
        state.report(ticket, update(1, stage));
        assert.equal(state.expire(ticket), false);
        assert.equal(state.notSent(ticket), false);
        assert.equal(state.view().stage, stage);
    }
});

test("input and output mutations do not alter stored mode or report", () => {
    const state = model();
    const input = snapshot();
    state.setRecipient(input);
    input.mode = "MANUAL";
    const { ticket } = state.begin("move");
    const data = update(1, "rejected", "Причина");
    state.report(ticket, data);
    data.reason = "Подмена";
    const view = state.view();
    view.modeText = "Подмена";
    assert.match(state.view().modeText, /ИИ/);
    assert.equal(state.view().reasonText, "Причина");
});

test("recipient cache is bounded without evicting unresolved state", () => {
    const state = model();
    for (let n = 0; n < 10; n++) { assert.equal(state.setRecipient(snapshot(String(n))), true); }
    const { ticket } = state.begin("move");
    assert.equal(state.setRecipient(snapshot("11")), false);
    assert.equal(state.view().ticket, ticket);
    assert.equal(state.setRecipient(snapshot("__proto__")), false);
});

test("disposal prevents updates, reports and further requests", () => {
    const state = model();
    state.setRecipient(snapshot("__proto__"));
    const { ticket } = state.begin("move");
    state.dispose();
    assert.equal(state.setRecipient(snapshot()), false);
    assert.equal(state.report(ticket, update(1, "completed")), false);
    assert.equal(state.begin("attack"), null);
    assert.equal(state.view().closed, true);
    assert.equal(state.view().ticket, null);
});

function panels(options = {}) {
    const nodes = new Map();
    const timers = new Map();
    const forbidden = [];
    const config = {};
    let serial = 0;
    function panel(id) {
        let value = "";
        return { id, valid: true, visible: true, enabled: false, html: true, events: {},
            IsValid() { return this.valid; },
            FindChildTraverse(name) { return nodes.get(name); },
            SetPanelEvent(name, callback) { this.events[name] = callback; },
            ClearPanelEvent(name) { delete this.events[name]; },
            get text() { return value; },
            set text(next) { if (options.failText === id) { throw new Error("label unavailable"); } value = next; }
        };
    }
    const root = panel("root");
    for (const name of ["OrderRecipient", "OrderMode", "OrderRequestRecipient", "OrderAction",
        "OrderResult", "OrderReason", "OrderEligibility", "OrderMove", "OrderAttack"]) { nodes.set(name, panel(name)); }
    if (options.missing) { nodes.delete(options.missing); }
    const context = vm.createContext({});
    function deny(name) {
        return new Proxy({}, { get(target, key) {
            return () => { forbidden.push(name + "." + String(key)); throw new Error("game API forbidden"); };
        } });
    }
    for (const name of ["GameEvents", "Players", "Entities", "Game"]) { context[name] = deny(name); }
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
        CancelScheduled(handle) { timers.delete(handle); }
    };
    execute(context, "orders_state.js");
    execute(context, "orders_panel.js");
    return { nodes, root, context, timers, forbidden, config, options,
        bind: send => context.DotaCoachOrderPanels.bind(root, send),
        runTimer(delay) {
            const entry = [...timers].find(([, timer]) => timer.delay === delay);
            assert.ok(entry, "scheduled timer with delay " + delay);
            timers.delete(entry[0]);
            entry[1].callback();
        },
        demo(data = true) {
            if (data) { execute(context, "orders_demo_data.js"); }
            execute(context, "orders_demo.js");
        }
    };
}

test("panel without a gateway displays unknown mode and never enables commands", () => {
    const p = panels();
    const ui = p.bind();
    assert.match(p.nodes.get("OrderMode").text, /не получен/);
    ui.setRecipient(snapshot());
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.equal(p.nodes.get("OrderAttack").enabled, false);
    assert.match(p.nodes.get("OrderEligibility").text, /переходник/);
    assert.deepEqual(p.forbidden, []);
});

test("panel click sends once and keeps accepted separate from completed", () => {
    const p = panels();
    const sent = [];
    let reply;
    const ui = p.bind((intent, callback) => { sent.push(plain(intent)); reply = callback; });
    ui.setRecipient(snapshot("a", { playerName: "<b>Игрок</b>" }));
    const click = p.nodes.get("OrderMove").events.onactivate;
    click();
    click();
    assert.equal(sent.length, 1);
    assert.equal(sent[0].action, "move");
    assert.equal(p.nodes.get("OrderRecipient").html, false);
    assert.match(p.nodes.get("OrderRecipient").text, /<b>Игрок<\/b>/);
    assert.equal(p.nodes.get("OrderAttack").enabled, false);
    reply(update(1, "accepted"));
    assert.match(p.nodes.get("OrderResult").text, /выполнение не подтверждено/);
    assert.equal(p.timers.size, 0);
    reply(update(2, "executing"));
    reply(update(3, "completed"));
    assert.equal(p.nodes.get("OrderMove").enabled, true);
    assert.deepEqual(p.forbidden, []);
});

test("panel timeout does not permit duplicate and late response may complete", () => {
    const p = panels();
    let reply;
    const ui = p.bind((intent, callback) => { reply = callback; });
    ui.setRecipient(snapshot());
    p.nodes.get("OrderAttack").events.onactivate();
    p.runTimer(2);
    assert.match(p.nodes.get("OrderResult").text, /неизвестен/);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    reply(update(1, "completed"));
    assert.equal(p.nodes.get("OrderMove").enabled, true);
});

test("synchronous response then transport throw preserves authoritative status", () => {
    for (const stage of ["accepted", "completed"]) {
        const p = panels();
        const ui = p.bind((intent, report) => {
            report(update(1, stage));
            throw new Error("transport failed after reply");
        });
        ui.setRecipient(snapshot());
        p.nodes.get("OrderMove").events.onactivate();
        assert.match(p.nodes.get("OrderResult").text, stage === "completed" ? /Выполнен/ : /Принят/);
        assert.equal(p.timers.size, 0);
        assert.equal(p.nodes.get("OrderMove").enabled, stage === "completed");
    }
});

test("transport exception without response remains unknown and locked", () => {
    const p = panels();
    const ui = p.bind(() => { throw new Error("may already have sent"); });
    ui.setRecipient(snapshot());
    p.nodes.get("OrderMove").events.onactivate();
    assert.match(p.nodes.get("OrderResult").text, /неизвестен/);
    assert.equal(p.nodes.get("OrderMove").enabled, false);
    assert.equal(p.timers.size, 0);
});

test("timer failure before send reports not-sent and permits retry", () => {
    const p = panels({ failSchedule: true });
    let sent = 0;
    const ui = p.bind(() => { sent++; });
    ui.setRecipient(snapshot());
    p.nodes.get("OrderMove").events.onactivate();
    assert.equal(sent, 0);
    assert.match(p.nodes.get("OrderResult").text, /Не отправлен/);
    assert.equal(p.nodes.get("OrderMove").enabled, true);
});

test("old click after A to B to A cannot send a new command", () => {
    const p = panels();
    let sent = 0;
    const ui = p.bind(() => { sent++; });
    ui.setRecipient(snapshot("a"));
    const oldClick = p.nodes.get("OrderMove").events.onactivate;
    ui.setRecipient(snapshot("b"));
    ui.setRecipient(snapshot("a"));
    oldClick();
    assert.equal(sent, 0);
    p.nodes.get("OrderMove").events.onactivate();
    assert.equal(sent, 1);
});

test("old response and cancelled timer cannot finish a newer epoch request", () => {
    const p = panels();
    const replies = [];
    const ui = p.bind((intent, report) => { replies.push(report); });
    ui.setRecipient(snapshot());
    p.nodes.get("OrderMove").events.onactivate();
    const oldTimer = [...p.timers.values()][0].callback;
    ui.setRecipient(snapshot("a", { epoch: 2, revision: 0 }));
    p.nodes.get("OrderAttack").events.onactivate();
    const before = p.nodes.get("OrderResult").text;
    replies[0](update(1, "completed"));
    oldTimer();
    assert.equal(p.nodes.get("OrderResult").text, before);
    assert.equal(p.timers.size, 1);
    replies[1](update(1, "rejected", "Тестовая цель недоступна"));
    assert.equal(p.nodes.get("OrderReason").text, "Тестовая цель недоступна");
});

test("partial rendering failure hides buttons and releases timers", () => {
    const p = panels();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.setRecipient(snapshot());
    const oldClick = p.nodes.get("OrderMove").events.onactivate;
    oldClick();
    p.options.failText = "OrderMode";
    ui.setRecipient(snapshot("a", { revision: 2 }));
    assert.equal(ui.isDisposed(), true);
    assert.equal(p.timers.size, 0);
    assert.equal(p.nodes.get("OrderMove").visible, false);
    assert.equal(p.nodes.get("OrderAttack").events.onactivate, undefined);
    assert.match(p.nodes.get("OrderResult").text, /недоступна/);
    assert.doesNotThrow(() => reply(update(1, "completed")));
    assert.doesNotThrow(oldClick);
});

test("missing panels and initial rendering failure leave no callbacks", () => {
    for (const options of [{ missing: "OrderMode" }, { failText: "OrderResult" }]) {
        const p = panels(options);
        assert.throws(() => p.bind(() => {}));
        assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
        assert.equal(p.timers.size, 0);
    }
});

test("disposed panel ignores replies and stale timers", () => {
    const p = panels();
    let reply;
    const ui = p.bind((intent, report) => { reply = report; });
    ui.setRecipient(snapshot());
    p.nodes.get("OrderMove").events.onactivate();
    const timer = [...p.timers.values()][0].callback;
    ui.dispose();
    const before = p.nodes.get("OrderResult").text;
    reply(update(1, "completed"));
    timer();
    assert.equal(ui.setRecipient(snapshot()), false);
    assert.equal(p.nodes.get("OrderResult").text, before);
    assert.equal(p.timers.size, 0);
});

test("explicit demo uses synthetic data and simulated reports without game APIs", () => {
    const p = panels();
    p.demo();
    assert.match(p.nodes.get("OrderRecipient").text, /Тестовый игрок/);
    p.nodes.get("OrderMove").events.onactivate();
    p.runTimer(0.1);
    assert.match(p.nodes.get("OrderResult").text, /Принят/);
    p.runTimer(0.1);
    assert.match(p.nodes.get("OrderResult").text, /Исполняется/);
    p.runTimer(0.1);
    assert.match(p.nodes.get("OrderResult").text, /Выполнен/);
    assert.equal(p.timers.size, 1);
    assert.deepEqual(p.forbidden, []);
});

test("demo reload cancels old reports and context destruction clears all timers", () => {
    const p = panels();
    p.demo();
    p.nodes.get("OrderMove").events.onactivate();
    const oldPhase = [...p.timers.values()].find(t => t.delay === 0.1).callback;
    p.demo();
    assert.equal(p.timers.size, 1);
    const before = p.nodes.get("OrderResult").text;
    oldPhase();
    assert.equal(p.nodes.get("OrderResult").text, before);
    p.nodes.get("OrderAttack").events.onactivate();
    p.root.valid = false;
    p.runTimer(0.25);
    assert.equal(p.timers.size, 0);
    assert.equal(p.config.dotaCoachOrdersDemo, null);
    assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
});

test("demo missing fixtures and startup schedule failure do not keep a client", () => {
    for (const options of [{}, { failSchedule: true }]) {
        const p = panels(options);
        p.demo(!!options.failSchedule);
        assert.equal(p.config.dotaCoachOrdersDemo, null);
        assert.equal(p.timers.size, 0);
        assert.equal(p.nodes.get("OrderMove").events.onactivate, undefined);
        assert.match(p.nodes.get("OrderResult").text, /недоступна/);
    }
});

test("demo releases simulated reports immediately after adapter rendering failure", () => {
    const p = panels();
    p.demo();
    p.nodes.get("OrderMove").events.onactivate();
    p.options.failText = "OrderMode";
    p.runTimer(0.1);
    assert.equal(p.timers.size, 0);
    assert.equal(p.config.dotaCoachOrdersDemo, null);
});

test("report copying cannot dereference a request cleared by an input getter", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    const data = update(1, "completed");
    Object.defineProperty(data, "reason", { enumerable: true, get() {
        state.setRecipient(snapshot("a", { epoch: 2, revision: 0 }));
        return null;
    } });
    assert.equal(state.report(ticket, data), false);
    assert.equal(state.view().ticket, null);
    assert.equal(state.view().stage, "idle");
});

test("report copying cannot apply an old response to a reentrant new request", () => {
    const state = model();
    state.setRecipient(snapshot());
    const { ticket } = state.begin("move");
    let next;
    const data = update(2, "accepted");
    Object.defineProperty(data, "reason", { enumerable: true, get() {
        state.report(ticket, update(1, "completed"));
        next = state.begin("attack");
        return null;
    } });
    assert.equal(state.report(ticket, data), false);
    assert.equal(state.view().ticket, next.ticket);
    assert.equal(state.view().stage, "pending");
});

test("previous order reason cannot hide the new recipient's command eligibility", () => {
    for (const extra of [{ side: "opponent" }, { availability: "dead" }, { availability: "unsupported" }]) {
        const p = panels();
        let reply;
        const ui = p.bind((intent, report) => { reply = report; });
        ui.setRecipient(snapshot("a"));
        p.nodes.get("OrderMove").events.onactivate();
        reply(update(1, "rejected", "Старая цель недоступна"));
        ui.setRecipient(snapshot("b", extra));
        assert.equal(p.nodes.get("OrderMove").enabled, false);
        assert.equal(p.nodes.get("OrderReason").text, "Старая цель недоступна");
        assert.match(p.nodes.get("OrderEligibility").text, /Чужому|мёртв|не поддерживается/);
        ui.setRecipient(snapshot("a", { epoch: 2, revision: 0, availability: "dead" }));
        assert.match(p.nodes.get("OrderReason").text, /не подтверждено/);
        assert.match(p.nodes.get("OrderEligibility").text, /мёртв/);
    }
});

test('snapshot read returns exactly seven independent fields of validated actor',()=>{const state=model();const row=snapshot();state.setRecipient(row);const copy=state.snapshot();assert.deepEqual(plain(copy),row);assert.equal(Object.keys(copy).length,7);copy.mode='MANUAL';copy.id='bad';row.playerName='changed';assert.equal(state.snapshot().mode,'AI');assert.equal(state.snapshot().playerName,'Тестовый игрок a');});
test('snapshot querying known actor does not change selection or current order',()=>{const state=model();state.updateRecipient(snapshot('a'));state.updateRecipient(snapshot('b'));state.selectRecipient('a','A',true);const intent=state.begin('move');const before=plain(state.view());assert.equal(state.snapshot('b').id,'b');assert.deepEqual(plain(state.view()),before);assert.equal(state.view().ticket,intent.ticket);assert.equal(state.snapshot().id,'a');});
test('snapshot unknown invalid bounds and coercion objects return null without reads',()=>{const state=model();state.setRecipient(snapshot());let reads=0;const id={toString(){reads++;return 'a';}};for(const input of [id,null,true,0,'',' '.repeat(3),'a'.repeat(65),'missing',' a'])assert.equal(state.snapshot(input),null);assert.equal(reads,0);});
test('snapshot read does not consume actor revision or create an unknown actor',()=>{const state=model();state.setRecipient(snapshot());assert.equal(state.snapshot('b'),null);assert.equal(state.updateRecipient(snapshot('a',{revision:0})),false);assert.equal(state.snapshot().revision,1);assert.equal(state.updateRecipient(snapshot('a',{revision:2,mode:'MANUAL'})),true);assert.equal(state.snapshot('a').mode,'MANUAL');});
test('snapshot no recipient or closed state yields null for every known actor',()=>{const state=model();assert.equal(state.snapshot(),null);state.updateRecipient(snapshot());assert.equal(state.snapshot(),null);assert.equal(state.snapshot('a').id,'a');state.dispose();assert.equal(state.snapshot(),null);assert.equal(state.snapshot('a'),null);});
test('snapshot omitted argument queries current but explicit undefined is an invalid id',()=>{const state=model();state.setRecipient(snapshot());assert.equal(state.snapshot().id,'a');assert.equal(state.snapshot(undefined),null);assert.equal(state.snapshot('a').id,'a');});
