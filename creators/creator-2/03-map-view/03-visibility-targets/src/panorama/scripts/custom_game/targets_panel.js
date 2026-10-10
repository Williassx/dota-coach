/* Explicit caller-supplied observations and clock. Display only; no entity polling. */
var DotaCoachTargetPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Target panel unavailable"); }
        return panel;
    }
    function bind(root, options) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Target root already bound"); }
        var title = valid(root.FindChildTraverse("TargetTitle"));
        var details = valid(root.FindChildTraverse("TargetDetails"));
        var status = valid(root.FindChildTraverse("TargetStatus"));
        var model = null;
        var closed = false, timer = null, generation = 0;
        owners.push(root);
        function close(reason) {
            if (closed) { return; }
            closed = true;
            generation += 1;
            if (model) { model.dispose(); }
            var reset = [[title, "Цель не выбрана.", false], [details, "", false], [status, reason, true]];
            for (var n = 0; n < reset.length; n += 1) {
                try {
                    valid(reset[n][0]);
                    reset[n][0].visible = reset[n][2];
                    reset[n][0].html = false;
                    reset[n][0].text = reset[n][1];
                } catch (error) { /* Hidden/destroyed renderer may reject writes. */ }
            }
            if (timer !== null) {
                try { $.CancelScheduled(timer); } catch (error) { /* Root/timer may be gone. */ }
                timer = null;
            }
            var owner = owners.indexOf(root);
            if (owner !== -1) { owners.splice(owner, 1); }
        }
        function dispose() { close("Просмотр цели закрыт."); }
        function available() {
            if (closed) { return false; }
            if (!root.IsValid() || model.isDisposed()) { dispose(); return false; }
            return true;
        }
        function current(version) { return available() && generation === version; }
        function write(panel, text, version) {
            if (!current(version)) { return false; }
            valid(panel);
            if (!current(version)) { return false; }
            panel.html = false;
            if (!current(version)) { return false; }
            panel.visible = true;
            if (!current(version)) { return false; }
            panel.text = text;
            return current(version);
        }
        function fail() {
            if (closed) { return false; }
            close("Панель целей недоступна.");
            return false;
        }
        function render() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view();
                if (!current(version)) { return false; }
                var row = view.target;
                if (!write(title, row ? row.label : "Цель не выбрана.", version)) { return false; }
                if (!write(details, row ? (row.team === "ally" ? "Союзный " : "Вражеский ") +
                    (row.kind === "hero" ? "герой" : "крип") + (row.alive ? " · жив" : " · мёртв") : "", version)) { return false; }
                return write(status, view.message, version);
            } catch (error) { return current(version) ? fail() : false; }
        }
        function watch() {
            if (!available()) { return; }
            timer = null;
            render();
            if (!available()) { return; }
            try { timer = $.Schedule(0.1, watch); } catch (error) { fail(); }
        }
        var api = {
            update: function (input) {
                if (!available()) { return false; }
                var accepted = model.update(input);
                return available() && render() && accepted;
            },
            select: function (id) {
                if (!available()) { return false; }
                var accepted = model.select(id);
                return available() && render() && accepted;
            },
            refresh: render,
            dispose: dispose,
            isDisposed: function () { return closed; }
        };
        try { model = DotaCoachTargets.create(options); }
        catch (error) { dispose(); throw error; }
        if (!render()) { throw new Error("Target view unavailable"); }
        try { timer = $.Schedule(0.1, watch); }
        catch (error) { fail(); throw error; }
        return api;
    }
    return { bind: bind };
}());
