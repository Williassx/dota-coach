# Проверки source feedback

[Подпункт](../README.md) · [voice-panel.test.cjs](voice-panel.test.cjs) ·
[test_voice_panel_graph.py](test_voice_panel_graph.py).
VM проверяет local UI callbacks/lifecycle; XML checks не являются компиляцией Dota.

## Native fixture

[native-text-preview](native-text-preview/README.md) — отдельный explicit test driver,
не ресурс fixed kind. Anonymous-root regression входит в test_voice_panel_graph.py.

[Actual synthetic grammar cases](synthetic-grammar-cases-2026-10-13.json) — source JSON/SHA, три новых VM regression сценария: ready→reject cleanup, captured revision, stale ownership.
