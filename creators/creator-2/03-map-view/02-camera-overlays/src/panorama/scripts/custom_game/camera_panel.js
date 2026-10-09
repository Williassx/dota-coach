/* One explicit focus button, supplied target and gateway. No automatic native binding. */
var DotaCoachCameraPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Camera panels unavailable"); }
        return panel;
    }
    function text(value, max) {
        return typeof value === "string" && value.length > 0 && value.length <= max && /\S/.test(value);
    }
    function copy(input, fields) {
        if (!input || Object.prototype.toString.call(input) !== "[object Object]" ||
                Object.keys(input).length !== fields.length) { return null; }
        var result = {};
        for (var n = 0; n < fields.length; n += 1) {
            if (!Object.prototype.hasOwnProperty.call(input, fields[n])) { return null; }
            result[fields[n]] = input[fields[n]];
        }
        return result;
    }
    function readResult(input, field) {
        var row = copy(input, [field, "reason"]);
        if (!row || typeof row[field] !== "boolean" ||
                (row[field] ? row.reason !== null : !text(row.reason, 160))) {
            throw new Error("Invalid camera result");
        }
        return row;
    }
    function bind(root, gateway) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Camera root already bound"); }
        var recipient = valid(root.FindChildTraverse("CameraRecipient"));
        var availability = valid(root.FindChildTraverse("CameraAvailability"));
        var result = valid(root.FindChildTraverse("CameraResult"));
        var button = valid(root.FindChildTraverse("CameraFocus"));
        var ready = !!gateway && typeof gateway.check === "function" && typeof gateway.focus === "function";
        var target = null;
        var previousName = "";
        var previousId = null;
        var previousEntity = null;
        var previousResult = "Фокус ещё не запрошен.";
        var generation = 0;
        var closed = false;
        owners.push(root);

        function dispose() {
            if (closed) { return; }
            closed = true;
            generation += 1;
            target = null;
            var owner = owners.indexOf(root);
            if (owner !== -1) { owners.splice(owner, 1); }
            try {
                if (button.IsValid()) {
                    button.ClearPanelEvent("onactivate");
                    button.enabled = false;
                    button.visible = false;
                }
            } catch (error) { /* Root may have been destroyed. */ }
        }
        function available() {
            if (closed) { return false; }
            if (!root.IsValid()) { dispose(); return false; }
            return true;
        }
        function current(version, active) {
            return available() && generation === version && target === active;
        }
        function write(panel, value) { valid(panel); panel.html = false; panel.text = value; }
        function fail() {
            if (closed) { return false; }
            dispose();
            try { write(result, "Панель камеры недоступна."); } catch (error) { /* Status unavailable. */ }
            return false;
        }
        function inspect(active) {
            if (!active) { return { available: false, reason: "Выберите игрока для фокуса камеры." }; }
            if (!ready) { return { available: false, reason: "Камера ещё не подключена." }; }
            return readResult(gateway.check(active.entityIndex), "available");
        }
        function publish(message) {
            if (!available()) { return false; }
            var active = target;
            var version = ++generation;
            try {
                valid(button);
                button.ClearPanelEvent("onactivate");
                button.enabled = false;
                button.visible = true;
                var guard = inspect(active);
                if (!current(version, active)) { return false; }
                write(recipient, active ? "Выбран: " + active.playerName : "Игрок не выбран.");
                write(availability, message || (guard.available ? "Доступен фокус героя своей команды." : guard.reason));
                var previousPrefix = active && active.id === previousId && active.entityIndex === previousEntity ?
                    "Для " + previousName + ": " : "Предыдущий выбор — " + previousName + ": ";
                write(result, previousName ? previousPrefix + previousResult : previousResult);
                button.enabled = guard.available;
                if (guard.available) {
                    button.SetPanelEvent("onactivate", function () { focus(version, active); });
                }
                return current(version, active);
            } catch (error) { return current(version, active) ? fail() : false; }
        }
        function focus(version, active) {
            if (!current(version, active)) { return; }
            try {
                var guard = inspect(active);
                if (!current(version, active)) { return; }
                if (!guard.available) { publish(""); return; }
                var outcome;
                try { outcome = gateway.focus(active.entityIndex); }
                catch (error) {
                    outcome = { requested: false,
                        reason: "Запрос фокуса не подтверждён; положение камеры неизвестно." };
                }
                var report = readResult(outcome, "requested");
                if (!current(version, active)) { return; }
                previousName = active.playerName;
                previousId = active.id;
                previousEntity = active.entityIndex;
                previousResult = report.requested ?
                    "Запрос фокуса передан клиенту; положение камеры не подтверждено." : report.reason;
                publish("");
            } catch (error) { if (current(version, active)) { fail(); } }
        }
        var api = {
            setTarget: function (input) {
                if (!available()) { return false; }
                var version = generation;
                var row = null;
                try {
                    if (input !== null) { row = copy(input, ["id", "playerName", "entityIndex"]); }
                } catch (error) { /* Reject invalid input without changing selection. */ }
                if (!available() || generation !== version) { return false; }
                if (input !== null && (!row || !text(row.id, 64) || /^\s|\s$/.test(row.id) ||
                        !text(row.playerName, 64) || typeof row.entityIndex !== "number" ||
                        row.entityIndex < 0 || row.entityIndex > 2147483647 || row.entityIndex % 1 !== 0)) {
                    publish("Цель не обновлена; показаны предыдущие данные.");
                    return false;
                }
                target = row;
                return publish("");
            },
            refresh: function () { return publish(""); },
            dispose: dispose,
            isDisposed: function () { return closed; }
        };
        if (!publish("")) { throw new Error("Camera view unavailable"); }
        return api;
    }
    return { bind: bind };
}());
