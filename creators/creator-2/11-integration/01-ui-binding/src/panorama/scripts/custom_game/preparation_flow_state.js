/* Three private local preparation models; no panels, server or match start. */
var DotaCoachPreparationFlow = (function () {
    "use strict";
    function same(left, right) { return JSON.stringify(left) === JSON.stringify(right); }
    function create() {
        var team = DotaCoachTeamPicker.create(), heroes = DotaCoachHeroRoles.create(), preparation = DotaCoachPreparation.create();
        var closed = false, busy = false, generation = 0, lastTeam = null, lastHeroes = null, notice = null;
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1; busy = false;
            team.dispose(); heroes.dispose(); preparation.dispose(); lastTeam = null; lastHeroes = null; notice = null;
        }
        function available() {
            if (closed) { return false; }
            if (team.isDisposed() || heroes.isDisposed() || preparation.isDisposed()) { dispose(); return false; }
            return true;
        }
        function current(version) { return available() && generation === version; }
        function synchronize(accepted) {
            var nextTeam = team.draft(), marked = false;
            if (!same(lastTeam, nextTeam)) {
                var hadDownstream = heroes.draft() !== null || preparation.draft() !== null;
                heroes.reset(); preparation.reset();
                if (hadDownstream) { notice = "Состав изменился; предложения героев и подготовка сняты."; marked = true; }
                lastTeam = nextTeam;
            }
            var nextHeroes = heroes.draft();
            if (!same(lastHeroes, nextHeroes)) {
                var hadPreparation = preparation.draft() !== null;
                preparation.reset();
                if (hadPreparation) { notice = "Назначения изменились; варианты подготовки сняты."; marked = true; }
                lastHeroes = nextHeroes;
            }
            if (!marked && accepted) { notice = null; }
            return available();
        }
        function run(target, method, args, kind) {
            if (!available() || busy) { return false; }
            var upstream = kind === "heroes" ? team.draft() : (kind === "preparation" ? heroes.draft() : null);
            if ((kind === "heroes" || kind === "preparation") && (!upstream || !upstream.complete)) { return false; }
            var version = ++generation;
            busy = true;
            try {
                var accepted = target[method].apply(target, args);
                if (!current(version)) { return false; }
                if (kind === "heroes") {
                    var heroDraft = heroes.draft();
                    if (heroDraft && !same(heroDraft.team, upstream)) { heroes.reset(); accepted = false; }
                } else if (kind === "preparation") {
                    var preparationDraft = preparation.draft();
                    if (preparationDraft && !same(preparationDraft.lineup, upstream)) { preparation.reset(); accepted = false; }
                }
                if (!current(version) || !synchronize(accepted) || !current(version)) { return false; }
                busy = false; return accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function views() {
            if (!available()) { return { status: "disposed", message: "Локальная цепь подготовки закрыта.", team: null, heroes: null, preparation: null, complete: false }; }
            if (busy) { return { status: "updating", message: "Подготовка обновляется; локальные данные недоступны.", team: null, heroes: null, preparation: null, complete: false }; }
            var teamDraft = team.draft(), heroDraft = heroes.draft(), preparationDraft = preparation.draft();
            var teamView = team.view(), heroView = heroes.view(), preparationView = preparation.view(), status, step, detail;
            if (!teamDraft || !teamDraft.complete) {
                status = "team"; step = "Выберите пять игроков для локального состава."; detail = teamView.message;
            } else if (!heroDraft || !heroDraft.complete) {
                status = "heroes"; step = heroDraft ? "Назначьте героя и позицию каждому игроку." :
                    "Получите новые предложения героев и позиций для текущего состава."; detail = heroView.message;
            } else if (!preparationDraft || !preparationDraft.complete) {
                status = "preparation"; step = preparationDraft ? "Выберите план и вариант разговора." :
                    "Получите новые варианты подготовки для текущих назначений."; detail = preparationView.message;
            } else {
                status = "complete"; step = "Три шага заполнены локально; серверная готовность не подтверждена."; detail = preparationView.message;
            }
            return { status: status, message: (notice ? notice + " " : "") + step + " " + detail,
                team: teamView, heroes: heroView, preparation: preparationView, complete: status === "complete" };
        }
        function contexts() {
            if (!available() || busy) { return null; }
            return { team: team.draft(), heroes: heroes.draft(), preparation: preparation.draft() };
        }
        function draft() {
            if (!available() || busy) { return null; }
            var final = preparation.draft();
            return final && final.complete ? final : null;
        }
        return { updateTeam: function (frame) { return run(team, "update", [frame], "team"); },
            choosePlayer: function (id) { return run(team, "choose", [id], "team"); },
            removePlayer: function (id) { return run(team, "remove", [id], "team"); }, clearTeam: function () { return run(team, "clear", [], "team"); },
            updateHeroes: function (frame) { return run(heroes, "update", [frame], "heroes"); },
            assignHero: function (id, heroId, role) { return run(heroes, "assign", [id, heroId, role], "heroes"); },
            removeHero: function (id) { return run(heroes, "remove", [id], "heroes"); }, clearHeroes: function () { return run(heroes, "clear", [], "heroes"); },
            updatePreparation: function (frame) { return run(preparation, "update", [frame], "preparation"); },
            choosePlan: function (id) { return run(preparation, "choosePlan", [id], "preparation"); },
            chooseTalk: function (id) { return run(preparation, "chooseTalk", [id], "preparation"); },
            removePlan: function () { return run(preparation, "removePlan", [], "preparation"); },
            removeTalk: function () { return run(preparation, "removeTalk", [], "preparation"); },
            clearPreparation: function () { return run(preparation, "clear", [], "preparation"); },
            view: views, contexts: contexts, draft: draft, dispose: dispose, isDisposed: function () { return !available(); } };
    }
    return { create: create };
}());
