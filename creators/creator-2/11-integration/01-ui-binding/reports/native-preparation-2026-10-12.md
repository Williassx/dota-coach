# Native preparation — 12 октября2026

[Подпункт](../README.md) · [Дизайн](../native-preparation-design.md) · [План](../native-preparation-plan.md).
Windows D:/AI/dota2coach, исходный HEAD6a1383c/clean. Dota build_id25845666 заново
проверен в appmanifest_570.acf. Ведущая роль78, root единственный автор; C1 не изменён.
Это test-only scene существующей подготовки, не production bootstrap/начало матча.

## Исправления и native результат

Урок18 применён до native compile: canonical preparation shell теперь anonymous
outer CoachPreparationCanvas с внутренним CoachPreparationRoot. Composer принимает
точную outer topology, один child и прежний binding root. Fixed15resources/14links,
девять определений и три canonical XML inputs сохранены. Module XML — embedding
inputs; их отдельная native загрузка не проверялась.

Generated-root regression сначала RED; после исправления прошла. Добавлены отказные
outer id/class/extra child/wrong binding root scenarios. Production JS/API не меняются.

Первый отдельный addon dota_coach_c2_preparation_20261012 прошёл шесть native API
фаз и compile, shots0047–0052. Кадры обнаружили пустые навигационные кнопки и
complete выше тактики. Это не полноценный visual PASS несмотря на predicates.

Canonical CSS трёх standalone панелей получает scoped Control Label width:fit-children.
Изначальный Label width100% при Button без фиксированной ширины образовывал
зависимость child/parent размера; это вывод по CSS и изменению кадров, внутренний
алгоритм движка не исследован. JavaScript подписей не был причиной.
У final семи control labels native width/height>0 и непустой текст, actual кадры
показывают прежние подписи; tall пустой HeroRole control также исправлен.

Первый ScrollToBottom сразу после наполнения использовал прошлую geometry:
scroll=-693 при content2083/viewport640. Driver теперь ждёт0.5s native layout,
final scroll=-1293 при content1933/viewport640; actual кадр показывает весь блок
тактики/разговора и локальные выбранные намерения. Это API scroll, не mouse wheel.

## Изоляция и установка

[Builder](../../02-addon-packaging/tools/build_native_preparation_fixture.py)
использует existing guarded fixed policy, без расширения kind/probe. Fourteen
canonical outputs +test manifest/driver/derived layout дают17resources. Fifteen
byte-copied, two composed: retained canonical generated layout и test derivative.
Manifest strict exact tags/attrs/mixed text/DTD guard; output exclusive и bounded
read/escape/reparse policy reused. Guard refusals выполняются до writes.

Report хранит15canonical output hashes и18raw input hashes, включая3layout inputs.
Не выдаёт generated output hash за raw shell hash. Canonical subtree в derived
layout сохранён; TEST banner находится снаружи CoachPreparationRoot. После dispose
он остаётся виден. Source flags false; native evidence только в этом документе.

Final fresh fixture: build/dota_coach/native-preparation-20261012T101522Z-f52acb.
Final addon dota_coach_c2_preparation_r1_20261012; absent dirs checked перед copy,
17bundle→installed payloads и18source input hashes совпали. Valve template_map.vmap
и workshop_testbed/addoninfo.txt скопированы отдельно; Lua/server не добавлены.

```powershell
$dotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot = "$dotaRoot/content/dota_addons/dota_coach_c2_preparation_r1_20261012"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/custom_ui_manifest.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/coach_preparation.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/maps/template_map.vmap"
```

Оба addons: UI1/0, retained generated layout1/0, map13/0, exit0. Final17compiled
UI outputs146579bytes:16active dependencies +retained layout отдельно compiled.
Leaked KeyValues blocks162 сохранён, причина неизвестна; -novpk не используется.

| Объект | SHA-256 |
|---|---|
| generated canonical XML | 672f3d2461b412a5cb2728d7a50c5708250a2b47c368bf79a86c8beec9d8d214 |
| canonical composition CSS | 059cb004ca423a34b60477c04cea05d20f363a059085407f81886fe4de433a73 |
| map VPK3033460bytes | 52e3317559fe45c97832f679a525843d25788633bfeacf9ef0fb3b73531d7b27 |

## Native API и кадры

