# Продолжение в локальной Windows-задаче Codex

[Родитель](README.md) · [Порядок аудита](windows-start.md) ·
[Source handoff](../../../10-user-testing/01-install-guide/notes/install-guide.md).

Проект пользователя: `D:\AI\dota2coach`. Основной исполнитель — создатель2,
Windows/Dota2/Workshop Tools подтверждены пользователем. Работа автономная;
не задавать повторно вопросы о клоне/ОС и не перекладывать команды на пользователя.
Это задание локальному исполнителю, не подтверждение доступного Windows shell.

## Подтверждённое продолжение 11 октября

Локальный Windows-клон теперь подготовлен, пути и build25845666 обследованы.
Отдельный addon `dota_coach_c2_probe_20261011`: UI и template_map скомпилированы,
игровой клиент загрузил карту; panel_ready/request_sent и видимость панели/кнопки
подтверждены. [Отчёт со скриншотом](../reports/windows-foundation-2026-10-11.md)
имеет приоритет над исходным описанием непроведённой установки ниже.

При продолжении не повторять подготовку исходников или клонирование.
Для установленного resourcecompiler при сборке карты **не использовать -novpk**:
он исключал базовые VPK из GAME search paths. Рабочая команда — `-v -nop4
-game <absolute game/dota> -i <content addon/maps/template_map.vmap>`.
Для нового runtime журнала использовать `-con_logfile <новый путь>`; обычный
клиент принимает VConsole на loopback:29000. Проверять владение процессом и
живой echo; TCP-соединение без ответов не доказывает работоспособность Tools.
Штатная консольная команда `screenshot` без аргумента пишет новый TGA в
game/dota/screenshots. Внешний absolute screenshot path вызывает AbortMessage.
Оригинал проверять до использования; raw buffered logs/дампы не публиковать.

В продолжении 18:12 UTC отдельный `-tools -vconport 29002` прогон дошёл до
PRE_GAME/panel_ready; Tools HUD подтверждён новым engine screenshot. Ранняя
задержка ToolsStallMonitor разрешилась после загрузки. Для VConsole использовать
новый уникальный echo и учитывать задержку старта: первые 30 секунд без ответа
не доказывают окончательный отказ. Собственные процессы завершены через quit.
`@oai/sky` доступен, но захват Dota/Asset Browser завершился timeout; UI Automation
показывает только рамку окна. Проверенного канала клика в этом прогоне нет.

Следующие открытые шаги: timeout/retry/hittest/reload/dispose и C1 bootstrap/ping.
DXGI_ERROR_DEVICE_REMOVED первого прогона записан
отдельно от ошибки screenshot; драйвер не менялся. Реальный C1 обработчик
ещё отсутствует; fake server/sender не добавлять.

В следующем продолжении SessionFlags=1 подтвердил unlocked Windows session;
capture timeout воспроизведён в пустом Блокноте и после JS reset. Input geometry
недоступна даже для его UIA кнопки. Не повторять те же launch/capture попытки
без нового диагностического основания; не считать Hidden доказанной причиной.
Источник WTS и завершение собственных процессов записаны в Windows отчёте.

Выполнен независимый step5: [native mouse-targeting7/6 план](../../../05-intervention-ui/02-mouse-targeting/native-plan.md).
Source 2 root id error исправлена anonymous host с прежним MouseProposalRoot
внутри. Новый addon dota_coach_c2_mouse_r1_20261011 содержит семь скомпилированных
UI ресурсов; карты/bootstrap/bind там пока нет. Старый неудачный addon сохранён.
Source bundles5/4 и7/6 пересозданы/проверены; probe policy не менялась.
Full source run46/752 имеет6failed suites, verified=false; не объявлять regression
или mouse runtime зелёными. Точные [команды/открытые проверки](../../../05-intervention-ui/02-mouse-targeting/reports/native-mouse-2026-10-11.md).

## Сначала подтвердить среду и сохранить изменения

Последнее продолжение: sky Tab не дал наблюдаемого фокуса ProbeButton;
sky F6 реально открыл Panorama Debugger, но его UIA/захват тоже не дали доступа
к панели. Не повторять тот же путь без нового основания. Запускать полный набор
ранее проверенных flags, включая -vconsole; при HERO_SELECTION штатная native
справка подтверждает dota_pick_hero для local test scene. Не заменять этим C1.
Причина ложного manifest_changed теперь исправлена в C2 map helper (birthtime
cross-API, ctime same-API guards);28passed/6skipped,100stable associations.
Новый full runner192232Z имеет6failed suites/verified=false; map tests не падают,
но пропуски дают invalid_summary. [Актуальное evidence](../../../03-map-view/01-map-audit/reports/windows-identity-2026-10-11.md).

1. Определить фактические OS/shell/cwd. Начинать локальные команды только на Windows
   в указанном проекте, не использовать D:\AI\game или другие доступные проекты.
