/* Caller-driven local freshness composition. No mouse hooks, authority or transport. */
var DotaCoachMouseTargetingPanels = (function () {
    "use strict";
    function closedView() {
        return {mouse: null, observation: null, closed: true, evidence: "local_mouse_targeting",
            canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false};
    }
    function bind(root, options) {
        var targets = DotaCoachTargets.create(options), panel;
        try { panel = DotaCoachMouseProposalPanels.bind(root); }
        catch (error) { targets.dispose(); throw error; }
        var closed = false, busy = false;
        function dispose() {
            if (closed) { return; }
            closed = true;
            targets.dispose(); panel.dispose();
        }
        function alive() {
            if (closed) { return false; }
            if (panel.isDisposed()) { dispose(); }
            return !closed;
        }
        function clearTarget() {
            if (!alive()) { return false; }
            var state = panel.view();
            if (!state || state.closed || closed) { dispose(); return false; }
            if (state.proposal && state.proposal.target) { panel.proposeTarget(null); }
            return alive();
        }
        function sync() {
            if (!alive()) { return null; }
            var observation = targets.view();
            if (!alive()) { return null; }
            if (observation.status === "disposed") { dispose(); return null; }
            if (observation.status !== "ready" && !clearTarget()) { return null; }
            return observation;
        }
        function run(action, input) {
            if (closed || busy) { return action === "view" ? (closed ? closedView() : null) : false; }
            busy = true;
            try {
                if (!alive()) { return action === "view" ? closedView() : false; }
                if ((action === "update" || action === "select") && !clearTarget()) { return false; }
                var observation = sync();
                if (!observation) { return action === "view" ? closedView() : false; }
                var accepted;
                switch (action) {
                case "capture": accepted = panel.captureActor(input); break;
                case "update": accepted = targets.update(input); break;
                case "select": accepted = targets.select(input); break;
                case "target": accepted = panel.proposeTarget(observation); break;
                case "move": accepted = panel.proposeMove(input); break;
                case "reset":
                    accepted = panel.reset();
                    if (alive()) { targets.select(null); }
                    break;
                case "refresh": accepted = panel.refresh(); break;
                case "view": accepted = true; break;
                }
                // Finish all native checks before the final local freshness sample.
                var state = panel.view();
                if (!state || state.closed || !alive()) { dispose(); return action === "view" ? closedView() : false; }
                observation = targets.view();
                if (closed || observation.status === "disposed") {
                    dispose(); return action === "view" ? closedView() : false;
                }
                if (observation.status !== "ready") {
                    if (!clearTarget()) { return action === "view" ? closedView() : false; }
                    state = panel.view();
                    if (!state || state.closed || closed) { dispose(); return action === "view" ? closedView() : false; }
                }
                // No native callback follows a successful final clock barrier.
                if (action === "target") { return accepted && observation.status === "ready" && !!state.proposal && !!state.proposal.target; }
                if (action === "view") {
                    return {mouse: state, observation: observation, closed: false, evidence: "local_mouse_targeting",
                        canSend: false, nativeConfirmed: false, sourceAuthorizationConfirmed: false};
                }
                return !!accepted;

            } catch (error) { dispose(); return action === "view" ? closedView() : false; }
            finally { busy = false; }
        }
        return {
            captureActor: function (input) { return run("capture", input); },
            updateTargets: function (input) { return run("update", input); },
            selectTarget: function (id) { return run("select", id); },
            proposeTarget: function () { return run("target"); },
            proposeMove: function (input) { return run("move", input); },
            refresh: function () { return run("refresh"); },
            reset: function () { return run("reset"); },
            view: function () { return run("view"); },
            dispose: dispose,
            isDisposed: function () {
                if (closed || busy) { return closed; }
                busy = true;
                try { alive(); return closed; }
                finally { busy = false; }
            }
        };
    }
    return {bind: bind};
}());
