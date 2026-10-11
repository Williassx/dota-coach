# Windows: сравнение метаданных файлов

Спецификация: [design.md](design.md). Ведущая роль — C2 аудит файлов; область —
existing inspect_map_workspace.py, его tests и отчёт. Исполнитель один.

Проблема воспроизведена на Python3.12.14: после повторной записи неизменённого
fixture lstat/fstat иногда возвращают разные st_ctime_ns при одинаковых
dev/ino/size/mtime/birthtime. Проверка принимает это за manifest_changed.
Причина различия legacy поля внутри Python/Windows не установлена; данные
двух API нельзя сравнивать по этому полю как по одинаковой семантике.

Решение: только на win32 при доступном st_birthtime_ns использовать его в
cross-API identity; POSIX и legacy Python сохраняют ctime. Проверку ctime
сохранять для двух snapshot одного API: path до/после, handle до/после.
Нет retry/sleep/tolerance и ослабления symlink/reparse, лимитов или связи root.

1. RED для Windows cross-API identity и отдельной same-API metadata identity;
   POSIX ctime/legacy fallback и изменения каждого identity поля покрыты.
2. Исправить helper; сохранить дескрипторный snapshot перед чтением, сравнить
   каждый источник сам с собой после чтения в manifest и digest. Проверить
   ctime-only изменения пути/дескриптора для обоих входов, existing mutation test.
3. Полная map suite, повтор 100 fixture associations и реальный bounded audit;
   новый полный source runner. Отчёт разделяет passed, skipped, failed и runtime.
4. Ссылки/graph/diff/один final critic; журнал/ledger, обычный main push с SHA check.

Приёмка исправления: ложный статус на стабильных fixtures отсутствует, настоящие
изменения metadata/hash не получают build_id/SHA. Это не атомарный security
snapshot и не подтверждение версии патча, карты или native gameplay.
