# Windows source portability — 12 октября 2026

[Родитель](../README.md) · [Дизайн](../windows-portability-design.md) ·
[План](../windows-portability-plan.md). Baseline3785a4d/main/clean, Windows
D:/AI/dota2coach, Python3.12.14. Ведущая роль114. Root владеет runner/helper/docs;
reused windows_learning — только10packaging/handoff test files. Production guards,
OS/security/Developer Mode/C1/shared contracts и fixed source recipes не менялись.

## Причины и изменения

Предыдущий full133855Z-3b442f:46suites/753passed/6failed/verified=false.
OK(skipped=N) в трёх наборах ошибочно назван invalid_summary. В остальных файлах
symlink fixture creation дала12WinError1314 до production guard: packaging8,
handoff2, runner2. Runner имел также два timeout failures из-за sandbox taskkill.
Не все ошибки были symlink; junction не доказывает file-symlink coverage.

Разрешённый запуск17runner tests вне sandbox дал только2symlink errors, без timeout
failures. Никаких OS/privilege changes. Windows taskkill завершается только для PID
собственных тестовых процессов; sandbox termination failure остаётся настоящим
неподтверждённым завершением, не маскируется новой причиной.

Runner принимает однозначный согласованный OK(skipped=N) или TAP skip summary,
считает passed без skipped, добавляет skipped_tests/incomplete_suites/error_suites.
Legacy failed_suites сохраняет все unverified IDs. При skips reason=skipped_tests,
verified=false/CLIexit1; malformed/duplicate/impossible/empty summaries, FAILED,
process errors/timeout остаются errors. Недостоверные/failed summaries не дают
passed count; raw logs сохраняются. Source2/runtime flagsfalse не повышаются.

Общий test-only require_symlink сначала создаёт настоящую file/directory ссылку
в отдельном owned temporary child, проверяет тип, удаляет только ссылку и проверяет
сохранность target. Только Windows OSError.winerror1314 даёт explicit unsupported
skip. Иные ошибки и fake ordinary-file probe не проходят. Пробник до mutations.
Seven mixed packaging cases разделены; targeting aliases сохраняют проверки.
Preparation skip только symlink subTest, missing/oversize продолжаются. Handoff
external path отделён от directory link, runner ordinary preservation/file link/
nested directory/output link проверяются раздельно. Actual guard assertions
сохранены и исполняются при доступной capability. Actual junction cases не убраны.

## Проверки

RED14новых cases:8failures/5errors/одна existing rejection PASS. После реализации
targeted14:12PASS/2real capability skips. Runner36:31PASS/5skips, включая actual
junction и timeout tests вне sandbox. Packaging169:161PASS/8skips; handoff15:13PASS/
2skips. Точные targeted logs сохранены в build/dota_coach/windows-portability-*,
packaging-portability-20261012.log и handoff-portability-20261012.log.

Первый full141136Z-8e8a46:989passed/23counted skips/5incomplete/1error. Новое
ожидание root ошибочно отнесло third skip fixture старого mixed test к error.
Это ошибка тестового ожидания, не runner. Разделён explicit expected classification;
targeted regression1PASS, повтор полного прогона обязателен и выполнен.

Final report: build/dota_coach/source-checks-20261012T141407Z-b03abd/source-checks.json.

| Набор с неполным покрытием | Passed | Skipped | Exit | Причина |
|---|---:|---:|---:|---|
| python-c2-01-01 | 10 | 3 | 0 | skipped_tests |
| python-c2-01-02 | 24 | 4 | 0 | skipped_tests |
| python-c2-03-01 | 28 | 6 | 0 | skipped_tests |
| python-c2-11-02 | 161 | 8 | 0 | skipped_tests |
| python-c2-10-01 | 13 | 2 | 0 | skipped_tests |
| python-c2-11-03 | 31 | 5 | 0 | skipped_tests |

Полный каталог46suites:1020passed_tests/28skipped_tests, error_suites=[],
incomplete_suites=6. Все suite process exits0; overall verified=false/CLIexit1.
Legacy failed_suites содержит те же6IDs. Остальные40наборов verified=true.
28skips:25symlink capability WinError1314, два deep/long-path случая, один Unix FIFO.
Ни один skip не переименован в PASS; missing/oversize/tamper/integrity/preservation
cases выполнены независимо от symlink availability. Расход токенов/стоимость null.

## Границы и зависимости

Результат — source portability/reporting, не полное security coverage/игровая
приёмка. File/directory symlink, два deep-path случая и FIFO остаются неподтверждёнными
в этой среде. Условия Windows не изменены ради тестов. Native/API/physical input,
server/real identity/lease/ИИ return/map/commonHUD/human second owner не закрыты.
C1-04-01/02/03 повторно проверены: только README/plans, реализации нет. Поэтому
C2-05-03 cancel/AI-return adapter не строился по выдуманному серверному контракту.
Windows channel теперь доступен; прежний cloud audit остаётся историческим фактом.

Один reused final critic не выявил существенных замечаний: strict parser/counters, legacy IDs, capability probe/cleanup и split guards проверены. Это AI review; human second owner остаётся открытым.

Финальные документные проверки: 15 изменённых Markdown / 169 локальных ссылок без разрывов, 28 уроков с пятью обязательными полями, 40 уникальных usage tasks. Граф 50/213 (23.5%) и git diff --check проходят. Product checklist не повышен. Публикация определяется Git history и отдельной сверкой remote SHA.
