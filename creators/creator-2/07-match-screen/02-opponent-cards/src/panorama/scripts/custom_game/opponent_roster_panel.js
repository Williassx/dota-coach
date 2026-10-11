/* Explicit inert source panel: public names only, no commands or native game API. */
var DotaCoachOpponentPanels = (function () {
    "use strict";
    var owners = [], labels = ["OpponentRosterStatus", "OpponentRosterHint"], containers = ["OpponentCards"];
    for (var n = 0; n < 5; n += 1) {
        labels.push("OpponentName" + n, "OpponentHero" + n, "OpponentInformation" + n);
        containers.push("OpponentCard" + n);
    }
    var required = labels.concat(containers);
    function valid(node) { if (!node || !node.IsValid()) { throw new Error("Opponent node unavailable"); } return node; }
    function closedView() {
        return {ready: false, revision: null, players: [], closed: true,
            evidence: "supplied_public_roster", sourceAuthorizationConfirmed: false};
    }
    function bind(root) {
        if (!root) { throw new Error("Opponent root unavailable"); }
        if (owners.indexOf(root) >= 0) { throw new Error("Opponent root already bound"); }
        owners.push(root);
        var binding = true, closed = false, busy = false, staging = false, generation = 0;
        var nodes = {}, model = null;
        function release() { var index = owners.indexOf(root); if (index >= 0) { owners.splice(index, 1); } }
        function wipe() {
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            for (var i = 0; i < labels.length; i += 1) {
                try {
                    var node = nodes[labels[i]];
                    if (node && node.IsValid()) { node.html = false; node.text = ""; }
                } catch (error) { /* Partial or destroyed tree. */ }
            }
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if (model) { model.dispose(); }
            var alreadyBusy = busy; busy = true;
            try { wipe(); }
            finally { busy = alreadyBusy; if (!busy && !binding) { release(); } }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                if (!binding && !staging && root.visible === false) { throw new Error("Opponent root hidden"); }
                for (var i = 0; i < required.length; i += 1) {
                    if (closed) { return false; }
                    var node = nodes[required[i]];
                    valid(node);
                    if (node.visible === false || root.FindChildTraverse(required[i]) !== node) {
                        throw new Error("Opponent node hidden or replaced");
                    }
                }
                if (model.view().closed) { throw new Error("Opponent model closed"); }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return !closed && generation === version && available(); }
        function write(name, value, version) {
            if (!current(version)) { return false; }
            nodes[name].html = false;
            if (!current(version)) { return false; }
            nodes[name].text = value;
            return current(version);
        }
        function visibility(value, version) {
            if (!current(version)) { return false; }
            root.visible = value;
            return current(version);
        }
        function stage(version) {
            staging = true;
            if (!visibility(false, version)) { return false; }
            for (var i = 0; i < labels.length; i += 1) {
                if (!write(labels[i], "", version)) { return false; }
            }
            return true;
        }
        function paint(version) {
            var state = model.view();
            if (!state || state.closed) { dispose(); return false; }
            if (!write("OpponentRosterStatus", state.ready ? "Публичный состав: " + state.players.length + " из 5." :
                    "Источник состава недоступен.", version) ||
                    !write("OpponentRosterHint", "Публичный состав соперника. Боевые данные неизвестны.", version)) { return false; }
            for (var i = 0; i < 5; i += 1) {
                var row = state.players[i];
                if (!write("OpponentName" + i, state.ready ? (row ? row.playerText : "Имя неизвестно") : "", version) ||
                        !write("OpponentHero" + i, state.ready ? (row ? row.heroText : "Герой неизвестен") : "", version) ||
                        !write("OpponentInformation" + i, state.ready ? "Боевые данные неизвестны." : "", version)) { return false; }
            }
            return visibility(true, version);
        }
        function finish() {
            if (closed) { wipe(); }
            busy = false; staging = false;
            if (closed && !binding) { release(); }
        }
        function run(operation) {
            if (closed || busy) { return false; }
            busy = true; var version = ++generation;
            try {
                if (!available() || !stage(version) || !current(version)) { return false; }
                var accepted = operation();
                return current(version) && paint(version) && accepted;
            } catch (error) { dispose(); return false; }
            finally { finish(); }
        }
        var api = {
            update: function (input) { return run(function () { return model.update(input); }); },
            refresh: function () { return run(function () { return true; }); },
            view: function () {
                if (closed) { return closedView(); }
                if (busy) { return null; }
                busy = true;
                try { return available() ? model.view() : closedView(); }
                finally { finish(); }
            },
            dispose: dispose,
            isDisposed: function () {
                if (closed || busy) { return closed; }
                busy = true;
                try { available(); return closed; }
                finally { finish(); }
            }
        };
        try {
            valid(root);
            for (var i = 0; i < required.length; i += 1) { nodes[required[i]] = valid(root.FindChildTraverse(required[i])); }
            model = DotaCoachOpponentRoster.create();
            if (!run(function () { return true; })) { throw new Error("Opponent initial render failed"); }
            return api;
        } catch (error) { dispose(); throw error; }
        finally { binding = false; if (closed) { release(); } }
    }
    return {bind: bind};
}());
