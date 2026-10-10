/* Explicit preparation composition on an existing panel tree; no bootstrap or server. */
var DotaCoachPreparationBindings = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("Preparation panel unavailable"); }
        return panel;
    }
    function bind(root) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Preparation root already bound"); }
        owners.push(root);
        var closed = false, binding = true, owned = false, busy = false, generation = 0, timer = null;
        var flow = null, status = null, scopes = [], panes = [];
        function releaseOwner() {
            var index = owners.indexOf(root);
            if (index !== -1) { owners.splice(index, 1); }
        }
        function cleanupPanes() {
            for (var n = 0; n < panes.length; n += 1) {
                try { panes[n].dispose(); } catch (error) { /* Continue partial cleanup. */ }
            }
        }
        function dispose() {
            if (closed) { return; }
            closed = true; busy = false; generation += 1;
            if (flow) { flow.dispose(); }
            if (timer !== null) {
                try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ }
                timer = null;
            }
            cleanupPanes();
            // A rejected bind must not hide an independently owned child through its parent.
            try { if (owned && root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            try { if (status && status.IsValid()) {
                status.html = false; status.text = "Локальная подготовка закрыта; серверная готовность не подтверждена.";
            } } catch (error) { /* Destroyed status. */ }
            if (!binding) { releaseOwner(); }
        }
        function basic() {
            if (closed) { return false; }
            try {
                valid(root); valid(status);
                for (var n = 0; n < scopes.length; n += 1) { valid(scopes[n]); }
                if (!flow || flow.isDisposed()) { dispose(); return false; }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function available() {
            if (!basic()) { return false; }
            if (binding) { return false; }
            try {
                if (panes.length !== 3) { dispose(); return false; }
                for (var n = 0; n < panes.length; n += 1) {
                    if (panes[n].isDisposed()) { dispose(); return false; }
                }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return available() && generation === version; }
        function paint(version) {
            for (var n = 0; n < panes.length; n += 1) {
                if (!current(version)) { return false; }
                if (!panes[n].refresh()) {
                    if (current(version)) { dispose(); }
                    return false;
                }
                if (!current(version)) { return false; }
            }
            status.html = false;
            if (!current(version)) { return false; }
            status.text = flow.view().message;
            return current(version);
        }
        function invoke(method, args) {
            if (!available() || busy) { return false; }
            var version = ++generation;
            busy = true;
            try {
                for (var n = 0; n < panes.length; n += 1) {
                    if (!current(version)) { return false; }
                    if (!panes[n].suspend()) {
                        if (current(version)) { dispose(); }
                        return false;
                    }
                    if (!current(version)) { return false; }
                }
                status.html = false;
                if (!current(version)) { return false; }
                status.text = "Подготовка обновляется; локальные данные недоступны.";
                if (!current(version)) { return false; }
                var accepted = flow[method].apply(flow, args);
                if (!current(version)) { return false; }
                busy = false;
                return paint(version) && accepted;
            } catch (error) { if (current(version)) { dispose(); } return false; }
        }
        function facade(section, methods) {
            var facadeClosed = false, result = {
                view: function () {
                    if (facadeClosed || !basic() || busy) { throw new Error("Projection unavailable"); }
                    return flow.view()[section];
                },
                draft: function () {
                    if (facadeClosed || !basic() || busy) { return null; }
                    return flow.contexts()[section];
                },
                dispose: function () { facadeClosed = true; },
                isDisposed: function () { return facadeClosed || !basic(); }
            };
            for (var name in methods) {
                if (Object.prototype.hasOwnProperty.call(methods, name)) {
                    (function (localName, method) {
                        result[localName] = function () {
                            if (facadeClosed) { return false; }
                            return invoke(method, Array.prototype.slice.call(arguments));
                        };
                    }(name, methods[name]));
                }
            }
            return result;
        }
        function watch() {
            var scheduled = $.Schedule(0.25, function () {
                timer = null;
                if (available()) {
                    try { watch(); } catch (error) { dispose(); }
                }
            });
            if (closed) {
                try { $.CancelScheduled(scheduled); } catch (error) { /* Context unavailable. */ }
            } else { timer = scheduled; }
        }
        try {
            status = valid(root.FindChildTraverse("CoachPreparationStatus"));
            var ids = ["TeamPickerRoot", "HeroRoleRoot", "PreparationRoot"];
            for (var n = 0; n < ids.length; n += 1) {
                var scope = valid(root.FindChildTraverse(ids[n]));
                if (scope === root || scope === status || scopes.indexOf(scope) !== -1) {
                    throw new Error("Preparation scopes must be distinct");
                }
                scopes.push(scope);
            }
            flow = DotaCoachPreparationFlow.create();
            panes.push(DotaCoachTeamPickerPanels.bind(scopes[0], facade("team", {
                update: "updateTeam", choose: "choosePlayer", remove: "removePlayer", clear: "clearTeam"
            })));
            if (!basic()) { throw new Error("Preparation binding interrupted"); }
            panes.push(DotaCoachHeroRolePanels.bind(scopes[1], facade("heroes", {
                update: "updateHeroes", assign: "assignHero", remove: "removeHero", clear: "clearHeroes"
            })));
            if (!basic()) { throw new Error("Preparation binding interrupted"); }
            panes.push(DotaCoachPreparationPanels.bind(scopes[2], facade("preparation", {
                update: "updatePreparation", choosePlan: "choosePlan", chooseTalk: "chooseTalk",
                removePlan: "removePlan", removeTalk: "removeTalk", clear: "clearPreparation"
            })));
            owned = true; binding = false;
            if (!available()) { throw new Error("Preparation binding unavailable"); }
            var initial = ++generation;
            root.visible = true;
            if (!current(initial) || !paint(initial)) { throw new Error("Preparation view unavailable"); }
            watch();
            if (!available()) { throw new Error("Preparation watcher unavailable"); }
        } catch (error) {
            dispose(); cleanupPanes(); binding = false; releaseOwner(); throw error;
        }
        var api = {
            contexts: function () { return available() && !busy ? flow.contexts() : null; },
            draft: function () { return available() && !busy ? flow.draft() : null; },
            selectHeroPlayer: function (id) {
                if (!available() || busy) { return false; }
                var version = ++generation;
                try { var accepted = panes[1].selectPlayer(id); return current(version) && accepted; }
                catch (error) { if (current(version)) { dispose(); } return false; }
            },
            refresh: function () {
                if (!available() || busy) { return false; }
                var version = ++generation;
                try { return paint(version); } catch (error) { if (current(version)) { dispose(); } return false; }
            },
            dispose: dispose, isDisposed: function () { return !available(); }
        };
        var publicMethods = ["updateTeam", "choosePlayer", "removePlayer", "clearTeam", "updateHeroes",
            "assignHero", "removeHero", "clearHeroes", "updatePreparation", "choosePlan", "chooseTalk",
            "removePlan", "removeTalk", "clearPreparation"];
        for (var p = 0; p < publicMethods.length; p += 1) {
            (function (method) {
                api[method] = function () { return invoke(method, Array.prototype.slice.call(arguments)); };
            }(publicMethods[p]));
        }
        return api;
    }
    return { bind: bind };
}());
