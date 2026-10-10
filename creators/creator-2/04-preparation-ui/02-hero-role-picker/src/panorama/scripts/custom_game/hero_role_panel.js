/* Explicit proposed assignments screen. Focus is local; no submit or match start. */
var DotaCoachHeroRolePanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Hero role panel unavailable"); }
        return panel;
    }
    function find(id, rows) {
        for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
        return null;
    }
    function bind(root) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Hero role root already bound"); }
        owners.push(root);
        var closed = false, generation = 0, page = 0, active = null, timer = null, model = null;
        var nodes = [], labels = [], buttons = [], players = [], options = [], assigned = [];
        var status = null, count = null, recipient = null, pageText = null, previous = null, next = null, clearButton = null;
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
            closed = true; generation += 1; active = null;
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
            try { if (status && status.IsValid()) { status.text = "Панель назначений закрыта; состав не подтверждён."; } }
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
        function selectPlayer(id) {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view(), profile = typeof id === "string" ? find(id, view.players) : null;
                if (!current(version)) { return false; }
                if (!profile) { render(); return false; }
                if (!active || active.id !== profile.id || active.profileVersion !== profile.profileVersion) { page = 0; }
                active = { id: profile.id, profileVersion: profile.profileVersion };
                return render();
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function movePage(delta) { if (!available()) { return; } page += delta; render(); }
        function coverage(row) {
            return row.coverage === "unknown" ? "Охват данных неизвестен." :
                (row.coverage === "limited" ? "Источник сообщает ограниченный охват." :
                    "Охват указан источником; роль, герой и патч здесь не проверены.");
        }
        function playerSlot(slot, row, version) {
            if (!button(slot.button, !!row, !!row, function () { selectPlayer(row.id); }, version)) { return false; }
            slot.button.SetHasClass("HeroRoleFocused", !!row && !!active && row.id === active.id && row.profileVersion === active.profileVersion);
            if (!current(version)) { return false; }
            return fields(slot, [row ? row.playerName : "", row ? "Версия: " + row.profileVersion : "",
                row ? (row.kind === "synthetic" ? "Синтетический профиль. " : "Сходство модели здесь не проверено. ") + row.sourceLabel : "",
                row ? "Показать предложения" : ""], version);
        }
        function optionSlot(slot, row, profile, view, version) {
            var chosen = false;
            var old = profile ? find(profile.id, view.assignments) : null;
            if (row && old) { chosen = old.heroId === row.heroId && old.role === row.role; }
            var id = profile ? profile.id : null, profileVersion = profile ? profile.profileVersion : null;
            if (!button(slot.button, !!row, !!row && !chosen, function () {
                if (active && active.id === id && active.profileVersion === profileVersion) { invoke("assign", [id, row.heroId, row.role]); }
            }, version)) { return false; }
            return fields(slot, [row ? row.heroName : "", row ? "Позиция " + row.role : "",
                row ? coverage(row) : "", row ? (chosen ? "Уже назначено" : "Назначить в черновике") : ""], version);
        }
        function assignedSlot(slot, row, view, version) {
            if (!button(slot.button, !!row, !!row, function () { invoke("remove", [row.id]); }, version)) { return false; }
            var profile = row ? find(row.id, view.players) : null, warnings = [];
            for (var n = 0; row && n < view.warnings.length; n += 1) { if (view.warnings[n].id === row.id) { warnings.push(view.warnings[n].text); } }
            return fields(slot, [profile ? profile.playerName : "", row ? row.heroName + " · позиция " + row.role : "",
                warnings.join("\n"), row ? "Убрать назначение" : ""], version);
        }
        function render() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view(), profile = active ? find(active.id, view.players) : null;
                if (!profile || profile.profileVersion !== active.profileVersion) { active = null; profile = null; page = 0; }
                var pages = profile ? Math.ceil(profile.choices.length / 5) : 0;
                page = Math.max(0, Math.min(page, Math.max(0, pages - 1)));
                root.visible = true;
                var focusText = profile ? "Выбран: " + profile.playerName + " · версия " + profile.profileVersion +
                    (profile.choices.length ? "" : "; нет предложенных сочетаний.") : "Выберите игрока для просмотра предложений.";
                if (!current(version) || !write(status, view.message, version) ||
                        !write(count, "Локальные назначения: " + view.assignments.length + "/5", version) ||
                        !write(recipient, focusText, version) ||
                        !write(pageText, pages ? "Страница " + (page + 1) + " из " + pages : (profile ? "Для этого игрока нет предложений" : "Сначала выберите игрока"), version)) { return false; }
                if (!button(previous, true, page > 0, function () { movePage(-1); }, version) ||
                        !button(next, true, page + 1 < pages, function () { movePage(1); }, version) ||
                        !button(clearButton, true, view.assignments.length > 0, function () { invoke("clear", []); }, version)) { return false; }
                for (var n = 0; n < 5; n += 1) {
                    if (!playerSlot(players[n], view.players[n], version) ||
                            !optionSlot(options[n], profile ? profile.choices[page * 5 + n] : null, profile, view, version) ||
                            !assignedSlot(assigned[n], view.assignments[n], view, version)) { return false; }
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
            status = node("HeroRoleStatus", true); count = node("HeroRoleCount", true);
            recipient = node("HeroRoleRecipient", true); pageText = node("HeroRolePage", true);
            previous = node("HeroRolePrevious", false); next = node("HeroRoleNext", false); clearButton = node("HeroRoleClear", false);
            for (var n = 0; n < 5; n += 1) {
                players.push(group("HeroRolePlayer", ["Name", "Version", "Origin", "Action"], n));
                options.push(group("HeroRoleOption", ["Hero", "Position", "Coverage", "Action"], n));
                assigned.push(group("HeroRoleAssigned", ["Name", "Choice", "Warnings", "Action"], n));
            }
            model = DotaCoachHeroRoles.create();
            if (!render()) { throw new Error("Hero role view unavailable"); }
            watch();
        } catch (error) { dispose(); throw error; }
        return { update: function (frame) { return invoke("update", [frame]); }, selectPlayer: selectPlayer,
            assign: function (id, heroId, role) { return invoke("assign", [id, heroId, role]); },
            remove: function (id) { return invoke("remove", [id]); }, clear: function () { return invoke("clear", []); },
            draft: function () { return available() ? model.draft() : null; }, dispose: dispose,
            isDisposed: function () { return !available(); } };
    }
    return { bind: bind };
}());
