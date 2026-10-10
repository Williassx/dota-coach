/* Explicit local coach intentions screen; no gameplay effect, submit or match start. */
var DotaCoachPreparationPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Preparation panel unavailable"); }
        return panel;
    }
    function find(id, rows) {
        for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
        return null;
    }
    function bind(root, projection) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Preparation root already bound"); }
        owners.push(root);
        var closed = false, generation = 0, timer = null, model = null;
        var nodes = [], labels = [], buttons = [], planSlots = [], talkSlots = [];
        var status = null, count = null, warnings = null, planHint = null, talkHint = null, lineup = null, clearButton = null;
        var chosenPlan = null, chosenTalk = null;
        function node(id, label) {
            var panel = valid(root.FindChildTraverse(id)); nodes.push(panel);
            (label ? labels : buttons).push(panel); return panel;
        }
        function group(prefix, fields, index) {
            var slot = { button: node(prefix + index, false), fields: [] };
            for (var f = 0; f < fields.length; f += 1) { slot.fields.push(node(prefix + fields[f] + index, true)); }
            return slot;
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            try { if (model) { model.dispose(); } } catch (error) { /* Continue UI cleanup. */ }
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
            try { if (status && status.IsValid()) { status.text = "Панель подготовки закрыта; исполнение не подтверждено."; } }
            catch (error) { /* Status unavailable. */ }
            var owner = owners.indexOf(root);
            if (owner !== -1) { owners.splice(owner, 1); }
        }
        function pendingValid() {
            if (closed) { return false; }
            try { valid(root); for (var n = 0; n < nodes.length; n += 1) { valid(nodes[n]); } }
            catch (error) { return false; }
            return !closed;
        }
        function suspend() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                root.visible = false;
                if (!current(version)) { return false; }
                for (var b = 0; b < buttons.length; b += 1) {
                    if (!button(buttons[b], false, false, null, version)) { return false; }
                }
                for (var l = 0; l < labels.length; l += 1) {
                    if (!write(labels[l], "", version)) { return false; }
                }
                return current(version);
            } catch (error) { if (current(version)) { dispose(); } return false; }
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
            panel.text = value; return current(version);
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
        function fields(slot, values, version) {
            for (var n = 0; n < values.length; n += 1) { if (!write(slot.fields[n], values[n], version)) { return false; } }
            return current(version);
        }
        function invoke(method, args) {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var accepted = model[method].apply(model, args);
                if (!current(version)) { return false; }
                return render() && accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function hint(rows, selected, name) {
            if (!rows.length) { return "Источник: нет вариантов " + name + "."; }
            return selected ? "Вариант " + name + " выбран локально; эффект не подтверждён." :
                "Выберите вариант " + name + "; намерение показано до выбора.";
        }
        function optionSlot(slot, row, selected, method, caption, version) {
            var chosen = !!row && !!selected && row.id === selected.id && row.optionVersion === selected.optionVersion;
            var id = row ? row.id : null;
            if (!button(slot.button, !!row, !!row && !chosen, function () { invoke(method, [id]); }, version)) { return false; }
            return fields(slot, [row ? row.label : "", row ? "Версия варианта: " + row.optionVersion : "",
                row ? row.intent : "", row ? (chosen ? "Уже выбрано" : caption) : ""], version);
        }
        function chosenSlot(slot, row, method, caption, version) {
            if (!button(slot.button, !!row, !!row, function () { invoke(method, []); }, version)) { return false; }
            return fields(slot, [row ? row.label : "", row ? "Версия варианта: " + row.optionVersion : "",
                row ? row.intent : "", row ? caption : ""], version);
        }
        function summary(row) {
            if (!row) { return ""; }
            var lines = ["Локальный состав: 5 записей и 5 назначений. Внутренние идентификаторы:"];
            for (var n = 0; n < row.assignments.length; n += 1) {
                var item = row.assignments[n];
                lines.push(item.id + " · версия " + item.profileVersion + " · герой " + item.heroId + " · позиция " + item.role);
            }
            return lines.join("\n");
        }
        function render() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view(), visible = view.status === "ready", selected = (view.plan ? 1 : 0) + (view.talk ? 1 : 0);
                root.visible = true;
                if (!current(version) || !write(status, view.message, version) ||
                        !write(count, "Локальный выбор подготовки: " + selected + "/2", version) ||
                        !write(warnings, view.warnings.join("\n"), version) || !write(lineup, summary(view.lineup), version) ||
                        !write(planHint, visible ? hint(view.plans, view.plan, "тактики") : "Предложения тактики недоступны.", version) ||
                        !write(talkHint, visible ? hint(view.talks, view.talk, "разговора") : "Предложения разговора недоступны.", version)) { return false; }
                if (!button(clearButton, true, selected > 0, function () { invoke("clear", []); }, version) ||
                        !chosenSlot(chosenPlan, view.plan, "removePlan", "Снять выбор плана", version) ||
                        !chosenSlot(chosenTalk, view.talk, "removeTalk", "Снять выбор разговора", version)) { return false; }
                for (var n = 0; n < 8; n += 1) {
                    if (!optionSlot(planSlots[n], view.plans[n], view.plan, "choosePlan", "Выбрать план", version) ||
                            !optionSlot(talkSlots[n], view.talks[n], view.talk, "chooseTalk", "Выбрать вариант разговора", version)) { return false; }
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
            status = node("PreparationStatus", true); count = node("PreparationCount", true);
            warnings = node("PreparationWarnings", true); planHint = node("PreparationPlanHint", true);
            talkHint = node("PreparationTalkHint", true); lineup = node("PreparationLineup", true);
            clearButton = node("PreparationClear", false);
            for (var n = 0; n < 8; n += 1) {
                planSlots.push(group("PreparationPlan", ["Label", "Version", "Intent", "Action"], n));
                talkSlots.push(group("PreparationTalk", ["Label", "Version", "Intent", "Action"], n));
            }
            chosenPlan = group("PreparationChosenPlan", ["Label", "Version", "Intent", "Action"], "");
            chosenTalk = group("PreparationChosenTalk", ["Label", "Version", "Intent", "Action"], "");
            model = projection === undefined ? DotaCoachPreparation.create() :
                DotaCoachPanelPorts.adopt(projection, ["update", "choosePlan", "chooseTalk", "removePlan", "removeTalk", "clear", "view", "draft"], pendingValid);
            if (!render()) { throw new Error("Preparation view unavailable"); }
            watch();
        } catch (error) { dispose(); throw error; }
        return { update: function (frame) { return invoke("update", [frame]); },
            choosePlan: function (id) { return invoke("choosePlan", [id]); },
            chooseTalk: function (id) { return invoke("chooseTalk", [id]); },
            removePlan: function () { return invoke("removePlan", []); }, removeTalk: function () { return invoke("removeTalk", []); },
            clear: function () { return invoke("clear", []); }, draft: function () { return available() ? model.draft() : null; },
            dispose: dispose, refresh: render, suspend: suspend, isDisposed: function () { return !available(); } };
    }
    return { bind: bind };
}());
