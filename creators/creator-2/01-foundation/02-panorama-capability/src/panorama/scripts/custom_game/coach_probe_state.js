/* Engine-independent diagnostic state. Deliberately uses plain ES5 JavaScript. */
var DotaCoachProbe = (function () {
    "use strict";

    function create(options) {
        var active = null;
        var closed = false;
        var subscription;

        function log(event, id) {
            if (options.log) { options.log(event, id || ""); }
        }

        function cancel(request) {
            if (request && request.timer !== null) {
                try { options.cancelTimer(request.timer); }
                catch (error) { log("timer_cancel_failed"); }
                request.timer = null;
            }
        }

        function shutdown() {
            if (closed) { return; }
            closed = true;
            cancel(active);
            active = null;
            try { options.unsubscribe(subscription); }
            catch (error) { log("unsubscribe_failed"); }
        }

        function publish(state, reason) {
            try {
                options.render(state, reason || "none");
                return true;
            } catch (error) {
                shutdown();
                log("render_failed");
                if (options.onUnavailable) {
                    try { options.onUnavailable(); }
                    catch (notifyError) { log("unavailable_notify_failed"); }
                }
                return false;
            }
        }

        function finish(request, state, reason) {
            if (closed || active !== request) { return; }
            active = null;
            cancel(request);
            if (publish(state, reason)) { log(state, request.id); }
        }

        function receive(message) {
            if (closed || !active) { return; }
            if (!message || typeof message !== "object" || message.protocol_version !== 1 ||
                    message.request_id !== active.id) {
                log("reply_ignored");
                return;
            }
            if (message.status === "ok" && message.reason === "none") {
                finish(active, "ok", "none");
            } else if (message.status === "rejected" &&
                    (message.reason === "unsupported_version" || message.reason === "invalid_request")) {
                finish(active, "rejected", message.reason);
            } else {
                log("reply_ignored");
            }
        }

        subscription = options.subscribe(receive);
        if (!publish("idle", "none")) { throw new Error("Diagnostic view unavailable"); }

        return {
            request: function () {
                if (closed || active) { return false; }
                var id;
                try {
                    id = options.nextRequestID();
                    if (typeof id !== "string" || !id.length || id.length > 64) {
                        throw new Error("Invalid diagnostic ID");
                    }
                } catch (error) {
                    publish("error", "request_failed");
                    log("request_id_failed");
                    return false;
                }
                var request = { id: id, timer: null };
                active = request;
                if (!publish("pending", "none")) { return false; }
                try {
                    request.timer = options.schedule(2, function () {
                        finish(request, "timeout", "none");
                    });
                    options.send({ protocol_version: 1, request_id: id });
                    log("request_sent", id);
                    return true;
                } catch (error) {
                    finish(request, "error", "request_failed");
                    return false;
                }
            },
            dispose: function () {
                if (closed) { return; }
                shutdown();
                publish("unavailable", "none");
            }
        };
    }

    return { create: create };
}());
