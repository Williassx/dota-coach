/* Explicit read-only source-history panel; no game API, timers or transport. */
var DotaCoachOrdersTimelinePanels = (function () {
    "use strict";
    var owners = [];
    var names = ["TimelineTitle", "TimelineSummary", "TimelineHint"];
    for (var n = 0; n < 6; n += 1) { names.push("TimelineEvent" + n); }
    function valid(node) { if (!node || !node.IsValid()) { throw new Error("Timeline node unavailable"); } return node; }

    function bind(root) {
        if (!root) { throw new Error("Timeline root unavailable"); }
        if (owners.indexOf(root) !== -1) { throw new Error("Timeline root already bound"); }
        owners.push(root);
        var binding = true, closed = false, busy = false, staging = false, generation = 0;
        var sourceReady = false, displayed = null, history = null, labels = {};
        function release() { var at = owners.indexOf(root); if (at !== -1) { owners.splice(at, 1); } }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1; sourceReady = false; displayed = null;
            if (history) { history.dispose(); }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            for (var i = 0; i < names.length; i += 1) {
                try {
                    var node = labels[names[i]];
                    if (node && node.IsValid()) { node.html = false; node.text = ""; }
                } catch (error) { /* Partial or destroyed label. */ }
            }
            if (!binding) { release(); }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                if (!binding && !staging && root.visible === false) { throw new Error("Timeline root hidden"); }
                for (var i = 0; i < names.length; i += 1) {
                    if (closed) { return false; }
                    var node = labels[names[i]];
                    valid(node);
                    if (node.visible === false || root.FindChildTraverse(names[i]) !== node) {
                        throw new Error("Timeline label hidden or replaced");
                    }
                }
                if (history.view().closed) { throw new Error("Timeline history closed"); }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return !closed && generation === version && available(); }
        function write(name, text, version) {
            if (!current(version)) { return false; }
            labels[name].html = false;
            if (!current(version)) { return false; }
            labels[name].text = text;
            return current(version);
        }
        function visibility(value, version) {
            if (!current(version)) { return false; }
            root.visible = value;
            return current(version);
        }
        function stage(version) {
            staging = true; displayed = null;
            if (!visibility(false, version)) { return false; }
            for (var i = 0; i < names.length; i += 1) { if (!write(names[i], "", version)) { return false; } }
            return true;
        }
        function paint(version) {
            var state = history.view();
            if (!state || state.closed) { dispose(); return false; }
            var shown = sourceReady ? state.events.slice(-6) : [];
            var total = sourceReady ? state.events.length : 0;
            var dropped = sourceReady ? state.droppedEvents : 0;
            var summary = !sourceReady ? "Источник истории недоступен." :
                "Показано: " + shown.length + " из " + total + ". Скрыто сохранённых: " + (total - shown.length) +
                ". Вытеснено: " + dropped + ".";
            if (!write("TimelineTitle", "История приказов", version) || !write("TimelineSummary", summary, version) ||
                    !write("TimelineHint", "Снимки интерфейса. Игровой эффект не подтверждён.", version)) { return false; }
            for (var i = 0; i < 6; i += 1) {
                var item = shown[i];
                var text = item ? "#" + item.eventIndex + " · " + item.actorName + "\n" + item.actionText +
                    "\n" + item.stageText + (item.reasonText ? "\n" + item.reasonText : "") : "";
                if (!write("TimelineEvent" + i, text, version)) { return false; }
            }
            if (!current(version)) { return false; }
            displayed = {ready: sourceReady, events: shown, totalStored: total,
                hiddenStored: total - shown.length, droppedEvents: dropped, closed: false};
            return visibility(true, version);
        }
        function run(operation) {
            if (closed || busy) { return false; }
            busy = true; var version = ++generation;
            try {
                if (!available() || !stage(version) || !current(version)) { return false; }
                var accepted = operation();
                return current(version) && paint(version) && accepted;
            } catch (error) { dispose(); return false; }
            finally { busy = false; staging = false; }
        }
        var api = {
            record: function (input) {
                return run(function () {
                    sourceReady = false;
                    var result = history.record(input);
                    if (closed) { return false; }
                    if (result.status === "closed") { dispose(); return false; }
                    sourceReady = result.status === "recorded" || result.status === "unchanged";
                    return sourceReady;
                });
            },
            refresh: function () { return run(function () { return true; }); },
            view: function () {
                if (closed) { return {ready: false, events: [], totalStored: 0, hiddenStored: 0, droppedEvents: 0, closed: true}; }
                if (busy) { return null; }
                busy = true;
                try { return available() && displayed ? JSON.parse(JSON.stringify(displayed)) : null; }
                finally { busy = false; }
            },
            dispose: dispose,
            isDisposed: function () {
                if (closed || busy) { return closed; }
                busy = true;
                try { available(); return closed; }
                finally { busy = false; }
            }
        };
        try {
            valid(root);
            for (var i = 0; i < names.length; i += 1) {
                labels[names[i]] = valid(root.FindChildTraverse(names[i]));
            }
            history = DotaCoachOrdersTimeline.create();
            if (!run(function () { return true; })) { throw new Error("Timeline initial render failed"); }
            return api;
        } catch (error) { dispose(); throw error; }
        finally { binding = false; if (closed) { release(); } }
    }
    return { bind: bind };
}());
