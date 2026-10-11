# Проверка общего порта запроса

[Подпункт](../README.md) · [План](../intervention-port-plan.md).
Дата UTC: 2026-10-11. Основа: a197706.

14 начальных сценариев RED→GREEN. Затем три отдельных RED→GREEN: смена selection
в staging setter, из последней проверки дерева, configured flow без send панели.
Причина первых двух: callbacks между сравнением view и begin. Повторное сравнение
после staging и атомарный requestPort.begin не допускают невидимого адресата.

Новый suite: 19 PASS. Полная проверка: 29 suites / 667 PASS, failures=0.
Логи сессии /tmp/intervention-port-final-regression-0..28.log и
/tmp/intervention-port-final-regression-results.json не являются переносимыми артефактами.
Actual build/verify: build/dota_coach/probe-ui-20261011T073550Z-ed7957:
6 ресурсов/5 ссылок, package_verified=true; compiled/runtime=false.

Проверены shared selection/gate, captured actor, ACK/timeout/late response,
stale screen, внешний MANUAL/cancel timer, duplicate ownership, dispose/no old
DTO reads, busy getter и malformed port. Единственные selection/panel изменены;
новый Requests в портовой ветке не создаётся. Standalone recipes/ветка сохранены.
Общий экран/Roster panel/recipe, native, server authority, lease, mouse input,
возврат ИИ и другой человеческий владелец остаются открытыми.

Один итоговый критик нашёл блокировку busy при смене shared request после установки
ACK timer, но до dispatch. В одной fix pass добавлены два RED→GREEN: наблюдён MANUAL
или новая epoch очищает запрос на этом шаге. Активный ticket/stage проверяются;
при прекращении pending таймер отменяется, busy снимается и экран обновляется.
Полная регрессия после изменения кода повторена, без skips/cancelled/todo.
