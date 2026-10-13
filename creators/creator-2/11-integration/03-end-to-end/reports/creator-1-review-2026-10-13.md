# Рассмотрение передачи создателя 1

Поручение пользователя выполнено в существующем checkout. Переданные коммиты
`1c44da4`, `b1f2c48`, `71b20c0` уже находились поверх `99555eb` в локальном main:
172 изменённых файла C1. Переносить или копировать исходники в C2 не потребовалось.
Один root автор общих файлов; helper изменял только voice gate и его тесты.
[Локальный дизайн](../../../../creator-1/11-integration/01-ui-contracts/review-design-2026-10-13.md).

## Исправления, подтверждённые исполнением

- Арбитр больше не принимает coach/AI во время MANUAL; неверные id/NaN/infinite/
  fractional revision не портят seen/highwater. В одной revision ниже принятого
  приоритета отклоняется; новая revision начинает новый epoch. Это streaming gate,
  не пакетная очередь и не отмена уже исполненного действия.
- Voice producer выдаёт поддерживаемый `source=coach`, отдельно `origin=voice`;
  проверяет форму и типы DTO. Все voice actions закрыты во время MANUAL.
  Предварительный `admit` не записывает IDs/revision: commit владеет общий арбитр.
- Return manager имеет публичный `EnterManual` и требует строго новую observation
  revision при `FinishReturn`; три pure цикла cancel/timeout/release проходят.
  Число от caller не доказывает настоящую переоценку в Dota.
- Binding возвращает копию snapshot; Bind/Respawn одинаково отвергают неверный
  owner/index. Отказ MANUAL очищает captured actor.

Lua исходники реально исполнены в тестовом Lua 5.1 через изолированный Lupa 2.6.
Wheel `lupa-2.6-cp312-cp312-win_amd64.whl`, 1688529 bytes, SHA256
`c735a1ce8ee60edb0fe71d665f1e6b7c55c6021f1d340eb8c865952c602cd36f`
сверен с PyPI metadata; зависимости только в ignored `build/dota_coach/c1-review-lua-20261013`.
Тесты не устанавливают пакеты на import. Без Lupa — явные skips, не ложный PASS.

## Проверки

Семь новых Lua сценариев сначала дали RED (7 errors на старой реализации), затем
GREEN. Итоговый набор — **8 PASS**, включая actual voice producer→actual Lua arbiter
и повтор ID. Voice gate — **13 PASS**, RED/GREEN logs сохранены.

Общий каталог вырос 50→85 за счёт 35 отсутствовавших наборов C1; существующий C1
environment набор сохранён. Верхний предел 64 уже не вмещал реальную библиотеку:
расширен до 128, byte/path/schema/ownership guards сохранены. Матрица проверяет
полное владение всеми существующими Node/Python наборами.

Итог `source-checks-20261013T105504Z-498303`: **85 наборов, 1242 PASS, 28 skips,
6 incomplete, 0 error suites**, все 85 процессов exit0. Строгий `verified=false`
и CLI exit1 сохранены. C1 отдельно: **36 наборов /188 PASS /0 skips /0 errors**.
Предыдущий sandbox timeout отказ сохранён; после передачи C1 отдельный ошибочный
прогон воспроизвёл отсутствие 35 путей в каталоге. Прогон во время helper RED не
выдаётся за итоговый. [JSON metadata](creator-1-review-2026-10-13.json).

Генератор C1 подтверждает 112/181 (61.9%) и равенство трёх progress артефактов;
новые checkbox не отмечались. BLOCKERS пересобран: 69 открытых полных действий,
вместо устаревших 75; исправлены относительные ссылки и историческая передача.
Один итоговый критик обнаружил разрывы и после исправлений не нашёл новых
существенных ошибок в согласованном объёме. Это техническое рассмотрение C2,
не human/native приёмка всей игры.

## Открытые границы

Общий контракт пока только предложение: entityIndex C1, stable actor ID C2,
revision, vocabulary/action и форма target ещё требуют единого authoritative
enrichment/transport. C2 `hold/regroup` не объявлены C1 `gather/attack` автоматически.
Арбитр пока не исполняет engine orders, не привязан к actor/lease и не имеет
bounded lifetime seen-registry; это предстоит определить с серверным lifecycle.

Нативные C1 r1–r8 рассмотрены как переданные отчёты, самостоятельно не повторены.
Attack causality, ownership, настоящая карта/матч/возврат ИИ остаются открытыми.
Остальные Lua модули преимущественно проверены статически. Некоторые Python pure
модули требуют отдельной строгой валидации malformed input и защиты mutable aliases;
TEST heldout API пока не обеспечивает автоматический lock/split/coverage. Передача
не даёт оснований объявлять все C1 части готовыми к подключению в live игру.
Реальные данные/персональное сходство/права/Valve/release/human owner не закрыты.
