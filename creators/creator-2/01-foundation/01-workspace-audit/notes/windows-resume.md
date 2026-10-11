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

## Сначала подтвердить среду и сохранить изменения

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

Все действия отдельно в creators/creator-2/00-action-log/YYYY-MM-DD.md, UTC.
Новые исходники сначала в библиотеке создателя2. Прочие отделы/контракты не менять.
Чекбоксы/graph только по evidence; source checks не заменяют native/second owner.
Экономный порядок agents: root solo, один final critic после готового подпроекта,
точные token/cost неизвестны → null. Подходящие checks, docs/graph/Git diff check,
normal fast-forward main push, remote SHA/clean; публикация ранее разрешена.
