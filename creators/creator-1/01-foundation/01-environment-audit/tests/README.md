# Проверки диагностического помощника

[test_inspect_environment.py](test_inspect_environment.py) использует временные
файлы и реальные Git-репозитории, без сетевого доступа. Проверяет происхождение клона,
сохранение пользовательских данных/индекса, чтение Steam и честность статуса Dota.

Из корня репозитория:

```text
python3 -m unittest discover -s creators/creator-1/01-foundation/01-environment-audit/tests -v
```

На Windows используйте доступный Python 3.9+ вместо `python3`.
