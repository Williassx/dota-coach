# C2-05-02 — локальные предложения мыши

[Родитель](README.md) · [API](../notes/mouse-targeting.md).

Дата UTC: 2026-10-11. База: 707eac8. Исполнитель: root/создатель 2.
Реализована одна pure private модель. Actor фиксируется явным capture; следующий
propose заменяет действие и сохраняет actor. Move, attack enemy hero, last_hit
enemy creep и deny ally creep различаются; ally hero/dead/non-ready отклоняются.
Нет native ввода, transport, permission/lease или фактического игрового эффекта.

Первый RED: 16 тестов отсутствующего модуля. После реализации 16 GREEN.
Добавлен meaningful integration test с реальным Targets.view и его expiry:
17 PASS. Targeted 2 suites / 53 PASS. Full 43 suites / 915 PASS, fail/skip/cancel/
todo = 0. Логи: `build/dota_coach/source-checks-20261011T132450Z-e27f12/source-checks.json`.
Новый Node suite внесён в каталог; catalog completeness проверяет все реальные
Node/Python paths. Повторный полный прогон без изменений не нужен.

Самостоятельная проверка: exact own fields/accessor/symbol/extra no-read, primitive
числа без coercion, copied input/output, immutable captured identity, serial/reset,
ready/visible input schema, non-ready target не инспектируется, index не выводится,
busy/reset/dispose/cancel-commit и closed API без чтения. Модель не подписывает
наблюдение ready как permission и не принимает решение о пороге добивания.

Один повторно используемый финальный критик завершил проверку без существенных
замечаний; новые агенты/повторное review не запускались. График 42/209 (20.1%).
Cloud draft revision 44 сохранён/read-back: 43 / 915 и новый API, другие поля
сохранены; это draft, callable activation/publish нет.

Native мышь,
point/geometry/identity/clock, real target permissions, серверные правила добивания,
lease/manual AI return, UI/остаток времени и другой человеческий владелец открыты.
Во всех view canSend/nativeConfirmed/sourceAuthorizationConfirmed=false.
