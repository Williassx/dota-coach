/* Explicit isolated pre-match draft screen. No match start, transport or bootstrap. */
var DotaCoachTeamPickerPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Team picker panel unavailable"); }
        return panel;
    }
    function bind(root) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Team picker root already bound"); }
        owners.push(root);
        var closed = false, generation = 0, page = 0, timer = null, model = null;
        var nodes = [], labels = [], buttons = [], candidates = [], selected = [];
        var status = null, count = null, pageText = null, previous = null, next = null, clearButton = null;
        function node(id, label) {
            var panel = valid(root.FindChildTraverse(id));
            nodes.push(panel);
            (label ? labels : buttons).push(panel);
            return panel;
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if (model) { model.dispose(); }
            if (timer !== null) {
                try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ }
                timer = null;
            }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Root destroyed. */ }
            for (var n = 0; n < buttons.length; n += 1) {
                try { if (buttons[n].IsValid()) {
                    buttons[n].ClearPanelEvent("onactivate"); buttons[n].enabled = false; buttons[n].visible = false;
                } } catch (error) { /* Partial/destroyed button. */ }
            }
            for (var l = 0; l < labels.length; l += 1) {
                try { if (labels[l].IsValid()) { labels[l].html = false; labels[l].text = ""; } }
                catch (error) { /* Partial/destroyed label. */ }
            }
            try { if (status && status.IsValid()) { status.text = "Панель выбора закрыта; состав не подтверждён."; } }
            catch (error) { /* Status unavailable. */ }
            var owner = owners.indexOf(root);
            if (owner !== -1) { owners.splice(owner, 1); }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                for (var n = 0; n < nodes.length; n += 1) { valid(nodes[n]); }
                if (!model || model.isDisposed()) { dispose(); return false; }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return available() && generation === version; }
        function write(panel, value, version) {
            if (!current(version)) { return false; }
            panel.html = false;
            if (!current(version)) { return false; }
            panel.text = value;
            return current(version);
        }
        function button(panel, visible, enabled, callback, version) {
            if (!current(version)) { return false; }
            panel.ClearPanelEvent("onactivate");
            if (!current(version)) { return false; }
            panel.enabled = false;
            if (!current(version)) { return false; }
            panel.visible = visible;
            if (!current(version)) { return false; }
            if (enabled) {
                panel.SetPanelEvent("onactivate", function () { if (current(version)) { callback(); } });
                if (!current(version)) { return false; }
                panel.enabled = true;
            }
            return current(version);
        }
        function invoke(method, args) {
            if (!available()) { return false; }
            // Disable stale page/selection handlers before any input getter executes.
            var version = ++generation;
            try {
                var accepted = model[method].apply(model, args);
                if (!current(version)) { return false; }
                return render() && accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function movePage(delta) { if (!available()) { return; } page += delta; render(); }
        function coverage(row) {
            return row.coverage === "unknown" ? "Охват данных неизвестен." :
                (row.coverage === "limited" ? "Источник сообщает ограниченный охват." :
                    "Охват указан источником; роль, герой и патч здесь не проверены.");
        }
        function candidateSlot(slot, row, view, version) {
            var chosen = false;
            for (var n = 0; row && n < view.selected.length; n += 1) {
                if (view.selected[n].id === row.id) { chosen = true; }
            }
            var enabled = !!row && !chosen && view.count < 5;
            if (!button(slot.button, !!row, enabled, function () { invoke("choose", [row.id]); }, version)) { return false; }
            var values = [row ? row.playerName : "", row ? "Версия: " + row.profileVersion : "",
                row ? (row.kind === "synthetic" ? "Синтетический профиль. " : "Сходство модели здесь не проверено. ") + row.sourceLabel : "",
                row ? coverage(row) : "", row ? (chosen ? "Уже в черновике" :
                    (view.count === 5 ? "В черновике уже пять записей" : "Добавить в черновик")) : ""];
            for (var f = 0; f < slot.fields.length; f += 1) {
                if (!write(slot.fields[f], values[f], version)) { return false; }
            }
            return current(version);
        }
        function selectedSlot(slot, row, view, version) {
            if (!button(slot.button, !!row, !!row, function () { invoke("remove", [row.id]); }, version)) { return false; }
            var warnings = [];
            for (var w = 0; row && w < view.warnings.length; w += 1) {
                if (view.warnings[w].id === row.id) { warnings.push(view.warnings[w].text); }
            }
            var values = [row ? row.playerName : "", row ? "Версия: " + row.profileVersion : "",
                warnings.join("\n"), row ? "Убрать из черновика" : ""];
            for (var f = 0; f < slot.fields.length; f += 1) {
                if (!write(slot.fields[f], values[f], version)) { return false; }
            }
            return current(version);
        }
        function render() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view();
                var pages = Math.ceil(view.profiles.length / 5);
                page = Math.max(0, Math.min(page, Math.max(0, pages - 1)));
                root.visible = true;
                if (!current(version) || !write(status, view.message, version) ||
                        !write(count, "Локальный выбор: " + view.count + "/5", version) ||
                        !write(pageText, pages ? "Страница " + (page + 1) + " из " + pages : "Нет записей для выбора", version)) {
                    return false;
                }
                if (!button(previous, true, page > 0, function () { movePage(-1); }, version) ||
                        !button(next, true, page + 1 < pages, function () { movePage(1); }, version) ||
                        !button(clearButton, true, view.count > 0, function () { invoke("clear", []); }, version)) { return false; }
                for (var n = 0; n < 5; n += 1) {
                    if (!candidateSlot(candidates[n], view.profiles[page * 5 + n], view, version) ||
                            !selectedSlot(selected[n], view.selected[n], view, version)) { return false; }
                }
                return current(version);
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function watch() {
            timer = $.Schedule(0.25, function () {
                timer = null;
                if (!available()) { return; }
                try { watch(); } catch (error) { dispose(); }
            });
        }
        try {
            status = node("TeamPickerStatus", true); count = node("TeamPickerCount", true); pageText = node("TeamPickerPage", true);
            previous = node("TeamPagePrevious", false); next = node("TeamPageNext", false); clearButton = node("TeamClear", false);
            for (var n = 0; n < 5; n += 1) {
                var candidate = { button: node("TeamCandidate" + n, false), fields: [] };
                var chosen = { button: node("TeamSelected" + n, false), fields: [] };
                var cf = ["Name", "Version", "Source", "Coverage", "Hint"];
                var sf = ["Name", "Version", "Warnings", "Action"];
                for (var c = 0; c < cf.length; c += 1) { candidate.fields.push(node("TeamCandidate" + cf[c] + n, true)); }
                for (var s = 0; s < sf.length; s += 1) { chosen.fields.push(node("TeamSelected" + sf[s] + n, true)); }
                candidates.push(candidate); selected.push(chosen);
            }
            model = DotaCoachTeamPicker.create();
            if (!render()) { throw new Error("Team picker view unavailable"); }
            watch();
        } catch (error) { dispose(); throw error; }
        return {
            update: function (snapshot) { return invoke("update", [snapshot]); },
            choose: function (id) { return invoke("choose", [id]); },
            remove: function (id) { return invoke("remove", [id]); },
            clear: function () { return invoke("clear", []); },
            draft: function () { return available() ? model.draft() : null; },
            dispose: dispose,
            isDisposed: function () { return !available(); }
        };
    }
    return { bind: bind };
}());
