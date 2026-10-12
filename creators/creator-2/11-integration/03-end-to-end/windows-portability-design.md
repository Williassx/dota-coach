# Честный Windows source report

[Родитель](README.md). Root/роль114; пользователь поручил продолжать самостоятельно.
Existing source regression остаётся strict: skips/cancelled/todo не дают verified.
Проблемы текущего Windows прогона: OK(skipped=N) назван invalid_summary; symlink
fixture creation WinError1314 до guard; sandbox taskkill Access denied.
Разрешённый targeted run вне sandbox подтвердил timeout tests без failures.

Сохраняем failed_suites как все unverified IDs для совместимости. Добавляем
skipped_tests и incomplete_suites/error_suites; reason skipped_tests только для
однозначного согласованного exit0 summary с пропусками. Passed — реально выполненные
успешные tests из согласованного success summary; failed/недостоверный summary не
добавляет passed count. CLI exit1/verified=false при incomplete, source/native flagsfalse.
Malformed/duplicated/empty summaries, process errors/timeout по-прежнему failures.

Один test-only helper require_symlink(test_case, root, directory=False) сначала
создаёт реальную пробную ссылку в отдельном owned temporary child. Только Windows
OSError.winerror1314 сообщает explicit unsupported file/directory skip. Иные ошибки
не скрываются; при доступности реальные guard assertions исполняются. Смешанные
symlink/tamper/preservation cases разделяются, чтобы доступные проверки не терялись.
Actual junction tests сохраняются отдельно; они не заменяют symlink coverage.

Root владеет runner/helper/tests/docs. Reused windows_learning владеет только
packaging test portability и handoff tests по заранее согласованному helper API.
Production guards/OS/privileges/Developer Mode/C1/shared contracts не изменяются.
Приёмка: RED→GREEN summary/capability regressions, targeted source suites, full
прогон вне sandbox с правом завершать исключительно свои тестовые процессы,
точный skipped/error breakdown, один final critic, graph/links/journal/publication.
