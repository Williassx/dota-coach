/* Local coach intentions only. Does not execute plans or calculate morale. */
var DotaCoachPreparation = (function () {
    "use strict";
    var MAX = 9007199254740991;
    function integer(value) { return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0; }
    function text(value, max, identifier) {
        return typeof value === "string" && value.length > 0 && value.length <= max && /\S/.test(value) &&
            (!identifier || !/^\s|\s$/.test(value));
    }
    function copy(value) { return value === null ? null : JSON.parse(JSON.stringify(value)); }
    function find(id, rows) {
        for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
        return null;
    }
    function same(left, right) { return JSON.stringify(left) === JSON.stringify(right); }
    function choiceDraft(row) { return row ? { id: row.id, optionVersion: row.optionVersion } : null; }
    function create() {
        var closed = false, generation = 0, highWater = -1, revision = null, preparationRevision = 0;
        var status = "empty", message = "Предложения подготовки не получены.";
        var lineup = null, plans = [], talks = [], plan = null, talk = null;
        var resetMessage = null;
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if ((plan || talk) && preparationRevision < MAX) { preparationRevision += 1; }
            lineup = null; plans = []; talks = []; plan = null; talk = null; revision = null; resetMessage = null;
            status = "disposed"; message = "Черновик подготовки закрыт.";
        }
        function bump() {
            if (preparationRevision >= MAX) { dispose(); return false; }
            preparationRevision += 1; return true;
        }
        function current(version) { return !closed && generation === version; }
        function guard(version) { if (!current(version)) { throw new Error("Stale preparation"); } }
        function exact(input, fields, version) {
            guard(version);
            if (!input || typeof input !== "object" || Array.isArray(input)) { throw new Error("Invalid object"); }
            var names = Object.getOwnPropertyNames(input); guard(version);
            if (!same(names.sort(), fields.slice().sort())) { throw new Error("Invalid schema"); }
        }
        function take(input, fields, version) {
            exact(input, fields, version);
            var row = {};
            for (var n = 0; n < fields.length; n += 1) { row[fields[n]] = input[fields[n]]; guard(version); }
            exact(input, fields, version); return row;
        }
        function array(input, min, max, version, decode) {
            guard(version);
            if (!Array.isArray(input)) { throw new Error("Invalid array"); }
            var length = input.length; guard(version);
            if (!integer(length) || length < min || length > max) { throw new Error("Invalid size"); }
            var rows = [];
            for (var n = 0; n < length; n += 1) {
                var value = input[n]; guard(version); rows.push(decode(value)); guard(version);
            }
            var finalLength = input.length; guard(version);
            if (finalLength !== length) { throw new Error("Array changed"); }
            return rows;
        }
        function decodeTeam(input, version) {
            var row = take(input, ["catalogRevision", "draftRevision", "complete", "serverConfirmed", "players"], version);
            if (!integer(row.catalogRevision) || !integer(row.draftRevision) || row.complete !== true || row.serverConfirmed !== false) {
                throw new Error("Invalid local team");
            }
            var ids = [];
            row.players = array(row.players, 5, 5, version, function (player) {
                var item = take(player, ["id", "profileVersion"], version);
                if (!text(item.id, 64, true) || !text(item.profileVersion, 64, true) || ids.indexOf(item.id) !== -1) {
                    throw new Error("Invalid player");
                }
                ids.push(item.id); return item;
            });
            return row;
        }
        function decodeLineup(input, version) {
            var row = take(input, ["revision", "assignmentRevision", "team", "assignments", "complete", "serverConfirmed"], version);
            if (!integer(row.revision) || !integer(row.assignmentRevision) || row.complete !== true || row.serverConfirmed !== false) {
                throw new Error("Incomplete local lineup");
            }
            row.team = decodeTeam(row.team, version);
            var ids = [], heroes = [], roles = [];
            row.assignments = array(row.assignments, 5, 5, version, function (assignment) {
                var item = take(assignment, ["id", "profileVersion", "heroId", "role"], version);
                var player = find(item.id, row.team.players);
                if (!player || player.profileVersion !== item.profileVersion || ids.indexOf(item.id) !== -1 ||
                        !text(item.heroId, 64, true) || heroes.indexOf(item.heroId) !== -1 || !integer(item.role) ||
                        item.role < 1 || item.role > 5 || roles.indexOf(item.role) !== -1) { throw new Error("Invalid assignment"); }
                ids.push(item.id); heroes.push(item.heroId); roles.push(item.role); return item;
            });
            row.assignments = row.team.players.map(function (player) { return find(player.id, row.assignments); });
            return row;
        }
        function decodeOptions(input, version) {
            var ids = [];
            return array(input, 0, 8, version, function (option) {
                var row = take(option, ["id", "optionVersion", "label", "intent"], version);
                if (!text(row.id, 64, true) || !text(row.optionVersion, 64, true) || !text(row.label, 80, false) ||
                        !text(row.intent, 240, false) || ids.indexOf(row.id) !== -1) { throw new Error("Invalid option"); }
                ids.push(row.id); return row;
            });
        }
        function invalidate(version) {
            if (!current(version)) { return false; }
            if ((plan || talk) && !bump()) { return false; }
            generation += 1; revision = null; lineup = null; plans = []; talks = []; plan = null; talk = null;
            resetMessage = "Проекция некорректна; подготовка снята."; status = "invalid"; message = resetMessage;
            return false;
        }
        function normalMessage() {
            var missing = [];
            if (!plans.length) { missing.push("нет вариантов тактики"); }
            if (!talks.length) { missing.push("нет вариантов разговора"); }
            if (missing.length) { message = (resetMessage ? resetMessage + " " : "") + "Источник: " + missing.join("; ") + ". Полнота требует плана и варианта разговора."; return; }
            if (resetMessage) { message = resetMessage; return; }
            message = plan && talk ? "План и разговор выбраны локально; исполнение сервером не подтверждено." :
                "Для локальной полноты выберите план и вариант разговора; эффект сервером не подтверждён.";
        }
        function retained(previous, options) {
            var row = previous ? find(previous.id, options) : null;
            return row && same(previous, row) ? row : null;
        }
        function update(input) {
            if (closed) { return false; }
            var entry = generation, nextRevision;
            try { nextRevision = input && input.revision; } catch (error) { return invalidate(entry); }
            if (!current(entry)) { return false; }
            if (!integer(nextRevision)) { return invalidate(entry); }
            if (nextRevision <= highWater) { return false; }
            highWater = nextRevision;
            var recovering = status === "invalid";
            var version = ++generation;
            status = "staging"; message = "Подготовка обновляется; выбор недоступен.";
            try {
                exact(input, ["revision", "lineup", "plans", "talks"], version);
                var lineupInput = input.lineup; guard(version);
                var newLineup = decodeLineup(lineupInput, version);
                var plansInput = input.plans; guard(version);
                var newPlans = decodeOptions(plansInput, version);
                var talksInput = input.talks; guard(version);
                var newTalks = decodeOptions(talksInput, version);
                exact(input, ["revision", "lineup", "plans", "talks"], version);
                var contextChanged = lineup !== null && !same(lineup, newLineup);
                var nextPlan = contextChanged ? null : retained(plan, newPlans);
                var nextTalk = contextChanged ? null : retained(talk, newTalks);
                var removed = (plan && !nextPlan) || (talk && !nextTalk);
                guard(version);
                if (removed && !bump()) { return false; }
                lineup = newLineup; plans = newPlans; talks = newTalks; plan = nextPlan; talk = nextTalk;
                revision = nextRevision; status = "ready";
                if (removed) { resetMessage = contextChanged ? "Состав изменился; подготовка снята. Выберите заново." :
                    "Выбранный вариант изменился или исчез; соответствующий выбор снят."; }
                if (recovering && !removed) { resetMessage = "Прежняя проекция была некорректна; подготовка снята. Новые варианты загружены."; }
                normalMessage(); return true;
            } catch (error) { return invalidate(version); }
        }
        function writable() { return !closed && status === "ready"; }
        function choose(group, id) {
            if (!writable()) { return false; }
            var options = group === "plan" ? plans : talks, old = group === "plan" ? plan : talk;
            var row = typeof id === "string" ? find(id, options) : null;
            if (!row || (old && old.id === row.id)) { normalMessage(); return false; }
            if (!bump()) { return false; }
            generation += 1;
            if (group === "plan") { plan = row; } else { talk = row; }
            resetMessage = null; normalMessage(); return true;
        }
        function remove(group) {
            if (!writable()) { return false; }
            var old = group === "plan" ? plan : talk;
            if (!old) { normalMessage(); return false; }
            if (!bump()) { return false; }
            generation += 1;
            if (group === "plan") { plan = null; } else { talk = null; }
            resetMessage = null; normalMessage(); return true;
        }
        function clear() {
            if (!writable()) { return false; }
            if (plan || talk) {
                if (!bump()) { return false; }
                generation += 1; plan = null; talk = null; resetMessage = null;
            }
            normalMessage(); return true;
        }
        function view() {
            var visible = status === "ready";
            return { status: status, message: message, lineup: visible ? copy(lineup) : null,
                plans: visible ? plans.map(copy) : [], talks: visible ? talks.map(copy) : [],
                plan: visible ? copy(plan) : null, talk: visible ? copy(talk) : null, complete: visible && !!plan && !!talk,
                warnings: visible ? ["Подготовка локальная; исполнение и эффект сервером не подтверждены.",
                    "Мораль и доверие — игровые допущения; это не сведения о характере реального человека."] : [] };
        }
        function draft() {
            if (!writable()) { return null; }
            return { revision: revision, preparationRevision: preparationRevision, lineup: copy(lineup),
                plan: choiceDraft(plan), talk: choiceDraft(talk), complete: !!plan && !!talk, serverConfirmed: false };
        }
        return { update: update, choosePlan: function (id) { return choose("plan", id); },
            chooseTalk: function (id) { return choose("talk", id); }, removePlan: function () { return remove("plan"); },
            removeTalk: function () { return remove("talk"); }, clear: clear, view: view, draft: draft,
            dispose: dispose, isDisposed: function () { return closed; } };
    }
    return { create: create };
}());
