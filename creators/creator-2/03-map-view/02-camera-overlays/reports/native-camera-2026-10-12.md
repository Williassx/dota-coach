# Native camera: запрос проверен, прибытие не подтверждено

12 октября 2026, Windows, Dota build_id **25845666**, template_map, addon
`dota_coach_c2_camera_20261012`. Ведущий 76, C2; builder/helper 107/114.
[Дизайн](../native-design.md), [план](../native-plan.md),
[машинное свидетельство с hashes/UTC](native-camera-2026-10-12.json).

Ограниченный API/render smoke прошёл семь фаз. Реальная программная активация
`$.DispatchEvent("Activated", button, "mouse")` вызвала существующий native gateway
ровно один раз; его результат отобразился в видимой панели. Production JS/XML/CSS,
fixed HUD13 и probe policy не изменены. Это не проверка физической мыши/клавиатуры.

| Фаза | Фактический результат | Кадр UTC |
|---|---|---|
| bound | Нет цели, кнопка отключена, focus calls=0 | [17:24:07.031](native-camera-r1-bound-2026-10-12.png) |
| selected | TEST Axe/entity123, кнопка доступна, calls=0 | [17:24:19.010](native-camera-r1-selected-2026-10-12.png) |
| refreshed | calls=0, непосредственные before/after позиции равны | [17:24:30.964](native-camera-r1-refreshed-2026-10-12.png) |
| focused | calls=1, requested отображён; arrival не доказан | [17:24:44.430](native-camera-r1-focused-2026-10-12.png) |
| rejected | native.focus(-1) → requested=false; wrapper calls остаётся1 | [17:24:56.618](native-camera-r1-rejected-2026-10-12.png) |
| disposed | API closed, кнопка disabled/hidden | [17:25:08.571](native-camera-r1-disposed-2026-10-12.png) |
| rebound | Новый bind без цели, старый setTarget=false, id getter reads=0 | [17:25:20.526](native-camera-r1-rebound-2026-10-12.png) |

Все семь actual engine TGA преобразованы в PNG и осмотрены, **1280×720**. Панель
справа читается, статус TEST снизу виден. Чёрная minimap и голубая область в нижней
части сохраняются; геометрия настоящей карты не доказана. Проверка getter относится
только к id: она не является полным Proxy/ownKeys instrumentation всех DTO reads.

Выбор и refresh дали calls=0 и непосредственные before/after
`[-127.999977,-7592.000488,127.999962]`. Через1,5s после focus:
lookAt `[-128,-4584.369629,128]`, собственный разрешённый живой realhero
origin `[-128,-64,128]`, **distanceXY=4520.369629**. К rejected фокус вернулся к
`[-128,-7592.000488,128]`. Это перемещение наблюдаемой позиции без выполненного
критерия совпадения с целью. Причина возврата не установлена: влияние ввода,
ограничения template_map и семантика native API требуют отдельной диагностики.
Не менять gateway на слежение или иной camera API ради зелёного результата.

Сборщик создал15outputs, canonical input hashes13 совпадают, retained HUD subtree
сохранён. `resourcecompiler`: UI1/canonical1/map13 compiled, 0failed/0skipped,
все три exit0. Active UI14 плюс retained inert coach_hud отдельно:15compiled
outputs/98838bytes. Map3033412bytes, SHA256
`19c9bd88ad5e0b1b818a0982091a85ac8bb2001b9a4ae9e4c645b5dc95b33302`.
Source-only builder flags остаются false; его JSON не превращён в runtime приёмку.

Локальные raw logs: `build/dota_coach/native-camera-r1-20261012-*`;
bundle `native-camera-20261012T171931Z-b1cb00`. Свежий HERO_SELECTION проверен перед
каждым sv_cheats/dota_pick_hero; PRE_GAME19:23:58 local. Own PID29544 завершён через
quit, отсутствие проверено; Steam12336 сохранён. Первое quit было безопасно
заблокировано из-за string vs ConvertFrom-Json DateTime; одинаковые timestamps
639274225179114656 ticks сверены, строгое сравнение UTC ticks исправлено и проверено.
Нет forcekill, OS/security изменений или чужого клиента.

Проверки: новый builder **7PASS**, existing camera **27PASS**, JS syntax PASS.
Required full `source-checks-20261012T172222Z-1386ef`: **48suites/1031passed/28skipped/
6incomplete/0error suites**, все48process exit0, strict verified=false/CLIexit1.
Причины skips прежние:25symlink Win1314/2long-path/1UnixFIFO. Каталог не запускает
native-command/capture-command, микрофон или Dota как обычные тесты.

Открыты: actual arrival, stable virtual-player→hero mapping, physical input/hittest,
маркеры, масштабирование, real map/обзор, C1/server contract и второй человек.
Следующая диагностика должна раздельно измерить camera motion, native input state
и допустимые границы этой сцены; requested не заменяет эту приёмку.

Один reused final technical critic существенных замечаний не нашёл. Помощник
сборщика остановился по usage limit после записи файлов; root выполнил GREEN.
Это техническая проверка, human second-owner review остаётся открытым.
