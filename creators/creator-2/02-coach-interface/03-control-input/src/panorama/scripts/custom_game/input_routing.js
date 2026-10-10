/* Local routing of existing UI adapters. No Dota mouse hook or transport. */
var DotaCoachInputRouting = (function () {
    "use strict";
    function bind(rosterRoot, ordersRoot, send, onSelection) {
        var roster = null;
        var orders = null;
        var watcher = null;
        var closed = false;
        function dispose() {
            if (closed) { return; }
            closed = true;
            if (watcher !== null) {
                try { $.CancelScheduled(watcher); } catch (error) { /* Context unavailable. */ }
                watcher = null;
            }
            if (roster) { roster.dispose(); }
            if (orders) { orders.dispose(); }
        }
        function available() {
            if (closed) { return false; }
            try {
                if (!rosterRoot || !ordersRoot || !rosterRoot.IsValid() || !ordersRoot.IsValid() ||
                        !roster || !orders || roster.isDisposed() || orders.isDisposed()) {
                    dispose(); return false;
                }
            } catch (error) { dispose(); return false; }
            return true;
        }
        function selected(card) {
            // Initial roster publication happens before its bind returns.
            if (closed || !orders || !orders.selectRecipient(card ? card.id : null,
                    card ? card.playerName : "", card ? card.availableForOrders : false)) {
                throw new Error("Orders selection unavailable");
            }
            if (typeof onSelection === "function") {
                onSelection(card ? { id: card.id, playerName: card.playerName } : null);
            }
        }
        function scopedSend(intent, report) {
            if (!available()) { return; }
            send(intent, function (update) {
                if (available()) { report(update); }
            });
        }
        function watch() {
            watcher = $.Schedule(0.25, function () {
                watcher = null;
                if (!available()) { return; }
                try { watch(); } catch (error) { dispose(); }
            });
        }
        try {
            orders = DotaCoachOrderPanels.bind(ordersRoot, typeof send === "function" ? scopedSend : undefined);
            roster = DotaCoachRosterPanels.bind(rosterRoot, selected);
            if (!available()) { throw new Error("Input routing unavailable"); }
            watch();
        } catch (error) {
            dispose();
            throw error;
        }
        function invoke(child, method, args) {
            if (!available()) { return false; }
            try {
                var accepted = child[method].apply(child, args);
                return available() && accepted;
            } catch (error) { dispose(); return false; }
        }
        return {
            replaceRoster: function (rows) { return invoke(roster, "replace", [rows]); },
            updateControl: function (snapshot) { return invoke(orders, "updateRecipient", [snapshot]); },
            select: function (id) { return invoke(roster, "select", [id]); },
            clearSelection: function () { return invoke(roster, "clearSelection", []); },
            dispose: dispose,
            isDisposed: function () { return !available(); }
        };
    }
    return { bind: bind };
}());
