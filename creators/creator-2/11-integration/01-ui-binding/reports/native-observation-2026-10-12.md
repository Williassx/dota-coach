# Native observation — 12 октября2026

[Родитель](../README.md) · [Дизайн](../native-observation-design.md) ·
[План](../native-observation-plan.md) · [Fixture](../tests/native-observation/README.md).
Windows D:/AI/dota2coach, исходный HEAD3b24a7d/clean. Установка Dota build_id25845666
повторно проверена в appmanifest_570.acf. Ведущая роль75; root единственный автор,
read-only windows_learning дал exact DTO/assertions. C1/production JS не изменены.

## Canonical layout и отдельный тестовый пакет

Урок18 применён до compiler: shell имеет anonymous CoachMatchObservationCanvas
с внутренним CoachMatchObservation. Existing root/38ID/две canonical child scopes
сохранены. Composer требует exact outer class/attrs/один child и прежний hidden
binding root. RED root regression→GREEN; guards запрещают outer id/другой class/
extra child/переименованный inner root. Fixed kind10resources/9links, пять JS
definitions и два XML inputs не расширены. CSS добавляет только outer size100%.
Module XML — embedding inputs; самостоятельная native загрузка не проверена.

Isolated [builder](../../02-addon-packaging/tools/build_native_observation_fixture.py)
получает каноническую композицию, сохраняет generated layout и добавляет свой
manifest/driver/derived layout.12sources:10byte copies/2composed outputs;
11active resources +retained generated canonical XML отдельно compiled.
Canonical subtree сохранён, TEST banner находится вне binding root.
Report разделяет10canonical output hashes и12raw input hashes с2XML inputs.
Strict fixed recipe/path policy reused; exact non-executable Hud manifest, fresh
output, missing/escape/mapping guards до writes. Source flagsfalse сохранены.

Первый bundle120546Z-a11e06 установился в отсутствующие directories addon
dota_coach_c2_observation_20261012. Final fixture121249Z-c2f272 — отдельный addon
dota_coach_c2_observation_r1_20261012. Twelve installed payloads совпали с bundle,
12raw canonical source hashes заново проверены; retained layout не active dependency.
Valve addon_template/maps/template_map.vmap и workshop_testbed/addoninfo.txt
скопированы отдельно. Lua/сервер/production bootstrap не добавлены.

```powershell
$dotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot = "$dotaRoot/content/dota_addons/dota_coach_c2_observation_r1_20261012"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/custom_ui_manifest.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/coach_match_observation.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/maps/template_map.vmap"
```

Оба addons: UI1compiled/0failed, retained layout1/0, map13/0, exits0.
Final12compiled UI files60637bytes:11active +retained canonical. Warning
Leaked KeyValues blocks162 сохранён, причина не установлена. Флаг -novpk не применён.
MapVPK3033459bytes SHA256b2037e6bb56af3084837e386f03f5952c8772a6550221823ad9b6f6c7d3c5cb7.
Exact source/compiled hashes находятся в ignored native-observation-r1-hashes-20261012.json.


| Canonical output | SHA-256 |
|---|---|
| coach_match_observation.xml | f030007d8bd90329000df7ac086161701dbb8d200d3c5fb708f3935d7e707556 |
| coach_match_observation.css | 8e1a729fe43153996eb1618e81f2fcbb1415b59c2b9999bbc137fd5cd191afd5 |

## Первый run и исправление ожидания

Own PID25624,1280×720. Fresh HERO_SELECTION checked непосредственно перед cheats
и dota_pick_hero; Axe виден на actual кадрах. Hero не связан с TEST IDs/heroName.
Пять фаз bound/ready/opponents-invalid/history-invalid/disposed прошли; кадры
shot0059–0063 сохранены и осмотрены. Rebound assertion failed: fixture ожидала пустую
OpponentName1 при available roster из одного игрока. Canonical panel.paint для
ready source и отсутствующего slot показывает «Имя неизвестно». Это дефект
ожидания driver, не ошибка production model. Исправлен только TEST assertion.
Этот цикл не PASS; full cycle/шестой кадр не объявляются выполненными.
Quit marker и последующая проверка подтвердили отсутствие owned PID25624.

[Первый ready](native-observation-ready-2026-10-12.png) ·
[Roster invalid, history сохранена](native-observation-opponents-invalid-2026-10-12.png) ·
[History invalid, roster сохранён](native-observation-history-invalid-2026-10-12.png) ·
[Disposed](native-observation-disposed-2026-10-12.png).

