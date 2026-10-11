/* Local click proposal only: no input authority, transport, mouse hook or native API. */
var DotaCoachMouseProposals = (function () {
    "use strict";
    var maximum = 9007199254740991;
    function shape(object, expected) {
        if (!object || typeof object !== "object" || Array.isArray(object)) { throw new Error("Expected local DTO"); }
        var names = Object.getOwnPropertyNames(object);
        if (names.length !== expected.length || names.some(function (name) { return expected.indexOf(name) < 0; }) ||
                (typeof Object.getOwnPropertySymbols === "function" && Object.getOwnPropertySymbols(object).length)) {
            throw new Error("Unexpected local fields");
        }
    }
    function data(object, key) {
        var descriptor = Object.getOwnPropertyDescriptor(object, key);
        if (!descriptor || !descriptor.enumerable || !Object.prototype.hasOwnProperty.call(descriptor, "value")) {
            throw new Error("Expected own enumerable data");
        }
        return descriptor.value;
    }
    function text(value) { return typeof value === "string" && value.length > 0 && value.length <= 64 && value.trim().length > 0; }
    function identity(value) { return text(value) && value.trim() === value && !/[\x00-\x1f\x7f]/.test(value); }
    function integer(value, cap) { return typeof value === "number" && value >= 0 && value <= cap && value % 1 === 0; }
    function actorCopy(row) { return row ? {id: row.id, playerName: row.playerName, epoch: row.epoch} : null; }
    function readActor(input) {
        shape(input, ["id", "playerName", "epoch"]);
        var row = {id: data(input, "id"), playerName: data(input, "playerName"), epoch: data(input, "epoch")};
        if (!identity(row.id) || !text(row.playerName) || !integer(row.epoch, maximum)) { throw new Error("Invalid actor"); }
        return row;
    }
    function readMove(input) {
        shape(input, ["x", "y", "z"]);
        var point = {};
        ["x", "y", "z"].forEach(function (key) {
            var value = data(input, key), cap = key === "z" ? 8192 : 32768;
            if (typeof value !== "number" || !isFinite(value) || Math.abs(value) > cap) { throw new Error("Invalid local point"); }
            point[key] = value;
        });
        return {action: "move", point: point, target: null};
    }
    function readTarget(input) {
        shape(input, ["status", "message", "target"]);
        if (data(input, "status") !== "ready") { throw new Error("Target observation unavailable"); }
        var message = data(input, "message");
        if (typeof message !== "string" || message.length > 256) { throw new Error("Invalid observation message"); }
        var target = data(input, "target");
        shape(target, ["id", "label", "team", "kind", "alive", "entityIndex"]);
        var row = {};
        ["id", "label", "team", "kind", "alive", "entityIndex"].forEach(function (key) { row[key] = data(target, key); });
        if (!identity(row.id) || !text(row.label) || ["ally", "enemy"].indexOf(row.team) < 0 ||
                ["hero", "creep"].indexOf(row.kind) < 0 || row.alive !== true || !integer(row.entityIndex, 2147483647)) {
            throw new Error("Invalid target identity");
        }
        var action = row.kind === "creep" ? (row.team === "ally" ? "deny" : "last_hit") : (row.team === "enemy" ? "attack" : null);
        if (!action) { throw new Error("No proposal for allied hero"); }
        return {action: action, point: null, target: {id: row.id, label: row.label, team: row.team, kind: row.kind}};
    }
    function create() {
        var actor = null, proposal = null, serial = 0, closed = false, busy = false;
        function propose(input, read) {
            if (closed || busy || !actor) { return false; }
            proposal = null;
            if (serial === maximum) { return false; }
            busy = true;
            try {
                var draft = read(input);
                if (closed) { return false; }
                serial += 1;
                proposal = {serial: serial, action: draft.action, actor: actorCopy(actor), point: draft.point, target: draft.target};
                return true;
            } catch (error) { return false; }
            finally { busy = false; }
        }
        return {
            captureActor: function (input) {
                if (closed || busy || actor) { return false; }
                busy = true;
                try { var copied = readActor(input); if (closed) { return false; } actor = copied; return true; }
                catch (error) { return false; }
                finally { busy = false; }
            },
            proposeMove: function (input) { return propose(input, readMove); },
            proposeTarget: function (input) { return propose(input, readTarget); },
            reset: function () { if (closed || busy) { return false; } actor = null; proposal = null; return true; },
            view: function () {
                if (busy && !closed) { return null; }
                var copied = proposal ? {serial: proposal.serial, action: proposal.action, actor: actorCopy(proposal.actor),
                    point: proposal.point ? {x: proposal.point.x, y: proposal.point.y, z: proposal.point.z} : null,
                    target: proposal.target ? {id: proposal.target.id, label: proposal.target.label,
                        team: proposal.target.team, kind: proposal.target.kind} : null} : null;
                return {actor: actorCopy(actor), proposal: copied, closed: closed, evidence: "local_click_proposal",
                    canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false};
            },
            dispose: function () { closed = true; actor = null; proposal = null; serial = 0; }
        };
    }
    return {create: create};
}());
