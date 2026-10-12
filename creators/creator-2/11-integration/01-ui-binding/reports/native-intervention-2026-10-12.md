# Native intervention screen — 12 октября2026

[Родитель](../README.md) · [Дизайн](../native-intervention-design.md) ·
[План](../native-intervention-plan.md) · [Fixture](../tests/native-intervention/README.md).
Windows D:/AI/dota2coach, исходный HEAD83094d1/clean. Dota build_id25845666 повторно
проверен в appmanifest_570.acf. Ведущая роль74, root единственный автор; read-only
windows_learning дал exact DTO/assertions. C1/production JS/контракты не изменены.

## Canonical source и изолированная установка

Урок18 применён до compiler: anonymous CoachInterventionCanvas с прежним
CoachInterventionScreen внутри. Exact outer attrs/один child и inner root проверяет
composer. Root regression RED→GREEN; guards запрещают outer id/class/extra child/
изменённый binding root. Existing packaged VM bind получает inner scope. Fixed
kind13resources/12links/2XML inputs,8JS definitions/50ID и единственное объявленное
переименование CoachRoster→CoachInterventionRoster сохранены. Child scopes — прежние
canonical inputs, их отдельная native загрузка не проверена.

Отдельный [builder](../../02-addon-packaging/tools/build_native_intervention_fixture.py)
reuse fixed guarded policy, свой exact non-executable Hud manifest/driver/banner.
15sources:13byte copies/2composed;14active dependencies плюс retained generated
canonical layout отдельно compiled. Canonical subtree сохранён. Report различает
13canonical output hashes и15raw source hashes, включая2layout inputs. Unsafe
manifest/mapping/missing/output escape/existing output отклоняются до writes.
Source flagsfalse; этот driver не включается в kind/probe/production bootstrap.

Initial bundle125605Z-573df9/addon dota_coach_c2_intervention_20261012;
final130634Z-cd6b3e/addon dota_coach_c2_intervention_r1_20261012, directories отсутствовали
до установки. Fifteen installed payloads совпали с bundle;15raw canonical input
hashes заново проверены. Valve template_map.vmap и workshop_testbed/addoninfo.txt
скопированы отдельно. Existing addons не заменены; Lua/сервер/AI не добавлены.

```powershell
$dotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot = "$dotaRoot/content/dota_addons/dota_coach_c2_intervention_r1_20261012"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/custom_ui_manifest.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/coach_intervention.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/maps/template_map.vmap"
```

Оба addons: UI1compiled/0failed, retained layout1/0, map13/0, exits0.
Final15compiled UI files105259bytes:14active +retained layout отдельно.
Leaked KeyValues blocks162 сохранён, причина неизвестна. Флаг -novpk не применён.
Final mapVPK3033460bytes SHA2567cee1865b837042332ffc5656e258bc9478e51ba15ea82046d105e5809742633.
Exact source/compiled hashes: ignored build/dota_coach/native-intervention-r1-hashes-20261012.json.


| Canonical output | SHA-256 |
|---|---|
| coach_intervention.xml | fcf2f86773f1400f0376205f1c435e7119ff45dc276be0b11f157762c5f170fd |
| coach_intervention.css | 93bfb456276e37e7ace79393c4d6c0daca3a20d6dabcaea5c53f7af5c319e853 |

## Первый run: API работает, панель не видна

Own PID27436/1280×720, fresh HERO_SELECTION непосредственно перед cheats/hero commands;
Axe виден на actual кадрах и не связан с TEST IDs/control frames. Eight API phases
и cycle PASS; shots0070–0077 сохранены и осмотрены. Правая панель запроса отсутствует
на кадрах, хотя её labels/state/handlers доступны API. Это visual defect, не full PASS.

Исходный ManualRequestRoot имел height100% в host с автоматической высотой;
fixed-width720/centered ManualRequestWindow переносился из standalone screen.
Зависимость размера/выравнивания — вывод по CSS/композиции и кадрам, initial native
geometry отдельно не записана, внутренний алгоритм engine clipping не исследован.
Исправление ограничено canonical composition CSS: root height:fit-children;
scoped window width100%/top/left. Standalone request CSS/XML не изменяются.
TEST driver теперь проверяет positive native root/window dimensions на visible phases.

[Первый ready: правая панель отсутствует](native-intervention-ready-2026-10-12.png) ·
[Initial ACK](native-intervention-accepted-2026-10-12.png) ·
[Initial unknown](native-intervention-timeout-unknown-2026-10-12.png).
Первый own client quit→gone, Steam сохранён. Его stdout/logs не переименованы в final.

## Исправленная сцена и восемь фаз

Own PID29568/1280×720, fresh console log, HERO_SELECTION проверена непосредственно
перед hero commands. PRE_GAME13:11:19UTC; всех8predicates/cycle PASS, восемь final
actual frames осмотрены. Вместе с initial сохранено16PNG; первый API cycle сохраняет
visual defect. Final positive native root/window geometry подтверждена; при unknown
оба сообщают width374.4/height281. Эти getters не заменяют actual кадры.

- bound: roster/control ещё отсутствуют, canRequest false, request null/button disabled.
- ready:5synthetic TEST cards; A selected, supplied AI frames A/B. Selection не send;
  canRequest true/manualModeReported false, request button enabled для local intent.
