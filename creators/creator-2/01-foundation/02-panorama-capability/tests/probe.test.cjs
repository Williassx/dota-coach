"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const scripts = path.join(__dirname, "../src/panorama/scripts/custom_game");

function fixture() {
    let now = 0;
    let next = 0;
    let root;
    const listeners = new Map();
    const timers = new Map();
    const sent = [];
    const logs = [];
    const shared = {};
    const engine = { sendFails: false, timerFails: false, subscribeFails: false, renderFailures: 0 };

    function panel() {
        const parent = { valid: true, IsValid() { return this.valid; } };
        function child() {
            return { text: "", enabled: true, handler: null,
                IsValid() { return parent.valid; },
                SetPanelEvent(event, callback) { assert.equal(event, "onactivate"); this.handler = callback; },
                ClearPanelEvent(event) { assert.equal(event, "onactivate"); this.handler = null; } };
        }
        parent.button = child();
        parent.status = child();
        let text = "";
        Object.defineProperty(parent.status, "text", {
            get: () => text,
            set(value) {
                if (engine.renderFailures > 0) {
                    engine.renderFailures -= 1;
                    throw new Error("native label write failed");
                }
                text = value;
            }
        });
        parent.FindChildTraverse = id => ({ ProbeButton: parent.button, ProbeStatus: parent.status }[id] || null);
        return parent;
    }

    const context = vm.createContext({
        GameUI: { CustomUIConfig: () => shared },
        GameEvents: {
            Subscribe(name, callback) {
                if (engine.subscribeFails) throw new Error("unavailable engine");
                assert.equal(name, "dota_coach_probe_result");
                const id = next++;
                listeners.set(id, callback);
                return id;
            },
            Unsubscribe: id => listeners.delete(id),
            SendCustomGameEventToServer(name, payload) {
                if (engine.sendFails) throw new Error("transport failed");
                assert.equal(name, "dota_coach_probe_request");
                assert.equal(listeners.size, 1, "subscribe before sending");
                assert.deepEqual(Object.keys(payload).sort(), ["protocol_version", "request_id"]);
                sent.push(JSON.parse(JSON.stringify(payload)));
                if (engine.onSend) engine.onSend(payload);
            }
        },
        $: {
            GetContextPanel: () => root,
            Msg: (...values) => logs.push(values),
            Schedule(delay, callback) {
                if (engine.timerFails) throw new Error("scheduler failed");
                const id = next++;
                timers.set(id, { at: now + delay, delay, callback });
                return id;
            },
            CancelScheduled: id => timers.delete(id)
        }
    });

    function boot() {
        root = panel();
        for (const name of ["coach_probe_state.js", "coach_probe.js"]) {
            vm.runInContext(fs.readFileSync(path.join(scripts, name), "utf8"), context, { filename: name });
        }
        return root;
    }

    function emit(payload) { for (const callback of [...listeners.values()]) callback(payload); }
    function reply(request, status = "ok", reason = "none") {
        return { protocol_version: 1, request_id: request.request_id, status, reason };
    }
    function advance(seconds) {
        const end = now + seconds;
        let iterations = 0;
        while (true) {
            const due = [...timers].filter(([, timer]) => timer.at <= end)
                .sort((a, b) => a[1].at - b[1].at)[0];
            if (!due) break;
            assert.ok(iterations++ < 1000, "timer loop is bounded in fixture");
            timers.delete(due[0]);
            now = due[1].at;
            due[1].callback();
        }
        now = end;
    }
    return { boot, emit, reply, advance, listeners, timers, sent, logs, shared, engine };
}

test("startup subscribes once without sending a request", () => {
    const f = fixture(); const ui = f.boot();
    assert.equal(f.listeners.size, 1);
    assert.equal(f.sent.length, 0);
    assert.equal(ui.button.enabled, true);
    assert.match(ui.status.text, /Проверить связь/);
});

test("two activations while waiting send only one diagnostic request", () => {
    const f = fixture(); const ui = f.boot();
    ui.button.handler(); ui.button.handler();
    assert.equal(f.sent.length, 1);
    assert.equal(ui.button.enabled, false);
    assert.match(ui.status.text, /Ожидаем/);
    assert.equal(f.sent[0].protocol_version, 1);
    assert.ok(f.sent[0].request_id.length <= 64);
});

test("success cancels timeout and permits a fresh unique request", () => {
    const f = fixture(); const ui = f.boot();
    ui.button.handler(); f.emit(f.reply(f.sent[0]));
    const success = ui.status.text;
    assert.match(success, /Сервер ответил/);
    assert.equal(ui.button.enabled, true);
    assert.equal([...f.timers.values()].filter(t => t.delay === 2).length, 0);
    f.advance(3); assert.equal(ui.status.text, success);
    ui.button.handler();
    assert.equal(f.sent.length, 2);
    assert.notEqual(f.sent[0].request_id, f.sent[1].request_id);
});

test("rejection remains visible after the timeout interval and duplicate reply", () => {
    const f = fixture(); const ui = f.boot();
    ui.button.handler();
    f.emit(f.reply(f.sent[0], "rejected", "invalid_request"));
    const rejected = ui.status.text;
    assert.match(rejected, /Запрос отклонён/);
    f.advance(3); f.emit(f.reply(f.sent[0]));
    assert.equal(ui.status.text, rejected);
    assert.equal(ui.button.enabled, true);
});

