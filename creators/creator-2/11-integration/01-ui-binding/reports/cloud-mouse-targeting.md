# Локальный интегратор свежести цели

[Родитель](README.md) · [План](../mouse-targeting-plan.md).
2026-10-11, Linux cloud; root inline, один reused final critic после source блока.

Real Targets + MouseProposals + MouseProposalPanel, без copied implementations.
17 RED missing binder → 16 PASS/1 FAIL; ошибочное ожидание записи в destroyed root
исправлено: invalid native свойства не трогаются. Отдельный regression, 18 PASS.
Targeted 4 suites / 84 PASS, full 46 / 956 PASS.

Финальный критик нашёл TTL race: после последнего clock ещё были native callbacks.
Два новых regression (action/view, clock barriers1..6) воспроизвели 18 PASS/2 FAIL.
Native checks перенесены перед final Targets.view, после successful read нет native
callbacks. Final targeted 4 / 86 PASS, full 46 suites / 958 PASS, zero fail/skip/
cancel/todo; source-checks-20261011T142505Z-5c8470. Full повторён из-за production fix.
Повторного review/новых агентов нет. Истечение/потеря/смерть снимают target proposal,
actor сохраняется. Move независим, новое выделение не переиздаёт действия.

Busy до clock/DTO/native; disposal и tree damage закрывают оба private components,
old handles не пишут новый bind. Clock/entity/projection локальные и предварительные:
canSend/nativeConfirmed/sourceAuthorizationConfirmed=false, no hooks/transport/
lease/commands/gameplay/AI return. Рецепт standalone mouse остаётся прежним; новый
coordinator ещё не упакован. Source2/Windows/C1 и второй человеческий владелец открыты.
