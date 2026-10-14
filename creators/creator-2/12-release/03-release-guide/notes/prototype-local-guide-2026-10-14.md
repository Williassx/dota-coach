# Повторение ранней source/native сцены

14 октября 2026. Нужен полный checkout D:\AI\dota2coach и локальная установка
Dota 2 с Workshop Tools на Windows. Технический review archive является excerpt,
не standalone installer; Valve map/template/engine в нём отсутствуют. Права и
пользовательская установка сторонним человеком этим руководством не подтверждены.

## Повторяемая source проверка

PowerShell из корня checkout; Python path получен из bundled runtime. Новый suffix
для каждого запуска сохраняет старые результаты. Команды не устанавливают аддон.

```powershell
$taskPython = 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskBuilder = 'creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py'
$taskSuffix = [guid]::NewGuid().ToString('N').Substring(0,12)
$taskNormal = "build/dota_coach/coach-guide-normal-$taskSuffix"
$taskFixture = "build/dota_coach/coach-guide-test-$taskSuffix"
& $taskPython -X utf8 creators/creator-2/11-integration/02-addon-packaging/tests/test_coach_scene_bundle.py
if ($LASTEXITCODE -ne 0) { throw 'Source tests failed' }
& $taskPython -X utf8 $taskBuilder --output $taskNormal
if ($LASTEXITCODE -ne 0) { throw 'Normal build refused' }
& $taskPython -X utf8 $taskBuilder --verify $taskNormal
if ($LASTEXITCODE -ne 0) { throw 'Normal verification refused' }
& $taskPython -X utf8 $taskBuilder --test-fixture --output $taskFixture
if ($LASTEXITCODE -ne 0) { throw 'TEST build refused' }
& $taskPython -X utf8 $taskBuilder --verify $taskFixture
if ($LASTEXITCODE -ne 0) { throw 'TEST verification refused' }
```

Ожидается exact 15 / 18 source outputs. Normal: 8 Lua, 3 JS, 2 XML, CSS, manifest;
TEST переназначает wrapper как coach_scene_game_mode.lua, добавляет TEST Lua как
addon_game_mode.lua, fixture JS и derived fixture XML. Normal UI compilation 7
(6 active+1 retained), TEST 9 (7 active+2 retained), проверяется только native compiler.
Source2/runtime flags остаются false даже после успешной source проверки.

## Нативная диагностическая процедура и сохранение чужой работы

Подтверждённая версия R2 — build25894101, template_map,1280×720. Дрейф build требует
новой компиляции и новых доказательств. [Existing command](../../../11-integration/03-end-to-end/tests/01-native-coach-scene/native-command.ps1)
принимает Install/Launch/Check/Quit, Bundle/Addon/Run. Его конечный
[executor](../../../05-intervention-ui/03-return-feedback/tests/native-move/native-command.ps1)
проверяет exact source receipt, fresh content/game directories, evidence и own PID/start UTC.

Список Addon фиксирован и исторические имена уже могут быть заняты. До нового native
повторения исполнитель проверяет их фактическую доступность; если свободного разрешённого
имени нет, сначала нужен новый рассмотренный диагностический suffix в executor. Не
удаляйте старый аддон/receipt и не подменяйте whitelist ради повторения. Руководство не
заявляет, что приведённое историческое имя сейчас свободно.

После выбора свободного **разрешённого** имени и нового Run:
Install проверяет source package/компиляцию; Launch создаёт own process receipt; Check
проверяет PID+точный start UTC; shared capture executor с `--scenario coach` собирает
actual TGA→PNG и API phases. Capture параметры берутся из его `--help`; нельзя выбирать
старый PNG path. TEST управляет own hero через programmatic API и не проверяет physical
input. Normal package не содержит TEST lifecycle driver. В конце Quit допустим только
после успешного Check; подтверждение gone записывается отдельной проверкой PID.
Существующий клиент Dota и Steam сохраняются. Установка не выполнялась в рамках этого guide.

## Частые отказы

| Отказ | Действие |
|---|---|
| Existing output / fresh addon directories required | Выбрать новый свободный output/addon после проверки; сохранить старые результаты. |
| Missing source / fixture | Проверить полный checkout и exact paths; не генерировать заглушки. |
| Hash/receipt mismatch | Сохранить failing bundle; собрать новый из current canonical sources. |
| Reparse/output boundary refusal | Использовать обычный child build/dota_coach; не ослаблять policy. |
| Existing Dota client preserved | Не вмешиваться в чужой клиент; native этап ждёт свободной среды. |
| Wrong compiled count/build drift | Сохранить журнал и заново проверять свежую компиляцию; source PASS недостаточно. |
| TEST phase failure | Сохранить negative frame/log; проверить actual transition до изменения assertion. |
| Strict source runner exit1 при known skips | Сохранить verified=false; не переименовывать incomplete в full acceptance. |

## Буквальная приёмка C2-12-03

«Инструкция соответствует проверенному пакету; отдельная игра описывается только при
необходимых правах». Source команды проверены для current 15/18 recipes. Приведена
реальная native процедура с fresh/own guard, но пользовательская установка третьим
лицом, совместное принятие владельцами и право распространения открыты. Standalone
продукт здесь не устанавливается. Это early limited prototype guide, не готовый выпуск.

[Native evidence](../../../11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.json) ·
[Пакет демонстрации](../../02-valve-presentation/notes/prototype-packet-2026-10-14.md).
