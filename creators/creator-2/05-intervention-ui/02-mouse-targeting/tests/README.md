# tests — проверки локального предложения

[Родитель](../README.md).

[mouse-proposals.test.cjs](mouse-proposals.test.cjs) — 17 сценариев. Проверяются
фиксированный actor, замена предложения, типы целей/границы координат, own data
schema, unknown/dead/stale, no-read hidden getters, copied view/reentry/dispose.
Один сценарий использует реальный Targets.view и локальное истечение наблюдения.

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-mouse-proposals --suite node-targets
```

Это partial source-проверка; полный runner запускается без --suite. Нет real mouse
hook, native gameplay, lease или подтверждения реального последнего удара.

[mouse-panel.test.cjs](mouse-panel.test.cjs) — 13 VM сценариев: четыре действия,
фиксированный адресат, plain labels, clear-beforeDTO, ownership/reentry/dispose.
[test_mouse_layout.py](test_mouse_layout.py) — 3 проверки исходного графа/loader,
включая anonymous XML root для Source 2 при сохранении 7 component IDs.
