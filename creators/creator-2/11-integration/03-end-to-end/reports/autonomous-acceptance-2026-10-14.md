# C2-11-03 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Цепочка выполнена на клиенте; скриншот макета не заменяет запуск.

## Фактическое покрытие

Canonical source runner/catalog запускает проверенные suites, различает skipped/incomplete/error и сохраняет strict verifiedfalse при28skips.

## Непроведённые проверки и зависимости

Полная клиентская цепь состав→подготовка→приказы→мышь→итог не выполнена. Native one TEST hero не матч5×5, voice failure/readability не end-to-end acceptance.

## Прочитанные материалы и воспроизводимость

- [tests/01-native-coach-scene/native-command.ps1](../tests/01-native-coach-scene/native-command.ps1) — SHA256 e551e299506aa78659753c8d8fbbf89d471c2fd1bbd693cc2aeff1026e93d3cf.
- [tests/symlink_capability.py](../tests/symlink_capability.py) — SHA256 ddd3f16cfe17f6b4d38dbcffc3a2374ce93e7340b01e634a49bd7c9a05242fcb.
- [tests/test_directory_redirect_guards.py](../tests/test_directory_redirect_guards.py) — SHA256 ad83a82ab598567c88e6ed63b5c5179ccec237a2dfd2b3668e9857e9cc3cff75.
- [tests/test_source_checks.py](../tests/test_source_checks.py) — SHA256 d6f1a54f11953cbddf9fb51ccf60bcffd5d1b1ab1f5b7570185be913891780a0.
- [tests/test_symlink_capability.py](../tests/test_symlink_capability.py) — SHA256 37d66134c5ad975742d76ddbab0979c63a42afdf9f400f49de93ad7a12d68999.
- [tools/run_source_checks.py](../tools/run_source_checks.py) — SHA256 b23fae208ea1d4ddd1f4312412bcc084d088761e53a15a26ac6c72c45d206274.
- Предыдущий отчёт: [cloud-source-checks.md](cloud-source-checks.md).
- Предыдущий отчёт: [creator-1-review-2026-10-13.md](creator-1-review-2026-10-13.md).
- Предыдущий отчёт: [native-coach-scene-2026-10-14.md](native-coach-scene-2026-10-14.md).
- Предыдущий отчёт: [windows-portability-2026-10-12.md](windows-portability-2026-10-12.md).
- Предыдущий отчёт: [windows-reparse-2026-10-11.md](windows-reparse-2026-10-11.md).
- Предыдущий отчёт: [windows-runner-2026-10-11.md](windows-runner-2026-10-11.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.

## Обновление доказательств после исходного среза

Прочитан новый [native coach scene report](native-coach-scene-2026-10-14.md) и JSON: автор root сообщает12APIфаз r2PASS/13actualPNG с сохранённым negative r1, pause2.202s/game delta0, death/respawn generation1→2 и stale oldhandle DTOreads0. Это actual oneTEST hero/server TEST roster, не physical input или полный5×5. Source89/1390PASS/28skip/6incomplete/0errors/strictfalse. Этот reviewer не запускал Dota; новое свидетельство отдельно от старых fixtures.

## Повторное документальное рассмотрение normal UI3

14PNG двухAPIruns+normalUI3 независимо проверены1280×720/SHA256 безрасхождений. ActualnormalUI3 screenshot визуально просмотрен: serverSynccaption,5TESTassignments иweakcoverage читаемы; справаAI/serverremaining0.0. Это ordinaryUI15source/7compiled безTESTdriver, не physicalclick/hittest proof. Rootreceipt actualcurrentsha рассмотрен C2peer отдельно. Source snapshot89/1390/28skip/strictfalse остаётся датированным; следующий fullrun root отдельно.
