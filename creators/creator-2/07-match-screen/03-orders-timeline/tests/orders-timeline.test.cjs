"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const root = path.resolve(__dirname, "../../../../..");
const orderFile = path.join(root, "creators/creator-2/02-coach-interface/02-status-orders/src/panorama/scripts/custom_game/orders_state.js");
const timelineFile = path.join(__dirname, "../src/panorama/scripts/custom_game/orders_timeline_state.js");
const plain = value => JSON.parse(JSON.stringify(value));
const actor = (id = "a", extra = {}) => ({ id, playerName: "Игрок " + id, mode: "AI", epoch: 1,
    revision: 1, side: "own", availability: "alive", ...extra });

function setup() {
    const context = vm.createContext({});
    vm.runInContext(fs.readFileSync(orderFile, "utf8"), context);
    vm.runInContext(fs.readFileSync(timelineFile, "utf8"), context);
    const orders = context.DotaCoachOrders.create(true);
    orders.setRecipient(actor());
    const history = context.DotaCoachOrdersTimeline.create();
    return { orders, history };
}
const snapshot = (orders, extra = {}) => ({ ...plain(orders.view()), ...extra });
const report = (orders, stage, sequence, reason = null) => orders.report(orders.view().ticket, { stage, sequence, reason });

test("idle selection creates no event and source-only metadata is explicit", () => {
    const { orders, history } = setup();
    assert.equal(history.record(orders.view()).status, "unchanged");
    const view = history.view();
    assert.equal(view.events.length, 0);
    assert.equal(view.capacity, 64);
    assert.equal(view.droppedEvents, 0);
    assert.equal(view.closed, false);
});

test("pending accepted executing completed form distinct chronological events", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    for (const [index, stage] of ["accepted", "executing", "completed"].entries()) {
        assert.equal(report(orders, stage, index), true);
        assert.equal(history.record(orders.view()).status, "recorded");
    }
    const events = history.view().events;
    assert.deepEqual(plain(events.map(e => e.stage)), ["pending", "accepted", "executing", "completed"]);
    assert.deepEqual(plain(events.map(e => e.eventIndex)), [1, 2, 3, 4]);
    assert.equal(events[0].outcomeUnknown, true);
    assert.equal(events[3].outcomeUnknown, false);
    assert.match(events[1].stageText, /выполнение не подтверждено/);
    assert.match(events[3].stageText, /Источник сообщил/);
    assert.match(events[3].stageText, /не проверен/);
    assert.ok(events.every(e => e.evidence === "presentation_snapshot" && e.nativeConfirmed === false));
});

test("selection and mode updates do not duplicate or retarget a captured request", () => {
    const { orders, history } = setup();
    orders.begin("attack");
    history.record(orders.view());
    orders.setRecipient(actor("b"));
    assert.equal(history.record(orders.view()).status, "unchanged");
    orders.setRecipient(null);
    assert.equal(history.record(orders.view()).status, "unchanged");
    report(orders, "completed", 0);
    history.record(orders.view());
    assert.ok(history.view().events.every(e => e.actorName === "Игрок a"));
    assert.ok(history.view().events.every(e => e.actionText === "Атаковать тестовую цель"));
});

test("late first completed snapshot does not invent earlier stages", () => {
    const { orders, history } = setup();
    orders.begin("move");
    report(orders, "completed", 0);
    history.record(orders.view());
    assert.deepEqual(plain(history.view().events.map(e => e.stage)), ["completed"]);
});

test("rejected cancelled and not-sent remain distinct from completion", () => {
    for (const stage of ["rejected", "cancelled", "not-sent"]) {
        const { orders, history } = setup();
        const { ticket } = orders.begin("move");
        history.record(orders.view());
        if (stage === "not-sent") orders.notSent(ticket);
        else report(orders, stage, 0, "Проверочная причина");
        history.record(orders.view());
        assert.equal(history.view().events.at(-1).stage, stage);
        assert.notEqual(history.view().events.at(-1).reasonText, "");
    }
});

