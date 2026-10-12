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

Следующий actual native smoke: existing explicit HUD bind выполнен в отдельном
addon dota_coach_c2_hud_binding_20261012. Пять TEST/synthetic фаз1280×720:
bind5cards,selectTEST0,removeTEST0,dispose,rebindTEST-FRESH/stale methods false
безDTOreads. Все predicates+5actual кадров проверены, sender/gateway/resolver нет.
Это direct public API calls, не mouse/hittest; TEST control AI не серверное evidence.
Test-only source15/active compiled14; retained inert layout не загружался.
Targeted7builder/20HUDpackage/26binding PASS. Full080904Z-4ab77b всё ещё
46suites/752passed/6failed/verified=false. Owned PID21460 закрыт черезquit;
PID исчез после короткого завершения, безforcekill. [Отчёт и команды](../../../11-integration/01-ui-binding/reports/native-hud-binding-2026-10-12.md).

Следующее независимое native продолжение: text preview в отдельной fixture.
Canonical voice XML corrected anonymous outer / inner VoiceTextRoot; TextEntry
получил explicit readable styling. Fixed voice6/5 сохранён; test-only8sources,
7active compiled +canonical retained XML compiled отдельно. R1/R2 по6фаз PASS,
12engine frames осмотрены; public preview не physical keyboard/button.
Stale handle Proxy inspection0, source revision clear/history сохранены.
UI1/0, canonical1/0, map13/0; PID18976/24436 gone черезquit. Targeted56PASS;
voice package10/11 с WinError1314. Full085259Z-1dac4b:46/753/6failed/false.
[Native voice report](../../../06-voice/03-voice-feedback/reports/native-voice-text-2026-10-12.md).
Уроки18/19 применять перед native layout/input. Physical input/capture channel,
C1 bootstrap/contracts, microphone/ASR и человеческая проверка остаются открытыми;
независимая подготовка native preparation scene возможна по её existing source plan.

Native preparation continuation завершило ограниченный API/render smoke existing
трёх private drafts в отдельной fixture. Canonical anonymous outer / inner
CoachPreparationRoot компилируется; fixed preparation15/14 сохранён. Test-only
17sources:16active compiled +retained generated XML отдельно. В двух launches
шесть фаз bound/team/complete/reset/disposed/rebound и12actual кадров1280×720.
Первый run выявил пустые navigation labels и scroll до старого layout; scoped
Label width:fit-children в трёх canonical styles и отложенный API scroll проверены
повторным запуском. Local complete/serverConfirmed=false, remove fifth player
очищает heroes/preparation; stale Proxy inspections0. PID27560/28100 gone черезquit.
Targeted45PASS; preparation package20/21 с WinError1314. Required full101831Z-b01147:
46suites/753passed/6failed/verified=false. Уроки20–22, source-only handoff15/14,
один technical critic без замечаний; human second owner остаётся открытым.
[Native preparation evidence](../../../11-integration/01-ui-binding/reports/native-preparation-2026-10-12.md).
Следующее продолжение сначала сверяет текущий PLAN/PROGRESS и зависимости: physical
input/hittest, другой размер экрана и общий UI transition ещё не проверены. API scroll
не mouse evidence; TEST profiles/hero IDs не real identity. C1 bootstrap/contracts,
server readiness/effects/start, права ручного ввода и возврат ИИ остаются открытыми.

