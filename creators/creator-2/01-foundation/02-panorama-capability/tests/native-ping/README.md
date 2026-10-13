# Native diagnostic ping TEST fixture

[Дизайн](../../native-ping-design-2026-10-13.md).
Existing Probe state и XML/CSS получают отдельный TEST adapter с actual
GameEvents; programmatic requests не являются физическими кликами.
Fixed probe manifest/policy5, auto adapter и game HUD остаются прежними.
Серверные исходники единственные у C1; builder только копирует их в ignored output.

Фазы: bound, valid, unsupported, extra, spoofed-player-id, valid-again, disposed.
Spoof phase фиксирует реальное поведение engine metadata, не заранее объявляет его.
Unknown native sender fails closed без fallback по payload PlayerID.
Fresh addon/owned PID/UTCticks/записи компиляции/screenshots/quit проверяются отдельно.

Variant adapter сохраняет active original coach_probe.js; observer вызывает
$.DispatchEvent(Activated,...,mouse). Это synthetic/native UI event, не мышиный клик.
[Native command](native-command.ps1) и [capture](capture-command.py) explicit only.
