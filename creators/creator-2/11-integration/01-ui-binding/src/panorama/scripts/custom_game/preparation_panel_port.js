/* Optional owned model projection for explicit preparation panel composition. */
var DotaCoachPanelPorts = (function () {
    "use strict";
    var owners = [];
    function adopt(projection, required, isCurrent) {
        if (!projection || typeof projection !== "object" || Array.isArray(projection) ||
                !Array.isArray(required) || required.length > 16 || typeof isCurrent !== "function") {
            throw new Error("Invalid panel model port");
        }
        if (owners.indexOf(projection) !== -1) { throw new Error("Panel model already owned"); }
        owners.push(projection);
        var closed = false, methods = {}, names = ["dispose", "isDisposed"], port = {};
        function release() {
            var index = owners.indexOf(projection);
            if (index !== -1) { owners.splice(index, 1); }
        }
        function dispose() {
            if (closed) { return; }
            closed = true;
            try { if (methods.dispose) { methods.dispose.call(projection); } }
            catch (error) { /* Cleanup still releases port ownership. */ }
            release();
        }
        function guard() {
            if (closed) { return false; }
            try { if (!isCurrent()) { dispose(); return false; } }
            catch (error) { dispose(); return false; }
            return !closed;
        }
        function alive() {
            if (!guard()) { return false; }
            try { if (methods.isDisposed.call(projection)) { dispose(); return false; } }
            catch (error) { dispose(); return false; }
            return guard();
        }
        function unavailable(name) {
            if (name === "view") { throw new Error("Panel model view unavailable"); }
            return name === "draft" ? null : false;
        }
        function wrap(name) {
            return function () {
                if (!alive()) { return unavailable(name); }
                try {
                    var result = methods[name].apply(projection, arguments);
                    return alive() ? result : unavailable(name);
                } catch (error) { dispose(); throw error; }
            };
        }
        try {
            if (!guard()) { throw new Error("Panel model adoption unavailable"); }
            for (var n = 0; n < required.length; n += 1) {
                var name = required[n];
                if (typeof name !== "string" || !/^[A-Za-z][A-Za-z0-9]*$/.test(name)) { throw new Error("Invalid port method"); }
                if (names.indexOf(name) === -1) { names.push(name); }
            }
            for (var m = 0; m < names.length; m += 1) {
                var descriptor = Object.getOwnPropertyDescriptor(projection, names[m]);
                if (descriptor && typeof descriptor.value === "function") { methods[names[m]] = descriptor.value; }
                if (!guard() || !descriptor || typeof descriptor.value !== "function") { throw new Error("Invalid owned model method"); }
            }
            if (!guard()) { throw new Error("Panel model adoption unavailable"); }
            for (var f = 2; f < names.length; f += 1) { port[names[f]] = wrap(names[f]); }
            port.dispose = dispose; port.isDisposed = function () { return !alive(); };
            return port;
        } catch (error) { dispose(); throw error; }
    }
    return { adopt: adopt };
}());
