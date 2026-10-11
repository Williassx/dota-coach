# Windows: настоящие directory reparse points

[Подпроект](../README.md) · [Spec](../design.md) · [План](../implementation-plan.md) ·
[Тесты](../tests/test_directory_redirect_guards.py)

Ведущая роль: C2 проверка границ файлов. Existing production guards и все
file-symlink tests сохранены. Цель — дополнительно проверить actual directory
redirect без изменения Developer Mode/privileges, а не получить искусственный
полный PASS на Windows.

## Среда и сценарии

Установленный wsl.exe найден, но --list --quiet вернул help/exit1, --status —
exit50. Локальная Linux среда для выполнения tests не подтверждена; WSL/дистрибутивы
не устанавливались. PowerShell New-Item -ItemType Junction создал scoped fixture
в build/dota_coach без изменения прав; observed LinkType=Junction,
Attributes=Directory,ReparsePoint. Это другое условие, чем file symlink.

Новые три acceptance tests создают настоящие Windows junction во временных
каталогах теста. Для POSIX предусмотрен directory symlink; эта ветка в текущей
Windows сессии не запускалась. Metadata подтверждает redirect, guard должен
выдать именно Symlink/reparse ValueError. Path.open дополнительно перехвачен:
попытка открыть external fixture через alias провалит тест.

- read_source отклоняет источник под junction до открытия external file.
- output_path отклоняет junction ancestor; external new-output не создан.
- load_catalog отклоняет nested test directory redirect, build output отсутствует.

Контрольный внешний файл не изменён. Cleanup проверяет lstat reparse/symlink и
удаляет только redirect без рекурсивного обхода target, затем проверяет файл.
Отдельная capability junction также удалена nonrecursive rmdir после проверки
пути и target; контрольный target сохранён. Symlink/reparse guards не ослаблены.

## Фактический прогон

Команда с bundled Python3.12.14:
`python -m unittest discover -s creators/creator-2/11-integration/03-end-to-end/tests -p test_directory_redirect_guards.py -v`.
3tests/3passed, без skip/errors. После добавления external-open assertions
выполнен свежий прогон:3PASS; log build/dota_coach/windows-junction-acceptance-20261011.log.
Production исправления не требовалось: это evidence существующих guards.

Полный runner вне sandbox (для owned taskkill) после добавления tests:
build/dota_coach/source-checks-20261011T201328Z-306f81/source-checks.json.
46suites/752passed_tests/6failed, verified=false. Own runner suite20tests:
18passed/2file-symlink errors WinError1314. Все3new tests также PASS в общем логе;
их результат не включён в aggregate752 из-за отказа всей suite. Existing8packaging
и2handoff symlink errors, foundation/map skip-summary ограничения остаются.

Это частичное подтверждение Windows filesystem guards. File-symlink coverage,
полная Windows регрессия, native UI/input/hittest, C1 transport/lease/AI return
и человеческая совместная приёмка остаются открытыми. Junction evidence их не заменяет.
