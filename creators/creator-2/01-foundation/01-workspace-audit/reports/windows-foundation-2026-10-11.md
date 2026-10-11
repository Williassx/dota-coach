# Windows foundation — 11 октября 2026 года

## Итог последнего прогона

Штатный вызов `screenshot` без аргумента успешно сохраняет новый файл в
game/dota/screenshots. Исполнитель проверил оригинальный TGA и PNG 1280×720.
На [скриншоте игрового HUD](native-probe-hud-2026-10-11.png) видны заголовок
«Dota Coach — проверка связи», idle-статус «Нажмите “Проверить связь”» и кнопка.
В native-final-20261011.log зафиксирован panel_ready в 15:26:01 UTC.
Эта стадия подтверждает видимость и исполнение панели; геометрия штатного
тестового HUD/карты, внешнее hittest и другие масштабы отдельно не проверены.
После сохранения evidence клиенту передана штатная команда quit.

| Проверка | Фактический итог |
|---|---|
| Компиляция пяти UI-ресурсов | Exit 0, outputs проверены |
| Компиляция template_map | Exit 0, 13 compiled, VPK записан и проверен |
| Запуск локального игрового клиента/карты | Подтверждён native log |
| Native JS/bind и видимые панель/кнопка | panel_ready и проверенный скриншот |
| Событие запроса | request_sent в первом игровом прогоне |
| Тайм-аут/повторный запрос | Не подтверждены; первый прогон прерван DXGI-падением |
| Ответ C1, корреляция, адресность | Не проводились; обработчика нет |
| Ввод вне панели/hittest/reload/dispose | Не проводились |
| Workshop Tools runtime | Отдельная попытка не подтверждена; игровой режим не выдаётся за Tools |

Скриншот HUD не содержит SteamID/персональных путей. Полные логи и дампы,
включая account/config сведения, остаются только локально.

## Продолжение: карта собрана, Panorama исполняется

После первоначального отчёта установлена причина отказа сборки карты:
в этой установленной версии `-novpk` исключает базовые VPK из GAME search paths.
При verbose-прогоне с этим флагом GAME содержал только отдельный addon;
без флага видны dota/core pak01 и shaders_pc. Дополнительно resourceinfo успешно
прочитал `materials/error.vmat_c` непосредственно из установленного core VPK.
Отсутствие ресурса на диске не было причиной прежних сообщений ERROR_FILEOPEN.

Успешная команда (DOTA — фактический root, указанный ниже):

```powershell
& "$DOTA/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$DOTA/game/dota" -i "$DOTA/content/dota_addons/dota_coach_c2_probe_20261011/maps/template_map.vmap"
```

Exit 0, `OK: 13 compiled, 0 failed, 0 skipped`, 17 секунд. Компилятор записал и
проверил `game/dota_addons/dota_coach_c2_probe_20261011/maps/template_map.vpk`,
3033412 байт, MD5 `b3a862cff019a53ab280400db98fe05b`.
Нет ключей подписи для локального VPK; unsigned не означает опубликованную игру.
Сохранены сообщения о generic.vfx для tool materials; итоговый compile exit 0.
Локальный полный журнал: `build/dota_coach/native-map-vpk-20261011.log`.

Нативный запуск без `-tools` с `-game <absolute game/dota> -steam -addon
dota_coach_c2_probe_20261011 -novid -windowed -w 1280 -h 720 -console -dev
-insecure -con_logfile <новый локальный журнал> +dota_launch_custom_game
dota_coach_c2_probe_20261011 template_map` подтвердил Spawn Server,
Host activate, клиентскую template_map и переход PRE_GAME.
В `native-game-20261011.log` есть `[DotaCoachProbe]panel_ready` и
`request_sentprobe-mv3ys9v5-25tmq7-1`: игровые JS и привязка панели исполнялись.
Это не доказывает внешний hittest, видимость/качество текста или серверный ответ.
`scripts/vscripts/addon_game_mode` отсутствует; C1 bootstrap/ping не добавлялся.