test("timeout unknown may resolve by a late matching source report", () => {
    const { orders, history } = setup();
    const { ticket } = orders.begin("move");
    history.record(orders.view());
    orders.expire(ticket);
    history.record(orders.view());
    report(orders, "completed", 0);
    history.record(orders.view());
    assert.deepEqual(plain(history.view().events.map(e => e.stage)), ["pending", "unknown", "completed"]);
});

test("epoch clears tracking without pretending cancellation or completion", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    orders.setRecipient(actor("a", { epoch: 2, revision: 0 }));
    assert.equal(history.record(orders.view()).status, "recorded");
    const event = history.view().events.at(-1);
    assert.equal(event.kind, "tracking-ended");
    assert.equal(event.stage, "tracking-ended");
    assert.equal(event.ticket, 1);
    assert.equal(event.outcomeUnknown, true);
    assert.match(event.stageText, /итог неизвестен/);
    assert.equal(history.record(orders.view()).status, "unchanged");
});

test("switch to a newer ticket notes lost tracking and captures a new actor", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    orders.setRecipient(actor("a", { epoch: 2, revision: 0 }));
    orders.setRecipient(actor("b"));
    orders.begin("attack");
    assert.equal(history.record(orders.view()).added, 2);
    assert.deepEqual(plain(history.view().events.map(e => [e.ticket, e.kind, e.actorName])),
        [[1, "state", "Игрок a"], [1, "tracking-ended", "Игрок a"], [2, "state", "Игрок b"]]);
});

test("new ticket after a known terminal result adds only the new state", () => {
    const { orders, history } = setup();
    orders.begin("move");
    report(orders, "completed", 0);
    history.record(orders.view());
    orders.begin("attack");
    assert.equal(history.record(orders.view()).added, 1);
    assert.deepEqual(plain(history.view().events.map(e => e.stage)), ["completed", "pending"]);
});

test("older tickets identity changes regressions and invalid stage cannot mutate history", () => {
    const { orders, history } = setup();
    orders.begin("move");
    report(orders, "executing", 0);
    history.record(orders.view());
    const before = plain(history.view());
    for (const change of [{ ticket: 0 }, { stage: "accepted" }, { stage: "pending" }, { stage: "unknown" },
        { stage: "other" }, { requestRecipientText: "Подмена" }, { actionText: "Подмена" }]) {
        assert.equal(history.record(snapshot(orders, change)).status, "invalid");
        assert.deepEqual(plain(history.view()), before);
    }
});

test("terminal result cannot be overwritten even with a different reason", () => {
    const { orders, history } = setup();
    orders.begin("move");
    report(orders, "completed", 0);
    history.record(orders.view());
    assert.equal(history.record(snapshot(orders, { reasonText: "Подмена" })).status, "invalid");
    assert.equal(history.record(snapshot(orders, { stage: "rejected" })).status, "invalid");
    assert.equal(history.view().events.length, 1);
});

test("same stage may add a changed nonterminal reason while identical snapshots deduplicate", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    report(orders, "accepted", 0, "Первая причина");
    history.record(orders.view());
    report(orders, "accepted", 1, "Обновлённая причина");
    assert.equal(history.record(orders.view()).status, "recorded");
    assert.equal(history.record(orders.view()).status, "unchanged");
    assert.equal(history.view().events.length, 3);
});

test("finished tracking cannot revive the old local ticket or a new model serial", () => {
    const { orders, history } = setup();
    orders.begin("move");
    const old = snapshot(orders);
    history.record(old);
    orders.setRecipient(actor("a", { epoch: 2, revision: 0 }));
    history.record(orders.view());
    assert.equal(history.record(old).status, "invalid");
    assert.equal(history.record({ ...old, stage: "completed" }).status, "invalid");
    assert.equal(history.view().events.length, 2);
});

