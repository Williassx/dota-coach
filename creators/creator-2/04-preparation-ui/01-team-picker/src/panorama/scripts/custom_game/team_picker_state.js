/* Private local draft projection. No server confirmation, persistence or native work. */
var DotaCoachTeamPicker = (function () {
    "use strict";
    var MAX = 9007199254740991;
    var FIELDS = ["id", "playerName", "profileVersion", "kind", "sourceLabel", "coverage"];
    function integer(value) { return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0; }
    function text(value, max, identifier) {
        return typeof value === "string" && value.length > 0 && value.length <= max && /\S/.test(value) &&
            (!identifier || !/^\s|\s$/.test(value));
    }
    function shape(input, fields) {
        return !!input && typeof input === "object" && !Array.isArray(input) &&
            JSON.stringify(Object.getOwnPropertyNames(input).sort()) === JSON.stringify(fields.slice().sort());
    }
    function clone(row) {
        var copy = {};
        for (var n = 0; n < FIELDS.length; n += 1) { copy[FIELDS[n]] = row[FIELDS[n]]; }
        return copy;
    }
    function decode(input) {
        if (!shape(input, FIELDS)) { throw new Error("Invalid profile schema"); }
        var row = clone(input);
        if (!shape(input, FIELDS) || !text(row.id, 64, true) || !text(row.playerName, 64, false) ||
                !text(row.profileVersion, 64, true) || !text(row.sourceLabel, 160, false) ||
                ["synthetic", "player_model"].indexOf(row.kind) === -1 ||
                ["unknown", "limited", "reported"].indexOf(row.coverage) === -1) {
            throw new Error("Invalid profile projection");
        }
        return row;
    }
    function create() {
        var closed = false, generation = 0, highWater = -1, catalogRevision = null, draftRevision = 0;
        var status = "empty", message = "Каталог игроков не получен.";
        var profiles = [], choices = [];
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if (choices.length && draftRevision < MAX) { draftRevision += 1; }
            profiles = []; choices = []; catalogRevision = null;
            status = "disposed"; message = "Выбор состава закрыт.";
        }
        function bump() {
            if (draftRevision >= MAX) { dispose(); return false; }
            draftRevision += 1;
            return true;
        }
        function current(version) { return !closed && version === generation; }
        function normalMessage() {
            message = choices.length === 5 ?
                "Выбрано 5 разных записей: локальный черновик, не подтверждён сервером." :
                "Каталог загружен; состав не подтверждён.";
        }
        function invalidate(version) {
            if (!current(version)) { return false; }
            if (choices.length && !bump()) { return false; }
            generation += 1;
            profiles = []; choices = []; catalogRevision = null;
            status = "invalid"; message = "Каталог некорректен; черновик снят.";
            return false;
        }
        function find(id, rows) {
            for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
            return null;
        }
        function update(input) {
            if (closed) { return false; }
            var entry = generation, revision;
            try { revision = input && input.revision; }
            catch (error) { return invalidate(entry); }
            if (!current(entry)) { return false; }
            if (!integer(revision)) { return invalidate(entry); }
            if (revision <= highWater) { return false; }
            highWater = revision;
            var version = ++generation;
            status = "invalid"; message = "Каталог обновляется; выбор недоступен.";
            try {
                if (!shape(input, ["revision", "profiles"])) { throw new Error("Invalid snapshot schema"); }
                var rows = input.profiles;
                if (!current(version)) { return false; }
                if (!Array.isArray(rows)) { throw new Error("Invalid catalog array"); }
                var length = rows.length, decoded = [], ids = [];
                if (!current(version)) { return false; }
                if (!integer(length) || length > 64) { throw new Error("Invalid catalog size"); }
                for (var n = 0; n < length; n += 1) {
                    var row = decode(rows[n]);
                    if (!current(version)) { return false; }
                    if (ids.indexOf(row.id) !== -1) { throw new Error("Duplicate player id"); }
                    ids.push(row.id); decoded.push(row);
                }
                if (rows.length !== length || !shape(input, ["revision", "profiles"])) {
                    throw new Error("Catalog shape changed");
                }
                if (!current(version)) { return false; }
                var retained = [];
                for (var c = 0; c < choices.length; c += 1) {
                    var replacement = find(choices[c].id, decoded);
                    if (replacement && replacement.profileVersion === choices[c].profileVersion) { retained.push(replacement); }
                }
                var changed = retained.length !== choices.length;
                if (changed && !bump()) { return false; }
                profiles = decoded; choices = retained; catalogRevision = revision;
                status = "ready"; normalMessage();
                if (changed) { message = "Каталог обновлён; прежний выбор изменён или исчез и снят. Выберите заново."; }
                return true;
            } catch (error) { return invalidate(version); }
        }
        function writable() {
            if (closed) { return false; }
            if (status !== "ready") {
                if (status === "empty") { message = "Каталог недоступен; выбор не изменён."; }
                return false;
            }
            return true;
        }
        function choose(id) {
            if (!writable()) { return false; }
            var row = typeof id === "string" ? find(id, profiles) : null;
            if (!row) { message = "Запись отсутствует в каталоге."; return false; }
            if (find(id, choices)) { message = "Запись уже выбрана."; return false; }
            if (choices.length === 5) { message = "В черновике уже пять записей."; return false; }
            if (!bump()) { return false; }
            generation += 1; choices.push(row); normalMessage(); return true;
        }
        function remove(id) {
            if (!writable()) { return false; }
            var row = typeof id === "string" ? find(id, choices) : null;
            if (!row) { message = "Запись не выбрана."; return false; }
            if (!bump()) { return false; }
            generation += 1; choices.splice(choices.indexOf(row), 1); normalMessage(); return true;
        }
        function clear() {
            if (!writable()) { return false; }
            if (choices.length) {
                if (!bump()) { return false; }
                generation += 1; choices = [];
            }
            normalMessage(); return true;
        }
        function view() {
            var visible = status === "ready";
            var selected = visible ? choices.map(clone) : [], warnings = [];
            for (var n = 0; n < selected.length; n += 1) {
                var row = selected[n];
                warnings.push({ id: row.id, text: row.kind === "synthetic" ?
                    "Используется синтетический профиль." : "Сходство модели игрока здесь не проверено." });
                warnings.push({ id: row.id, text: row.coverage === "unknown" ? "Охват данных неизвестен." :
                    (row.coverage === "limited" ? "Источник сообщает ограниченный охват." :
                        "Охват указан источником; роль, герой и патч здесь не проверены.") });
            }
            return { status: status, message: message, profiles: visible ? profiles.map(clone) : [],
                selected: selected, count: selected.length, complete: selected.length === 5, warnings: warnings };
        }
        function draft() {
            if (closed || status !== "ready") { return null; }
            return { catalogRevision: catalogRevision, draftRevision: draftRevision, complete: choices.length === 5,
                serverConfirmed: false, players: choices.map(function (row) {
                    return { id: row.id, profileVersion: row.profileVersion };
                }) };
        }
        return { update: update, choose: choose, remove: remove, clear: clear, view: view, draft: draft,
            dispose: dispose, isDisposed: function () { return closed; } };
    }
    return { create: create };
}());
