# Windows microphone: ограниченное обследование

[Карточка](../README.md) · [Спецификация](../design.md) · [План](../implementation-plan.md) · [Источники](../notes/voice-capabilities.md).
12октября2026. Baseline fded769/main/clean; ведущая76, root76/107/173/174/175. Reused read-only helper76/107 исследовал официальные источники, source command/docs имеют одного автора root. Установка Windows10.0.19045, Python3.12.14. Dota/Steam/OS/privacy/default devices/C1 не изменялись.

## Фактический ввод

[Read-only inventory](../../../../../build/dota_coach/microphone-devices-20261012.json): waveInGetNumDevs=4; у всех caps/query PCM16000mono16 return0, query handlesfalse. Доступность формата не означает открытие/запись/permission/ASR.

| Index этого запуска | CAPS name (может быть усечено) | Query return |
|---|---|---:|
|0|Микрофон (fifine Microphone)|0|
|1|Microphone (Trust QHD Webcam)|0|
|2|SteelSeries Sonar - Microphone|0|
|3|Стерео микшер (Realtek High Def…)|0|

Для actual capture выбран только explicit FIFINE0, rechecked name доopen. Не default device, не loopback/stereo mixer. [Единственная команда](../notes/capture-command.py): один96kBбуфер,3секунды PCM16000Hz/mono/16bit, WHDR_DONE poll с deadline5секунд. Нет capture на import/в регулярном тестовом каталоге.

Первый [sandbox result160053Z-b12a57](../../../../../build/dota_coach/microphone-20261012T160053Z-b12a57/capture-result.json): caps0/open1, аудио не записано, handle не открыт. waveInGetErrorTextW(1) return0: «Неизвестная внешняя ошибка». Service query: Audiosrv/AudioEndpointBuilder Running; registry privacy query не дала результата, CIM Win32_SoundDevice — access denied. Из этого не установлена privacy policy или неисправность устройства. Дополнительные две страницы Microsoft error-code help были недоступны через web; локальный return text сохранён в выводе команды.

Одобренный повтор той же команды вне sandbox [result160121Z-93f38d](../../../../../build/dota_coach/microphone-20261012T160121Z-93f38d/capture-result.json): все8API results0 (caps/open/prepare/add/start/reset/unprepare/close), WHDR_DONE observed, bytes_recorded96000. cleanup_verified=true; reset/unprepare/close фактически выполнены. Разница установлена между контекстами исполнения; низкоуровневая причина open1 отдельно не установлена, OS/settings не менялись.

Независимый wave reader [verification](../../../../../build/dota_coach/microphone-20261012T160121Z-93f38d/wav-verification.json):48000frames/16000Hz/mono/2bytes/3.000s;96000PCM/96044WAVbytes. SHA25694ab5c110254af6692377fe983120b3b1cf6319e4526875f9c875d62d6bf9b0e совпадает с capture report. RMS−51.715dBFS,peak−38.160dBFS,47780nonzero samples. Probe elapsed3.103519s/ownCPU0.03125s; это одно наблюдение capture overhead, не ASR latency/resources или benchmark. Новая папка проверена ignored; raw WAV не в Git и не отправлялся в сеть. SyntaxASTPASS.

## Что не принято

Захват реального PCM подтверждён; разборчивая настоящая речь/транскрипт/speaker identity не подтверждены. Nonzero samples могут быть шумом. Synth/TTS не использовались вместо реальной речи.

Speech/ASR/русский runtime, язык/словарь/ошибки распознавания, сеть/ресурсы ASR, companion→Dota bridge/C1 authentication/ACK/исполнение приказов, микрофон из Panorama и human second owner остаются открытыми. Документированный поддерживаемый сквозной путь ещё не найден; отсутствие доступной VDC страницы не является отказом Valve. Workaround memory injection не создавался. Нативный voice text preview другого подпункта не повышен до голоса.

C2-06-01 не завершён: общий критерий требует настоящей речи И проверенного пути. Выполнены запись фактов/конкретной зависимости и сопоставление с критерием; исследования поддерживаемой интеграции и реальные ASR проверки остаются открытыми.

## Воспроизведение

Запуск намеренно активирует микрофон на3секунды и создаёт новый локальный ignored output. Указанный device0 должен снова совпасть с FIFINE; иначе команда откажется до записи. Не запускать автоматически в CI/обычных tests.

```powershell
$env:PYTHONUTF8='1'
& 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' creators/creator-2/06-voice/01-microphone-probe/notes/capture-command.py
```

Разрешённый внеsandbox запуск нужен в этой сессии дляactualopen. Автономная команда фиксирует reset/unprepare/close; приunsafecleanup сохраняетfailedresult и завершает только свой процесс без освобождения возможноqueued Pythonbuffer. Не повышать такойfailure доcleanupPASS. Fresh UUID child сохраняет старые results.

## Регрессия исходников

Required full [source-checks160217Z-80e9f2](../../../../../build/dota_coach/source-checks-20261012T160217Z-80e9f2/source-checks.json):46suites/1020passed/28skipped/6incomplete/error_suites[]/verifiedfalse; all suite process exits0, overall CLIexit1 из-за incomplete. Это существующий source-test catalog, не проверка микрофона или сборка игры. Новый диагностический probe не добавлен в обычный catalog, чтобы checks не активировали микрофон. Его native success/error path и WAV проверены отдельно; другие device/timeout/cleanup failure paths не испытаны.

## Исправление после final review

ОдинP2 обнаружен и подтверждён: ошибка JSON/stdout могла помешать emergencyexit приunsafecleanup. Diagnostic writer теперь finally вызывает os._exit1 даже приошибкелогирования. Новые4noncapturing tests RED4errors(missing writer)→GREEN4PASS, logs build/dota_coach/microphone-cleanup-{red,green}-20261012.log. Tests mock exit sentinel; hardware cleanup failure не вызывался и не объявлен испытанным. Только этот safe suite добавлен вcatalog: regular checks/import не включаютcapture. Защитныйpostcapturefix не требует повторнойзаписи; повторfull [160830Z-3a670b](../../../../../build/dota_coach/source-checks-20261012T160830Z-3a670b/source-checks.json) завершён:47suites/1024passed/28skipped/6incomplete/error_suites[]/verifiedfalse/CLIexit1. Все47suiteprocess exits0, новыйpython-c2-06-01:4PASS/0skips/verifiedtrue. Контроль P2 тем же reusedcritic подтвердил исправление, новых существенных замечаний нет. AIreview неhumansecondowner.

Финальные проверки:14изменённых Markdown/173локальные ссылки без разрывов,29уроков с пятьюполями,41uniqueusage task. AST новыхPython, сохранённыйWAVhash, progress--check52/213(24.4%) иgitdiff--check проходят. Rawcaptureignored; source/tests/docs тольковбиблиотекеC2, server/sharedcontractsнеизменны. Normalpublication/remoteSHA определяютсяGit history и отдельнойсверкой.
