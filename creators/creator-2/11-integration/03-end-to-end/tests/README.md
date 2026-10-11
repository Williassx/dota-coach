# tests C2-11-03

Проверки каталога, результатов и CLI помощника на малых fixtures.

[Подпроект](../README.md).

[test_source_checks.py](test_source_checks.py) — 17 проверок. Собственная suite
не запускает полный каталог рекурсивно: реальные процессы ограничены малыми fixtures.
Проверка полноты сравнивает каталог с Node/Python test paths в обеих библиотеках.

[Windows timeout/diagnostics и оставшиеся symlink errors](../reports/windows-runner-2026-10-11.md).
