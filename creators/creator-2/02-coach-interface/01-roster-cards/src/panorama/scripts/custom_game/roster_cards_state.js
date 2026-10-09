/* Local inspection state only. No game entities, commands or server protocol. */
var DotaCoachRoster = (function () {
    "use strict";
    var fields = ["id", "playerName", "heroName", "role", "source", "side", "availability"];
    var sources = ["synthetic", "measured", "estimate", "unknown"];
    var roles = ["", "Позиция 1 — керри", "Позиция 2 — мид", "Позиция 3 — офлейн",
        "Позиция 4 — поддержка", "Позиция 5 — поддержка"];
    var origins = {
        synthetic: "Синтетический профиль",
        measured: "Измеренные признаки",
        estimate: "Оценка модели",
        unknown: "Источник профиля неизвестен"
    };

    function text(value) {
        return typeof value === "string" && value.length > 0 && value.length <= 64 && /\S/.test(value);
    }

    function copy(input) {
        if (!input || Object.prototype.toString.call(input) !== "[object Object]" ||
                Object.keys(input).length !== fields.length) { return null; }
        var result = {};
        for (var i = 0; i < fields.length; i += 1) {
            var field = fields[i];
            if (!Object.prototype.hasOwnProperty.call(input, field)) { return null; }
            result[field] = input[field];
        }
        if (!text(result.id) || /^\s|\s$/.test(result.id) || !text(result.playerName) ||
                !(result.heroName === null || text(result.heroName)) ||
                typeof result.role !== "number" || result.role % 1 !== 0 || result.role < 1 || result.role > 5 ||
                sources.indexOf(result.source) === -1 || ["own", "opponent"].indexOf(result.side) === -1 ||
                ["alive", "dead", "unsupported"].indexOf(result.availability) === -1) { return null; }
        return result;
    }

    function selectable(row) {
        return row.side === "own" && row.availability !== "unsupported" && row.source !== "unknown";
    }

    function hint(row) {
        if (row.side !== "own") { return "Другая команда — выбор недоступен."; }
        if (row.availability === "unsupported") { return "Игрок не поддерживается."; }
        if (row.source === "unknown") { return "Происхождение профиля неизвестно."; }
        return "Просмотр игрока.";
    }

    function create() {
        var rows = [];
        var selected = null;
        var closed = false;

        function find(id) {
            for (var i = 0; i < rows.length; i += 1) {
                if (rows[i].id === id) { return rows[i]; }
            }
            return null;
        }

        return {
            replace: function (input) {
                if (closed || !Array.isArray(input) || input.length > 5) { return false; }
                var count = input.length;
                var next = [];
                var ids = [];
                try {
                    for (var i = 0; i < count; i += 1) {
                        var row = copy(input[i]);
                        if (!row || ids.indexOf(row.id) !== -1) { return false; }
                        ids.push(row.id);
                        next.push(row);
                    }
                    if (input.length !== count) { return false; }
                } catch (error) { return false; }
                rows = next;
                var current = find(selected);
                if (!current || !selectable(current)) { selected = null; }
                return true;
            },
            select: function (id) {
                if (closed || typeof id !== "string") { return false; }
                var row = find(id);
                if (!row || !selectable(row)) { return false; }
                selected = id;
                return true;
            },
            clearSelection: function () {
                if (closed) { return false; }
                selected = null;
                return true;
            },
            view: function () {
                var cards = [];
                for (var i = 0; i < rows.length; i += 1) {
                    var row = rows[i];
                    cards.push({
                        id: row.id,
                        playerName: row.playerName,
                        heroName: row.heroName === null ? "Герой не назначен" : row.heroName,
                        roleText: roles[row.role],
                        sourceText: origins[row.source],
                        availabilityText: row.availability === "dead" ? "Мёртв" :
                            (row.availability === "unsupported" ? "Нет поддержки" : "В игре"),
                        selected: selected === row.id,
                        selectable: selectable(row),
                        selectionHint: hint(row)
                    });
                }
                return { cards: cards, selectedId: selected, closed: closed };
            },
            dispose: function () {
                closed = true;
                rows = [];
                selected = null;
            }
        };
    }

    return { create: create };
}());
