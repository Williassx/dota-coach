# tests C2-11-03

Проверки каталога, результатов и CLI помощника на малых fixtures.

[Подпроект](../README.md).

[test_source_checks.py](test_source_checks.py) — 25 проверок. Собственная suite
не запускает полный каталог рекурсивно: реальные процессы ограничены малыми fixtures.
Проверка полноты сравнивает каталог с Node/Python test paths в обеих библиотеках.

[Windows timeout/diagnostics и оставшиеся symlink errors](../reports/windows-runner-2026-10-11.md).

[test_directory_redirect_guards.py](test_directory_redirect_guards.py) — ещё три
actual directory redirect проверки; Windows junction/POSIX directory symlink.
Исторический Windows3PASS: [ограничения](../reports/windows-reparse-2026-10-11.md).

[symlink_capability.py](symlink_capability.py) — общий test-only probe реальной
file/directory ссылки в owned fixture. Только Windows1314 даёт явный skip до
мутаций; production guards не меняются. [test_symlink_capability.py](test_symlink_capability.py)
содержит8проверок known/unknown errors, fake probe и настоящих capabilities.
Всего36tests; source suite с пропусками остаётся incomplete/verified=false.
