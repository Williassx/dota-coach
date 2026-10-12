/* Separate native acceptance fixture, never a production bootstrap. */
(function () {
    "use strict";
    var context, root, phase, ui, old, failed = false;
    function node(id) {
        var p = context.FindChildTraverse(id);
        if (!p || !p.IsValid()) { throw new Error("Missing TEST node " + id); }
        return p;
    }
    function ensure(value, why) { if (!value) { throw new Error(why); } }
    function player(id, name, role) {
        return {id: id, playerName: name, heroName: "Synthetic", role: role,
            source: "synthetic", side: "own", availability: "alive"};
    }
    function noProposal() {
        ensure(ui.view().result === null, "proposal retained");
        ["Input", "Normalized", "Address", "Action"].forEach(function (name) {
            ensure(node("VoiceText" + name).text === "", "retained " + name);
        });
    }
    function plainLabels() {
        ["Status", "Normalized", "Address", "Action", "Hint"].forEach(function (name) {
            ensure(node("VoiceText" + name).html === false, "nonplain " + name);
        });
        ensure(node("VoiceTextHint").text.indexOf("Микрофон не подключён") !== -1, "missing microphone warning");
    }
    function record(name, assertion) {
        try {
            assertion();
            phase.text = "TEST ONLY: synthetic roster; no microphone/server/input | " + name + " PASS";
            $.Msg("[C2NativeVoice] " + name + " pass=true");
        } catch (error) {
            failed = true;
            phase.text = "TEST ONLY | " + name + " FAIL: " + String(error);
            $.Msg("[C2NativeVoice] " + name + " pass=false reason=" + String(error));
            if (ui) { ui.dispose(); }
        }
    }
    function after(delay, action, name, assertion) {
        $.Schedule(delay, function () {
            if (failed || !context.IsValid()) { return; }
            try { action(); } catch (error) { record(name, function () { throw error; }); return; }
            $.Schedule(1, function () { if (!failed && context.IsValid()) { record(name, assertion); } });
        });
    }
    $.Schedule(1, function () {
        context = $.GetContextPanel(); root = node("VoiceTextRoot"); phase = node("NativeVoiceFixtureStatus");
        var a = player("TEST-a", "TEST Альфа", 1), b = player("TEST-b", "TEST Бета", 2);
        after(0, function () {
            ui = DotaCoachVoicePanels.bind(root);
            ensure(ui.updateRoster({revision: 1, players: [a, b]}), "TEST roster rejected");
        }, "bound", function () {
            ensure(!ui.isDisposed() && root.visible, "scope closed");
            ensure(node("VoiceTextInput").enabled && node("VoiceTextPreviewButton").enabled, "preview disabled");
            ensure(node("VoiceTextInput").actuallayoutwidth > 0 && node("VoiceTextInput").actuallayoutheight > 0,
                "TextEntry has no geometry"); noProposal(); plainLabels();
        });
        after(15, function () {
            node("VoiceTextInput").text = "КЕРРИ, отступай";
            ensure(ui.preview(node("VoiceTextInput").text), "preview rejected");
        }, "ready", function () {
            var v = ui.view();
            ensure(v.result.status === "ready" && v.result.proposal.action === "retreat" &&
                v.result.proposal.recipientIds[0] === "TEST-a", "wrong local proposal");
            ensure(node("VoiceTextNormalized").text === "керри отступай" &&
                node("VoiceTextAddress").text === "TEST Альфа" &&
                node("VoiceTextAction").text === "Отступление", "wrong labels");
            ensure(node("VoiceTextStatus").text.indexOf("Ничего не отправлено") !== -1, "missing no-send warning");
            plainLabels();
        });
        after(30, function () {
            ensure(ui.updateRoster({revision: 2, players: [a, player("TEST-b", "TEST Альфа", 2)]}), "duplicate name roster rejected");
            ensure(ui.preview("TEST Альфа фарми") === false, "ambiguous preview accepted");
        }, "ambiguous", function () {
            ensure(ui.view().result.reason === "ambiguous_address" && ui.view().result.proposal === null,
                "wrong ambiguous result");
            ensure(node("VoiceTextStatus").text === "Адресат неоднозначен." &&
                node("VoiceTextAddress").text === "" && node("VoiceTextAction").text === "", "stale proposal labels");
            plainLabels();
        });
        after(45, function () {
            ensure(ui.preview("керри фарми"), "role preview rejected");
            node("VoiceTextInput").text = "керри отступай";
            ensure(ui.updateRoster({revision: 3, players: [b]}), "revision update rejected");
        }, "reset", function () {
            ensure(ui.view().parser.revision === 3 && ui.view().parser.consumed === 3, "revision/history changed");
            noProposal(); plainLabels();
        });
        after(60, function () { old = ui; old.dispose(); }, "disposed", function () {
            ensure(old.isDisposed() && old.view() === null && root.visible === false, "dispose failed");
            ["Status", "Normalized", "Address", "Action", "Hint", "Input"].forEach(function (name) {
                ensure(node("VoiceText" + name).text === "", "dispose retained " + name);
            });
            ensure(!node("VoiceTextInput").enabled && !node("VoiceTextPreviewButton").enabled &&
                !node("VoiceTextClearButton").enabled, "disposed input enabled");
        });
        after(75, function () {
            ui = DotaCoachVoicePanels.bind(root);
            ensure(ui.updateRoster({revision: 1, players: [player("TEST-fresh", "TEST Новый", 1)]}), "fresh roster rejected");
            var reads = 0;
            var poison = new Proxy({}, {ownKeys: function () { reads += 1; return []; },
                getOwnPropertyDescriptor: function () { reads += 1; return undefined; },
                get: function () { reads += 1; return undefined; }});
            ensure(old.updateRoster(poison) === false && old.receive(poison) === false &&
                old.preview("керри фарми") === false && old.clear() === false && reads === 0,
                "stale API accepted or inspected DTO");
        }, "rebound", function () {
            ensure(!ui.isDisposed() && ui.view().parser.revision === 1 && ui.view().parser.consumed === 0,
                "fresh binding corrupted");
            noProposal(); plainLabels();
            $.Msg("[C2NativeVoice] cycle pass=true microphone=absent transport=absent server=absent physical_input=not_tested");
        });
    });
}());
