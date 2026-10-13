"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const driver = path.join(__dirname, "reset_fixture.js");
const trialNames = ["immediate-a", "delayed-a", "immediate-b", "delayed-b"];
const starts = [12, 27.5, 43, 58.5];
const workPorts = ["geometry", "input", "prepare", "reset", "scrollBottom", "scrollTop", "validateReset"];

function load() {
    assert.ok(fs.existsSync(driver), "Missing TEST reset_fixture.js implementation (expected RED)");
    const autoSchedules = [];
    const context = vm.createContext({
        $: {
            Schedule(delay, fn) { autoSchedules.push({ delay, fn }); },
            Msg() {}
        }
    });
    vm.runInContext(fs.readFileSync(driver, "utf8"), context, { filename: driver });
    assert.equal(typeof context.DotaCoachPreparationResetTrace?.start, "function");
    // Native autostart callbacks are deliberately retained, never executed in this suite.
    return { api: context.DotaCoachPreparationResetTrace, autoSchedules };
}

function quietInput() {
    return { cursor: [100, 100], buttons: [false, false, false, false, false],
        alt: false, control: false, shift: false };
}

function harness(options = {}) {
    const { api, autoSchedules } = load();
    let clock = 0;
    let serial = 0;
    let valid = true;
    let currentGeometry = { scroll: 0, content: 2000, viewport: 600 };
    const timers = [];
    const operations = [];
    const records = [];
    const reads = Object.fromEntries(workPorts.map(name => [name, 0]));
    let disposed = 0;
    function operation(name) {
        reads[name]++;
        operations.push({ name, at: clock });
    }
    const ports = {
        isValid() { return valid; },
        now() { return clock * 1000; },
        schedule(delay, fn) {
            assert.ok(Number.isFinite(delay) && delay >= 0, "bounded timer delay required");
            timers.push({ at: clock + delay, serial: ++serial, fn });
        },
        geometry() {
            operation("geometry");
            return options.geometry ? options.geometry(clock) : { ...currentGeometry };
        },
        input() {
            operation("input");
            return options.input ? options.input(clock) : quietInput();
        },
        prepare() {
            operation("prepare");
            currentGeometry = { scroll: 0, content: 2000, viewport: 600 };
        },
        reset() {
            operation("reset");
            currentGeometry = { ...currentGeometry, content: 1400 };
        },
        scrollBottom() {
            operation("scrollBottom");
            currentGeometry.scroll = currentGeometry.viewport - currentGeometry.content;
        },
        scrollTop() {
            operation("scrollTop");
            currentGeometry.scroll = 0;
        },
        validateReset() { operation("validateReset"); return true; },
        disposeUI() { disposed++; },
        record(name, data) { records.push({ name, at: clock, data: structuredClone(data) }); }
    };
    const handle = api.start(ports);
    assert.equal(typeof handle?.dispose, "function");
    function until(target) {
        let count = 0;
        while (timers.length) {
            timers.sort((a, b) => a.at - b.at || a.serial - b.serial);
            if (timers[0].at > target + 1e-8) break;
            assert.ok(++count < 10000, "timer loop must terminate");
            const next = timers.shift();
            clock = next.at;
            next.fn();
        }
        clock = target;
    }
    return { handle, until, records, operations, reads, autoSchedules, ports,
        invalidate() { valid = false; },
        disposed: () => disposed };
}

function atTimes(h, name) {
    return h.operations.filter(x => x.name === name).map(x => Number(x.at.toFixed(6)));
}
function sampleRecords(h, trial) {
    return h.records.filter(x => x.name === "sample" && x.data.trial === trial);
}
function noFailures(h) {
    assert.equal(h.records.filter(x => x.name === "failed").length, 0);
}

test("four independent ABAB trials preserve reset/top delays and finish the cycle", () => {
    const h = harness();
    assert.equal(h.records[0].name, "bound");
    assert.equal(h.records[0].data.physicalInputControlled, false);
    assert.equal(h.autoSchedules.every(x => typeof x.fn === "function"), true);
    h.until(80);
    noFailures(h);
    assert.deepEqual(atTimes(h, "prepare"), starts);
    assert.deepEqual(atTimes(h, "reset"), starts.map(t => t + 1.5));
    assert.deepEqual(atTimes(h, "scrollTop"), starts.map((t, i) => t + (i % 2 ? 2 : 1.5)));
    assert.deepEqual(atTimes(h, "validateReset"), starts.map(t => t + 3.5));
    const bottoms = atTimes(h, "scrollBottom");
    assert.equal(bottoms.length, 4);
    for (let i = 0; i < 4; i++) {
        assert.ok(bottoms[i] >= starts[i] && bottoms[i] < starts[i] + 1.5);
        const phase = h.records.filter(x => x.name === trialNames[i]);
        assert.equal(phase.length, 1);
        assert.equal(Number(phase[0].at.toFixed(6)), starts[i] + 3.5);
        assert.ok(sampleRecords(h, trialNames[i]).length > 1);
    }
    assert.equal(h.records.filter(x => x.name === "cycle").length, 1);
    assert.equal(h.records.find(x => x.name === "cycle").at, 74);
    assert.equal(h.records.filter(x => x.name === "disposed").length, 1);
    assert.equal(h.disposed(), 1);
});