test("late reply cannot complete a retry after timeout", () => {
    const f = fixture(); const ui = f.boot();
    ui.button.handler(); f.advance(2.1);
    assert.match(ui.status.text, /Ответ не получен/);
    ui.button.handler(); f.emit(f.reply(f.sent[0]));
    assert.match(ui.status.text, /Ожидаем/);
    assert.equal(ui.button.enabled, false);
    f.emit(f.reply(f.sent[1])); assert.match(ui.status.text, /Сервер ответил/);
});

test("wrong ID, version, status and reason never confirm a pending request", () => {
    const f = fixture(); const ui = f.boot(); ui.button.handler();
    const valid = f.reply(f.sent[0]);
    for (const invalid of [null, {}, { ...valid, request_id: "other" },
        { ...valid, protocol_version: 2 }, { ...valid, status: "executed" },
        { ...valid, reason: "invalid_request" }, { ...valid, status: "rejected", reason: "none" }]) {
        f.emit(invalid);
        assert.match(ui.status.text, /Ожидаем/);
    }
    f.emit(valid); assert.match(ui.status.text, /Сервер ответил/);
});

test("cancelled callback cannot time out a newer request", () => {
    const f = fixture(); const ui = f.boot(); ui.button.handler();
    const oldTimer = [...f.timers.values()].find(t => t.delay === 2).callback;
    f.emit(f.reply(f.sent[0])); ui.button.handler(); oldTimer();
    assert.match(ui.status.text, /Ожидаем/);
    f.emit(f.reply(f.sent[1])); assert.match(ui.status.text, /Сервер ответил/);
});

test("transport failure clears pending state and permits retry", () => {
    const f = fixture(); const ui = f.boot(); f.engine.sendFails = true;
    ui.button.handler();
    assert.match(ui.status.text, /Не удалось отправить/);
    assert.equal(ui.button.enabled, true);
    assert.equal([...f.timers.values()].filter(t => t.delay === 2).length, 0);
    f.engine.sendFails = false; ui.button.handler();
    assert.equal(f.sent.length, 1);
    f.emit(f.reply(f.sent[0])); assert.match(ui.status.text, /Сервер ответил/);
});

test("request timer failure does not leave a disabled button", () => {
    const f = fixture(); const ui = f.boot(); f.engine.timerFails = true;
    ui.button.handler();
    assert.equal(ui.button.enabled, true);
    assert.equal(f.sent.length, 0);
    assert.match(ui.status.text, /Не удалось отправить/);
});

test("reload disposes old subscription and timers and preserves unique IDs", () => {
    const f = fixture(); const old = f.boot(); old.button.handler();
    const oldListener = [...f.listeners.values()][0];
    const oldTimer = [...f.timers.values()].find(t => t.delay === 2).callback;
    const current = f.boot(); current.button.handler();
    assert.equal(f.listeners.size, 1);
    assert.equal(old.button.handler, null);
    assert.notEqual(f.sent[0].request_id, f.sent[1].request_id);
    oldListener(f.reply(f.sent[0])); oldTimer();
    assert.match(current.status.text, /Ожидаем/);
    assert.equal(f.timers.size, 2, "one watcher and one request timeout");
    f.emit(f.reply(f.sent[1])); assert.match(current.status.text, /Сервер ответил/);
});

test("destroying panel disposes all subscriptions and timers", () => {
    const f = fixture(); const ui = f.boot(); ui.button.handler();
    const click = ui.button.handler;
    ui.valid = false; f.advance(0.3); click();
    assert.equal(f.listeners.size, 0);
    assert.equal(f.timers.size, 0);
    assert.equal(f.sent.length, 1);
});

test("disposed callbacks do not change the previous UI", () => {
    const f = fixture(); const ui = f.boot(); ui.button.handler();
    const listener = [...f.listeners.values()][0];
    const callbacks = [...f.timers.values()].map(timer => timer.callback);
    f.boot();
    const afterDispose = ui.status.text;
    listener(f.reply(f.sent[0])); callbacks.forEach(callback => callback());
    assert.equal(ui.status.text, afterDispose);
    assert.equal(f.listeners.size, 1);
    assert.equal(f.timers.size, 1);
});

test("response during send succeeds because listener and timeout exist first", () => {
    const f = fixture(); const ui = f.boot();
    f.engine.onSend = request => f.emit(f.reply(request));
    ui.button.handler();
    assert.match(ui.status.text, /Сервер ответил/);
    assert.equal(ui.button.enabled, true);
    assert.equal(f.timers.size, 1);
});

test("subscription failure shows unavailable UI without timers", () => {
    const f = fixture(); f.engine.subscribeFails = true;
    const ui = f.boot();
    assert.match(ui.status.text, /недоступна/);
    assert.equal(ui.button.enabled, false);
    assert.equal(f.listeners.size, 0);
    assert.equal(f.timers.size, 0);
});

test("initial label failure rolls back subscription and all timers", () => {
    const f = fixture(); f.engine.renderFailures = 1;
    const ui = f.boot();
    assert.equal(f.listeners.size, 0);
    assert.equal(f.timers.size, 0);
    assert.equal(ui.button.enabled, false);
    assert.match(ui.status.text, /недоступна/);
});

test("pending label failure disposes panel without a stranded request", () => {
    const f = fixture(); const ui = f.boot();
    f.engine.renderFailures = 1;
    ui.button.handler();
    assert.equal(f.listeners.size, 0);
    assert.equal(f.timers.size, 0);
    assert.equal(f.sent.length, 0);
    assert.equal(ui.button.handler, null);
    assert.match(ui.status.text, /недоступна/);
});
