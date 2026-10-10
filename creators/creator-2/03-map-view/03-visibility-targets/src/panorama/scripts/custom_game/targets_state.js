/* Private UI observation projection. No native reads, positions or action authority. */
var DotaCoachTargets = (function () {
    "use strict";
    function integer(value, max) {
        return typeof value === "number" && value >= 0 && value <= max && value % 1 === 0;
    }
    function text(value) {
        return typeof value === "string" && value.length > 0 && value.length <= 64 && /\S/.test(value);
    }
    function object(value) {
        return value && Object.prototype.toString.call(value) === "[object Object]";
    }
    function copy(value, fields, expectedVisibility) {
        if (!object(value) || Object.getOwnPropertyNames(value).length !== fields.length) { return null; }
        var row = {};
        for (var n = 0; n < fields.length; n += 1) {
            if (!Object.prototype.hasOwnProperty.call(value, fields[n])) { return null; }
            row[fields[n]] = value[fields[n]];
            if (fields[n] === "visibility" && row.visibility !== expectedVisibility) { return null; }
        }
        if (Object.getOwnPropertyNames(value).length !== fields.length) { return null; }
        return row;
    }
    function targetCopy(row) {
        return { id: row.id, label: row.label, team: row.team, kind: row.kind,
            alive: row.alive, entityIndex: row.entityIndex };
    }
    function decode(input, expectedRevision) {
        var header = copy(input, ["revision", "targets"]);
        if (!header || header.revision !== expectedRevision || !Array.isArray(header.targets)) { return null; }
        var count = header.targets.length;
        if (!integer(count, 32)) { return null; }
        var rows = [], ids = Object.create(null);
        for (var n = 0; n < count; n += 1) {
            var source = header.targets[n];
            if (!object(source)) { return null; }
            var visibility = source.visibility;
            var visible = visibility === "visible";
            if (!visible && visibility !== "hidden" && visibility !== "gone" && visibility !== "unknown") { return null; }
            var row = copy(source, visible ?
                ["id", "visibility", "label", "team", "kind", "alive", "entityIndex"] : ["id", "visibility"], visibility);
            if (!row || row.visibility !== visibility || !text(row.id) || /^\s|\s$/.test(row.id) || ids[row.id]) { return null; }
            if (visible && (!text(row.label) || (row.team !== "ally" && row.team !== "enemy") ||
                    (row.kind !== "hero" && row.kind !== "creep") || typeof row.alive !== "boolean" ||
                    !integer(row.entityIndex, 2147483647))) { return null; }
            ids[row.id] = true;
            rows.push(row);
        }
        return header.targets.length === count ? rows : null;
    }
    function create(options) {
        var config = copy(options, ["now", "maxAgeMs"]);
        if (!config || typeof config.now !== "function" || !integer(config.maxAgeMs, 60000) || config.maxAgeMs < 1) {
            throw new Error("Explicit monotonic clock and bounded maxAgeMs required");
        }
        var rows = [], selected = null, revision = -1, received = null, lastTime = null;
        var status = "empty", message = "Выберите цель на карте.";
        var generation = 0, closed = false;
        function current(version) { return !closed && generation === version; }
        function clear(nextStatus, nextMessage) {
            generation += 1;
            rows = []; selected = null; received = null;
            status = nextStatus; message = nextMessage;
        }
        function clock(version) {
            var time;
            try { time = config.now(); }
            catch (error) {
                if (current(version)) { clear("invalid", "Время наблюдения недоступно; выберите цель после обновления."); }
                return null;
            }
            if (!current(version)) { return null; }
            if (typeof time !== "number" || !isFinite(time) || time < 0 || time > 9007199254740991 ||
                    (lastTime !== null && time < lastTime)) {
                clear("invalid", "Время наблюдения неверно; выберите цель после обновления.");
                return null;
            }
            lastTime = time;
            return time;
        }
        function expire(time) {
            if (received !== null && time - received >= config.maxAgeMs) {
                clear("stale", "Наблюдение устарело; дождитесь обновления и выберите цель.");
            }
        }
        function find(id) {
            for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
            return null;
        }
        function lose(row) {
            selected = null;
            status = "unavailable";
            message = !row || row.visibility === "gone" ? "Цель больше не наблюдается; выберите другую." :
                row.visibility === "hidden" ? "Цель больше не видна; выберите другую." :
                "Доступность цели неизвестна; выберите другую.";
        }
        function describe(row) {
            status = row.alive ? "ready" : "dead";
            message = row.alive ? "Цель видна; исполнение действий не проверено." : "Цель наблюдается мёртвой.";
        }
        function output() {
            var row = selected === null ? null : find(selected);
            return { status: status, message: message,
                target: row && row.visibility === "visible" ? targetCopy(row) : null };
        }
        return {
            update: function (input) {
                if (closed) { return false; }
                var version = ++generation;
                var time = clock(version);
                if (time === null) { return false; }
                expire(time); version = generation;
                var nextRevision, nextRows;
                try {
                    nextRevision = object(input) ? input.revision : null;
                    if (!current(version)) { return false; }
                    if (!integer(nextRevision, 9007199254740991)) {
                        clear("invalid", "Наблюдение недоступно; дождитесь нового обновления."); return false;
                    }
                    if (nextRevision <= revision) { return false; }
                    revision = nextRevision;
                    nextRows = decode(input, nextRevision);
                } catch (error) { nextRows = null; }
                if (!current(version)) { return false; }
                if (nextRows === null) {
                    clear("invalid", "Наблюдение недоступно; дождитесь нового обновления."); return false;
                }
                rows = nextRows; received = time;
                if (selected !== null) {
                    var row = find(selected);
                    if (!row || row.visibility !== "visible") { lose(row); }
                    else { describe(row); }
                } else if (status !== "unavailable") {
                    status = "empty"; message = "Наблюдение обновлено; выберите цель на карте.";
                }
                return true;
            },
            select: function (id) {
                if (closed) { return false; }
                var time = clock(++generation);
                if (time === null) { return false; }
                expire(time);
                if (status === "stale" || status === "invalid") { return false; }
                if (id === null) { selected = null; status = "empty"; message = "Выберите цель на карте."; return true; }
                if (!text(id) || /^\s|\s$/.test(id)) { return false; }
                var row = find(id);
                if (!row || row.visibility !== "visible") {
                    selected = null; status = "unavailable"; message = "Цель недоступна для просмотра; выберите другую.";
                    return false;
                }
                selected = id; describe(row); return true;
            },
            view: function () {
                if (closed) { return { status: "disposed", message: "Просмотр цели закрыт.", target: null }; }
                var time = clock(generation);
                if (time !== null) { expire(time); }
                if (closed) { return { status: "disposed", message: "Просмотр цели закрыт.", target: null }; }
                return output();
            },
            dispose: function () {
                if (closed) { return; }
                clear("disposed", "Просмотр цели закрыт."); closed = true;
            },
            isDisposed: function () { return closed; }
        };
    }
    return { create: create };
}());
