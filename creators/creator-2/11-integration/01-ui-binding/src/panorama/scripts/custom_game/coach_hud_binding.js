/* Explicit local composition only. No bootstrap, server authority or entity discovery. */
var DotaCoachHudPanels = (function () {
    "use strict";
    var owners = [];
    function valid(panel) {
        if (!panel || !panel.IsValid()) { throw new Error("HUD panel unavailable"); }
        return panel;
    }
    function bind(root, options) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("HUD root already bound"); }
        owners.push(root);
        var closed = false, binding = true, timer = null, generation = 0;
        var route = null, camera = null, targets = null;
        var rosterRoot = null, ordersRoot = null, cameraRoot = null, targetsRoot = null, status = null;
        var selection = null, resolver = null, transport = null, gateway = null;
        var ownRoute = false, ownCamera = false, ownTargets = false;
        function dispose() {
            if (closed) { return; }
            closed = true;
            generation += 1;
            selection = null;
            if (timer !== null) {
                try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ }
                timer = null;
            }
            if (route) { route.dispose(); }
            if (camera) { camera.dispose(); }
            if (targets) { targets.dispose(); }
            var scopes = [[rosterRoot, ownRoute], [ordersRoot, ownRoute],
                [cameraRoot, ownCamera], [targetsRoot, ownTargets]];
            for (var n = 0; n < scopes.length; n += 1) {
                try { if (scopes[n][1] && scopes[n][0].IsValid()) { scopes[n][0].visible = false; } }
                catch (error) { /* Destroyed scope. */ }
            }
            try { if (status && status.IsValid()) {
                status.html = false; status.text = "Общий HUD недоступен. Локальная привязка закрыта.";
            } } catch (error) { /* Status unavailable. */ }
            if (!binding) { releaseOwner(); }
        }
        function releaseOwner() {
            var owner = owners.indexOf(root);
            if (owner !== -1) { owners.splice(owner, 1); }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root); valid(rosterRoot); valid(ordersRoot); valid(cameraRoot); valid(targetsRoot); valid(status);
                if (!camera || !targets || camera.isDisposed() || targets.isDisposed() ||
                        (!binding && !route) || (route && route.isDisposed())) {
                    dispose(); return false;
                }
            } catch (error) { dispose(); return false; }
            return true;
        }
        function current(version) { return available() && version === generation; }
        function resolveSelection() {
            if (!available()) { return false; }
            var active = selection, version = ++generation;
            // Invalidate the old camera handler BEFORE an external resolver can reenter.
            if (!camera.setRecipient(active ? { id: active.id, playerName: active.playerName } : null)) {
                if (current(version)) { dispose(); }
                return false;
            }
            if (!current(version)) { return false; }
            if (!active || !resolver) { return true; }
            var index = null;
            try { index = resolver(active.id); } catch (error) { /* Unknown mapping is not a group failure. */ }
            if (!current(version)) { return false; }
            if (typeof index !== "number" || index < 0 || index > 2147483647 || index % 1 !== 0) { return true; }
            var accepted = camera.setTarget({ id: active.id, playerName: active.playerName, entityIndex: index });
            if (!current(version)) { return false; }
            if (!accepted) { dispose(); return false; }
            return true;
        }
        function selected(card) {
            if (!available()) { throw new Error("HUD selection unavailable"); }
            selection = card ? { id: card.id, playerName: card.playerName } : null;
            var accepted = resolveSelection();
            if (!accepted && (binding || closed)) { throw new Error("HUD selection unavailable"); }
        }
        function scopedSend(intent, report) {
            if (!available()) { return; }
            transport(intent, function (update) { if (available()) { report(update); } });
        }
        function cameraCall(method, index) {
            if (!available()) { return method === "check" ?
                { available: false, reason: "Общий HUD недоступен." } :
                { requested: false, reason: "Общий HUD недоступен." }; }
            return gateway[method](index);
        }
        function watch() {
            timer = $.Schedule(0.25, function () {
                timer = null;
                if (!available()) { return; }
                try { watch(); } catch (error) { dispose(); }
            });
        }
        try {
            rosterRoot = valid(root.FindChildTraverse("CoachRoster"));
            ordersRoot = valid(root.FindChildTraverse("CoachOrders"));
            cameraRoot = valid(root.FindChildTraverse("CoachCamera"));
            targetsRoot = valid(root.FindChildTraverse("CoachTargets"));
            status = valid(root.FindChildTraverse("CoachHudStatus"));
            if (!options || Object.prototype.toString.call(options) !== "[object Object]") {
                throw new Error("Explicit HUD options required");
            }
            var fields = Object.getOwnPropertyNames(options);
            var allowed = ["now", "maxAgeMs", "send", "cameraGateway", "resolveCameraEntity"];
            var config = {};
            for (var n = 0; n < fields.length; n += 1) {
                if (allowed.indexOf(fields[n]) === -1) { throw new Error("Unknown HUD option"); }
                config[fields[n]] = options[fields[n]];
                if (closed) { throw new Error("HUD closed during options"); }
            }
            if (JSON.stringify(Object.getOwnPropertyNames(options).sort()) !== JSON.stringify(fields.slice().sort())) {
                throw new Error("HUD options changed during copy");
            }
            if (typeof config.now !== "function" || typeof config.maxAgeMs !== "number" ||
                    config.maxAgeMs < 1 || config.maxAgeMs > 60000 || config.maxAgeMs % 1 !== 0 ||
                    (fields.indexOf("send") !== -1 && typeof config.send !== "function") ||
                    (fields.indexOf("resolveCameraEntity") !== -1 && typeof config.resolveCameraEntity !== "function")) {
                throw new Error("Invalid HUD options");
            }
            transport = config.send; resolver = config.resolveCameraEntity;
            if (fields.indexOf("cameraGateway") !== -1) {
                if (!config.cameraGateway) { throw new Error("Invalid camera gateway"); }
                var check = config.cameraGateway.check;
                var focus = config.cameraGateway.focus;
                if (closed || typeof check !== "function" || typeof focus !== "function") {
                    throw new Error("Invalid camera gateway");
                }
                // Capture methods once; preserve their receiver without rereading getters.
                gateway = { check: function (index) { return check.call(config.cameraGateway, index); },
                    focus: function (index) { return focus.call(config.cameraGateway, index); } };
            }
            camera = DotaCoachCameraPanels.bind(cameraRoot, gateway ? {
                check: function (index) { return cameraCall("check", index); },
                focus: function (index) { return cameraCall("focus", index); }
            } : undefined);
            ownCamera = true;
            targets = DotaCoachTargetPanels.bind(targetsRoot, { now: config.now, maxAgeMs: config.maxAgeMs });
            ownTargets = true;
            route = DotaCoachInputRouting.bind(rosterRoot, ordersRoot,
                transport ? scopedSend : undefined, selected);
            ownRoute = true;
            binding = false;
            if (!available()) { throw new Error("HUD binding unavailable"); }
            rosterRoot.visible = true; ordersRoot.visible = true; cameraRoot.visible = true; targetsRoot.visible = true;
            status.html = false;
            status.text = "HUD связан локально. Исполнение в Dota не подтверждено.";
            if (!available()) { throw new Error("HUD status unavailable"); }
            watch();
        } catch (error) {
            dispose();
            // A handle returned after reentrant closure still belongs to this bind.
            if (route) { route.dispose(); }
            if (camera) { camera.dispose(); }
            if (targets) { targets.dispose(); }
            binding = false;
            releaseOwner();
            throw error;
        }
        function invoke(child, method, args) {
            if (!available()) { return false; }
            try { var accepted = child[method].apply(child, args); return available() && accepted; }
            catch (error) { dispose(); return false; }
        }
        return {
            replaceRoster: function (rows) { return invoke(route, "replaceRoster", [rows]); },
            updateControl: function (snapshot) { return invoke(route, "updateControl", [snapshot]); },
            selectPlayer: function (id) { return invoke(route, "select", [id]); },
            clearSelection: function () { return invoke(route, "clearSelection", []); },
            updateTargets: function (snapshot) { return invoke(targets, "update", [snapshot]); },
            selectTarget: function (id) { return invoke(targets, "select", [id]); },
            refreshCamera: resolveSelection,
            dispose: dispose,
            isDisposed: function () { return closed; }
        };
    }
    return { bind: bind };
}());