test("bounded history drops old events with a visible counter and retains current correlation", () => {
    const { orders, history } = setup();
    for (let n = 0; n < 80; n++) {
        orders.begin("move");
        report(orders, "completed", 0);
        history.record(orders.view());
    }
    const view = history.view();
    assert.equal(view.events.length, 64);
    assert.equal(view.droppedEvents, 16);
    assert.equal(view.events[0].eventIndex, 17);
    assert.equal(view.events.at(-1).ticket, 80);
    assert.equal(history.record(orders.view()).status, "unchanged");
    assert.equal(history.view().droppedEvents, 16);
});

test("caller mutations of input and output do not rewrite stored events", () => {
    const { orders, history } = setup();
    orders.begin("move");
    const input = snapshot(orders);
    history.record(input);
    input.requestRecipientText = "Подмена";
    const output = history.view();
    output.events[0].actorName = "Подмена";
    output.events.push({});
    assert.equal(history.view().events.length, 1);
    assert.equal(history.view().events[0].actorName, "Игрок a");
});

test("malformed descriptors extra keys invalid fields and accessors are atomic", () => {
    const { orders, history } = setup();
    orders.begin("move");
    const good = snapshot(orders);
    let reads = 0;
    const getter = { ...good };
    Object.defineProperty(getter, "reasonText", { enumerable: true, get() { reads++; return "Подмена"; } });
    for (const bad of [null, [], { ...good, extra: 1 }, { ...good, ticket: Number.MAX_SAFE_INTEGER + 1 },
        { ...good, closed: 1 }, { ...good, canIssue: "yes" }, { ...good, reasonText: "x".repeat(513) },
        { ...good, stage: "idle" }, getter]) {
        assert.equal(history.record(bad).status, "invalid");
        assert.equal(history.view().events.length, 0);
    }
    assert.equal(reads, 0);
});

test("busy lock precedes proxy traps and prevents reentry reads", () => {
    const { orders, history } = setup();
    orders.begin("move");
    const good = snapshot(orders);
    let nestedReads = 0;
    const nested = new Proxy(good, { ownKeys() { nestedReads++; return Reflect.ownKeys(good); } });
    const input = new Proxy(good, { ownKeys() {
        assert.equal(history.record(nested).status, "busy");
        assert.equal(history.view(), null);
        return Reflect.ownKeys(good);
    } });
    assert.equal(history.record(input).status, "recorded");
    assert.equal(nestedReads, 0);
    assert.equal(history.view().events.length, 1);
});

test("dispose during proxy inspection cancels commit and clears old history", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    const input = new Proxy(snapshot(orders), { ownKeys(target) { history.dispose(); return Reflect.ownKeys(target); } });
    assert.equal(history.record(input).status, "closed");
    assert.equal(history.view().closed, true);
    assert.equal(history.view().events.length, 0);
});

test("closed source disposes history and future calls do not inspect input", () => {
    const { orders, history } = setup();
    orders.begin("move");
    history.record(orders.view());
    orders.dispose();
    assert.equal(history.record(orders.view()).status, "closed");
    const input = new Proxy({}, { ownKeys() { throw Error("must not inspect"); } });
    assert.equal(history.record(input).status, "closed");
    history.dispose();
    assert.equal(history.view().events.length, 0);
});

test("plain text names and reasons stay literal and stage claims are locally controlled", () => {
    const { orders, history } = setup();
    assert.equal(orders.setRecipient(actor("a", { playerName: "<b>Игрок</b>", revision: 2 })), true);
    orders.begin("move");
    report(orders, "completed", 0, "<script>literal</script>");
    history.record(snapshot(orders, { stageText: "Доказано исполнение в Dota" }));
    const event = history.view().events[0];
    assert.equal(event.actorName, "<b>Игрок</b>");
    assert.equal(event.reasonText, "<script>literal</script>");
    assert.doesNotMatch(event.stageText, /Доказано/);
    assert.equal(event.nativeConfirmed, false);
});
