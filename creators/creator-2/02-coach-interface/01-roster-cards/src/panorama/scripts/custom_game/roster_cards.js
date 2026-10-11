/* Explicit roster renderer. Selection is local inspection, never a game command. */
var DotaCoachRosterPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) { if (!panel || !panel.IsValid()) { throw new Error("Roster panels unavailable"); } return panel; }
    function bind(root, onSelection, projection) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Roster root already bound"); }
        owners.push(root);
        var status = null, slots = [], nodes = [], labelNodes = [], model = null;
        var closed = false, binding = true, busy = false, suspended = false, generation = 0;
        var names = ["Name", "Hero", "Role", "Source", "Availability", "Hint"], api;
        function release() { var index = owners.indexOf(root); if (index !== -1) { owners.splice(index, 1); } }
        function dispose() {
            if (closed) { return; }
            closed = true; busy = false; suspended = true; generation += 1;
            if (model) { model.dispose(); }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            for (var n = 0; n < slots.length; n += 1) {
                var slot = slots[n];
                try { if (slot.button.IsValid()) {
                    slot.button.ClearPanelEvent("onactivate"); slot.button.enabled = false;
                    slot.button.visible = false; slot.button.SetHasClass("RosterSelected", false);
                } } catch (error) { /* Continue cleanup. */ }
                for (var i = 0; i < names.length; i += 1) {
                    try { var label = slot.labels[names[i]]; if (label && label.IsValid()) { label.html = false; label.text = ""; } }
                    catch (error) { /* Partial/destroyed label. */ }
                }
            }
            try { if (status && status.IsValid()) { status.html = false; status.text = "Просмотр недоступен. Карточки отключены."; } }
            catch (error) { /* Destroyed status. */ }
            if (!binding) { release(); }
        }
        function treeAvailable() {
            if (closed) { return false; }
            try {
                valid(root);
                for (var n = 0; n < nodes.length; n += 1) { valid(nodes[n]); }
                for (var i = 0; i < labelNodes.length; i += 1) {
                    if (labelNodes[i].visible === false) { throw new Error("Required roster label hidden"); }
                }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function available() {
            if (!treeAvailable()) { return false; }
            try { if (!model || (projection !== undefined && model.isDisposed())) { dispose(); return false; } }
            catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return available() && generation === version; }
        function write(label, value, version) {
            if (!current(version)) { return false; }
            label.html = false;
            if (!current(version)) { return false; }
            label.text = value; return current(version);
        }
        function disable(slot, version) {
            slot.button.ClearPanelEvent("onactivate");
            if (!current(version)) { return false; }
            slot.button.enabled = false; return current(version);
        }
        function stage(version) {
            suspended = true; root.visible = false;
            if (!current(version)) { return false; }
            for (var n = 0; n < slots.length; n += 1) {
                if (!disable(slots[n], version)) { return false; }
                for (var i = 0; i < names.length; i += 1) {
                    if (!write(slots[n].labels[names[i]], "", version)) { return false; }
                }
            }
            return write(status, "Карточки обновляются; данные недоступны.", version);
        }
        function render(message) {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view(), selectedName = null;
                suspended = false; root.visible = true;
                if (!current(version)) { return false; }
                for (var n = 0; n < slots.length; n += 1) {
                    var slot = slots[n], card = view.cards[n];
                    if (!disable(slot, version)) { return false; }
                    slot.button.visible = !!card;
                    if (!current(version)) { return false; }
                    slot.button.SetHasClass("RosterSelected", !!card && card.selected);
                    if (!current(version)) { return false; }
                    var values = card ? [card.playerName, "Герой: " + card.heroName, card.roleText,
                        card.sourceText, card.availabilityText, card.selectionHint] : ["", "", "", "", "", ""];
                    for (var i = 0; i < names.length; i += 1) {
                        if (!write(slot.labels[names[i]], values[i], version)) { return false; }
                    }
                    slot.button.enabled = !!card && card.selectable;
                    if (!current(version)) { return false; }
                    if (card && card.selected) { selectedName = card.playerName; }
                    if (card && card.selectable) {
                        (function (button, id, version) {
                            button.SetPanelEvent("onactivate", function () {
                                if (closed || busy || suspended) { return; }
                                // Standalone old handlers inspect by stable ID; integrated handlers expire on repaint.
                                if (projection === undefined ? available() : current(version)) { api.select(id); }
                            });
                        }(slot.button, card.id, version));
                        if (!current(version)) { return false; }
                    }
                }
                return write(status, message || (selectedName ? "Просмотр: " + selectedName :
                    (view.cards.length ? "Выберите игрока для просмотра." : "Игроки не получены.")), version);
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function notify() {
            if (!available() || typeof onSelection !== "function") { return available(); }
            var version = generation, cards = model.view().cards, selected = null;
            for (var n = 0; n < cards.length; n += 1) { if (cards[n].selected) { selected = cards[n]; break; } }
            onSelection(selected); return current(version);
        }
        function invoke(method, args, failureMessage) {
            if (!available() || busy || suspended) { return false; }
            var version = ++generation; busy = true;
            try {
                if (!stage(version) || !current(version)) { return false; }
                var accepted = model[method].apply(model, args);
                if (!current(version)) { return false; }
                busy = false; suspended = false;
                if (!render(accepted ? "" : failureMessage)) { return false; }
                version = generation;
                return accepted ? notify() : false;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        api = {
            replace: function (rows) { return invoke("replace", [rows], "Список не обновлён; показаны предыдущие данные."); },
            select: function (id) { return invoke("select", [id], "Карточка недоступна для выбора."); },
            clearSelection: function () { return invoke("clearSelection", [], "Выбор не очищен."); },
            refresh: function () { return available() && !busy && render(""); },
            suspend: function () {
                if (!available() || busy) { return false; }
                var version = ++generation;
                try { return stage(version); } catch (error) { if (current(version)) { dispose(); } return false; }
            },
            dispose: dispose, isDisposed: function () { return !available(); }
        };
        try {
            status = valid(root.FindChildTraverse("RosterStatus")); nodes.push(status); labelNodes.push(status);
            for (var n = 0; n < 5; n += 1) {
                var slot = { button: valid(root.FindChildTraverse("RosterCard" + n)), labels: {} };
                slots.push(slot); nodes.push(slot.button);
                for (var i = 0; i < names.length; i += 1) {
                    slot.labels[names[i]] = valid(root.FindChildTraverse("Roster" + names[i] + n));
                    nodes.push(slot.labels[names[i]]);
                    labelNodes.push(slot.labels[names[i]]);
                }
            }
            model = projection === undefined ? DotaCoachRoster.create() :
                DotaCoachPanelPorts.adopt(projection, ["replace", "select", "clearSelection", "view"], treeAvailable);
            if (!render("") || !notify()) { throw new Error("Roster view unavailable"); }
            binding = false;
        } catch (error) { dispose(); binding = false; release(); throw error; }
        return api;
    }
    return { bind: bind };
}());
