# C2-11-03 — Сквозная проверка интерфейса

**Отдел:** создатель 2. **Проверяющий:** создатель 1.
**Статус:** частично выполнено: единый прогон исходников готов; клиентская цепочка открыта.

[Windows runner: timeout проверен, полный прогон остаётся verified=false](reports/windows-runner-2026-10-11.md).

[Actual Windows junction: три guard сценария PASS, file symlink открыт](reports/windows-reparse-2026-10-11.md).
**Зависимости:** [C2-11-02](../02-addon-packaging/README.md), [C2-07-03](../../07-match-screen/03-orders-timeline/README.md), [C2-08-03](../../08-analysis-ui/03-post-match/README.md).
**Рабочая папка:** `creators/creator-2/11-integration/03-end-to-end/`.

[Раздел](../README.md) · [План создателя](../../PLAN.md) · [Общие правила](../../../shared/WORKFLOW.md)

## Действия

- [x] Создать единый каталог и проверенный запуск всех облачных source suites с коротким отчётом.
- [ ] Пройти состав, подготовку, приказы, мышь и итог с сервером.
- [ ] Проверить отказ голоса и читаемость режима.
- [ ] Передать фактический отчёт в совместную приёмку.
- [ ] Сопоставить фактический результат с критерием ниже и записать непроведённые проверки.
- [ ] Передать изменение второму создателю для проверки, затем обновить этот статус.

## Результат и приёмка

Цепочка выполнена на клиенте; скриншот макета не заменяет запуск.

## Где размещать материалы

- [Проектирование](design.md) и [план](implementation-plan.md) — границы единого source-прогона.
- [Каталог](suite-catalog.json) — один источник наборов, без произвольных shell-команд.
- [tools](tools/README.md) — исполнитель проверок.
- [tests](tests/README.md) — проверки его поведения и отказов.
- [reports](reports/README.md) — фактические результаты и ограничения.

Новый вложенный каталог получает README с назначением и ссылкой из этого файла.
API, сигнатуры, конкретные файлы и команды проверки закрепляются в локальном
техническом плане после исследования входов; не подменяйте их выдуманными командами.

## Проверка исходников

Из корня репозитория (в Windows используйте подтверждённый launcher Python):

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --list
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-voice-text --suite node-voice-panel
```

Первый вызов выполняет полный каталог. Последний — только выбранные наборы,
`selection=partial`; он не заменяет обязательный полный прогон. Логи и JSON —
в новом каталоге `build/dota_coach/source-checks-*`; существующий output сохраняется.
Параметры: `--jobs 1..7` (по умолчанию 4), `--timeout` в секундах, максимум 600
(по умолчанию 180), `--output` — только новый путь под `build/dota_coach`.
Exit 0 — все выбранные наборы прошли без skipped/cancelled/todo; 1 — incomplete или провал
с сохранённым отчётом; 2 — ошибочные входы/среда, проверка не началась.

Python запускается тем же интерпретатором, Node — из PATH с TAP reporter. При timeout
POSIX убивает выделенную группу процессов; Windows использует `taskkill /T /F`
только для PID запускаемого набора. Отсутствие Node для выбранного Node-набора,
либо taskkill на Windows, блокирует запуск до создания output. Неудалённые процессы
при ошибке termination отмечаются отдельным провалом. Полный Windows source-прогон
выполняется с сохранёнными ограничениями; это не игровая приёмка.
Ссылка на тесты не является серверным контрактом, приёмкой движка или учётом токенов.

[Windows portability design](windows-portability-design.md) · [План](windows-portability-plan.md).
В JSON skipped_tests считает пропуски, incomplete_suites отделяет согласованные
exit0 summaries с пропусками от error_suites. Legacy failed_suites сохраняет все
unverified IDs; verified=false/exit1 при любой incomplete suite. Passed не включает
skipped cases. Source2/runtime flags остаются false.

[Windows portability report](reports/windows-portability-2026-10-12.md): final46suites/1020passed/28skipped/6incomplete/0errors/verifiedfalse. Пропуски не закрывают security/native acceptance; taskkill проверен только для собственных test processes вне разрешённой песочницы.

C2-06-01 добавил только [четыре безопасных diagnostic cleanup tests](../../06-voice/01-microphone-probe/tests/README.md) в canonical source catalog. Actual microphone capture не выполняется обычнымиchecks/import. Свежийfull160830Z-3a670b47suites/1024passed/28skipped/0errors/verifiedfalse — [отчёт](../../06-voice/01-microphone-probe/reports/microphone.md); speech/ASR/bridge остаются открытыми.
