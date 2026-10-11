/* Local model composition only; selected card, request actor and input authority differ. */
var DotaCoachInterventionSelection = (function () {
    "use strict";
    function create(adapterConfigured) {
        var roster = DotaCoachRoster.create();
        var requests = DotaCoachInterventionRequests.create(adapterConfigured === true);
        var closed = false, busy = false, generation = 0, listAccepted = false;
        function current(version) { return !closed && generation === version; }
        function selected(view) {
            for (var n = 0; n < view.cards.length; n += 1) {
                if (view.cards[n].id === view.selectedId) { return view.cards[n]; }
            }
            return null;
        }
        function synchronize() {
            var card = selected(roster.view());
            // Unknown control source must not leave the previous player selected in Requests.
            requests.select(null);
            if (card) { requests.select(card.id); }
        }
        function gate(rosterView, manual) {
            var card = selected(rosterView);
            return listAccepted && !!card && card.availableForOrders && manual.canRequest;
        }
        function transact(operation, failure) {
            if (closed || busy) { return failure; }
            var version = ++generation;
            busy = true;
            try {
                var result = operation();
                if (!current(version)) { return failure; }
                busy = false;
                return result;
            } catch (error) {
                if (current(version)) {
                    listAccepted = false;
                    requests.select(null);
                    busy = false;
                }
                return failure;
            }
        }
        function hiddenView() {
            var message = closed ? "Локальная связь закрыта; серверный запрос этим не отменяется." :
                "Данные карточек и запроса обновляются и недоступны.";
            return { roster: { cards: [], selectedId: null, closed: closed },
                manual: { status: closed ? "disposed" : "updating", selected: null, request: null,
                    canRequest: false, manualModeReported: false, message: message },
                canRequest: false, message: message };
        }
        function view() {
            if (closed || busy) { return hiddenView(); }
            var cards = roster.view(), manual = requests.view(), card = selected(cards);
            var canRequest = gate(cards, manual), message = manual.message, blockReason = "";
            if (!listAccepted) {
                blockReason = "Последний список не принят; новый запрос недоступен.";
            } else if (!card) {
                blockReason = cards.cards.length ? "Выберите карточку игрока." : "Список игроков пуст.";
            } else if (!card.availableForOrders) {
                blockReason = "Карточка " + card.playerName + " [" + card.id + "] недоступна для запроса.";
            } else if (!manual.selected) {
                blockReason = "Карточка " + card.playerName + " [" + card.id + "]: контрольный снимок недоступен.";
            }
            if (blockReason) {
                if (!manual.request) { message = blockReason; }
                else if (manual.canRequest && !canRequest) {
                    // Use structured captured result; the private model's retry hint omits the roster gate.
                    message = manual.request.playerName + " [" + manual.request.recipientId + "]: " +
                        manual.request.reason + " " + blockReason;
                } else { message += " " + blockReason; }
                manual.message = message;
            }
            manual.canRequest = canRequest;
            return { roster: cards, manual: manual, canRequest: canRequest, message: message };
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1; busy = false; listAccepted = false;
            roster.dispose(); requests.dispose();
        }
        return {
            replaceRoster: function (rows) {
                return transact(function () {
                    var accepted = roster.replace(rows);
                    if (closed) { return false; }
                    listAccepted = accepted;
                    synchronize(); return accepted;
                }, false);
            },
            selectPlayer: function (id) {
                return transact(function () {
                    var accepted = roster.select(id);
                    if (!closed && accepted) { synchronize(); }
                    return accepted;
                }, false);
            },
            clearSelection: function () {
                return transact(function () {
                    var accepted = roster.clearSelection();
                    if (!closed && accepted) { synchronize(); }
                    return accepted;
                }, false);
            },
            updateControl: function (frame) {
                return transact(function () {
                    var accepted = requests.update(frame);
                    if (!closed) { synchronize(); }
                    return accepted;
                }, false);
            },
            begin: function () {
                return transact(function () {
                    return gate(roster.view(), requests.view()) ? requests.begin() : null;
                }, null);
            },
            report: function (ticket, frame) {
                return transact(function () { return requests.report(ticket, frame); }, false);
            },
            expire: function (ticket) {
                return transact(function () { return requests.expire(ticket); }, false);
            },
            notSent: function (ticket) {
                return transact(function () { return requests.notSent(ticket); }, false);
            },
            view: view, dispose: dispose, isDisposed: function () { return closed; }
        };
    }
    return { create: create };
}());