## Исправленный native cycle

Own PID10788,1280×720, fresh console log и phase-scoped hero commands.
PRE_GAME12:16:43UTC. Все6фаз/cycle PASS; actual six final frames осмотрены.
Вместе с пятью initial frames сохранено11PNG; первый cycle остаётся failed.

- bound: visible group, оба источника недоступны, labels очищены.
- ready:5TEST opponents; null heroName показан как неизвестный. History1event,
  captured actor TEST Captured A, а не Selected B/Untrusted. Stage accepted с
  явным текстом «выполнение не подтверждено», presentation_snapshot/nativefalse.
- opponents-invalid: invalid source и stale revision1 rejected; карточки пусты,
  прежнее history событие остаётся, count не растёт.
- history-invalid: strictly-new roster revision2 accepted; invalid history и
  refresh не оживляют history gate; roster остаётся видимым.
- disposed: до dispose тот же order восстанавливает history без duplicate,
  events/totalStored1. Этот промежуточный recovery проверен predicate, отдельного
  кадра нет. Dispose скрывает root/очищает labels, view closed/null children.
- rebound: fresh source revision1/один TEST FRESH, остальные имена неизвестны.
  History новой private instance недоступна. Old updateOpponents/recordOrder/refresh
  false; Proxy get/ownKeys/descriptor inspections0, fresh display сохранён.

Screenshot через≥2s после phase, engine TGA→RGBPNG без изменения сцены.

| Final фаза | UTC кадра | TGA | Кадр |
|---|---|---|---|
| bound | 2026-10-12T12:16:47.888Z | shot_0064.tga | [PNG](native-observation-r1-bound-2026-10-12.png) |
| ready | 2026-10-12T12:17:02.823Z | shot_0065.tga | [PNG](native-observation-r1-ready-2026-10-12.png) |
| opponents-invalid | 2026-10-12T12:17:17.754Z | shot_0066.tga | [PNG](native-observation-r1-opponents-invalid-2026-10-12.png) |
| history-invalid | 2026-10-12T12:17:32.706Z | shot_0067.tga | [PNG](native-observation-r1-history-invalid-2026-10-12.png) |
| disposed | 2026-10-12T12:17:47.915Z | shot_0068.tga | [PNG](native-observation-r1-disposed-2026-10-12.png) |
| rebound | 2026-10-12T12:18:02.925Z | shot_0069.tga | [PNG](native-observation-r1-rebound-2026-10-12.png) |

Quit с fresh marker после кадров; последующая проверка owned PID10788 показала
gone=true. Steam сохранён; повторный quit/forcekill не применялись.

## Source проверки и границы

Builder RED7missing→GREEN7, existing binding15PASS:22targeted checks.
Existing package9cases:8passed/1WinError1314; suite не green.
Required full121351Z-60b1f6:46suites/753passed_tests/6failed/verified=false.
Packaging147cases/8WinError1314, остальные139passed, включая7fixture и outer guard.
Исторические invalid_summary после expected Windows skips и symlink failures
не скрыты; skip/OS/security changes нет. Initial full120640Z-f9a385 имел тот же итог.
Source-only handoff121608Z-e67cbc verified10/9, native flagsfalse/not_run сохранены.

Прямые public API calls не доказывают physical input/hittest. Пять TEST names и
heroName не real roster/identity. Group.nativeConfirmed и sourceAuthorizationConfirmed
остаются false; accepted event — presentation_snapshot без исполнения/серверного ACK.
Скрытие UI не отменяет серверный запрос. Common игровой HUD/C1/production bootstrap,
реальные данные/clock, server effects, полный обзор карты и human second owner открыты.
За TEST opponent layer видны элементы штатного Dota HUD. Первый run показывает
белый template minimap; final кадры после bound показывают чёрный minimap и голубую
область карты слева. Причина изменения сцены не установлена; driver не перемещает
камеру/героя. Это сохранённое ограничение render тестовой карты, не доказательство
исправной геометрии/обзора. Common layout/map acceptance smoke не закрывает.

Один final technical critic foundation_report_review не выявил существенных
замечаний. Это AI review, не приёмка другого человека. Graph50/213 проверен,
285local links без missing targets,23пятичастных урока,37уникальных usage records
и11native PNG подтверждены. Current byte-copied sources совпадают с final fixture;
Git diff --check проходит. Публикация/SHA определяются Git history и remote check.
