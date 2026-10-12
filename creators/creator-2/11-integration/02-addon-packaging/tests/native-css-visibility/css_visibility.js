/* Separate native test fixture. Never included by the HUD13 source kind. */
(function () {
    "use strict";
    $.Schedule(1, function () {
        var root = $.GetContextPanel(), slot = root.FindChildTraverse("NativeCssSlot"),
            phase = root.FindChildTraverse("NativeCssPhase");
        if (!slot || !phase || !slot.IsValid() || !phase.IsValid()) {
            $.Msg("[C2NativeCss] missing_required_panel");
            return;
        }
        function valid() { return root.IsValid() && slot.IsValid() && phase.IsValid(); }
        function record(name, expectedVisible) {
            if (!valid()) { return false; }
            var pass = slot.visible === expectedVisible;
            if (expectedVisible) {
                pass = pass && slot.actuallayoutwidth > 0 && slot.actuallayoutheight > 0 &&
                    root.visible === true && root.actuallayoutwidth > 0 && root.actuallayoutheight > 0;
            }
            if (name === "initial") {
                pass = pass && slot.actuallayoutwidth === 0 && slot.actuallayoutheight === 0;
            }
            phase.text = "TEST: " + name + " " + (pass ? "PASS" : "FAIL");
            $.Msg("[C2NativeCss] " + name + " visible=" + slot.visible +
                " width=" + slot.actuallayoutwidth + " height=" + slot.actuallayoutheight +
                " rootVisible=" + root.visible + " pass=" + pass);
            return pass;
        }
        var initial = record("initial", false), shown = false, hidden = false;
        $.Schedule(15, function () {
            if (!valid()) { return; }
            slot.visible = true;
            $.Schedule(1, function () { shown = record("shown", true); });
        });
        $.Schedule(30, function () {
            if (!valid()) { return; }
            slot.visible = false;
            $.Schedule(1, function () { hidden = record("hidden", false); });
        });
        $.Schedule(45, function () {
            if (!valid()) { return; }
            slot.visible = true;
            $.Schedule(1, function () {
                var reshown = record("reshown", true);
                $.Msg("[C2NativeCss] cycle pass=" + (initial && shown && hidden && reshown));
            });
        });
    });
}());
