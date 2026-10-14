# Проверки обследователя Panorama

[Подпункт](../README.md). Файловые сценарии работают в Linux и Windows;
они не запускают Dota и не подтверждают её API.

Из корня репозитория:

```sh
python -m unittest discover -s creators/creator-2/01-foundation/01-workspace-audit/tests -v
```

[test_autonomous_progress.py](test_autonomous_progress.py) — old flags/format correction, independent creator review, missing evidence and denominator guards.
