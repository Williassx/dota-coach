/* Panorama rendering adapter. Selection is local inspection, never a game command. */
var DotaCoachRosterPanels = (function () {
    "use strict";

    function requirePanel(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Roster panels unavailable"); }
        return panel;
    }

    function bind(root) {
        requirePanel(root);
        var status = requirePanel(root.FindChildTraverse("RosterStatus"));
        var slots = [];
        var names = ["Name", "Hero", "Role", "Source", "Availability", "Hint"];
        for (var i = 0; i < 5; i += 1) {
            var slot = { button: requirePanel(root.FindChildTraverse("RosterCard" + i)), labels: {} };
            for (var n = 0; n < names.length; n += 1) {
                slot.labels[names[n]] = requirePanel(root.FindChildTraverse("Roster" + names[n] + i));
            }
            slots.push(slot);
        }
        var model = DotaCoachRoster.create();
        var closed = false;
        var api;

        function dispose() {
            if (closed) { return; }
            closed = true;
            model.dispose();
            for (var n = 0; n < slots.length; n += 1) {
                try {
                    if (slots[n].button.IsValid()) {
                        slots[n].button.ClearPanelEvent("onactivate");
                        slots[n].button.enabled = false;
                        slots[n].button.visible = false;
                        slots[n].button.SetHasClass("RosterSelected", false);
                    }
                } catch (error) { /* Continue releasing the remaining slots. */ }
            }
        }

        function available() {
            if (closed) { return false; }
            if (!root.IsValid()) { dispose(); return false; }
            return true;
        }

        function write(label, value) {
            requirePanel(label);
            label.html = false;
            label.text = value;
        }

        function activate(button, id) {
            button.SetPanelEvent("onactivate", function () { api.select(id); });
        }

        function render(message) {
            var view = model.view();
            var selectedName = null;
            for (var n = 0; n < slots.length; n += 1) {
                var slot = slots[n];
                var card = view.cards[n];
                requirePanel(slot.button);
                slot.button.ClearPanelEvent("onactivate");
                slot.button.visible = !!card;
                slot.button.enabled = !!card && card.selectable;
                slot.button.SetHasClass("RosterSelected", !!card && card.selected);
                if (!card) { continue; }
                write(slot.labels.Name, card.playerName);
                write(slot.labels.Hero, "Герой: " + card.heroName);
                write(slot.labels.Role, card.roleText);
                write(slot.labels.Source, card.sourceText);
                write(slot.labels.Availability, card.availabilityText);
                write(slot.labels.Hint, card.selectionHint);
                if (card.selected) { selectedName = card.playerName; }
                if (card.selectable) { activate(slot.button, card.id); }
            }
            write(status, message || (selectedName ? "Просмотр: " + selectedName :
                (view.cards.length ? "Выберите игрока для просмотра." : "Игроки не получены.")));
        }

        function publish(message) {
            try { render(message); return true; }
            catch (error) {
                dispose();
                try { write(status, "Просмотр недоступен. Карточки отключены."); }
                catch (statusError) { /* The status panel may also be unavailable. */ }
                return false;
            }
        }

        api = {
            replace: function (rows) {
                if (!available()) { return false; }
                var accepted = model.replace(rows);
                var displayed = publish(accepted ? "" : "Список не обновлён; показаны предыдущие данные.");
                return accepted && displayed;
            },
            select: function (id) {
                if (!available()) { return false; }
                var accepted = model.select(id);
                var displayed = publish(accepted ? "" : "Карточка недоступна для выбора.");
                return accepted && displayed;
            },
            clearSelection: function () {
                if (!available()) { return false; }
                return model.clearSelection() && publish("");
            },
            dispose: dispose,
            isDisposed: function () { return closed; }
        };
        if (!publish("")) { throw new Error("Roster view unavailable"); }
        return api;
    }

    return { bind: bind };
}());
