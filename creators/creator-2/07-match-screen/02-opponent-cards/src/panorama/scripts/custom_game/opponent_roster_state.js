/* Public identity projection only; the supplier must enforce server permissions. */
var DotaCoachOpponentRoster = (function () {
    "use strict";
    var maximumRevision = 9007199254740991;
    function data(object, key, enumerable) {
        var descriptor = Object.getOwnPropertyDescriptor(object, key);
        if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, "value") ||
                descriptor.enumerable !== enumerable) { throw new Error("Expected own data field"); }
        return descriptor.value;
    }
    function noSymbols(object) {
        if (typeof Object.getOwnPropertySymbols === "function" && Object.getOwnPropertySymbols(object).length) {
            throw new Error("Unexpected symbol field");
        }
    }
    function fields(object, expected) {
        if (!object || typeof object !== "object" || Array.isArray(object)) { throw new Error("Expected DTO"); }
        var names = Object.getOwnPropertyNames(object);
        if (names.length !== expected.length || names.some(function (name) { return expected.indexOf(name) < 0; })) {
            throw new Error("Unexpected DTO fields");
        }
        noSymbols(object);
        var copy = {};
        expected.forEach(function (key) { copy[key] = data(object, key, true); });
        return copy;
    }
    function text(value) { return typeof value === "string" && value.length > 0 && value.length <= 64 && value.trim().length > 0; }
    function copyInput(input) {
        var snapshot = fields(input, ["revision", "players"]);
        var revision = snapshot.revision, players = snapshot.players;
        if (typeof revision !== "number" || revision < 0 || revision > maximumRevision || Math.floor(revision) !== revision) {
            throw new Error("Invalid local revision");
        }
        if (!Array.isArray(players)) { throw new Error("Expected roster array"); }
        var length = data(players, "length", false);
        if (typeof length !== "number" || length < 0 || length > 5 || Math.floor(length) !== length) {
            throw new Error("Invalid roster length");
        }
        var names = Object.getOwnPropertyNames(players);
        if (names.length !== length + 1) { throw new Error("Unexpected roster fields"); }
        noSymbols(players);
        var rows = [], ids = [];
        for (var i = 0; i < length; i += 1) {
            var row = fields(data(players, String(i), true), ["id", "playerName", "heroName"]);
            if (!text(row.id) || row.id.trim() !== row.id || /[\x00-\x1f\x7f]/.test(row.id) || ids.indexOf(row.id) >= 0 ||
                    (row.playerName !== null && !text(row.playerName)) || (row.heroName !== null && !text(row.heroName))) {
                throw new Error("Invalid public identity");
            }
            ids.push(row.id); rows.push(row);
        }
        return {revision: revision, players: rows};
    }
    function same(left, right) {
        return left.length === right.length && left.every(function (row, i) {
            return row.id === right[i].id && row.playerName === right[i].playerName && row.heroName === right[i].heroName;
        });
    }
    function create() {
        var ready = false, revision = null, rows = [], closed = false, busy = false;
        return {
            update: function (input) {
                if (closed || busy) { return false; }
                busy = true;
                var previousReady = ready, previousRows = rows;
                ready = false; rows = [];
                try {
                    var copied = copyInput(input);
                    if (closed || (revision !== null && copied.revision < revision) ||
                            (copied.revision === revision && (!previousReady || !same(previousRows, copied.players)))) { return false; }
                    revision = copied.revision; rows = copied.players; ready = true;
                    return true;
                } catch (error) { return false; }
                finally { busy = false; }
            },
            view: function () {
                if (busy) { return null; }
                return {ready: ready, revision: revision, players: rows.map(function (row) {
                    return {id: row.id, playerName: row.playerName, heroName: row.heroName,
                        playerText: row.playerName === null ? "Имя неизвестно" : row.playerName,
                        heroText: row.heroName === null ? "Герой неизвестен" : row.heroName,
                        informationText: "Боевые данные неизвестны.", canIssue: false};
                }), closed: closed, evidence: "supplied_public_roster", sourceAuthorizationConfirmed: false};
            },
            dispose: function () { closed = true; ready = false; revision = null; rows = []; }
        };
    }
    return {create: create};
}());