- pending: один injected send, exact intent ticket1/recipientIda/epoch1/actionrequest_manual;
  request sourceRevision1/sequence−1, statuspending, repeat gate closed.
- accepted: B selected, request actor остаётся A. Stub reply sequence0/stageaccepted/
  reasonnull передан через4scheduled секунды после request, до ACK timeout. Statusaccepted,
  mode MANUAL не подтверждён, repeat requestfalse/send count1. Обе разные подписи видны.
- timeout-pending: предыдущая группа закрыта, fresh bind/источники/A/local request.
  Stub не отвечает; timer cancellation/lifecycle предыдущей группы не переносится.
- timeout-unknown: actual existing $.Schedule(5) изменяет source без expire calls из
  driver; screen watcher обновляет summary. ActorA/statusunknown/repeatfalse/send count1.
  State/Message/common status показывают неизвестный исход, canRequestfalse/manualfalse.
- disposed: group closed/viewnull, root скрыт/labels очищены; закрытие UI не отменяет
  серверную операцию. TEST banner вне root остаётся виден.
- rebound: fresh source/A selected/requestnull/canRequesttrue, новых send нет.
  Old replaceRoster/updateControl/select/request/refresh false; обе старые reply
  callbacks false; Proxy get/ownKeys/descriptor inspections0. Fresh display сохранён.

TEST poll через0.25s записал первое unknown после4958ms initial/4952ms final от Date.now.
Это наблюдение local wall clock, не calibration engine scheduler или точность deadline.
$.Schedule(5) — source parameter; причина небольшого расхождения clock samples не
исследована. Нет server clock/lease/latency estimate/AI return evidence. Driver не
вызывал expire и не имитировал ход таймера. Native кадры подтверждают presentation.

Screenshot через≥2s после phase; pending записан до action ACK. Engine TGA→RGBPNG
без изменения сцены. Different clock domains и native getters отделены от изображения.

| Final фаза | UTC кадра | TGA | Кадр |
|---|---|---|---|
| bound | 2026-10-12T13:11:23.518Z | shot_0078.tga | [PNG](native-intervention-r1-bound-2026-10-12.png) |
| ready | 2026-10-12T13:11:38.510Z | shot_0079.tga | [PNG](native-intervention-r1-ready-2026-10-12.png) |
| pending | 2026-10-12T13:11:53.525Z | shot_0080.tga | [PNG](native-intervention-r1-pending-2026-10-12.png) |
| accepted | 2026-10-12T13:11:57.457Z | shot_0081.tga | [PNG](native-intervention-r1-accepted-2026-10-12.png) |
| timeout-pending | 2026-10-12T13:12:13.408Z | shot_0082.tga | [PNG](native-intervention-r1-timeout-pending-2026-10-12.png) |
| timeout-unknown | 2026-10-12T13:12:28.356Z | shot_0083.tga | [PNG](native-intervention-r1-timeout-unknown-2026-10-12.png) |
| disposed | 2026-10-12T13:12:43.319Z | shot_0084.tga | [PNG](native-intervention-r1-disposed-2026-10-12.png) |
| rebound | 2026-10-12T13:12:58.543Z | shot_0085.tga | [PNG](native-intervention-r1-rebound-2026-10-12.png) |

Quit с fresh VConsole marker после кадров; собственные PID27436/29568 отсутствуют
при последующей проверке. Steam сохранён; принудительное завершение не применялось.

## Source проверки и границы

Builder RED7missing→GREEN7, existing screen binding20PASS:27targeted checks.
Existing screen package12cases:11passed/1WinError1314, suite не green.
Required full130742Z-081143:46suites/753passed_tests/6failed/verified=false.
Packaging155cases/8WinError1314, остальные147passed, включая7fixture и outer guard.
Initial full125720Z-c40c6d тот же итог. Исторические expected Windows skips/
invalid_summary и symlink failures не скрыты, skip/OS/security changes нет.
Source-only handoff131100Z-d28045 verified13/12; native flagsfalse/not_run сохранены.

Методы selectPlayer/request — public API calls, не physical clicks/hittest.
Injected send/report — in-process TEST stub, не transport или server ACK.
Observed AI/control DTO не engine identity/авторизация. ACK не MANUAL; timeout unknown
не означает отказ сервера, отмену запроса или возврат ИИ. Закрытие UI не отменяет
серверную операцию. Полномочия input, lease/временность вмешательства/AI return,
C1/bootstrap/реальные profiles/server, другой размер экрана и human second owner открыты.
За TEST композицию виден стандартный Dota HUD. Initial minimap белый; final
minimap чёрный, верхняя область карты голубая. Причина изменения render не установлена;
driver не перемещает камеру/героя. Проверенная карта/geometry/visibility не заявляются. Common HUD/map/product transition acceptance открыта.

Один повторно использованный финальный technical critic не выявил существенных
замечаний: exact outer/inner guards, scoped CSS, captured actor, timer/watcher и
stale callbacks проверены. Это AI review; human second owner остаётся открытым.

Финальная проверка документов:16changed Markdown/297local links,26полных пятичастных уроков,38unique usage tasks;15current source-input hashes и16native PNG подтверждены. График50/213(23.5%), diff --check без ошибок. Source-only evidence не повышает product checklist. Публикация и remote SHA определяются Git history/последующей проверкой.
