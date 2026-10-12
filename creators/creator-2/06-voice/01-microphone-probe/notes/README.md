# Исследование микрофона

[Карточка](../README.md) · [Спецификация](../design.md).

- [Возможности и источники](voice-capabilities.md): Windows capture и неподтверждённый путь ASR/кастомки.
- [Диагностическая команда](capture-command.py): только Windows, explicit FIFINE device0,3секунды PCM, новый локальный build output, без сетевого транспорта. Запуск намеренно активирует микрофон. Импорт не записывает звук; actual capture не входит в addon/source-test catalog и не является production backend.

Не запускать автоматически как обычный тест или при импорте. Путь запуска и фактический результат — [отчёт](../reports/microphone.md). Device index/name — диагностическое предусловие этого опыта, не стабильная identity.

- [Windows inventory](system-speech-inventory.ps1): read-only языки/engines64/32bit.
- [ASR setup](asr-setup.md) и [smoke source](asr-smoke.py): pinnedlocalCPUmodel, existing WAV, никакогоmiccapture/приказов. Неordinarytests/import.
