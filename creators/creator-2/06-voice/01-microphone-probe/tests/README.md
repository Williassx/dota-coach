# Проверки аварийной диагностики

[Карточка](../README.md) · [Команда](../notes/capture-command.py).

[test_capture_cleanup.py](test_capture_cleanup.py):4failure-injection scenarios. Запись JSON/вывод могут отказать; unsafe branch всё равно вызывает emergency exit. При safe cleanup logging error не вызывает emergency exit. os._exit заменён sentinel в tests; WinMM/capture не вызываются, audio не читается. Это проверка регрессии после AI review, не доказательство hardware reset failure handling.

```powershell
python -m unittest discover -s creators/creator-2/06-voice/01-microphone-probe/tests -v
```

Набор входит в [общий source catalog](../../../11-integration/03-end-to-end/suite-catalog.json); import native command не активирует микрофон.
