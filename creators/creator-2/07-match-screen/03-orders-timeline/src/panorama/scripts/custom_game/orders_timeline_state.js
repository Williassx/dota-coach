/* Local presentation history for one Orders instance. Never game authority. */
var DotaCoachOrdersTimeline = (function () {
    "use strict";
    var MAX = 9007199254740991;
    var CAPACITY = 64;
    var fields = ["recipientText", "modeText", "requestRecipientText", "actionText", "stageText",
        "reasonText", "eligibilityText", "canIssue", "ticket", "stage", "closed"];
    var stages = ["idle", "pending", "unknown", "accepted", "executing", "completed",
        "rejected", "cancelled", "not-sent"];
    var labels = {
        pending: "Ожидается ответ источника.",
        unknown: "Ответ не получен; итог неизвестен.",
        accepted: "Источник сообщил о принятии; выполнение не подтверждено.",
        executing: "Источник сообщил об исполнении; эффект в игре не проверен.",
        completed: "Источник сообщил о выполнении; эффект в игре не проверен.",
        rejected: "Источник сообщил об отказе.",
        cancelled: "Источник сообщил об отмене.",
        "not-sent": "Источник сообщил: запрос не отправлен."
    };

    function integer(value) {
        return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0;
    }
    function terminal(stage) {
        return ["completed", "rejected", "cancelled", "not-sent"].indexOf(stage) !== -1;
    }
    function copy(input) {
        if (!input || typeof input !== "object" || Array.isArray(input)) { return null; }
        if (Object.getOwnPropertyNames(input).length !== fields.length ||
                (typeof Object.getOwnPropertySymbols === "function" && Object.getOwnPropertySymbols(input).length)) {
            return null;
        }
        var row = {};
        for (var i = 0; i < fields.length; i += 1) {
            var descriptor = Object.getOwnPropertyDescriptor(input, fields[i]);
            if (!descriptor || !descriptor.enumerable ||
                    !Object.prototype.hasOwnProperty.call(descriptor, "value")) { return null; }
            row[fields[i]] = descriptor.value;
        }
        for (i = 0; i < 7; i += 1) {
            var text = row[fields[i]];
            if (typeof text !== "string" || text.length > 512 || (i !== 5 && !/\S/.test(text))) { return null; }
        }
        if (typeof row.canIssue !== "boolean" || typeof row.closed !== "boolean" ||
                stages.indexOf(row.stage) === -1 ||
                (row.ticket === null ? row.stage !== "idle" :
                 !integer(row.ticket) || row.ticket < 1 || row.stage === "idle")) { return null; }
        return row;
    }
    function nextAllowed(previous, next) {
        if (terminal(previous)) { return false; }
        if (previous === next) { return true; }
        if (previous === "pending") { return next !== "idle"; }
        if (previous === "unknown") { return ["accepted", "executing", "completed", "rejected", "cancelled"].indexOf(next) !== -1; }
        if (previous === "accepted") { return ["executing", "completed", "rejected", "cancelled"].indexOf(next) !== -1; }
        return previous === "executing" && ["completed", "rejected", "cancelled"].indexOf(next) !== -1;
    }
    function cloneEvent(event) {
        var result = {};
        var keys = Object.keys(event);
        for (var i = 0; i < keys.length; i += 1) { result[keys[i]] = event[keys[i]]; }
        return result;
    }
    function response(status, added) { return { status: status, added: added || 0 }; }

    function create() {
        var events = [];
        var current = null;
        var lastTicket = 0;
        var serial = 0;
        var dropped = 0;
        var closed = false;
        var busy = false;

        function event(row, ended) {
            var unknown = !terminal(row.stage);
            return { kind: ended ? "tracking-ended" : "state", ticket: row.ticket,
                actorName: row.actorName, actionText: row.actionText,
                stage: ended ? "tracking-ended" : row.stage,
                stageText: ended ? (unknown ? "Источник перестал отслеживать приказ; итог неизвестен." :
                    "Источник перестал отслеживать приказ; последняя сообщённая стадия сохранена.") : labels[row.stage],
                reasonText: ended ? "Отслеживание завершено; это не сообщение об отмене." : row.reasonText,
                lastReportedStage: row.stage, outcomeUnknown: unknown,
                evidence: "presentation_snapshot", nativeConfirmed: false };
        }
        function append(additions) {
            for (var i = 0; i < additions.length; i += 1) {
                serial += 1;
                additions[i].eventIndex = serial;
                events.push(additions[i]);
                if (events.length > CAPACITY) { events.shift(); dropped += 1; }
            }
        }
        function dispose() {
            closed = true;
            events = [];
            current = null;
            lastTicket = 0;
            serial = 0;
            dropped = 0;
        }

        return {
            record: function (input) {
                if (closed) { return response("closed"); }
                if (busy) { return response("busy"); }
                busy = true;
                try {
                    var row = copy(input);
                    if (closed) { return response("closed"); }
                    if (!row) { return response("invalid"); }
                    if (row.closed) { dispose(); return response("closed"); }
                    var additions = [];
                    var next = null;
                    if (row.ticket === null) {
                        if (!current) { return response("unchanged"); }
                        additions.push(event(current, true));
                    } else {
                        next = { ticket: row.ticket, actorName: row.requestRecipientText,
                            actionText: row.actionText, stage: row.stage, reasonText: row.reasonText };
                        if (current && row.ticket === current.ticket) {
                            if (next.actorName !== current.actorName || next.actionText !== current.actionText) {
                                return response("invalid");
                            }
                            if (next.stage === current.stage && next.reasonText === current.reasonText) {
                                return response("unchanged");
                            }
                            if (!nextAllowed(current.stage, next.stage)) { return response("invalid"); }
                        } else {
                            if (row.ticket <= lastTicket) { return response("invalid"); }
                            if (current && !terminal(current.stage)) { additions.push(event(current, true)); }
                        }
                        additions.push(event(next, false));
                    }
                    if (serial > MAX - additions.length || dropped > MAX - additions.length) {
                        return response("invalid");
                    }
                    append(additions);
                    current = next;
                    if (next) { lastTicket = next.ticket; }
                    return response("recorded", additions.length);
                } catch (error) { return response(closed ? "closed" : "invalid"); }
                finally { busy = false; }
            },
            view: function () {
                if (busy && !closed) { return null; }
                var rows = [];
                for (var i = 0; i < events.length; i += 1) { rows.push(cloneEvent(events[i])); }
                return { events: rows, capacity: CAPACITY, droppedEvents: dropped,
                    lastTicket: lastTicket || null, closed: closed };
            },
            dispose: dispose
        };
    }
    return { create: create };
}());
