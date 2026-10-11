/* Explicit source panel. Injected send is a caller adapter, never native input authority. */
var DotaCoachInterventionRequestPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) { if (!panel || !panel.IsValid()) { throw new Error("Manual request panel unavailable"); } return panel; }
    function handleValid(handle) { return typeof handle === "number" && handle >= 0 && handle <= 9007199254740991 && handle % 1 === 0; }
    function bind(root, send, projection) {
        if (send !== undefined && send !== null && typeof send !== "function") { throw new Error("Request adapter must be a function"); }
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Manual request root already bound"); }
        owners.push(root);
        var closed = false, binding = true, busy = false, generation = 0, model = null;
        var labels = {}, nodes = [], button = null, timer = null, replyTimer = null;
        var displayedSignature = null;
        var names = ["Recipient", "Mode", "Actor", "State", "Reason", "Message", "Hint"];
        var stages = { idle: "Нет текущего запроса.", pending: "Ожидается ответ на запрос.",
            accepted: "Принят запрос; MANUAL не подтверждён.", unknown: "Исход запроса неизвестен.",
            rejected: "Запрос отклонён.", cancelled: "Запрос отменён по ответу переходника.",
            "not-sent": "Не отправлен.", "mode-observed": "Наблюдён режим MANUAL; право ввода не подтверждено." };
        function releaseOwner() { var index = owners.indexOf(root); if (index !== -1) { owners.splice(index, 1); } }
        function cancelReply(ticket) {
            if (replyTimer && (ticket === undefined || replyTimer.ticket === ticket)) {
                var handle = replyTimer.handle; replyTimer = null;
                try { $.CancelScheduled(handle); } catch (error) { /* Context unavailable. */ }
            }
        }
        function dispose() {
            if (closed) { return; }
            closed = true; busy = false; generation += 1;
            displayedSignature = null;
            if (model) { model.dispose(); }
            cancelReply();
            if (timer !== null) { try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ } timer = null; }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            try { if (button && button.IsValid()) { button.ClearPanelEvent("onactivate"); button.enabled = false; } }
            catch (error) { /* Partial button. */ }
            for (var n = 0; n < names.length; n += 1) {
                try { var label = labels[names[n]]; if (label && label.IsValid()) { label.html = false; label.text = ""; } }
                catch (error) { /* Partial/destroyed label. */ }
            }
            if (!binding) { releaseOwner(); }
        }
        function treeAvailable() {
            if (closed) { return false; }
            try {
                valid(root);
                for (var n = 0; n < nodes.length; n += 1) {
                    valid(nodes[n]);
                    if (nodes[n].visible === false) { throw new Error("Required manual request node hidden"); }
                }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function available() {
            if (!treeAvailable()) { return false; }
            try { if (!model || model.isDisposed()) { dispose(); return false; } }
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
        function disable(version) {
            button.ClearPanelEvent("onactivate");
            if (!current(version)) { return false; }
            button.enabled = false; return current(version);
        }
        function stage(version) {
            displayedSignature = null;
            root.visible = false;
            if (!current(version) || !disable(version)) { return false; }
            for (var n = 0; n < names.length; n += 1) { if (!write(labels[names[n]], "", version)) { return false; } }
            return write(labels.Message, "Данные запроса обновляются и недоступны.", version);
        }
        function caption(row) { return row ? row.playerName + " [" + row.id + "]" : "Игрок не выбран или снимок недоступен."; }
        function render() {
            if (!available()) { return false; }
            var version = ++generation;
            try {
                var view = model.view(), signature = JSON.stringify(view), selected = view.selected, request = view.request;
                var canRequest = view.canRequest && typeof send === "function";
                var message = view.canRequest && !canRequest ? "Переходник запроса не подключён к панели." : view.message;
                var mode = !selected ? "Снимок недоступен." : (selected.mode === "AI" ? "Снимок: ИИ." :
                    (selected.mode === "MANUAL" ? "Снимок: MANUAL; право ввода проверяется отдельно." : "Снимок: неактивен."));
                root.visible = true;
                if (!current(version) || !write(labels.Recipient, caption(selected), version) ||
                        !write(labels.Mode, mode, version) ||
                        !write(labels.Actor, request ? request.playerName + " [" + request.recipientId + "]" : "Нет адресата запроса.", version) ||
                        !write(labels.State, stages[view.status] || "Состояние недоступно.", version) ||
                        !write(labels.Reason, request ? request.reason : "", version) ||
                        !write(labels.Message, message, version) ||
                        !write(labels.Hint, "Запросить ручное управление", version) || !disable(version)) { return false; }
                button.enabled = canRequest;
                if (!current(version)) { return false; }
                if (canRequest) {
                    button.SetPanelEvent("onactivate", function () { if (current(version) && !busy) { issue(); } });
                    if (!current(version)) { return false; }
                }
                displayedSignature = signature;
                return true;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function reconcileTimer() {
            var active = model.view().request;
            if (replyTimer && (!active || active.ticket !== replyTimer.ticket || active.stage !== "pending")) { cancelReply(); }
        }
        function refresh() {
            if (!available() || busy) { return false; }
            try { reconcileTimer(); return available() && render(); }
            catch (error) { dispose(); return false; }
        }
        function mutate(method, args) {
            if (!available() || busy) { return false; }
            var version = ++generation; busy = true;
            try {
                if (!stage(version) || !current(version)) { return false; }
                var accepted = model[method].apply(model, args);
                if (!current(version)) { return false; }
                reconcileTimer();
                if (!current(version)) { return false; }
                busy = false; return render() && accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function receive(ticket, frame) {
            if (!available() || busy) { return false; }
            var active = model.view().request;
            if (!active || active.ticket !== ticket || ["pending", "unknown", "accepted"].indexOf(active.stage) === -1) { return false; }
            return mutate("report", [ticket, frame]);
        }
        function issue() {
            if (!available() || busy || typeof send !== "function") { return false; }
            var version = ++generation; busy = true;
            try {
                // An externally changed flow must not dispatch to an actor absent from the displayed frame.
                if (projection !== undefined) {
                    var signature = JSON.stringify(model.view());
                    if (!current(version)) { return false; }
                    if (signature !== displayedSignature) {
                        reconcileTimer();
                        if (!current(version)) { return false; }
                        busy = false; render(); return false;
                    }
                }
                if (!stage(version) || !current(version)) { return false; }
                if (projection !== undefined) {
                    var stagedSignature = JSON.stringify(model.view());
                    if (!current(version)) { return false; }
                    if (stagedSignature !== signature) {
                        reconcileTimer();
                        if (!current(version)) { return false; }
                        busy = false; render(); return false;
                    }
                }
                var intent = projection === undefined ? model.begin() : model.begin(signature);
                if (!current(version)) { return false; }
                if (!intent) { busy = false; render(); return false; }
                // Keep pre-dispatch busy through pending render/arming: no orphaned unsent request on reentry.
                if (!render()) { return false; }
                version = generation;
                var dispatchVersion = version, ticket = intent.ticket, handle = null;
                try {
                    handle = $.Schedule(5, function () {
                        if (!available() || busy || !replyTimer || replyTimer.ticket !== ticket || replyTimer.handle !== handle) { return; }
                        replyTimer = null; mutate("expire", [ticket]);
                    });
                    if (!handleValid(handle)) { throw new Error("ACK timer has no usable handle"); }
                    if (!current(dispatchVersion)) {
                        try { $.CancelScheduled(handle); } catch (error) { /* Context unavailable. */ }
                        return false;
                    }
                    replyTimer = { ticket: ticket, handle: handle };
                } catch (error) {
                    if (current(dispatchVersion)) { model.notSent(ticket); busy = false; render(); }
                    return false;
                }
                if (!current(dispatchVersion)) { return false; }
                var active = model.view().request;
                if (!current(dispatchVersion)) { return false; }
                if (!active || active.ticket !== ticket || active.stage !== "pending") {
                    cancelReply(ticket);
                    if (!current(dispatchVersion)) { return false; }
                    busy = false; render(); return false;
                }
                busy = false;
                try {
                    send(intent, function (frame) { return receive(ticket, frame); });
                    return available();
                } catch (error) {
                    if (available()) {
                        cancelReply(ticket);
                        if (available() && model.expire(ticket)) { render(); }
                    }
                    return false;
                }
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function watch() {
            var handle = $.Schedule(0.25, function () {
                timer = null;
                if (available()) { try { watch(); } catch (error) { dispose(); } }
            });
            if (!handleValid(handle)) { throw new Error("Lifecycle timer has no usable handle"); }
            if (closed) { try { $.CancelScheduled(handle); } catch (error) { /* Context unavailable. */ } }
            else { timer = handle; }
        }
        try {
            for (var n = 0; n < names.length; n += 1) { labels[names[n]] = valid(root.FindChildTraverse("ManualRequest" + names[n])); nodes.push(labels[names[n]]); }
            button = valid(root.FindChildTraverse("ManualRequestButton")); nodes.push(button);
            model = projection === undefined ? DotaCoachInterventionRequests.create(typeof send === "function") :
                DotaCoachPanelPorts.adopt(projection,
                    ["update", "select", "begin", "report", "expire", "notSent", "view"], treeAvailable);
            if (!render()) { throw new Error("Manual request view unavailable"); }
            watch();
            if (!available()) { throw new Error("Manual request binding interrupted"); }
            binding = false;
        } catch (error) { dispose(); binding = false; releaseOwner(); throw error; }
        return { update: function (frame) { return mutate("update", [frame]); },
            select: function (id) { return mutate("select", [id]); }, request: issue,
            refresh: refresh,
            dispose: dispose, isDisposed: function () { return !available(); } };
    }
    return { bind: bind };
}());
