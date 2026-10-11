# Windows runner: тайм-аут и диагностика завершения

[Подпроект](../README.md) · [Спецификация](../design.md) · [План](../implementation-plan.md)

Роль: C2 проверка исходников. Python3.12.14/Windows; код только existing runner
и его tests. Новых механик/аддонов/контрактов/настроек ОС нет.

## Причина

Предыдущий полный прогон показал timeout_termination_failed и позднюю запись
дочернего fixture. Диагностический wrapper сохранил настоящий ответ штатного
taskkill /PID <owned pid> /T /F: returncode1, ERROR: Access denied в sandbox.
Тот же fixture вне sandbox: returncode0, owned process завершён. Existing
test_timeout_stops_owned_child_processes также прошёл вне sandbox. Это ограничение
канала, а не подтверждённая ошибка штатного taskkill/tree termination алгоритма.
Обход прав ОС, Developer Mode и расширение privilege не выполнялись.

Отдельный test_partial_selection_does_not_need_node_and_is_reported ошибочно
mock-скрывал все shutil.which, включая taskkill. Mock теперь скрывает только
Node; тест проверяет отсутствие поиска Node и поиск taskkill на Windows.
Production preflight и обязательность taskkill сохранены.

## Исправление и проверка

Runner раньше направлял taskkill stdout/stderr в DEVNULL, скрывая причину отказа.
Теперь output идёт в существующий suite log; catch записывает exception после
owned process tree termination failed. reason остаётся timeout_termination_failed,
fallback kill не выдаётся за доказательство остановки потомков. Summary/strict
skip policy/argv/kill scope не менялись.

Новый RED test увидел пустой log вместо access denied. GREEN: synthetic refusal
оставляет оба диагностических сообщения в log и verified=false. Первый запуск
нового stub некорректно обращался к DEVNULL как к handle; исправлен test stub,
затем записан надлежащий RED. Smoke absence-of-Node test прошёл в sandbox.

Вне sandbox выполнены три timeout tests: все3passed, включая настоящий owned
child и искусственный отказ завершения. Local log:
build/dota_coach/runner-timeout-green-20261011.log. Диагностика:
runner-timeout-diagnostic-20261011.json; RED:runner-termination-log-red-20261011.log
в той же build/dota_coach. Owned children создаются только тестами.

Полный каталог выполнен вне sandbox после изменения кода:
build/dota_coach/source-checks-20261011T194234Z-6d0d0b/source-checks.json.
46suites,752passed_tests,6failed, verified=false. Собственная suite:17tests,
15passed/2errors создания symlink (WinError1314),0failures. Timeout и partial
selection errors исчезли; suite всё ещё не зелёная и её15passed не входят в752.
Packaging suite также имеет8symlink errors; handoff suite2symlink errors.
Foundation и map suites с existing пропусками остаются invalid_summary.
Ни один тест не пропущен/ослаблен дополнительно для получения зелёного результата.

Этот результат подтверждает исходники и ограниченный механизм owned timeout
в проверенном режиме исполнения. Native input/hittest, сервер/lease/AI return,
микрофон и совместная человеческая приёмка остаются открытыми.
