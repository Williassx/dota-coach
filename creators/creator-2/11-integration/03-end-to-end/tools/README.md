# tools C2-11-03

Единый исполнитель каталога source checks; не устанавливает аддон.

[Подпроект](../README.md).

[run_source_checks.py](run_source_checks.py) — валидирует единый каталог, запускает
полный или явно частичный прогон, сохраняет новые логи и source-only JSON.
Защита путей и выходного каталога переиспользуется из foundation builder.

Output штатного Windows taskkill и ошибка owned tree termination остаются в
suite log. Sandbox Access denied не подтверждает остановку потомков;
[проверенные режимы и ограничения](../reports/windows-runner-2026-10-11.md).

Consistent success summaries с skipped cases дают skipped_tests/incomplete_suites и verified=false/exit1. error_suites содержит process/summary errors; legacy failed_suites сохраняет все unverified IDs. [Актуальные Windows результаты](../reports/windows-portability-2026-10-12.md).
