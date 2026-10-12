# Проверки source handoff

[Подпункт](../README.md) · [test_ui_handoff.py](test_ui_handoff.py).
Проверяют делегирование existing helpers, integrity/metadata/сохранность, не Dota.

File/directory symlink tests используют [общий capability probe](../../../11-integration/03-end-to-end/tests/symlink_capability.py). External-path/preservation checks выполняются независимо; Windows15tests/13PASS/2explicit WinError1314 skips. [Source отчёт](../../../11-integration/03-end-to-end/reports/windows-portability-2026-10-12.md).
