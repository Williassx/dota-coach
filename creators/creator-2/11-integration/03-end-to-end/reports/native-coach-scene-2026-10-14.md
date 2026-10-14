# Нативная coach scene: источник ИИ, серверный состав и жизненный цикл

14 октября 2026, установленный Dota build25894101, template_map,1280×720.
[Данные/хеши](native-coach-scene-2026-10-14.json) и real PNG в этой папке.
Это один TEST герой и пять server-confirmed TEST назначений, не реальный состав5×5
или подтверждённые персональные модели. Физические клики не выполнялись.

## Реализация

C1 actual observation→synthetic_policy→order_arbiter получает только собственную
разрешённую позицию и формирует fresh synthetic move. Actual event_log сохраняет
server game time/transition/order links. Existing manual v1 controller остаётся
владельцем grant/lease/Stop/life; sources/stream priority описаны отдельно от
общего будущего coach-command арбитра. Default7/TEST9 kind сохраняют состав.
Новый normal15/TEST18 source recipe проверяетexactpaths/hashes/graph; normalUI7,
TESTUI9compiled с retained canonical layouts. Старые fixed kinds не расширены.

Server roster validator actual Lua подтверждает пять фиксированных TEST профилей
со своим compatibility/coverage; native request не передаёт профили/назначения.
Addressed v1 snapshot принимается C2 exact8field/string-slot consumer, weak coverage
видно отдельно. Это не submit клиентского draft или start/fidelity.
Manual и roster callbacks проверяют IsValid обязательных nodes при bind и перед
render/action/event/tick; dispose перед DTO/getters, отдельные ownership tokens.

## Прогоны и измерения

r1 ownPID6264: ready/capabilities/pause/unpause PASS; TEST ожиданиеexpired упало,
поскольку target1200 был достигнут через3.8 игровыхсекунд. Actualarrival был
правильным, сохранены negative log/frame. Изменён только TEST distance на1800.

r2 ownPID5708: **12 API фаз PASS**,10actualPNG. Pause2.202s client wall: delta game0,
remaining4.799999237 unchanged, AI/manual counters unchanged. Unpause продолжил тот
же срок; expiry/actualnewAI observed через **5.033336639 игровых секунд** от grant.
Строгая остановка ровно5.000 не заявляется: .1Think обработал deadline на следующемтике.
Movement distance306.4491XY послеactualmove; cancel/arrival отдельноизвестныпо
transition и последующемуactualAIorder/изменениюorigins. Death INACTIVE/alivefalse;
respawngeneration1→2; oldgeneration move rejected/stale_generation безновогоmanualorder.
Actual rebind получилserverAIstate, staleoldhandleProxyDTOreads0.

PauseGame/ForceKill/RespawnHero capability сначала измерены наactualengine, вызовы
тольковTESTwrapper/ownhero. RawnativeTime() иgameTime разведены; clientDate.now
измеряетwallinterval. Ниcvars, privacy/security, чужойматч илиSteamloginне менялись.
OwnPIDs проверены поid/startUTC и завершены VCon; rawlogs/accountmetadata ignoredbuild.

[Серверный TEST состав](native-coach-r2-ready-2026-10-14.png) ·
[Пауза](native-coach-r2-paused-2026-10-14.png) ·
[Смерть](native-coach-r2-dead-2026-10-14.png) ·
[Возрождение](native-coach-r2-rebound-2026-10-14.png) ·
[Повторное подключение](native-coach-r2-reloaded-2026-10-14.png).

Capturer запрашивает screenshot послеloggedphase; задержкаVCon может дать более
поздний экран. Имена phase не атомарная привязкакадра, JSON еёfalse. Все13PNG двух
прогонов1280×720/hashпроверены, contactview просмотрен, r2ready полноразмерно.
Штатная белая minimap/крайtemplate вr1 неимеют установленнойпричины, mapacceptanceopen.
При просмотре найден невидимый serverSyncButton (auto width+child100%); generated
layout получил явныеwidth/height/style, fixed15/18 counts не изменились.
Обычная fresh ui3 после этой визуальной корректировки дала actual AI/server-linked
панель и все пять TEST assignments; [реальный кадр](native-coach-ui3-ready-2026-10-14.png)
подтверждает видимую кнопку «Обновить серверный состав» и weak coverage. Normal15/7,
TEST driver отсутствует. OwnPID9516 quit→gone. Предыдущий normal ownPID22208
пропустил hero selection до захвата; отрицательный log сохранён, quit→gone.
Всего14 actual frames; Steam13704 запущен, не затрагивался; прежний12964 уже отсутствует, причина не установлена.

## Source и peer проверки

Полный fresh каталог:89 suites/1390PASS/28skip/6incomplete/0errors/allprocessesexit0,
strictfalse runnerexit1. Report build/dota_coach/source-checks-20261014T062652Z-8b55ce/source-checks.json.
Peer C1↔C2 выявил и исправил5P2: kindpool, teamresourceconflict, nested save alias,
manual/roster invalidnode lifecycle. RED→GREEN и независимые regrade сохраняются
в соответствующих ownerreports. Это не product/legal/human approval.

Следующиеусловия: physicalmouse/hittest через supportedканал, полноценные map/visibility,
realvoice/профили, general preparation submit/coach commands/5×5/result/performance.
Прототип служит конкретным техническим доказательством, не готовым продуктом.
