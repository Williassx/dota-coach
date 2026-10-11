# Source-панель истории: облачная проверка

2026-10-11 UTC; база157a3b0; основной исполнитель отдела 2.
Канонические JS/XML/CSS созданы в своём subsection; [panel-design](../panel-design.md)
и [план](../panel-plan.md) записаны до реализации. Используется одна private pure история.

Первый RED14VM FAIL +2XML ERROR из-за отсутствия implementation/layout.
После реализации целевой прогон **16PASS**: explicit bind/no demo, настоящие стадии
Orders, captured actor, latest6/hiddenStored/drop counter, copied projection, очистка
до Proxy ownKeys, invalid gate/recovery, missing/hidden/invalid/replaced nodes,
ownership before discovery, partial cleanup/rebind, busy before native/DTO reentry,
dispose during DTO, closed old binding vs fresh root, sourceclosed/root hidden,
literal HTML-like text и exact inert XML dependencies/IDs. Game API закрыт VM proxy.

Нет watcher: invalidity выявляется по вызовам API; caller отвечает за доставку
снимков/своевременный dispose. Проверки не подтверждают native внешний вид, scroll/
hittest, Source 2 compilation или игру. Source package/общий HUD/сервер/другой
человеческий владелец остаются открытыми.

Полный actual прогон:38suites/826PASS без fail/skip/cancelled/todo. Отчёт:
`build/dota_coach/source-checks-20261011T091800Z-2e9abe/source-checks.json`.
График библиотеки34/202(16.8%), нативные пункты не закрыты.

Один final critic выявил isDisposed без проверки дерева. Дефект воспроизведён
новым тестом (15VM/1FAIL), исправлен busy guard + lifecycle preflight. Целевой
результат17PASS; итоговый full38suites/827PASS без fail/skip/cancelled/todo.
Актуальный отчёт: `build/dota_coach/source-checks-20261011T092016Z-bb7e0a/source-checks.json`.
Второй review не запрашивался; полный прогон повторён из-за нового production кода.

Cloud draft revision39 проверен чтением, остальные поля сохранены; требуется
публикация среды, которая недоступна инструментами. Экономный порядок действует
по AGENTS.md, telemetry tokens/cost null.