Оба own launches1280×720: -game/-steam/-addon/-novid/-windowed/-console/-dev/
-insecure/-vconsole/-vconport29000/-con_logfile и +dota_launch_custom_game. Первый
PID27560 достиг PRE_GAME10:10:23UTC по таймеру. Поздний dota_pick_hero не подтвердил
создание героя; первый disposed кадр показывает пустой hero HUD. Повторный запуск
PID28100 проверял текущий HERO_SELECTION непосредственно перед sv_cheats1 и
`dota_pick_hero 0 npc_dota_hero_axe`; PRE_GAME10:18:31UTC, Axe виден в final disposed
кадре. Этот герой не связан с TEST IDs/hero proposals и не подтверждает identity.

Driver explicitly bind inner root в composed XML, не canonical пустом shell.
Public methods, без настоящих clicks/scroll/input callbacks:

- bound: три child adapters доступны, draft null, статус plain; семь навигационных
  labels имеют native dimensions и text. Каталоги не получены.
- team: updateTeam revision0 с5synthetic/unknown TEST profiles; choosePlayer всех5;
  local count5/5, complete team true/serverConfirmed=false, общий draft null.
- complete:5synthetic hero-role proposals/assignments; plan/talk options TEST v1,
  оба local choices. draft complete=true, serverConfirmed=false; count2/2.
- reset: removePlayer TEST-p4 даёт count4, heroes/preparation/draft null; downstream
  labels очищены. ScrollToTop показывает состав. Старые предложения не возвращаются.
- disposed: handle closed, contexts/draft null, root скрыт; TEST banner остаётся.
- rebound: fresh catalog одного TEST profile/нулевой выбор. Old updateTeam/updateHeroes/
  updatePreparation/choosePlayer false; Proxy get/ownKeys/descriptor inspections0;
  свежий владелец не повреждён.

Все шесть predicates и cycle PASS в обоих runs, все12native frames осмотрены.
Первый run сохранил visual defects; final исправления подтверждены отдельно.
Screenshot через≥2сек после phase, TGA→RGBPNG без изменения сцены.

| Final фаза | UTC кадра | TGA | Кадр |
|---|---|---|---|
| bound | 2026-10-12T10:18:35.881Z | shot_0053.tga | [PNG](native-preparation-r1-bound-2026-10-12.png) |
| team | 2026-10-12T10:18:50.822Z | shot_0054.tga | [PNG](native-preparation-r1-team-2026-10-12.png) |
| complete | 2026-10-12T10:19:05.722Z | shot_0055.tga | [PNG](native-preparation-r1-complete-2026-10-12.png) |
| reset | 2026-10-12T10:19:20.601Z | shot_0056.tga | [PNG](native-preparation-r1-reset-2026-10-12.png) |
| disposed | 2026-10-12T10:19:35.744Z | shot_0057.tga | [PNG](native-preparation-r1-disposed-2026-10-12.png) |
| rebound | 2026-10-12T10:19:50.748Z | shot_0058.tga | [PNG](native-preparation-r1-rebound-2026-10-12.png) |

[Первый bound: пустые кнопки](native-preparation-bound-2026-10-12.png) ·
[Первый complete: тактика вне кадра](native-preparation-complete-2026-10-12.png).
Остальные initial frames сохранены как native-preparation-{phase}-2026-10-12.png.
После кадров quit с fresh VConsole marker; PID27560/28100 checked gone, Steam сохранён.

## Source проверки и пределы

Builder RED7missing→GREEN7; binding18 и flow20 проходят:45targeted checks.
Existing package21cases:20passed,1WinError1314 symlink creation, suite не green.
Final source-only handoff102132Z-315378 verified15/14; его native flagsfalse/not_run
сохранены, source report не превращён в installation/runtime approval.
Required full101831Z-b01147:46suites/753passed_tests/6failed/verified=false.
Packaging139cases,8WinError1314, остальные131passed включая7fixture/new outer test;
другие ошибки — прежние skips/invalid_summary и symlink suites. Skip/OS changes нет.
Raw scoped logs/hash/install/owner/captures: ignored build/dota_coach/native-preparation-*.

Физический input/scroll/hittest, другой размер экрана, production bootstrap,
C1/реальные source catalogs/identity/персональное сходство, server readiness,
тактические эффекты/разговор, начало матча и human second owner остаются открытыми.
Подготовка displayed внутри отдельной map fixture; общего UI перехода в игру нет.
Native Dota HUD просвечивает сквозь подготовку — product transition/layout acceptance
не закрыта. API stage complete не означает готовность игры.

Один final technical critic foundation_report_review не нашёл существенных
замечаний. Это AI review, не человеческая приёмка. Graph50/213 проверен;
262local links без missing targets,22пятичастных урока и36уникальных usage records
проверены. Git diff --check проходит; публикация и SHA определяются Git history.