Следующий bounded native smoke выполнен для existing match observation. Anonymous
canvas/inner CoachMatchObservation компилируется; fixed10/9/2XML inputs/38ID сохранён.
Test-only12sources/11active compiled +retained generated XML отдельно. First5фаз
PASS/rebound failed: ошибочное driver ожидание blank вместо ready missing slot
«Имя неизвестно». Production JS не изменён, final6/cycle PASS;11actual frames1280×720.
Invalid opponent source сохраняет history; invalid history сохраняет roster;
history recovery duplicate не добавляет; rebind TEST FRESH, stale Proxy reads0.
PID25624/10788 quit→gone; source-only handoff121608Z-e67cbc verified10/9/false flags.
Targeted22PASS, package8/9 с WinError1314; full121351Z-60b1f6:46/753/6failed/false.
[Evidence](../../../11-integration/01-ui-binding/reports/native-observation-2026-10-12.md).
Урок23 применять перед ready/missing native assertions. Template map render остаётся
ограниченным: final чёрный minimap/голубая область слева, причина неизвестна.
CommonHUD/physical input/C1/real identity/server authorization/human second owner
открыты. Следующий независимый шаг сверяет PLAN и existing intervention/mouse source
зависимости; не объявлять accepted history исполнением и TEST heroName entity mapping.

Продолжение existing intervention screen завершило bounded native smoke:8API фаз в двух launches,16actual кадров1280×720. Initial pane невидима при API PASS; canonical scoped CSS исправление проверено повторным запуском. Fixed13/12/2inputs/50ID сохранены; fixture15sources/14active compiled+retained XML. Selected B и captured A разделены, actual Schedule(5) приводит к unknown и блокирует повтор; ACK TEST stub не MANUAL. Date.now samples4958/4952ms не доказывают точность deadline/lease. Dispose/rebind: stale Proxy inspections0. Own PID27436/29568 gone послеquit, Steam сохранён. Targeted27PASS; package11/12 с WinError1314; required full130742Z-081143:46suites/753passed/6failed/false. Один technical critic без замечаний; human owner открыт. [Отчёт](../../../11-integration/01-ui-binding/reports/native-intervention-2026-10-12.md).
Следующее продолжение сверяет PLAN/PROGRESS и зависимости source mouse targeting; physical input/hittest, серверные полномочия, lease/AI return, identity, commonHUD/map и другой размер экрана остаются открытыми. Source-only handoff13/12 сохраняет native flagsfalse/not_run.

Existing mouse-targeting group проверена native:8API фаз/8actual кадров1280×720. Fixed7/6/7ID и production sources сохранены; fixture9outputs/8active compiled+retained canonical generated XML отдельно. Captured actor A, last_hit/deny/attack, controlled TTL boundary999/1000, move при hidden/stale, invalid/recovery и old API DTO reads0 проверены. Own PID27104 quit→gone, Steam сохранён. Targeted27PASS; package8/9 с WinError1314. Required full133855Z-3b442f46/753/6failed/false; packaging162/8WinError1314. Source-only handoff134114Z-00b8f6 verified7/6 с native false/not_run. Один technical critic без замечаний; AI review не второй человек. [Native evidence](../../../11-integration/01-ui-binding/reports/native-mouse-targeting-2026-10-12.md). Урок27 разделяет raw и generated fingerprints.
Следующий шаг сверяет PLAN/PROGRESS и независимые C2-05 зависимости; actual mouse/world mapping/authorized observations/clock/server/lease/возврат ИИ не подменять TEST API. Common HUD/map/другая resolution/человеческая приёмка открыты.

Windows source portability завершена: full141407Z-b03abd46suites/1020passed/28explicit skipped/6incomplete/0errors/verified=false/exit1. Legacy failed_suites сохраняет6unverified IDs. Root test-only probe skip только Windows1314 до fixture mutation, агент разделил mixed packaging/handoff cases; tamper/integrity/preservation/junction/ownedtimeout checks выполняются. Full запуск вне разрешённой песочницы не менял OS/security, taskkill только owned PIDs. Incomplete25symlink/2long-path/1UnixFIFO, не PASS. Один final critic без замечаний; human owner открыт. [Отчёт](../../../11-integration/03-end-to-end/reports/windows-portability-2026-10-12.md), урок28. C1-04 всё ещё без реализации; C2-05-03 adapter зависит от real contract. Следующее продолжение сверяет PLAN/PROGRESS/реальные входы; не менять OS ради зелёного отчёта и не подменять input/lease/AI return TEST API.
