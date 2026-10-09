/* Injected presentation gateway only. No Dota transport or hero control. */
var DotaCoachOrderPanels = (function () {
    "use strict";
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Orders panels unavailable"); }
        return panel;
    }
    function bind(root, send) {
        valid(root);
        var labels = {};
        var fields = ["Recipient", "Mode", "RequestRecipient", "Action", "Result", "Reason", "Eligibility"];
        for (var n = 0; n < fields.length; n += 1) {
            labels[fields[n]] = valid(root.FindChildTraverse("Order" + fields[n]));
        }
        var move = valid(root.FindChildTraverse("OrderMove"));
        var attack = valid(root.FindChildTraverse("OrderAttack"));
        var buttons = [move, attack];
        var state = DotaCoachOrders.create(typeof send === "function");
        var closed = false;
        var generation = 0;
        var replyTimer = null;

        function cancelReply(ticket) {
            if (replyTimer && (ticket === undefined || replyTimer.ticket === ticket)) {
                try { $.CancelScheduled(replyTimer.handle); } catch (error) { /* Already unavailable. */ }
                replyTimer = null;
            }
        }
        function dispose() {
            if (closed) { return; }
            closed = true;
            generation += 1;
            cancelReply();
            state.dispose();
            for (var n = 0; n < buttons.length; n += 1) {
                try {
                    if (buttons[n].IsValid()) {
                        buttons[n].ClearPanelEvent("onactivate");
                        buttons[n].enabled = false;
                        buttons[n].visible = false;
                    }
                } catch (error) { /* Release the other button as well. */ }
            }
        }
        function available() {
            if (closed) { return false; }
            if (!root.IsValid()) { dispose(); return false; }
            return true;
        }
        function write(label, value) { valid(label); label.html = false; label.text = value; }
        function button(panel, action, enabled) {
            valid(panel);
            panel.ClearPanelEvent("onactivate");
            panel.visible = true;
            panel.enabled = enabled;
            var binding = generation;
            if (enabled) {
                panel.SetPanelEvent("onactivate", function () {
                    if (available() && binding === generation) { issue(action); }
                });
            }
        }
        function publish(message) {
            try {
                var view = state.view();
                generation += 1;
                write(labels.Recipient, "Выбран: " + view.recipientText);
                write(labels.Mode, "Режим: " + view.modeText);
                write(labels.RequestRecipient, "Адресат приказа: " + view.requestRecipientText);
                write(labels.Action, view.actionText);
                write(labels.Result, view.stageText);
                write(labels.Reason, message || view.reasonText);
                write(labels.Eligibility, "Доступность: " + view.eligibilityText);
                button(move, "move", view.canIssue);
                button(attack, "attack", view.canIssue);
                return true;
            } catch (error) {
                dispose();
                try { write(labels.Result, "Панель приказов недоступна."); }
                catch (statusError) { /* The result label may also be unavailable. */ }
                return false;
            }
        }
        function issue(action) {
            var intent = state.begin(action);
            if (!intent || !publish("")) { return; }
            var ticket = intent.ticket;
            try {
                var handle = $.Schedule(2, function () {
                    if (!available()) { return; }
                    if (replyTimer && replyTimer.ticket === ticket) { replyTimer = null; }
                    if (state.expire(ticket)) { publish(""); }
                });
                replyTimer = { ticket: ticket, handle: handle };
            } catch (error) {
                state.notSent(ticket);
                publish("");
                return;
            }
            try {
                send(intent, function (update) {
                    if (!available() || !state.report(ticket, update)) { return; }
                    cancelReply(ticket);
                    publish("");
                });
            } catch (error) {
                cancelReply(ticket);
                if (available() && state.expire(ticket)) { publish(""); }
            }
        }
        var api = {
            setRecipient: function (snapshot) {
                if (!available()) { return false; }
                var before = state.view().ticket;
                var accepted = state.setRecipient(snapshot);
                if (state.view().ticket !== before) { cancelReply(); }
                var displayed = publish(accepted ? "" : "Состояние не обновлено; показаны последние данные.");
                return accepted && displayed;
            },
            dispose: dispose,
            isDisposed: function () { return closed; }
        };
        if (!publish("")) { throw new Error("Orders view unavailable"); }
        return api;
    }
    return { bind: bind };
}());
