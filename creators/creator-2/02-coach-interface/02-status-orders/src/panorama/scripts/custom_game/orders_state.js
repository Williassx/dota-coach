/* Private presentation state. Tickets are local correlation, never authority. */
var DotaCoachOrders = (function () {
    "use strict";
    var snapshotFields = ["id", "playerName", "mode", "epoch", "revision", "side", "availability"];
    var reportFields = ["sequence", "stage", "reason"];
    var modes = { AI: "ИИ (подтверждён)", MANUAL: "Вручную (подтверждён)",
        INACTIVE: "Неактивен (подтверждён)" };
    var stages = { idle: "Нет текущего приказа.", pending: "Ожидается ответ.",
        unknown: "Результат неизвестен.", accepted: "Принят сервером; выполнение не подтверждено.",
        executing: "Исполняется (ответ сервера).", completed: "Выполнен (ответ сервера).",
        rejected: "Отклонён сервером.", cancelled: "Отменён сервером.", "not-sent": "Не отправлен." };

    function text(value, limit) {
        return typeof value === "string" && value.length > 0 && value.length <= limit && /\S/.test(value);
    }
    function integer(value) {
        return typeof value === "number" && value >= 0 && value <= 9007199254740991 && value % 1 === 0;
    }
    function copy(input, fields) {
        try {
            if (!input || Object.prototype.toString.call(input) !== "[object Object]" ||
                    Object.keys(input).length !== fields.length) { return null; }
            var result = {};
            for (var n = 0; n < fields.length; n += 1) {
                if (!Object.prototype.hasOwnProperty.call(input, fields[n])) { return null; }
                result[fields[n]] = input[fields[n]];
            }
            return result;
        } catch (error) { return null; }
    }
    function terminal(stage) {
        return ["completed", "rejected", "cancelled", "not-sent"].indexOf(stage) !== -1;
    }

    function create(transportReady) {
        var known = [];
        var selected = null;
        var request = null;
        var serial = 0;
        var notice = "";
        var closed = false;

        function find(id) {
            for (var n = 0; n < known.length; n += 1) {
                if (known[n].id === id) { return n; }
            }
            return -1;
        }
        function recipient() { return selected === null ? null : known[find(selected)]; }
        function busy() { return !!request && !terminal(request.stage); }
        function canIssue() {
            var row = recipient();
            return !closed && transportReady === true && !!row && row.mode === "AI" &&
                row.side === "own" && row.availability === "alive" && !busy();
        }
        function guard() {
            var row = recipient();
            if (closed) { return "Панель закрыта."; }
            if (!transportReady) { return "Не подключён переходник к серверу."; }
            if (!row) { return "Выберите адресата."; }
            if (busy()) { return "Незавершённый приказ сохраняется при смене карточки."; }
            if (row.side !== "own") { return "Чужому игроку приказ недоступен."; }
            if (row.availability !== "alive") { return "Игрок мёртв или не поддерживается."; }
            if (row.mode !== "AI") { return "Приказы этой панели доступны только в подтверждённом AI."; }
            return "";
        }

        return {
            setRecipient: function (input) {
                if (closed) { return false; }
                if (input === null) { selected = null; return true; }
                var row = copy(input, snapshotFields);
                if (closed || !row || !text(row.id, 64) || /^\s|\s$/.test(row.id) || !text(row.playerName, 64) ||
                        ["AI", "MANUAL", "INACTIVE"].indexOf(row.mode) === -1 ||
                        !integer(row.epoch) || !integer(row.revision) ||
                        ["own", "opponent"].indexOf(row.side) === -1 ||
                        ["alive", "dead", "unsupported"].indexOf(row.availability) === -1) { return false; }
                var index = find(row.id);
                if (index === -1) {
                    if (known.length === 10) { return false; }
                    known.push(row);
                } else {
                    var previous = known[index];
                    if (row.epoch < previous.epoch ||
                            (row.epoch === previous.epoch && row.revision < previous.revision)) { return false; }
                    if (row.epoch === previous.epoch && row.revision === previous.revision) {
                        for (var n = 0; n < snapshotFields.length; n += 1) {
                            var field = snapshotFields[n];
                            if (previous[field] !== row[field]) { return false; }
                        }
                    } else { known[index] = row; }
                }
                if (request && request.recipientId === row.id && row.epoch > request.epoch) {
                    request = null;
                    notice = "Новая эпоха управления; завершение прежнего приказа не подтверждено.";
                }
                selected = row.id;
                return true;
            },
            begin: function (action) {
                if (!canIssue() || ["move", "attack"].indexOf(action) === -1 || serial === 9007199254740991) { return null; }
                var row = recipient();
                serial += 1;
                request = { ticket: serial, recipientId: row.id, playerName: row.playerName,
                    epoch: row.epoch, action: action, stage: "pending", sequence: -1, reason: "" };
                notice = "";
                return { ticket: serial, recipientId: row.id, epoch: row.epoch, action: action };
            },
            report: function (ticket, input) {
                if (closed || !request || request.ticket !== ticket || terminal(request.stage)) { return false; }
                var active = request;
                var row = copy(input, reportFields);
                if (closed || request !== active || !request || request.ticket !== ticket || terminal(request.stage) ||
                        !row || !integer(row.sequence) || row.sequence <= request.sequence ||
                        ["accepted", "executing", "completed", "rejected", "cancelled"].indexOf(row.stage) === -1 ||
                        !(row.reason === null || text(row.reason, 160)) ||
                        (["rejected", "cancelled"].indexOf(row.stage) !== -1 && row.reason === null) ||
                        (request.stage === "executing" && row.stage === "accepted")) { return false; }
                request.sequence = row.sequence;
                request.stage = row.stage;
                request.reason = row.reason || "";
                return true;
            },
            expire: function (ticket) {
                if (closed || !request || request.ticket !== ticket || request.stage !== "pending") { return false; }
                request.stage = "unknown";
                request.reason = "Ответ не получен; результат неизвестен. Повтор недоступен.";
                return true;
            },
            notSent: function (ticket) {
                if (closed || !request || request.ticket !== ticket || request.stage !== "pending") { return false; }
                request.stage = "not-sent";
                request.reason = "Таймер не запущен; приказ не отправлен.";
                return true;
            },
            view: function () {
                var row = recipient();
                var stage = request ? request.stage : "idle";
                return {
                    recipientText: row ? row.playerName : "Адресат не выбран.",
                    modeText: row ? modes[row.mode] : "Режим не получен.",
                    requestRecipientText: request ? request.playerName : "Нет адресата приказа.",
                    actionText: request ? (request.action === "move" ? "К контрольной точке" : "Атаковать тестовую цель") : "Нет приказа.",
                    stageText: stages[stage], reasonText: (request && request.reason) || notice,
                    eligibilityText: guard() || "Можно отправить запрос.",
                    canIssue: canIssue(), ticket: request ? request.ticket : null,
                    stage: stage, closed: closed
                };
            },
            dispose: function () { closed = true; selected = null; known = []; request = null; notice = ""; }
        };
    }
    return { create: create };
}());
