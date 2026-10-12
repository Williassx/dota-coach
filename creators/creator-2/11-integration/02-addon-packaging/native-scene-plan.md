# План нативной тестовой сцены HUD

> Исполнение: superpowers:executing-plans, основной исполнитель самостоятельно.
> Пользователь поручил продолжать весь план без рутинных остановок.

**Цель:** запустить существующий инертный HUD в отдельной локальной Dota сцене
и проверить фактическое изображение без выдуманных данных, bind или сервера.
**Архитектура:** exact source kind HUD13/12 устанавливается в новый addon;
штатные template_map и addoninfo добавляются как отдельная native fixture.
Сборка карты и UI — штатным resourcecompiler; запуск — установленным dota2.exe.
**Стек:** Windows / PowerShell, existing Python helpers, Source 2, live VConsole.
**Спецификация:** [HUD design](../../07-match-screen/01-own-cards/design.md),
[предыдущая компиляция](reports/native-hud-2026-10-11.md),
[интеграция](../../../shared/INTEGRATION.md).

## Ограничения и файлы

- Новый addon: dota_coach_c2_hud_scene_20261012. До копирования content/game
  destinations отсутствуют; существующие addons не заменять.
- Recipe bundle-manifest.json сохраняет 13 ресурсов/12 ссылок/10 JS definitions.
  Generated output не редактировать, source-only flags не переписывать.
- Карта из installed content/dota_addons/addon_template/maps/template_map.vmap;
  addoninfo из game/dota_addons/workshop_testbed/addoninfo.txt. Их назначения
  native fixture отдельно от HUD recipe; C1/Lua/bootstrap не добавлять.
- Отчёт reports/native-hud-scene-2026-10-12.md и настоящий engine screenshot
  reports/native-hud-scene-2026-10-12.png; обновить индексы, windows-resume,
  action log за дату UTC и учёт. Runtime logs/hashes/owner PID — ignored build.
- Не менять ОС/драйвер/Developer Mode/права. Закрывать только свой проверенный PID.
- Screenshot/compile не доказывают input/hittest, runtime identity, C1 contract,
  lease, AI return, готовность всей игры или проверку другого человеческого автора.

## Приёмка

- [x] Проверить fresh source handoff/verifier и source→bundle→installed SHA-256.
- [x] Скомпилировать UI и карту, проверить реальные compiled outputs/VPK.
- [x] Запустить свой клиент с проверенными flags и отдельным console log;
  живой unique echo подтверждает VConsole, не один TCP connect.
- [x] Дойти до PRE_GAME в локальной fixture; при HERO_SELECTION использовать
  ранее подтверждённый dota_pick_hero только для тестовой сцены.
- [x] Выполнить screenshot без аргумента, найти новый TGA по фактическому ответу,
  сохранить PNG и визуально проверить четыре пустые области HUD.
- [x] Записать видимые дефекты или границы. При дефекте сначала установить
  причину, затем source correction с подходящими RED/GREEN; output не редактировать.
- [x] Завершить свой клиент через quit и проверить отсутствие PID.
- [x] Проверить целевые suites, links/graph/diff; один final critic после результата.

После этих проверок выполняется обычный разрешённый main push, сверка remote SHA
и clean tree; revision публикации отражается в Git history и ответе исполнителя.

## Особые случаи проверки

Чужой процесс Dota — не закрывать; запуск отложить до доступной среды.
Source hash mismatch — остановить установку, не заменять исходники/аддон.
Длительная загрузка — сначала дождаться live echo/состояния, не считать первые
30 секунд окончательным отказом. Нет script output — инертный definitions-only
HUD не обязан печатать probe panel_ready. Скриншот сверять с новым engine кадром,
не использовать старый probe кадр как доказательство HUD.

## Обнаруженный native дефект и минимальная коррекция

Первый PRE_GAME кадр1280×720 показал пять пустых рамок, несмотря на XML
visible=false; status перекрывает штатную статистику, пустой roster перекрывает
верхнюю часть minimap. Native dump_panorama_css_properties подтверждает
visibility:collapse как исключение панели из изображения и layout.
Совместимость Panel.visible setter с default CSS подтверждена отдельно native
fixture cycle и четырьмя кадрами. Полный explicit roster bind остаётся открытым.

- [x] Добавить regression check default collapse пяти initial slots до CSS fix;
  существующий definitions-only/no-side-effects тест сохраняется.
- [x] Только canonical coach_hud.css: default collapse карточек; пустой roster
  сместить правее minimap, status ниже статистики и дать читаемый фон.
  XML/JS/13-resource allowlist/bootstrap не расширять.
- [x] Fresh handoff и новый addon dota_coach_c2_hud_scene_r1_20261012;
  предыдущую дефектную fixture сохранить. Повторить compile/run/screenshot.
- [x] Before/after actual frames и target/full source checks записать отдельно
  от проверки будущего bind, включения карточек и hittest.

В первом r1 кадре карточки скрылись, status читаем; для дополнительного отступа
от штатных круглых индикаторов рядом с minimap roster margin-left увеличен
с280 до320px. Обновление собственного r1 addon допустимо только после сверки
его всех13 исходных hashes с предыдущим handoff; новый generated bundle не
редактируется. Проверить новый кадр1280×720 и отдельный запуск1920×1080.
Нативная команда mat_setvideomode отсутствует: не использовать guessed command,
другой размер задать ранее проверенными launch flags -w/-h при новом owned run.

## Независимая проверка native visible setter

Перед публикацией default collapse проверить совместимость с существующим
Panel.visible=true. Отдельная test-only fixture в tests/native-css-visibility:
manifest, layout и JS, плюс единственный canonical coach_hud.css из C2-07-01.
Своя сцена dota_coach_c2_css_visibility_20261012 с той же штатной картой;
фиксированный HUD13/probe kind и их manifest/policy не расширять.
Fixture не bind HUD и не создаёт игроков/приказы/сервер/мышь. Её действие:
initial hidden→show→hide→show, native visible/layoutwidth/height и четыре
engine кадра между фазами, после завершения native layout.
Если ширина остаётся0 или card не виден, static CSS fix не публиковать без
совместимого исправления. Успех fixture доказывает только этот native setter,
не полный roster binding, server identity или настоящих игроков.

## Выполненные пункты и оставшиеся gates

Установка/hashes, UI/map compile, live echo, PRE_GAME, screenshot, source RED/GREEN,
before/after двух разрешений, отдельный native setter cycle и quit/owned PID
выполнены: [фактический отчёт](reports/native-hud-scene-2026-10-12.md).
Full source runner выполнен, verified=false/6 failed suites; полный bind,
input/C1/identity/lease/AI return, minimap fixture и другой создатель открыты.
Публикация выполняется после итогового review и document/graph/diff checks.