VConsole в обычном клиенте доступен на loopback:29000; echo-маркер подтверждён
живым ответом. В Tools-попытке на 29002 было лишь TCP-соединение без ответов:
оно не засчитывается как успешное управление Tools. Использован изученный
[пример протокола](https://github.com/ex3lite/Dota2_Workshop_MCP/blob/main/src/dota/vconsole.ts),
затем подтверждён собственным echo. Полные buffered логи содержат локальные
данные и остаются вне Git. Сторонний MCP не устанавливался.

Прогон завершился аварийно до подтверждённого timeout. Comment stream дампа
`crash_dota2.exe_20261011171458_1.dmp`: `DXGI_ERROR_DEVICE_REMOVED` в
LogD3DResult/CreateTexture2D. Причина потери графического устройства не установлена;
драйвер/системные параметры не менялись, это не доказанная ошибка панели.

Повторный прогон также загрузил карту. Попытка исполнителя сохранить screenshot
по абсолютному пути вне Game/Content вызвала engine AbortMessage с причиной
`Invalid screenshot path ...: D`; это ошибка диагностической команды.
Дамп `dota2_2026_1011_172008_0_error.mdmp` отделён от первого DXGI-сбоя.
Нельзя объявлять оба падения одной причиной или успешной полной приёмкой.
Команда исправлена на штатный `screenshot` без аргумента; результат следующего
прогона фиксируется отдельно. Дампы и полные журналы не публикуются.

Ниже сохранён исходный отчёт предыдущего этапа: его открытая сборка карты теперь
разрешена указанной выше командой. Позднейший скриншот подтвердил native visual;
timeout/reload/C1 и полная приёмка остаются открытыми.

[Подпункт](../README.md) · [Факты среды](../notes/workspace-audit.md).

Ведущая роль: создатель 2, аудит UI/Tools. Область: C2 foundation и отдельный
диагностический addon. Критерий: реальные пути, компиляция ресурсов и точное
разделение подтверждённых результатов от непроведённой нативной приёмки.

## Подготовка

Рабочая папка оказалась пустой. Выполнен `git clone
https://github.com/Williassx/dota-coach.git .`; origin/main на момент клонирования
`9d30deae4b0cd078288ec9572de2a5665f64cf60`. Пользовательских файлов в папке не было.
ОС Windows, PowerShell; Python 3.12.14, Node 24.19.0.

Для команд Python использован
`C:\Users\Dagda\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
Запущены существующие inspect_ui_workspace.py и prepare_ui_handoff.py (default probe).
Handoff: `build/dota_coach/probe-ui-20261011T145207Z-7fca7c.handoff.json`,
source_verified=true, installation=false, native checks=not_run. Его неизменяемые
статусы описывают подготовку source пакета; последующая установка записана здесь.

## Установка и компиляция UI

Dota root: `C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta`.
Build ID: `25845666`. Отдельное имя: `dota_coach_c2_probe_20261011`.
Перед созданием проверено отсутствие обоих addon destinations.
В новый content addon скопирован только Panorama из проверенного generated пакета.

Из корня репозитория выполнено (DOTA обозначает фактический root выше):

```powershell
& "$DOTA/game/bin/win64/resourcecompiler.exe" -nop4 -game "$DOTA/game/dota" -i "$DOTA/content/dota_addons/dota_coach_c2_probe_20261011/panorama/layout/custom_game/custom_ui_manifest.xml"
```

Exit 0: `OK: 1 compiled, 0 failed, 0 skipped`. В game addon проверены непустые
custom_ui_manifest.vxml_c, coach_probe.vxml_c, coach_probe.vjs_c,
coach_probe_state.vjs_c, coach_probe.vcss_c. Локальный полный журнал:
`build/dota_coach/native-compile-20261011.log`; финальное сообщение компилятора
`Leaked KeyValues blocks: 162` сохранено, оно не изменило код выхода.

Для отдельной карты скопированы штатные addon_template/maps/template_map.vmap
и workshop_testbed/addoninfo.txt; это тестовый шаблон с maps=template_map,
не серверная реализация C1.

## Ограничения

Компиляция карты с `-nop4 -novpk -game <absolute game/dota> -i <template_map.vmap>`
сообщает ERROR_FILEOPEN для базовых ресурсов (materials/error.vmat_c,
surfaceproperties/surfaceproperties.vsurf_c и других). Смена рабочего каталога
на game/bin/win64 и дополнительный `-retail` не устранили наблюдаемые сообщения.
Относительный game path отвергнут загрузчиком gameinfo.gi. Это не доказательство
повреждения установки: причина недоступности ресурсов ещё не установлена.
Завершённая сборка карты не подтверждена; незавершённые запуски прерваны исполнителем.
Журналы native-map*.log остаются в build, не публикуются полностью.

Выполнена попытка запуска dota2.exe с `-steam -tools -addon
dota_coach_c2_probe_20261011 -novid -windowed -w 1280 -h 720 -console
+con_logfile D:/AI/dota2coach/build/dota_coach/native-tools-console-20261011.log`.
Сам факт создания процесса не подтверждает загрузку Tools/карты/панели.
Запущенный исполнителем PID 9840 завершён после диагностики; существующий Steam
не закрывался. Console log не появился, видимая панель не подтверждена.
Для будущего запуска карты команда документирована в
[Valve Developer Community](https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/Addon_Overview/Playing_Addons):
`dota_launch_custom_game dota_coach_c2_probe_20261011 template_map`.
До успешной сборки карты нативные сценарии не засчитываются.

Полный существующий source runner запущен на Windows: 46 suites. Первый отчёт:
744 passed_tests, 8 failed suites. Повтор с process-local PYTHONUTF8=1:
751 passed_tests, 6 failed suites. UTF-8 устранил два отказа, но общий verified=false.
Остались WinError 1314 (symlink privilege), WinError 206 (длинные пути),
Windows taskkill/timeout и тестовые mocks платформенных инструментов.
Часть suites содержит skipped или errors; числа passed_tests не являются итогом
успешной полной регрессии. Проверки не ослаблены, системные настройки не изменены.
Отчёты: build/dota_coach/source-checks-20261011T145356Z-5a2f8b/source-checks.json
и source-checks-20261011T145522Z-b9a73c/source-checks.json.

Непроведены: визуальная приёмка, ввод вне панели/hittest, тайм-аут кнопки,
reload/dispose, C1 ping/адресность, mouse-targeting binding, права ручного ввода,
lease/cancellation/возврат ИИ. Обработка C1 не подменялась fake sender.
Foundation остаётся открытым; рассмотрение документов критиком не заменяет
приёмку второго человеческого владельца.

Финальный критик отчёта обнаружил одну неточную формулировку в native плане:
прочитанный manifest не доказывает загрузку. Формулировка исправлена.
Остальных существенных замечаний не получено. График checklist пересчитан
существующим инструментом: 49/213 (23.0%); это не готовность игры.
Для него matplotlib 3.10.8 установлен только в игнорируемый build/python-deps;
PYTHONPATH передан текущему процессу, глобальная среда не менялась.
