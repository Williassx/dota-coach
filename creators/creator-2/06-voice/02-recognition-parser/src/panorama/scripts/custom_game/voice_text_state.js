/* Local final-text proposals only: no microphone, transport or game authority. */
var DotaCoachVoiceText = (function () {
    "use strict";
    var MAX = 9007199254740991;
    var actions = [
        {action: "farm", phrases: ["фарми", "фармите"]},
        {action: "retreat", phrases: ["отступай", "отступайте"]},
        {action: "regroup", phrases: ["соберись", "соберитесь"]},
        {action: "hold", phrases: ["держи позицию", "держите позицию"]}
    ];
    var roleNames = ["керри", "мидер", "оффлейнер", "четверка", "пятерка"];
    var groups = ["все", "команда"];
    var playerFields = ["id", "playerName", "heroName", "role", "source", "side", "availability"];

    function integer(value) {
        return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0;
    }
    function identifier(value) {
        return typeof value === "string" && value.length > 0 && value.length <= 64 &&
            !/^\s|\s$/.test(value) && !/[\x00-\x1f\x7f]/.test(value);
    }
    function record(input, fields) {
        if (!input || typeof input !== "object" || Array.isArray(input)) { return null; }
        var names = Object.getOwnPropertyNames(input);
        if (names.length !== fields.length) { return null; }
        var next = {};
        for (var i = 0; i < fields.length; i += 1) {
            var field = fields[i];
            var descriptor = Object.getOwnPropertyDescriptor(input, field);
            if (!descriptor || !descriptor.enumerable ||
                    !Object.prototype.hasOwnProperty.call(descriptor, "value")) { return null; }
            next[field] = descriptor.value;
        }
        return next;
    }
    function players(input) {
        if (!Array.isArray(input)) { return null; }
        var length = Object.getOwnPropertyDescriptor(input, "length").value;
        if (!integer(length) || length > 5 || Object.getOwnPropertyNames(input).length !== length + 1) { return null; }
        var next = [];
        for (var i = 0; i < length; i += 1) {
            var item = Object.getOwnPropertyDescriptor(input, String(i));
            if (!item || !item.enumerable || !Object.prototype.hasOwnProperty.call(item, "value")) { return null; }
            var row = record(item.value, playerFields);
            if (!row) { return null; }
            next.push(row);
        }
        return next;
    }
    function normalize(value) {
        if (typeof value !== "string" || value.length > 256) { return null; }
        var normalized = value.toLowerCase().replace(/ё/g, "е").replace(/,/g, " ")
            .replace(/\s+/g, " ").replace(/^ | $/g, "").replace(/[.!?]+$/, "").replace(/ $/, "");
        if (!normalized || !/^[a-zа-я0-9 _-]+$/.test(normalized)) { return null; }
        return normalized;
    }
    function result(status, reason, normalized, proposal) {
        return {status: status, reason: reason, normalizedText: normalized, proposal: proposal};
    }
    function rejected(reason, normalized) { return result("rejected", reason, normalized || null, null); }

    function create() {
        if (typeof DotaCoachRoster === "undefined" || typeof DotaCoachRoster.create !== "function") {
            throw new Error("DotaCoachRoster must be loaded first");
        }
        var roster = DotaCoachRoster.create();
        var rows = [], revision = null, closed = false, busy = false, consumed = [];

        function resolve(address) {
            var interpretations = [], candidates = [];
            var role = roleNames.indexOf(address) + 1;
            if (role) {
                candidates = rows.filter(function (row) { return row.side === "own" && row.role === role; });
                interpretations.push({kind: "role", rows: candidates});
            }
            if (groups.indexOf(address) !== -1) {
                candidates = rows.filter(function (row) { return row.side === "own"; });
                interpretations.push({kind: "group", rows: candidates});
            }
            candidates = rows.filter(function (row) { return normalize(row.playerName) === address; });
            if (candidates.length) { interpretations.push({kind: "player", rows: candidates}); }
            if (interpretations.length > 1) { return {reason: "ambiguous_address"}; }
            if (!interpretations.length || !interpretations[0].rows.length) { return {reason: "unknown_address"}; }
            var match = interpretations[0];
            if (match.kind !== "group" && match.rows.length !== 1) { return {reason: "ambiguous_address"}; }
            var cards = roster.view().cards;
            for (var i = 0; i < match.rows.length; i += 1) {
                var id = match.rows[i].id;
                var card = cards.filter(function (value) { return value.id === id; })[0];
                if (!card || !card.availableForOrders) { return {reason: "address_unavailable"}; }
            }
            return {kind: match.kind, ids: match.rows.map(function (row) { return row.id; }),
                names: match.rows.map(function (row) { return row.playerName; })};
        }

        return {
            update: function (input) {
                if (closed || busy) { return false; }
                busy = true;
                try {
                    var frame = record(input, ["revision", "players"]);
                    if (closed || !frame || !integer(frame.revision) ||
                            (revision !== null && frame.revision <= revision)) { return false; }
                    var next = players(frame.players);
                    if (closed || !next || !roster.replace(next)) { return false; }
                    rows = next;
                    revision = frame.revision;
                    return true;
                } catch (error) { return false; }
                finally { busy = false; }
            },
            ingest: function (input) {
                if (closed) { return result("disposed", "disposed", null, null); }
                if (busy) { return rejected("busy"); }
                busy = true;
                try {
                    var event = record(input, ["utteranceId", "text", "rosterRevision", "final"]);
                    if (closed) { return result("disposed", "disposed", null, null); }
                    if (!event || !identifier(event.utteranceId) || !integer(event.rosterRevision) ||
                            typeof event.final !== "boolean") { return rejected("invalid_event"); }
                    if (!event.final) { return result("interim", "interim", null, null); }
                    if (consumed.indexOf(event.utteranceId) !== -1) { return rejected("duplicate"); }
                    if (consumed.length === 128) { return rejected("history_full"); }
                    consumed.push(event.utteranceId);
                    if (revision === null) { return rejected("no_roster"); }
                    if (event.rosterRevision !== revision) { return rejected("stale_roster"); }
                    var text = normalize(event.text);
                    if (!text) { return rejected("invalid_text"); }
                    if (/(^| )(не|нет)( |$)/.test(text)) { return rejected("negated", text); }
                    if (/(^| )(и|или|потом|затем)( |$)/.test(text)) { return rejected("multiple_commands", text); }
                    var action = null, address = null;
                    for (var i = 0; i < actions.length; i += 1) {
                        for (var p = 0; p < actions[i].phrases.length; p += 1) {
                            var phrase = actions[i].phrases[p];
                            if (text === phrase) { return rejected("missing_address", text); }
                            if (text.slice(-(phrase.length + 1)) === " " + phrase) {
                                action = actions[i].action;
                                address = text.slice(0, -(phrase.length + 1));
                            }
                        }
                    }
                    if (!action) { return rejected("unknown_action", text); }
                    var target = resolve(address);
                    if (target.reason) { return rejected(target.reason, text); }
                    return result("ready", "none", text, {
                        utteranceId: event.utteranceId, rosterRevision: revision,
                        action: action, recipientIds: target.ids, recipientNames: target.names, addressKind: target.kind
                    });
                } catch (error) {
                    return closed ? result("disposed", "disposed", null, null) : rejected("invalid_event");
                } finally { busy = false; }
            },
            view: function () {
                return {status: closed ? "disposed" : (busy ? "updating" : (revision === null ? "empty" : "ready")),
                    revision: closed ? null : revision, consumed: consumed.length, capacity: 128};
            },
            vocabulary: function () {
                return JSON.parse(JSON.stringify({actions: actions, roles: roleNames, groups: groups}));
            },
            dispose: function () {
                if (closed) { return; }
                closed = true;
                rows = [];
                revision = null;
                consumed = [];
                roster.dispose();
            }
        };
    }
    return {create: create};
}());
