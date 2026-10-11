# tests C2-07-02

Поведенческие Node VM и XML проверки.

- [opponent-roster.test.cjs](opponent-roster.test.cjs): 17 сценариев модели.
- [opponent-panel.test.cjs](opponent-panel.test.cjs): 13 сценариев панели/lifecycle.
- [test_opponent_layout.py](test_opponent_layout.py): 2 проверки структуры/зависимостей.

Из корня репозитория:

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-opponent-roster --suite node-opponent-panel --suite python-c2-07-02
```

Это частичный прогон; полный выполняется той же командой без `--suite`.

[Родитель](../README.md).
