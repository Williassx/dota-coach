"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const repo = path.resolve(__dirname, "../../../../..");
const base = "creators/creator-2/";
const plain = x => JSON.parse(JSON.stringify(x));
const snapshot = (revision = 1, name = "Enemy A") => ({revision,
    players: [{id: "a", playerName: name, heroName: null}]});
const order = (ticket = 1) => ({recipientText: "Selected B", modeText: "AI", requestRecipientText: "Captured A",
    actionText: "Move", stageText: "Untrusted", reasonText: "", eligibilityText: "View only",
    canIssue: false, ticket, stage: "accepted", closed: false});

function fixture() {
    const deny = new Proxy({}, {get() {throw Error("game API forbidden");}});
    const context = vm.createContext({$: deny, Game: deny});
    for (const source of [
        "07-match-screen/02-opponent-cards/src/panorama/scripts/custom_game/opponent_roster_state.js",
        "07-match-screen/02-opponent-cards/src/panorama/scripts/custom_game/opponent_roster_panel.js",
        "07-match-screen/03-orders-timeline/src/panorama/scripts/custom_game/orders_timeline_state.js",
        "07-match-screen/03-orders-timeline/src/panorama/scripts/custom_game/orders_timeline_panel.js",
        "11-integration/01-ui-binding/src/panorama/scripts/custom_game/match_observation_binding.js"]) {
        const file = path.join(repo, base + source);
        assert.ok(fs.existsSync(file), "match binding source must exist: " + source);
        vm.runInContext(fs.readFileSync(file, "utf8"), context);
    }
    const ids = ["CoachMatchObservation", "MatchObservationStatus", "MatchOpponentHost", "MatchHistoryHost",
        "OpponentRosterRoot", "OpponentRosterStatus", "OpponentRosterHint", "OpponentCards",
        "OrdersTimelineRoot", "TimelineTitle", "TimelineSummary", "TimelineHint"];
    for (let i = 0; i < 5; i++) ids.push("OpponentCard" + i, "OpponentName" + i, "OpponentHero" + i, "OpponentInformation" + i);
    for (let i = 0; i < 6; i++) ids.push("TimelineEvent" + i);
    const nodes = {};
    for (const id of ids) nodes[id] = {visible: true, valid: true, html: true, text: "old",
        IsValid() {return this.valid;}, FindChildTraverse(name) {return nodes[name];}};
    const root = nodes.CoachMatchObservation;
    root.visible = nodes.OpponentRosterRoot.visible = nodes.OrdersTimelineRoot.visible = false;
    return {context, root, nodes, bind: () => context.DotaCoachMatchObservationPanels.bind(root)};
}
test("explicit binding creates two empty read-only areas without demo or native claims", () => {
    const f = fixture(); assert.equal(f.root.visible, false);
    const p = f.bind(); assert.equal(f.root.visible, true);
    assert.equal(p.view().nativeConfirmed, false); assert.equal(p.view().opponents.ready, false);
    assert.equal(p.view().history.ready, false); assert.equal(f.nodes.MatchObservationStatus.html, false);
});
test("independent source updates display opponents and captured order actor", () => {
    const f = fixture(), p = f.bind();
    assert.equal(p.updateOpponents(snapshot()), true); assert.equal(p.recordOrder(order()), true);
    assert.equal(f.nodes.OpponentName0.text, "Enemy A");
    assert.match(f.nodes.TimelineEvent0.text, /Captured A/); assert.doesNotMatch(f.nodes.TimelineEvent0.text, /Selected B|Untrusted/);
    assert.equal(p.view().opponents.sourceAuthorizationConfirmed, false);
    assert.equal(p.view().history.events[0].nativeConfirmed, false);
    assert.equal(p.refresh(), true); assert.equal(p.view().history.events.length, 1);
});
test("invalid opponent source clears only that area's data", () => {
    const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order());
    assert.equal(p.updateOpponents(null), false);
    assert.equal(p.view().opponents.ready, false); assert.equal(p.view().history.ready, true);
    assert.equal(f.nodes.OpponentName0.text, ""); assert.match(f.nodes.TimelineEvent0.text, /Captured A/);
    assert.equal(p.updateOpponents(snapshot(1)), false); assert.equal(p.updateOpponents(snapshot(2)), true);
});
test("invalid order source leaves public opponents displayed", () => {
    const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order());
    assert.equal(p.recordOrder(null), false);
    assert.equal(p.view().opponents.ready, true); assert.equal(p.view().history.ready, false);
    assert.equal(f.nodes.TimelineEvent0.text, ""); assert.equal(f.nodes.OpponentName0.text, "Enemy A");
});
test("parent and changing area clear before input traps while group view is busy", () => {
    for (const method of ["updateOpponents", "recordOrder"]) {
        const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order()); let read = false;
        const input = new Proxy({}, {ownKeys() {
            read = true; assert.equal(f.root.visible, false); assert.equal(f.nodes.MatchObservationStatus.text, "");
            assert.equal(p.view(), null);
            assert.equal(f.nodes[method === "updateOpponents" ? "OpponentName0" : "TimelineEvent0"].text, "");
            return [];
        }});
        assert.equal(p[method](input), false); assert.equal(read, true); assert.equal(f.root.visible, true);
    }
});
test("returned child projections are copied", () => {
    const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order());
    const view = p.view(); view.opponents.players[0].playerName = "changed"; view.history.events[0].actorName = "changed";
    assert.equal(p.view().opponents.players[0].playerName, "Enemy A");
    assert.equal(p.view().history.events[0].actorName, "Captured A");
});
test("missing hidden replaced or invalid required nodes close both areas", () => {
    for (const id of ["MatchObservationStatus", "MatchOpponentHost", "MatchHistoryHost", "OpponentRosterRoot",
        "OrdersTimelineRoot", "OpponentCard4", "TimelineEvent5"]) {
        for (const issue of ["missing", "hidden", "replaced", "invalid"]) {
            const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order());
            if (issue === "missing") delete f.nodes[id];
            if (issue === "hidden") f.nodes[id].visible = false;
            if (issue === "replaced") f.nodes[id] = {...f.nodes[id]};
            if (issue === "invalid") f.nodes[id].valid = false;
            assert.equal(p.refresh(), false); assert.equal(p.isDisposed(), true);
            assert.equal(f.root.visible, false); assert.equal(f.nodes.OpponentName0.text, "");
            assert.equal(f.nodes.TimelineEvent0.text, "");
        }
    }
});
test("isDisposed inspects parent visibility and native tree on explicit call", () => {
    for (const mutate of [f => {f.root.visible = false;}, f => {delete f.nodes.MatchHistoryHost;}, f => {f.root.valid = false;}]) {
        const f = fixture(), p = f.bind(); mutate(f);
        assert.equal(p.isDisposed(), true); assert.equal(p.view().closed, true);
        assert.equal(p.view().opponents, null); assert.equal(p.view().history, null);
    }
});
test("parent ownership reserved before validity/discovery; duplicate keeps active scene", () => {
    const f = fixture();
    f.root.IsValid = function () {assert.throws(() => f.bind(), /already bound/); return this.valid;};
    const p = f.bind(); assert.throws(() => f.bind(), /already bound/);
    assert.equal(p.isDisposed(), false); assert.equal(f.root.visible, true);
});
test("partial child bind failure disposes the created child and permits repaired bind", () => {
    const f = fixture(), saved = f.nodes.TimelineEvent5;
    delete f.nodes.TimelineEvent5; assert.throws(() => f.bind());
    assert.equal(f.root.visible, false); assert.equal(f.nodes.OpponentRosterRoot.visible, false);
    f.nodes.TimelineEvent5 = saved; assert.equal(f.bind().isDisposed(), false);
});
test("aliased required scopes rejected before creating child bindings", () => {
    const f = fixture(), original = f.nodes.OrdersTimelineRoot;
    f.nodes.OrdersTimelineRoot = f.nodes.OpponentRosterRoot;
    assert.throws(() => f.bind()); f.nodes.OrdersTimelineRoot = original;
    assert.equal(f.bind().isDisposed(), false);
});
test("failed group acquisition preserves independently owned child and parent visibility", () => {
    for (const kind of ["opponents", "history"]) {
        const f = fixture(); f.root.visible = true;
        f.nodes.MatchObservationStatus.text = "Independent scene";
        const child = kind === "opponents" ? f.context.DotaCoachOpponentPanels.bind(f.nodes.OpponentRosterRoot) :
            f.context.DotaCoachOrdersTimelinePanels.bind(f.nodes.OrdersTimelineRoot);
        if (kind === "opponents") child.update(snapshot()); else child.record(order());
        assert.throws(() => f.bind(), /already bound/);
        assert.equal(f.root.visible, true); assert.equal(child.isDisposed(), false);
        assert.equal(f.nodes.MatchObservationStatus.text, "Independent scene");
        if (kind === "opponents") assert.equal(f.nodes.OpponentName0.text, "Enemy A");
        else assert.match(f.nodes.TimelineEvent0.text, /Captured A/);
        child.dispose(); assert.equal(f.bind().isDisposed(), false);
    }
});
test("busy native callbacks reject nested operations before DTO reads", () => {
    const f = fixture(), p = f.bind(), find = f.root.FindChildTraverse; let reads = 0;
    const unread = new Proxy({}, {ownKeys() {reads++; return [];}});
    f.root.FindChildTraverse = function (id) {
        assert.equal(p.updateOpponents(unread), false); assert.equal(p.recordOrder(unread), false);
        assert.equal(p.refresh(), false); assert.equal(p.view(), null); assert.equal(p.isDisposed(), false);
        return find.call(this, id);
    };
    assert.equal(p.updateOpponents(snapshot()), true); assert.equal(reads, 0);
});
test("dispose during input inspection closes both; old API cannot change new scene", () => {
    const f = fixture(), p = f.bind(); p.updateOpponents(snapshot()); p.recordOrder(order());
    const input = new Proxy(snapshot(2), {ownKeys(target) {p.dispose(); return Reflect.ownKeys(target);}});
    assert.equal(p.updateOpponents(input), false); assert.equal(p.isDisposed(), true);
    assert.equal(f.root.visible, false); assert.equal(f.nodes.OpponentName0.text, "");
    assert.equal(f.nodes.TimelineEvent0.text, "");
    const fresh = f.bind(); fresh.updateOpponents(snapshot(1, "New source"));
    const unread = new Proxy({}, {ownKeys() {throw Error("unread");}});
    assert.equal(p.updateOpponents(unread), false); assert.equal(p.recordOrder(unread), false);
    p.dispose(); p.refresh(); p.view(); p.isDisposed();
    assert.equal(f.nodes.OpponentName0.text, "New source"); assert.equal(fresh.isDisposed(), false);
});
test("native status setter disposal blocks new parent owner until cleanup finishes", () => {
    const f = fixture(), p = f.bind(); let text = "", fired = false;
    Object.defineProperty(f.nodes.MatchObservationStatus, "text", {get() {return text;}, set(value) {
        text = value;
        if (value && !fired) {fired = true; p.dispose(); assert.throws(() => f.bind(), /already bound/);}
    }});
    assert.equal(p.updateOpponents(snapshot()), false); assert.equal(fired, true);
    assert.equal(text, ""); assert.equal(f.root.visible, false); assert.equal(f.bind().isDisposed(), false);
});
