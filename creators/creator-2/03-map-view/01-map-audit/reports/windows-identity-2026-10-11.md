# Windows: стабильная идентичность manifest и map files

[Подпункт](../README.md) · [Спецификация](../design.md) · [План](../windows-identity-plan.md)

Ведущая роль: C2 файловый аудит. Python3.12.14; только existing C2 helper/tests,
без изменения C1, прав ОС или игровых ресурсов.

## Причина и исправление

Повторный Windows прогон воспроизвёл ложный manifest_changed: два association
subtests упали. Дополнительные100 fixture writes/read дали70manifest_changed и
30associated. Совпали dev/ino/size/mtime, но lstat/fstat вернули разные ctime.
Отдельная серия50/50 показала это различие при одинаковом st_birthtime_ns.
Почему legacy ctime внутри Windows/Python различается, отдельно не установлено.

Python документирует deprecated Windows ctime и явное birthtime начиная с3.12:
[официальная документация](https://docs.python.org/3.12/library/os.html#os.stat_result).
Cross-API identity теперь использует birthtime на win32 при его наличии;
POSIX и legacy fallback сохраняют ctime. После чтения path snapshot сверяется
с исходным path snapshot, descriptor — с исходным descriptor snapshot,
включая ctime на всех платформах. Нет tolerance/retry/sleep; guards/root
association/hash budgets/link/reparse policy сохранены.

RED: Windows identity test упал, same-API helper отсутствовал; POSIX test прошёл.
GREEN: четыре новых test methods, включая четыре ctime-only mutation subcases
(manifest/map × path/handle), прошли. Изменение каждого identity поля и existing
file mutation остаются отказами. Первый запуск новых tests имел FileExistsError
в повторном создании fixture; исправлена организация теста, не production code.

## Проверки

`python -m unittest discover -s creators/creator-2/03-map-view/01-map-audit/tests -v`
с bundled Python:34tests,28passed,6skipped,0failures/errors. Пропуски existing:
FIFO, symlink privilege/long paths; новых skip guards нет. Повтор100 fixture
associations после исправления:100associated,0manifest_changed.

Локальные RED/GREEN logs: build/dota_coach/map-identity-red-20261011.log и
map-identity-green-20261011.log. Diagnostics: map-identity-diagnostic-20261011.json,
map-stat-birthtime-20261011.json, map-identity-100-green-20261011.json в той же
build/dota_coach. Полные логи и инвентаризация остаются вне Git.

Реальный bounded read-only audit: build_id25845666 associated;83entries,
80resources,44complete hashes,11100022bytes read; partial_inventory и
truncated=true из-за лимита80files, CLI exit1. Runtime/geometry=false, patch=null.
Отчёт: build/dota_coach/native-map-identity-20261011-local.json. Это не полное
обследование ресурсов и не проверка загруженной карты.

Новый полный runner:
build/dota_coach/source-checks-20261011T192232Z-6b37d4/source-checks.json.
46suites/752passed_tests/6failed, verified=false. Map suite завершила34tests
без failures/errors, но runner отмечает invalid_summary из-за skipped tests;
её28passed не включены в aggregate752. Строгий статус не ослаблен.
Остальные failed suites: python-c2-01-01, python-c2-01-02, python-c2-11-02,
python-c2-10-01, python-c2-11-03. Полная Windows регрессия остаётся открытой.

Это диагностическое чтение, не атомарный security snapshot, не подтверждение
патча, обзора/геометрии, игровых полномочий или C1 native приёмки.
