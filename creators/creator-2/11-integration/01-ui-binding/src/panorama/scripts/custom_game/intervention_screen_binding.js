/* Explicit two-pane source composition; no bootstrap, native input or server authority. */
var DotaCoachInterventionScreenPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) { if (!panel || !panel.IsValid()) { throw new Error("Intervention screen unavailable"); } return panel; }
    function validHandle(value) { return typeof value === "number" && value >= 0 && value <= 9007199254740991 && value % 1 === 0; }
    function bind(root, send) {
        if (send !== undefined && send !== null && typeof send !== "function") { throw new Error("Explicit send function required"); }
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Intervention screen already bound"); }
        owners.push(root);
        var closed = false, binding = true, owned = false, busy = false, generation = 0, timer = null;
        var flow = null, status = null, rosterScope = null, manualScope = null, roster = null, manual = null;
        function release() { var index = owners.indexOf(root); if (index !== -1) { owners.splice(index, 1); } }
        function dispose() {
            if (closed) { return; }
            closed = true; busy = false; generation += 1;
            if (flow) { flow.dispose(); }
            if (timer !== null) { try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ } timer = null; }
            if (roster) { roster.dispose(); }
            if (manual) { manual.dispose(); }
            try { if (owned && root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            try { if (owned && status && status.IsValid()) {
                status.html = false; status.text = "Локальный экран закрыт; серверный запрос этим не отменяется.";
            } } catch (error) { /* Destroyed status. */ }
            if (!binding) { release(); }
        }
        function basic() {
            if (closed) { return false; }
            try {
                valid(root); valid(status); valid(rosterScope); valid(manualScope);
                if (!flow || flow.isDisposed()) { dispose(); return false; }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function available() {
            if (!basic()) { return false; }
            if (binding) { return false; }
            try { if (!roster || !manual || roster.isDisposed() || manual.isDisposed()) { dispose(); return false; } }
            catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return available() && generation === version; }
        function writeStatus(version, text) {
            if (!current(version)) { return false; }
            status.html = false;
            if (!current(version)) { return false; }
            status.text = text; return current(version);
        }
        function paint(version) {
            if (!current(version)) { return false; }
            root.visible = true;
            if (!current(version)) { return false; }
            if (!roster.refresh()) { if (current(version)) { dispose(); } return false; }
            if (!current(version)) { return false; }
            if (!manual.refresh()) { if (current(version)) { dispose(); } return false; }
            return current(version) && writeStatus(version, flow.view().message);
        }
        function invoke(method, args) {
            if (!available() || busy) { return false; }
            var version = ++generation; busy = true;
            try {
                root.visible = false;
                if (!current(version) || !roster.suspend() || !current(version) || !manual.suspend() || !current(version)) {
                    if (current(version)) { dispose(); } return false;
                }
                if (!writeStatus(version, "Экран обновляется; данные недоступны.")) { return false; }
                var accepted = flow[method].apply(flow, args);
                if (!current(version)) { return false; }
                busy = false; return paint(version) && accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function selected() {
            if (binding) { return; }
            if (!available() || busy) { return; }
            var version = ++generation;
            if (!manual.refresh()) { if (current(version)) { dispose(); } return; }
            if (current(version)) { writeStatus(version, flow.view().message); }
        }
        function scopedSend(intent, report) {
            if (!available() || busy) { return; }
            send(intent, function (frame) {
                if (!available() || busy) { return false; }
                var accepted = report(frame);
                if (available() && !busy) { var version = ++generation; writeStatus(version, flow.view().message); }
                return accepted;
            });
        }
        function watch() {
            var handle = $.Schedule(0.25, function () {
                timer = null;
                if (available()) {
                    try {
                        if (!busy) { var version = ++generation; writeStatus(version, flow.view().message); }
                        if (available()) { watch(); }
                    } catch (error) { dispose(); }
                }
            });
            if (!validHandle(handle)) { throw new Error("Group watcher handle unavailable"); }
            if (closed) { try { $.CancelScheduled(handle); } catch (error) { /* Context unavailable. */ } }
            else { timer = handle; }
        }
        try {
            status = valid(root.FindChildTraverse("CoachInterventionStatus"));
            rosterScope = valid(root.FindChildTraverse("CoachInterventionRoster"));
            manualScope = valid(root.FindChildTraverse("ManualRequestRoot"));
            if (rosterScope === manualScope || rosterScope === root || manualScope === root ||
                    rosterScope === status || manualScope === status || root === status) { throw new Error("Distinct scopes required"); }
            flow = DotaCoachInterventionSelection.create(typeof send === "function");
            roster = DotaCoachRosterPanels.bind(rosterScope, selected, flow.rosterPort());
            if (!basic()) { throw new Error("Roster binding interrupted"); }
            manual = DotaCoachInterventionRequestPanels.bind(manualScope,
                typeof send === "function" ? scopedSend : undefined, flow.requestPort());
            owned = true; binding = false;
            if (!available() || !paint(++generation)) { throw new Error("Screen binding interrupted"); }
            watch();
            if (!available()) { throw new Error("Screen watcher interrupted"); }
        } catch (error) { dispose(); binding = false; release(); throw error; }
        return {
            replaceRoster: function (rows) { return invoke("replaceRoster", [rows]); },
            updateControl: function (frame) { return invoke("updateControl", [frame]); },
            selectPlayer: function (id) { return invoke("selectPlayer", [id]); },
            clearSelection: function () { return invoke("clearSelection", []); },
            request: function () {
                if (!available() || busy) { return false; }
                var accepted = manual.request();
                if (available() && !busy) { var version = ++generation; writeStatus(version, flow.view().message); }
                return available() && accepted;
            },
            view: function () { return available() && !busy ? flow.view() : null; },
            refresh: function () {
                if (!available() || busy) { return false; }
                var version = ++generation;
                try { return paint(version); } catch (error) { if (current(version)) { dispose(); } return false; }
            },
            dispose: dispose, isDisposed: function () { return !available(); }
        };
    }
    return { bind: bind };
}());