test("cursor, button and modifier activity taint only the current trial", () => {
    const h = harness({ input(t) {
        const value = quietInput();
        if (t >= 12.4 && t < 12.9) value.cursor = [101, 100];
        if (t >= 27.9 && t < 28.4) value.buttons[0] = true;
        if (t >= 43.4 && t < 43.9) value.shift = true;
        return value;
    } });
    h.until(80);
    noFailures(h);
    for (const trial of trialNames.slice(0, 3)) {
        const samples = sampleRecords(h, trial);
        assert.ok(samples.length > 1);
        assert.equal(samples.at(-1).data.inputTainted, true, "taint must remain after activity ends");
        assert.equal(samples.at(-1).data.sampledInputQuiet, false);
    }
    const clean = sampleRecords(h, trialNames[3]);
    assert.ok(clean.length > 1);
    assert.ok(clean.every(x => x.data.inputTainted === false && x.data.sampledInputQuiet === true),
        "a new independent trial must not inherit prior taint");
});

test("quiet sampled input never becomes proof of physical input control", () => {
    const h = harness();
    h.until(80);
    noFailures(h);
    const samples = h.records.filter(x => x.name === "sample");
    assert.ok(samples.length > 10);
    assert.ok(h.records.every(x => x.data.physicalInputControlled === false),
        "bound, operation, phase, disposed and cycle payloads must preserve the limitation");
    for (const entry of samples) {
        assert.equal(entry.data.physicalInputControlled, false);
        assert.equal(entry.data.inputTainted, false);
        assert.equal(entry.data.sampledInputQuiet, true);
    }
    const rebinding = harness({ geometry(t) {
        return { scroll: 0, content: 2000, viewport: t >= 12.3 && t < 12.6 ? 0 : 600 };
    } });
    rebinding.until(80);
    noFailures(rebinding);
    assert.equal(rebinding.records.filter(x => x.name === "cycle").length, 1,
        "temporary zero viewport during layout is permitted before final interpretation");
});

test("malformed input or geometry reports failure, closes once and expires timers", () => {
    const badInputs = [
        { ...quietInput(), cursor: [100] },
        { ...quietInput(), cursor: [100, 100, 0] },
        { ...quietInput(), cursor: [NaN, 100] },
        { ...quietInput(), buttons: [false, false, false, false] },
        { ...quietInput(), buttons: ["false", false, false, false, false] },
        { ...quietInput(), alt: 0 },
        { ...quietInput(), control: undefined },
        { ...quietInput(), shift: null }
    ];
    const badGeometry = [
        { scroll: Infinity, content: 2000, viewport: 600 },
        { scroll: 0, content: NaN, viewport: 600 },
        { scroll: 0, content: -1, viewport: 600 },
        { scroll: 0, content: 2000, viewport: -1 }
    ];
    const cases = badInputs.map(value => ({ input: () => value }))
        .concat(badGeometry.map(value => ({ geometry: () => value })));
    for (const options of cases) {
        const h = harness(options);
        h.until(1);
        const failure = h.records.filter(x => x.name === "failed");
        assert.equal(failure.length, 1);
        assert.equal(failure[0].data.pass, false);
        assert.equal(failure[0].data.physicalInputControlled, false);
        assert.equal(h.disposed(), 1);
        const stopped = { ...h.reads };
        h.until(80);
        h.handle.dispose();
        assert.deepEqual(h.reads, stopped);
        assert.equal(h.disposed(), 1);
        assert.equal(h.records.filter(x => x.name === "cycle").length, 0);
    }
});

test("invalid context expires queued work before geometry, input or UI reads", () => {
    const h = harness();
    const before = { ...h.reads };
    h.invalidate();
    h.until(80);
    assert.deepEqual(h.reads, before);
    assert.equal(h.records.some(x => trialNames.includes(x.name) || x.name === "cycle"), false);
});

test("explicit dispose expires old timers and is idempotent", () => {
    const h = harness();
    h.until(12.2);
    const before = { ...h.reads };
    h.handle.dispose();
    h.handle.dispose();
    assert.equal(h.disposed(), 1);
    h.until(80);
    assert.deepEqual(h.reads, before);
    assert.equal(h.records.some(x => trialNames.includes(x.name) || x.name === "cycle"), false);
});

test("context lost synchronously during prepare stops subsequent snapshot reads", () => {
    const h = harness();
    const before = { ...h.reads };
    h.ports.prepare = () => h.invalidate();
    h.until(80);
    assert.equal(h.reads.geometry, before.geometry);
    assert.equal(h.reads.input, before.input);
    assert.equal(h.records.some(x => trialNames.includes(x.name)), false);
});

test("context lost during geometry stops the following input getter", () => {
    const h = harness();
    const before = h.reads.input;
    h.ports.geometry = () => { h.invalidate(); return { scroll: 0, content: 1000, viewport: 600 }; };
    h.until(80);
    assert.equal(h.reads.input, before);
    assert.equal(h.records.some(x => trialNames.includes(x.name)), false);
});
