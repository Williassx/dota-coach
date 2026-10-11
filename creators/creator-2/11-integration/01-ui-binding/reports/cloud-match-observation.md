# C2-11-01/02 — общая сцена наблюдения матча

[Родитель](README.md) · [API](../notes/match-observation.md).

Дата UTC: 2026-10-11. База: 638f377. Исполнитель: root, создатель 2.
Один owned parent связывает две канонические private панели. Источники независимы;
invalid input одной области не меняет готовность другой. Parent скрывается до
DTO reads, changing child очищает своё отображение. Повреждение обязательного
элемента закрывает обе области. Busy/ownership до native callbacks, explicit
dispose/reopen, старый API не пишет в нового владельца. Watcher/transport нет.

Сначала дизайн и план. Node suite: 14 RED missing binder → 14 GREEN.
Packaged suite: 8 сценариев, 5 RED unsupported recipe errors / 3 guard PASS →
8 GREEN. Первый targeted: 4 suites / 154 PASS, full: 42 suites / 897 PASS.
Финальный критик выявил failed-acquisition visibility: попытка group bind скрывала
parent независимо работающего child, хотя не получила его binding. Regression:
15 Node / 14 PASS / 1 FAIL. Исправление: claimed только после обоих handles,
ранний cleanup восстанавливает prior parent visibility, не пишет status и закрывает
лишь созданные child handles. Проверены оба варианта независимо owned child.
Финальный targeted: 155 PASS; full повтор после production fix: 42 / 898 PASS,
fail/skip/cancel/todo = 0. Логи:
`build/dota_coach/source-checks-20261011T131535Z-8ec1fc/source-checks.json`.

9-й fixed kind: 10 assets / 2 layout inputs / 9 links / 38 unique IDs.
Дизайн при подсчёте уточнён до 10 ресурсов до реализации recipe: пять JS,
три CSS и два XML. Canonical input validators вынесены в validate_layout у прежних
двух policy без изменения standalone ограничений; composer их переиспользует.
Raw input fingerprints и повторная композиция verifier подтверждают текущие XML.
Собственные и generated исходники не дублируются в библиотеках.

Первый handoff: `build/dota_coach/probe-ui-20261011T131200Z-2b115c`. После исправления
создан новый final handoff: `build/dota_coach/probe-ui-20261011T131534Z-4dc453` и companion
снаружи. Native flags false; установки нет. Actual packaged XML и пять JS в одном
VM проверены на public/unknown, captured actor, invalid isolation, plain Labels и
dispose. Registry equality проверяет все 9 вариантов, прежние сценарии прошли.
Самостоятельный просмотр production diff выполнен. Один reused final critic,
один существенный finding исправлен, других нет. Новые агенты и второе review
не запускались. Первый handoff сохранён; после изменения источника он не считается
актуальным для текущей проверки verifier. Final пакет сверяет текущие bytes.

График: 41/208 действий (19.7%). Cloud draft revision 43 сохранён/read-back:
42 / 898 и девять вариантов пакетов; прочие поля сохранены. Draft не активирован,
callable публикации среды нет.

Не проверены C1/общий server contract/реальный public источник, bootstrap всей
игры, Source 2 compilation/читаемость/геометрия/hittest, native история и второй
человеческий владелец. Нет заявлений о готовой карте, полной игре или игроках ИИ.
