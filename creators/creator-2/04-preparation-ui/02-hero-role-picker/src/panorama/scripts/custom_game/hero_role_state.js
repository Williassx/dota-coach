/* Private, unconfirmed hero/position proposals. No native, server or persistence. */
var DotaCoachHeroRoles = (function () {
    "use strict";
    var MAX = 9007199254740991;
    function integer(value) { return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0; }
    function text(value, max, identifier) {
        return typeof value === "string" && value.length > 0 && value.length <= max && /\S/.test(value) &&
            (!identifier || !/^\s|\s$/.test(value));
    }
    function cloneChoice(row) { return { heroId: row.heroId, heroName: row.heroName, role: row.role, coverage: row.coverage }; }
    function cloneProfile(row) { return { id: row.id, profileVersion: row.profileVersion, playerName: row.playerName,
        kind: row.kind, sourceLabel: row.sourceLabel, choices: row.choices.map(cloneChoice) }; }
    function cloneTeam(row) { return { catalogRevision: row.catalogRevision, draftRevision: row.draftRevision,
        complete: true, serverConfirmed: false, players: row.players.map(function (player) {
            return { id: player.id, profileVersion: player.profileVersion };
        }) }; }
    function cloneAssignment(row, named) {
        var copy = { id: row.id, profileVersion: row.profileVersion, heroId: row.heroId, role: row.role };
        if (named) { copy.heroName = row.heroName; }
        return copy;
    }
    function create() {
        var closed = false, generation = 0, highWater = -1, committedRevision = null, assignmentRevision = 0;
        var status = "empty", message = "Предложения героев и позиций не получены.";
        var team = null, profiles = [], assignments = [];
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1;
            if (assignments.length && assignmentRevision < MAX) { assignmentRevision += 1; }
            team = null; profiles = []; assignments = []; committedRevision = null;
            status = "disposed"; message = "Черновик назначений закрыт.";
        }
        function bump() {
            if (assignmentRevision >= MAX) { dispose(); return false; }
            assignmentRevision += 1; return true;
        }
        function current(version) { return !closed && generation === version; }
        function guard(version) { if (!current(version)) { throw new Error("Stale projection"); } }
        function exact(input, fields, version) {
            guard(version);
            if (!input || typeof input !== "object" || Array.isArray(input)) { throw new Error("Invalid object"); }
            var names = Object.getOwnPropertyNames(input);
            guard(version);
            if (JSON.stringify(names.sort()) !== JSON.stringify(fields.slice().sort())) { throw new Error("Invalid schema"); }
        }
        function take(input, fields, version) {
            exact(input, fields, version);
            var row = {};
            for (var n = 0; n < fields.length; n += 1) {
                row[fields[n]] = input[fields[n]];
                guard(version);
            }
            exact(input, fields, version);
            return row;
        }
        function array(input, min, max, version, decode) {
            guard(version);
            if (!Array.isArray(input)) { throw new Error("Invalid array"); }
            var length = input.length;
            guard(version);
            if (!integer(length) || length < min || length > max) { throw new Error("Invalid array size"); }
            var rows = [];
            for (var n = 0; n < length; n += 1) {
                var value = input[n]; guard(version);
                rows.push(decode(value)); guard(version);
            }
            var finalLength = input.length; guard(version);
            if (finalLength !== length) { throw new Error("Array changed"); }
            return rows;
        }
        function find(id, rows) {
            for (var n = 0; n < rows.length; n += 1) { if (rows[n].id === id) { return rows[n]; } }
            return null;
        }
        function choice(profile, heroId, role) {
            for (var n = 0; profile && n < profile.choices.length; n += 1) {
                var row = profile.choices[n];
                if (row.heroId === heroId && row.role === role) { return row; }
            }
            return null;
        }
        function decodeTeam(input, version) {
            var row = take(input, ["catalogRevision", "draftRevision", "complete", "serverConfirmed", "players"], version);
            if (!integer(row.catalogRevision) || !integer(row.draftRevision) || row.complete !== true || row.serverConfirmed !== false) {
                throw new Error("Invalid local team draft");
            }
            var ids = [];
            row.players = array(row.players, 5, 5, version, function (player) {
                var item = take(player, ["id", "profileVersion"], version);
                if (!text(item.id, 64, true) || !text(item.profileVersion, 64, true) || ids.indexOf(item.id) !== -1) {
                    throw new Error("Invalid team player");
                }
                ids.push(item.id); return item;
            });
            return row;
        }
        function decodeProfiles(input, decodedTeam, version) {
            var ids = [], heroIds = [], heroNames = [];
            var decoded = array(input, 5, 5, version, function (profile) {
                var row = take(profile, ["id", "profileVersion", "playerName", "kind", "sourceLabel", "choices"], version);
                var player = find(row.id, decodedTeam.players);
                if (!player || player.profileVersion !== row.profileVersion || ids.indexOf(row.id) !== -1 ||
                        !text(row.playerName, 64, false) || !text(row.sourceLabel, 160, false) ||
                        ["synthetic", "player_model"].indexOf(row.kind) === -1) { throw new Error("Mismatched profile proposal"); }
                ids.push(row.id);
                var pairs = [];
                row.choices = array(row.choices, 0, 32, version, function (proposal) {
                    var item = take(proposal, ["heroId", "heroName", "role", "coverage"], version);
                    var pair = JSON.stringify([item.heroId, item.role]);
                    if (!text(item.heroId, 64, true) || !text(item.heroName, 64, false) || !integer(item.role) ||
                            item.role < 1 || item.role > 5 || ["unknown", "limited", "reported"].indexOf(item.coverage) === -1 ||
                            pairs.indexOf(pair) !== -1) { throw new Error("Invalid choice proposal"); }
                    pairs.push(pair);
                    var hero = heroIds.indexOf(item.heroId);
                    if (hero !== -1 && heroNames[hero] !== item.heroName) { throw new Error("Conflicting hero name"); }
                    if (hero === -1) { heroIds.push(item.heroId); heroNames.push(item.heroName); }
                    return item;
                });
                return row;
            });
            return decodedTeam.players.map(function (player) { return find(player.id, decoded); });
        }
        function invalidate(version) {
            if (!current(version)) { return false; }
            if (assignments.length && !bump()) { return false; }
            generation += 1; team = null; profiles = []; assignments = []; committedRevision = null;
            status = "invalid"; message = "Проекция некорректна; назначения сняты.";
            return false;
        }
        function normalMessage() {
            var missing = 0;
            for (var n = 0; n < profiles.length; n += 1) { if (!profiles[n].choices.length) { missing += 1; } }
            message = missing ? "Для " + missing + " игроков нет предложенных сочетаний; назначения не подтверждены сервером." :
                (assignments.length === 5 ? "Пять локальных назначений; совместимость не подтверждена сервером." :
                    "Предложения загружены; назначения не подтверждены сервером.");
        }
        function makeAssignment(profile, proposal) {
            return { id: profile.id, profileVersion: profile.profileVersion, heroId: proposal.heroId,
                heroName: proposal.heroName, role: proposal.role, coverage: proposal.coverage };
        }
        function update(input) {
            if (closed) { return false; }
            var entry = generation, revision;
            try { revision = input && input.revision; } catch (error) { return invalidate(entry); }
            if (!current(entry)) { return false; }
            if (!integer(revision)) { return invalidate(entry); }
            if (revision <= highWater) { return false; }
            highWater = revision;
            var version = ++generation;
            status = "invalid"; message = "Предложения обновляются; выбор недоступен.";
            try {
                exact(input, ["revision", "team", "proposals"], version);
                var teamInput = input.team; guard(version);
                var decodedTeam = decodeTeam(teamInput, version);
                var proposalInput = input.proposals; guard(version);
                var decoded = decodeProfiles(proposalInput, decodedTeam, version);
                exact(input, ["revision", "team", "proposals"], version);
                var retained = [];
                for (var n = 0; n < assignments.length; n += 1) {
                    var previous = assignments[n], profile = find(previous.id, decoded);
                    var proposal = profile && profile.profileVersion === previous.profileVersion ?
                        choice(profile, previous.heroId, previous.role) : null;
                    if (proposal) { retained.push(makeAssignment(profile, proposal)); }
                }
                guard(version);
                var changed = retained.length !== assignments.length;
                if (changed && !bump()) { return false; }
                team = decodedTeam; profiles = decoded; assignments = retained; committedRevision = revision;
                status = "ready"; normalMessage();
                if (changed) { message = "Профиль или предложение изменилось; прежнее назначение снято. Выберите заново."; }
                return true;
            } catch (error) { return invalidate(version); }
        }
        function writable() {
            if (closed) { return false; }
            if (status !== "ready") {
                if (status === "empty") { message = "Предложения не получены; назначение невозможно."; }
                return false;
            }
            return true;
        }
        function assign(id, heroId, role) {
            if (!writable()) { return false; }
            var profile = typeof id === "string" ? find(id, profiles) : null;
            if (!profile) { message = "Игрок отсутствует в локальном составе."; return false; }
            var proposal = typeof heroId === "string" && integer(role) ? choice(profile, heroId, role) : null;
            if (!proposal) { message = "Для игрока нет такого предложенного сочетания."; return false; }
            var old = find(id, assignments);
            if (old && old.heroId === heroId && old.role === role) { message = "Назначение уже выбрано."; return false; }
            for (var n = 0; n < assignments.length; n += 1) {
                if (assignments[n].id === id) { continue; }
                if (assignments[n].heroId === heroId) { message = "Этот герой уже занят в локальном черновике."; return false; }
                if (assignments[n].role === role) { message = "Эта позиция уже занята в локальном черновике."; return false; }
            }
            if (!bump()) { return false; }
            generation += 1;
            if (old) { assignments.splice(assignments.indexOf(old), 1); }
            assignments.push(makeAssignment(profile, proposal)); normalMessage(); return true;
        }
        function remove(id) {
            if (!writable()) { return false; }
            var old = typeof id === "string" ? find(id, assignments) : null;
            if (!old) { message = "Назначение игрока не выбрано."; return false; }
            if (!bump()) { return false; }
            generation += 1; assignments.splice(assignments.indexOf(old), 1); normalMessage(); return true;
        }
        function clear() {
            if (!writable()) { return false; }
            if (assignments.length) {
                if (!bump()) { return false; }
                generation += 1; assignments = [];
            }
            normalMessage(); return true;
        }
        function ordered() {
            var rows = [];
            for (var n = 0; team && n < team.players.length; n += 1) {
                var row = find(team.players[n].id, assignments);
                if (row) { rows.push(row); }
            }
            return rows;
        }
        function view() {
            var visible = status === "ready", rows = visible ? ordered() : [], warnings = [];
            for (var n = 0; n < rows.length; n += 1) {
                var row = rows[n], profile = find(row.id, profiles);
                warnings.push({ id: row.id, text: profile.kind === "synthetic" ? "Используется синтетический профиль." :
                    "Сходство модели игрока здесь не проверено." });
                warnings.push({ id: row.id, text: "Сочетание предложено источником; совместимость модели сервером не подтверждена." });
                warnings.push({ id: row.id, text: row.coverage === "unknown" ? "Охват данных неизвестен." :
                    (row.coverage === "limited" ? "Источник сообщает ограниченный охват." :
                        "Охват указан источником; роль, герой и патч здесь не проверены.") });
            }
            return { status: status, message: message, players: visible ? profiles.map(cloneProfile) : [],
                assignments: rows.map(function (row) { return cloneAssignment(row, true); }), complete: rows.length === 5, warnings: warnings };
        }
        function draft() {
            if (closed || status !== "ready") { return null; }
            var rows = ordered();
            return { revision: committedRevision, assignmentRevision: assignmentRevision, team: cloneTeam(team),
                assignments: rows.map(function (row) { return cloneAssignment(row, false); }), complete: rows.length === 5, serverConfirmed: false };
        }
        return { update: update, assign: assign, remove: remove, clear: clear, view: view, draft: draft,
            dispose: dispose, isDisposed: function () { return closed; } };
    }
    return { create: create };
}());
