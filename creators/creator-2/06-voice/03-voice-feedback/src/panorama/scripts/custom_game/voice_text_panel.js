/* Explicit text preview UI only. Never microphone/ASR, transport or game input. */
var DotaCoachVoicePanels = (function () {
    "use strict";
    var owners = [], serial = 0;
    var MAX = 9007199254740991;
    var labelNames = ["Status", "Normalized", "Address", "Action", "Hint"];
    var actionNames = {farm: "Фарм", retreat: "Отступление", regroup: "Сбор команды", hold: "Удержание позиции"};
    var reasons = {invalid_event: "Входные данные недоступны.", invalid_text: "Текст не распознан.",
        unknown_action: "Действие не распознано.", missing_address: "Укажите адресата.",
        unknown_address: "Адресат не найден.", ambiguous_address: "Адресат неоднозначен.",
        address_unavailable: "Адресат недоступен.", negated: "Отрицание требует уточнения.",
        multiple_commands: "Введите одну команду.", stale_roster: "Состав изменился. Повторите команду.",
        duplicate: "Повтор уже разобранного события.", history_full: "Разбор недоступен в этой сессии.",
        no_roster: "Состав не получен.", busy: "Данные обновляются."};
    function valid(panel) { if (!panel || !panel.IsValid()) { throw new Error("Voice text panel unavailable"); } return panel; }
    function handleValid(value) { return typeof value === "number" && value >= 0 && value <= MAX && value % 1 === 0; }

    function bind(root) {
        valid(root);
        if (owners.indexOf(root) !== -1) { throw new Error("Voice text root already bound"); }
        if (serial === MAX) { throw new Error("Voice text instance capacity reached"); }
        owners.push(root);
        var prefix = "text-preview-" + (++serial) + "-", count = 0;
        var closed = false, binding = true, busy = false, staging = false, generation = 0, timer = null;
        var model = null, sourceReady = false, displayed = null, input = null, previewButton = null, clearButton = null;
        var nodes = [], labels = {};
        function release() { var n = owners.indexOf(root); if (n !== -1) { owners.splice(n, 1); } }
        function dispose() {
            if (closed) { return; }
            closed = true; generation += 1; sourceReady = false; displayed = null;
            if (model) { model.dispose(); }
            if (timer !== null) { try { $.CancelScheduled(timer); } catch (error) { /* Context unavailable. */ } timer = null; }
            try { if (root.IsValid()) { root.visible = false; } } catch (error) { /* Destroyed root. */ }
            [previewButton, clearButton].forEach(function (button) {
                try { if (button && button.IsValid()) { button.ClearPanelEvent("onactivate"); button.enabled = false; } }
                catch (error) { /* Partial button. */ }
            });
            for (var i = 0; i < labelNames.length; i += 1) {
                try { var label = labels[labelNames[i]]; if (label && label.IsValid()) { label.html = false; label.text = ""; } }
                catch (error) { /* Partial label. */ }
            }
            try { if (input && input.IsValid()) { input.enabled = false; input.text = ""; } } catch (error) { /* Partial input. */ }
            if (!binding) { release(); }
        }
        function available() {
            if (closed) { return false; }
            try {
                valid(root);
                if (!staging && !binding && root.visible === false) { throw new Error("Voice text root hidden"); }
                for (var i = 0; i < nodes.length; i += 1) {
                    var item = nodes[i]; valid(item.node);
                    if (item.node.visible === false || root.FindChildTraverse(item.id) !== item.node) {
                        throw new Error("Required voice text node hidden/replaced");
                    }
                }
                if (model && model.view().status === "disposed") { throw new Error("Voice parser disposed"); }
            } catch (error) { dispose(); return false; }
            return !closed;
        }
        function current(version) { return available() && generation === version; }
        function write(name, text, version) {
            if (!current(version)) { return false; }
            labels[name].html = false;
            if (!current(version)) { return false; }
            labels[name].text = text; return current(version);
        }
        function set(object, key, value, version) {
            if (!current(version)) { return false; }
            object[key] = value; return current(version);
        }
        function disable(button, version) {
            if (!current(version)) { return false; }
            button.ClearPanelEvent("onactivate");
            return set(button, "enabled", false, version);
        }
        function stage(version, clearInput) {
            staging = true;
            if (!set(root, "visible", false, version) || !disable(previewButton, version) ||
                    !disable(clearButton, version) || !set(input, "enabled", false, version)) { return false; }
            for (var i = 0; i < labelNames.length; i += 1) { if (!write(labelNames[i], "", version)) { return false; } }
            return !clearInput || set(input, "text", "", version);
        }
        function paint(version) {
            var state = model.view(), proposal = displayed && displayed.proposal;
            var canPreview = sourceReady && state.consumed < state.capacity;
            var status = !sourceReady ? "Состав недоступен." : (!displayed ? "Введите команду для разбора." :
                (displayed.status === "ready" ? "Предложение готово. Ничего не отправлено." :
                    (displayed.status === "interim" ? "Промежуточный текст. Разбор ожидает финальную фразу." :
                        (reasons[displayed.reason] || "Текст недоступен."))));
            if (!write("Status", status, version) ||
                    !write("Normalized", displayed && displayed.normalizedText || "", version) ||
                    !write("Address", proposal ? proposal.recipientNames.join(", ") : "", version) ||
                    !write("Action", proposal ? actionNames[proposal.action] : "", version) ||
                    !write("Hint", "Текстовый разбор. Микрофон не подключён. Ничего не отправляется." +
                        (sourceReady && !canPreview ? " Разбор недоступен в этой сессии." : ""), version) ||
                    !set(input, "enabled", canPreview, version) ||
                    !set(previewButton, "enabled", canPreview, version) ||
                    !set(clearButton, "enabled", true, version)) { return false; }
            if (canPreview) {
                previewButton.SetPanelEvent("onactivate", function () {
                    if (!busy && current(version)) { parseText(function () { return input.text; }); }
                });
                if (!current(version)) { return false; }
            }
            clearButton.SetPanelEvent("onactivate", function () { if (!busy && current(version)) { clear(); } });
            return current(version) && set(root, "visible", true, version);
        }
        function run(operation, clearInput) {
            if (closed || busy) { return false; }
            busy = true; var version = ++generation;
            try {
                if (!available() || !stage(version, clearInput) || !current(version)) { return false; }
                var accepted = operation(version);
                return current(version) && paint(version) && accepted;
            } catch (error) { if (!closed && generation === version) { dispose(); } return false; }
            finally { busy = false; staging = false; }
        }
        function parseText(read) {
            if (closed || busy || !sourceReady || model.view().consumed >= 128) { return false; }
            return run(function (version) {
                var revision = model.view().revision, text = read();
                if (!current(version)) { return false; }
                displayed = model.ingest({utteranceId: prefix + (++count), text: text, rosterRevision: revision, final: true});
                return displayed.status === "ready";
            }, false);
        }
        function clear() { return run(function () { displayed = null; return true; }, true); }
        function arm() {
            if (closed) { return false; }
            var handle;
            try {
                handle = $.Schedule(0.25, function () {
                    if (closed) { return; }
                    timer = null;
                    if (busy || available()) { arm(); }
                });
                if (closed) { if (handleValid(handle)) { $.CancelScheduled(handle); } return false; }
                if (!handleValid(handle)) { dispose(); return false; }
                timer = handle; return true;
            } catch (error) { dispose(); return false; }
        }
        var api = {
            updateRoster: function (snapshot) {
                return run(function () { displayed = null; sourceReady = model.update(snapshot); return sourceReady; }, true);
            },
            preview: function (text) { return parseText(function () { return text; }); },
            receive: function (event) {
                if (closed || busy || !sourceReady) { return false; }
                return run(function () { displayed = model.ingest(event); return displayed.status === "ready"; }, true);
            },
            clear: clear,
            view: function () {
                if (busy || !available()) { return null; }
                return {sourceReady: sourceReady, parser: model.view(), result: displayed ? JSON.parse(JSON.stringify(displayed)) : null};
            },
            dispose: dispose,
            isDisposed: function () { return closed || (!busy && !available()); }
        };
        try {
            if (typeof DotaCoachVoiceText === "undefined") { throw new Error("VoiceText must be loaded first"); }
            model = DotaCoachVoiceText.create();
            function find(name) {
                var id = "VoiceText" + name, node = valid(root.FindChildTraverse(id));
                nodes.push({id: id, node: node}); return node;
            }
            input = find("Input"); previewButton = find("PreviewButton"); clearButton = find("ClearButton");
            labelNames.forEach(function (name) { labels[name] = find(name); });
            busy = true; var version = ++generation;
            if (!stage(version, true) || !paint(version) || !arm()) { throw new Error("Voice text initialization failed"); }
            busy = false; staging = false; return api;
        } catch (error) { dispose(); throw error; }
        finally { binding = false; if (closed) { release(); } }
    }
    return {bind: bind};
}());
