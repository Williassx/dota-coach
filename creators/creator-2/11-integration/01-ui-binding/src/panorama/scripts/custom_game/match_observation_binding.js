/* Explicit read-only composition of two canonical panels; no transport or watchers. */
var DotaCoachMatchObservationPanels = (function () {
    "use strict";
    var owners = [];
    var names = ["MatchObservationStatus", "MatchOpponentHost", "MatchHistoryHost", "OpponentRosterRoot", "OrdersTimelineRoot"];
    function valid(node) { if (!node || !node.IsValid()) { throw new Error("Match observation node unavailable"); } return node; }
    function closedView() { return {closed: true, opponents: null, history: null, nativeConfirmed: false}; }
    function bind(root) {
        if (!root) { throw new Error("Match observation root unavailable"); }
        if (owners.indexOf(root) >= 0) { throw new Error("Match observation already bound"); }
        owners.push(root);
        var nodes = {}, opponents = null, history = null;
        var closed = false, binding = true, busy = true, staging = true, generation = 1;
        var claimed = false, savedVisibility = false, previousVisibility = false;
        function release() { var at = owners.indexOf(root); if (at >= 0) { owners.splice(at, 1); } }
        function wipe() {
            if (!claimed) {
                try { if (savedVisibility && root.IsValid()) { root.visible = previousVisibility; } }
                catch (error) { /* Failed acquisition must preserve an independent scene. */ }
                return;
            }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed parent. */ }
            try {
                var status = nodes.MatchObservationStatus;
                if (status && status.IsValid()) { status.html = false; status.text = ""; }
            } catch (error) { /* Partial or destroyed status. */ }
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            var alreadyBusy = busy; busy = true;
            try {
                try { if (opponents) { opponents.dispose(); } } catch (error) { /* Continue closing history. */ }
                try { if (history) { history.dispose(); } } catch (error) { /* Continue closing parent. */ }
                wipe();
            } finally { busy = alreadyBusy; if (!busy && !binding) { release(); } }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                if (!binding && !staging && root.visible === false) { throw new Error("Match parent hidden"); }
                for (var i = 0; i < names.length; i += 1) {
                    if (closed) { return false; }
                    var node = nodes[names[i]];
                    valid(node);
                    if (node.visible === false || root.FindChildTraverse(names[i]) !== node) {
                        throw new Error("Match node hidden or replaced");
                    }
                }
                if (!opponents || !history || opponents.isDisposed() || history.isDisposed()) {
                    throw new Error("Match child closed");
                }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return !closed && generation === version && available(); }
        function status(text, version) {
            if (!current(version)) { return false; }
            nodes.MatchObservationStatus.html = false;
            if (!current(version)) { return false; }
            nodes.MatchObservationStatus.text = text;
            return current(version);
        }
        function stage(version) {
            staging = true;
            if (!current(version)) { return false; }
            root.visible = false;
            return current(version) && status("", version);
        }
        function paint(version) {
            if (!current(version)) { return false; }
            var publicState = opponents.view(), timeline = history.view();
            if (!publicState || !timeline || publicState.closed || timeline.closed) { dispose(); return false; }
            var text = "Состав соперников: " + (publicState.ready ? publicState.players.length + " из 5" : "нет данных") +
                ". История приказов: " + (timeline.ready ? timeline.totalStored + " записей" : "нет данных") + ".";
            if (!status(text, version) || !current(version)) { return false; }
            root.visible = true;
            return current(version);
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
                if (!available() || !stage(version)) { return false; }
                var accepted = operation(version);
                return current(version) && paint(version) && accepted;
            } catch (error) { dispose(); return false; }
            finally { finish(); }
        }
        var api = {
            updateOpponents: function (input) { return run(function () { return opponents.update(input); }); },
            recordOrder: function (input) { return run(function () { return history.record(input); }); },
            refresh: function () {
                return run(function (version) { return opponents.refresh() && current(version) && history.refresh(); });
            },
            view: function () {
                if (closed) { return closedView(); }
                if (busy) { return null; }
                busy = true;
                try {
                    if (!available()) { return closedView(); }
                    var publicState = opponents.view(), timeline = history.view();
                    if (!publicState || !timeline || publicState.closed || timeline.closed || !available()) {
                        dispose(); return closedView();
                    }
                    return {closed: false, opponents: publicState, history: timeline, nativeConfirmed: false};
                } finally { finish(); }
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
            previousVisibility = root.visible;
            if (typeof previousVisibility !== "boolean") { throw new Error("Match visibility unavailable"); }
            savedVisibility = true; root.visible = false;
            var seen = [root];
            for (var i = 0; i < names.length; i += 1) {
                var node = valid(root.FindChildTraverse(names[i]));
                if (seen.indexOf(node) >= 0) { throw new Error("Distinct match scopes required"); }
                seen.push(node); nodes[names[i]] = node;
            }
            opponents = DotaCoachOpponentPanels.bind(nodes.OpponentRosterRoot);
            history = DotaCoachOrdersTimelinePanels.bind(nodes.OrdersTimelineRoot);
            claimed = true;
            if (!paint(generation)) { throw new Error("Match initial render failed"); }
            return api;
        } catch (error) { dispose(); throw error; }
        finally { binding = false; finish(); }
    }
    return {bind: bind};
}());
