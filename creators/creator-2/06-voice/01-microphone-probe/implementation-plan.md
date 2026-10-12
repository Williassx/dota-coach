# План обследования C2-06-01

[Спецификация](design.md) · [Карточка](README.md).
12 октября2026. Root — один автор новых файлов и shared usage; helper read-only официальные источники. Основа — existing Windows foundation, без изменений Dota/C1/контрактов.

1. Сохранить read-only WinMM inventory в build/dota_coach/microphone-devices-20261012.json; проверить device names/count/caps/query return codes. Выполнено до выбора capture.
2. Создать единственную диагностическую команду notes/capture-command.py: fixed explicit device0/PCM3seconds, fresh owned output, API result checks, bounded wait и cleanup. API сверить с Microsoft waveInOpen/WAVEHDR/prepare/add/start/reset/unprepare/close. Pythonstdlib без установки dependencies. Это native experiment, не production feature; прямой native capture и независимое чтение WAV заменяют тесты, копирующие команду.
3. Выполнить один capture; проверить WAV через независимый wave reader, duration/frames/PCM RMS/peak/SHA256 и result file. Raw audio локальный игнорируемый. Непредвиденный отказ сначала диагностировать, не менять ОС/permissions/selected device вслепую.
4. Сохранить notes/voice-capabilities.md с первичными URLs/access status; reports/microphone.md с точными фактами, кодами и ограничениями. Добавить notes/reports README и ссылки из карточки.
5. Обновить фактический статус, журнал, уроки по новой причине, windows-resume и unique usage(null для неизвестных tokens/cost). Генератор progress/--check, локальные ссылки, syntax/diff, required full source checks после новой диагностической команды; incomplete сохраняется.
6. Один reused final critic по готовому результату; AI не human second owner. Обычный commit/push main с независимой сверкой remote SHA и clean tree. Никаких писем/публикации audio/OS изменения.

## Подтверждённое замечание final review

ОдинP2: logging exception доemergencyexit мог раскрутитьmain stack приunsafequeuedbuffer. Дополненплан:4noncapturing failure-injection tests RED4errors→GREEN4PASS, diagnostic writer try/finally гарантируетosexit вunsafebranch. Толькоsafe diagnostics tests добавлены вcanonical sourcecatalog; actualcapture не запускается. Fullповтор послеfix/catalog обязателен; повтор записи не требуется, postcapture logging отдельно проверен.
