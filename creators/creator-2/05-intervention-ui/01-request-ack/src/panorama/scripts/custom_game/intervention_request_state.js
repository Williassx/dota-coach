/* Local correlation/display only. No native input, permission token, transport or lease. */
var DotaCoachInterventionRequests = (function () {
    "use strict";
    function text(value, limit) { return typeof value === "string" && value.length > 0 && value.length <= limit && /\S/.test(value); }
    function integer(value) { return typeof value === "number" && value >= 0 && value <= 9007199254740991 && value % 1 === 0; }
    function terminal(stage) { return ["rejected", "cancelled", "not-sent", "mode-observed"].indexOf(stage) !== -1; }
    function create(transportReady) {
        var source = DotaCoachOrders.create(true), configured = transportReady === true;
        var selected = null, fresh = [], request = null, serial = 0, notice = "";
        var closed = false, busy = false, generation = 0;
        function available() { return !closed && !busy; }
        function current(version) { return !closed && generation === version; }
        function observed(id) { return fresh.indexOf(id) !== -1 ? source.snapshot(id) : null; }
        function unresolved() { return request && !terminal(request.stage); }
        function eligible() {
            var row = observed(selected);
            return available() && configured && !!row && row.side === "own" && row.availability === "alive" && row.mode === "AI" && !unresolved();
        }
        function requestCopy() {
            if (!request) { return null; }
            return { ticket: request.ticket, recipientId: request.recipientId, playerName: request.playerName,
                epoch: request.epoch, sourceRevision: request.sourceRevision, action: request.action,
                stage: request.stage, sequence: request.sequence, reason: request.reason };
        }
        function update(frame) {
            if (!available()) { return false; }
            var version = ++generation;
            busy = true;
            try {
                var accepted = source.setRecipient(frame);
                if (!current(version)) { return false; }
                var row = accepted ? source.snapshot() : null;
                if (!current(version)) { return false; }
                if (!row) { fresh = []; busy = false; return false; }
                if (fresh.indexOf(row.id) === -1) { fresh.push(row.id); }
                if (request && request.recipientId === row.id) {
                    if (row.epoch > request.epoch) {
                        notice = "Новая эпоха игрока " + request.playerName + " [" + request.recipientId + "]; прежний исход не подтверждён.";
                        request = null;
                    } else if (!terminal(request.stage) && row.epoch === request.epoch &&
                            row.revision > request.sourceRevision && row.mode === "MANUAL") {
                        request.stage = "mode-observed";
                        request.reason = "Наблюдён режим MANUAL; это не даёт прав на ввод и не доказывает причину перехода.";
                    }
                }
                busy = false; return true;
            } catch (error) {
                if (current(version)) { fresh = []; busy = false; }
                return false;
            }
        }
        function select(id) {
            if (!available()) { return false; }
            if (id !== null && (!text(id, 64) || /^\s|\s$/.test(id) || !source.snapshot(id))) { return false; }
            generation += 1; selected = id; return true;
        }
        function begin() {
            if (!eligible() || serial === 9007199254740991) { return null; }
            var row = observed(selected);
            generation += 1; serial += 1; notice = "";
            request = { ticket: serial, recipientId: row.id, playerName: row.playerName, epoch: row.epoch,
                sourceRevision: row.revision, action: "request_manual", stage: "pending", sequence: -1, reason: "" };
            return { ticket: serial, recipientId: row.id, epoch: row.epoch, action: "request_manual" };
        }
        function report(ticket, input) {
            if (!available() || !request || request.ticket !== ticket || terminal(request.stage)) { return false; }
            var version = ++generation, active = request;
            busy = true;
            try {
                var row = {}, fields = ["sequence", "stage", "reason"];
                if (!input || Object.prototype.toString.call(input) !== "[object Object]" || !current(version)) {
                    if (current(version)) { busy = false; } return false;
                }
                var keys = Object.getOwnPropertyNames(input);
                if (!current(version)) { return false; }
                if (typeof Object.getOwnPropertySymbols === "function") {
                    var symbols = Object.getOwnPropertySymbols(input);
                    if (!current(version)) { return false; }
                    if (symbols.length) { busy = false; return false; }
                }
                if (keys.length !== fields.length) { busy = false; return false; }
                for (var n = 0; n < fields.length; n += 1) {
                    var hasField = Object.prototype.hasOwnProperty.call(input, fields[n]);
                    if (!current(version)) { return false; }
                    if (!hasField) { busy = false; return false; }
                    row[fields[n]] = input[fields[n]];
                    if (!current(version)) { return false; }
                }
                if (!integer(row.sequence) || row.sequence <= active.sequence ||
                        ["accepted", "rejected", "cancelled"].indexOf(row.stage) === -1 ||
                        !(row.reason === null || text(row.reason, 160)) ||
                        (row.stage !== "accepted" && row.reason === null)) { busy = false; return false; }
                active.sequence = row.sequence; active.stage = row.stage; active.reason = row.reason || "";
                busy = false; return true;
            } catch (error) { if (current(version)) { busy = false; } return false; }
        }
        function localOutcome(ticket, stage) {
            if (!available() || !request || request.ticket !== ticket || request.stage !== "pending") { return false; }
            generation += 1; request.stage = stage;
            request.reason = stage === "unknown" ? "Исход неизвестен; повтор недоступен." : "Запрос заведомо не отправлен.";
            return true;
        }
        function message(row) {
            var detail = "";
            if (request) {
                var actor = request.playerName + " [" + request.recipientId + "]: ";
                if (request.stage === "pending") { detail = actor + "ожидается ответ на запрос; режим не подтверждён."; }
                else if (request.stage === "unknown") { detail = actor + "исход неизвестен; повтор недоступен."; }
                else if (request.stage === "accepted") { detail = actor + "запрос принят; режим MANUAL не подтверждён."; }
                else if (request.stage === "mode-observed") { detail = actor + request.reason; }
                else { detail = actor + request.reason; }
            }
            var gate;
            if (!configured) { gate = "Переходник не настроен; запрос недоступен."; }
            else if (selected === null) { gate = "Выберите игрока; запрос сам не отправляется."; }
            else if (!row) { gate = "Снимок выбранного игрока недоступен; нужен принятый снимок этого игрока."; }
            else if (row.side !== "own") { gate = "Чужому игроку запрос недоступен."; }
            else if (row.availability !== "alive") { gate = "Игрок мёртв или не поддерживается."; }
            else if (unresolved()) { gate = "Незавершённый запрос сохраняет прежнего адресата; повтор недоступен."; }
            else if (row.mode !== "AI") { gate = "Снимок сообщает " + row.mode + "; это не даёт прав на ручной ввод."; }
            else { gate = "Можно создать локальный запрос; сервер и право ручного ввода проверяются отдельно."; }
            return (notice ? notice + " " : "") + (detail ? detail + " " : "") + gate;
        }
        function view() {
            if (closed || busy) {
                return { status: closed ? "disposed" : "updating", selected: null, request: null,
                    canRequest: false, manualModeReported: false,
                    message: closed ? "Проекция закрыта; серверный запрос этим не отменяется." : "Данные запроса обновляются и недоступны." };
            }
            var row = observed(selected);
            return { status: request ? request.stage : "idle", selected: row, request: requestCopy(),
                canRequest: eligible(), manualModeReported: !!row && row.mode === "MANUAL", message: message(row) };
        }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1; busy = false;
            source.dispose(); selected = null; fresh = []; request = null; notice = "";
        }
        return { update: update, select: select, begin: begin, report: report,
            expire: function (ticket) { return localOutcome(ticket, "unknown"); },
            notSent: function (ticket) { return localOutcome(ticket, "not-sent"); },
            view: view, dispose: dispose, isDisposed: function () { return closed; } };
    }
    return { create: create };
}());
