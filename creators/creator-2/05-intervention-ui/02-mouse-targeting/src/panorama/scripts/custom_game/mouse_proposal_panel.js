/* Explicit proposal display; no handlers, timers, native mouse hook or sender. */
var DotaCoachMouseProposalPanels = (function () {
    "use strict";
    var owners = [], names = ["MouseActor", "MouseAction", "MouseTarget", "MouseState", "MouseLease", "MouseHint"];
    var captions = {move: "Движение", attack: "Атака героя", last_hit: "Добивание вражеского крипа", deny: "Денай союзного крипа"};
    function valid(node) { if (!node || !node.IsValid()) { throw new Error("Mouse proposal node unavailable"); } return node; }
    function closedView() {
        return {actor: null, proposal: null, closed: true, evidence: "local_click_proposal",
            canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false};
    }
    function bind(root) {
        if (!root) { throw new Error("Mouse proposal root unavailable"); }
        if (owners.indexOf(root) >= 0) { throw new Error("Mouse proposal root already bound"); }
        owners.push(root);
        var model = null, nodes = {}, closed = false, binding = true, busy = false, staging = false, generation = 0;
        function release() { var at = owners.indexOf(root); if (at >= 0) { owners.splice(at, 1); } }
        function wipe() {
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            names.forEach(function (name) {
                try { var node = nodes[name]; if (node && node.IsValid()) { node.html = false; node.text = ""; } }
                catch (error) { /* Partial or destroyed label. */ }
            });
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if (model) { model.dispose(); }
            var wasBusy = busy; busy = true;
            try { wipe(); }
            finally { busy = wasBusy; if (!busy && !binding) { release(); } }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                if (!binding && !staging && root.visible === false) { throw new Error("Mouse proposal root hidden"); }
                for (var i = 0; i < names.length; i += 1) {
                    if (closed) { return false; }
                    var node = nodes[names[i]];
                    valid(node);
                    if (node.visible === false || root.FindChildTraverse(names[i]) !== node) {
                        throw new Error("Mouse proposal label hidden or replaced");
                    }
                }
                if (!model || model.view().closed) { throw new Error("Mouse proposal model closed"); }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return !closed && generation === version && available(); }
        function write(name, text, version) {
            if (!current(version)) { return false; }
            nodes[name].html = false;
            if (!current(version)) { return false; }
            nodes[name].text = text;
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
            for (var i = 0; i < names.length; i += 1) { if (!write(names[i], "", version)) { return false; } }
            return true;
        }
        function paint(version) {
            var state = model.view();
            if (!state || state.closed) { dispose(); return false; }
            var draft = state.proposal;
            var values = [state.actor ? state.actor.playerName : "Адресат не назначен.", draft ? captions[draft.action] : "",
                draft ? (draft.point ? "Точка выбрана." : draft.target.label) : "",
                draft ? "Предложение сформировано." : (state.actor ? "Предложения нет." : "Сначала назначьте адресата."),
                "Время вмешательства неизвестно.", "Действие ещё не выполнено."];
            for (var i = 0; i < names.length; i += 1) { if (!write(names[i], values[i], version)) { return false; } }
            return visibility(true, version);
        }
        function finish() {
            if (closed) { wipe(); }
            busy = false; staging = false;
            if (closed && !binding) { release(); }
        }
        function run(method, input) {
            if (closed || busy) { return false; }
            busy = true; var version = ++generation;
            try {
                if (!available() || !stage(version)) { return false; }
                var accepted = method === null ? true : model[method](input);
                return current(version) && paint(version) && accepted;
            } catch (error) { dispose(); return false; }
            finally { finish(); }
        }
        var api = {
            captureActor: function (input) { return run("captureActor", input); },
            proposeMove: function (input) { return run("proposeMove", input); },
            proposeTarget: function (input) { return run("proposeTarget", input); },
            reset: function () { return run("reset"); },
            refresh: function () { return run(null); },
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
            valid(root); var seen = [root];
            for (var i = 0; i < names.length; i += 1) {
                var node = valid(root.FindChildTraverse(names[i]));
                if (seen.indexOf(node) >= 0) { throw new Error("Distinct mouse labels required"); }
                seen.push(node); nodes[names[i]] = node;
            }
            model = DotaCoachMouseProposals.create();
            if (!run(null)) { throw new Error("Mouse initial render failed"); }
            return api;
        } catch (error) { dispose(); throw error; }
        finally { binding = false; if (closed) { release(); } }
    }
    return {bind: bind};
}());