2. Прочитать root AGENTS.md, creators/creator-2/AGENTS.md и README foundation.
3. Проверить Git root/origin/branch/status. Рабочие файлы сохранять. Fetch разрешён;
   pull только fast-forward при совместимом чистом checkout. Не применять reset,
   force push, stash, очистку или перезапись чужих файлов автоматически.
4. Получить актуальный origin/main и читать последний журнал, не начинать cloud
   source реализацию заново. Доступные на момент передачи source проверки:46/966;
   опубликованы mouse proposal/panel, targeting freshness binding и оба пакета.
5. Выбрать реально установленный Python launcher и Node. Не объявлять их наличие
   по облачным версиям. Команды/пути запуска брать из existing tools/notes.

## Выполнить native foundation

1. Запустить bounded inspect_ui_workspace.py по windows-start.md; JSON локально
   вне Git, реальный Steam/Dota/build_id/content/game/Tools/template определить по
   найденным данным. Не предполагать папку Steam равной папке репозитория.
2. Подготовить source handoff сначала probe, используя фактический Python launcher.
   Existing helper build/verify, fresh output, native checks остаются not_run.
3. Исследовать существующий Workshop Tools шаблон и его настоящий build/run flow.
   Создать отдельный тестовый addon по реальным путям, не заменять имеющийся addon.
4. Скомпилировать/запустить диагностическую панель только по проверенному API.
   Зафиксировать реальные commands/errors/logs. Не отмечать server ping, пока C1
   не предоставляет реальный обработчик; не придумывать сетевое подтверждение.
5. По результату оформить native план дальнейшего explicit binding/UI/hittest
   для mouse-targeting7/6. Local proposals не дают input authority/lease/send.
6. C2-05-03 cancellation/AI return требует настоящего C1 contract; спецификация и
   подробный план уже находятся в этой папке проекта. Не создавать fake sender.

## Документация и публикация

Следующее подтверждённое продолжение: Windows taskkill/tree timeout работает
вне sandbox на owned fixtures; sandbox выдаёт Access denied. Runner теперь
сохраняет stdout/stderr taskkill и exception в suite log, не меняя отказ/kill scope.
Node-only mock исправлен без отключения taskkill preflight. Новый полный прогон
194234Z вне sandbox:46/752/6failed; runner17tests15passed2symlink errors, timeout
и partial-selection проходят. [Команды/evidence/границы](../../../11-integration/03-end-to-end/reports/windows-runner-2026-10-11.md).
Не менять ОС/Developer Mode/symlink privilege ради зелёного статуса. Native
input/capture, C1 bootstrap/lease/AI return и full verification остаются открытыми.

Дополнительно проверены actual Windows junction guards для source/output/nested
tests directory:3PASS без изменения прав. Existing file-symlink tests сохранены;
новый full201328Z46/752/6failed, own suite20tests18passed2symlink errors.
WSL не предоставил подтверждённую local Linux среду; ничего не устанавливалось.
[Reparse evidence и ограничения](../../../11-integration/03-end-to-end/reports/windows-reparse-2026-10-11.md).

Следующий независимый native результат: fixed inert HUD13/12 установлен в новый
addon dota_coach_c2_hud_20261011 и скомпилирован штатным resourcecompiler, exit0.
13/13 source hashes совпадают, 13 непустых compiled outputs; 19 package и26binding
tests PASS. Source-only handoff/report не переписаны: native evidence отдельно.
Map/bootstrap/bind не добавлены, runtime/input/сервер/второй владелец открыты.
Перед запуском согласовать отдельную fixture scene/manifest; не накладывать HUD
на diagnostic probe. [Команды и evidence](../../../11-integration/02-addon-packaging/reports/native-hud-2026-10-11.md).

Все действия отдельно в creators/creator-2/00-action-log/YYYY-MM-DD.md, UTC.
Новые исходники сначала в библиотеке создателя2. Прочие отделы/контракты не менять.
Чекбоксы/graph только по evidence; source checks не заменяют native/second owner.
Порядок agents: полный каталог по этапам из agent-activation-2026-10-12.md,
полезные независимые группы в пределах четырёх процессов; один final critic после готового подпроекта,
точные token/cost неизвестны → null. Подходящие checks, docs/graph/Git diff check,
normal fast-forward main push, remote SHA/clean; публикация ранее разрешена.

Последнее native продолжение 12 октября: отдельная Dota fixture HUD13/12 реально
показала пустые области при1280×720 и1920×1080. CSS исправлен по кадрам:
collapse initial cards, roster справа от minimap, status ниже статистики.
Manifest incremental skip не перекомпилировал CSS: явный CSS compile и owned
restart обязательны при таком результате. Fixed kinds/JS/bootstrap сохранены.
Отдельная test-only setter fixture проверяет переключение Panel.visible;
она не является полным bind. Белый участок template minimap, full regression,
input/C1/identity/lease/возврат ИИ и другой создатель остаются открытыми.
[Native evidence](../../../11-integration/02-addon-packaging/reports/native-hud-scene-2026-10-12.md).
Перед похожими действиями применяйте [уроки](windows-lessons.md); каталог всех
175 ролей и условия назначения — [реестр](agent-activation-2026-10-12.md).
