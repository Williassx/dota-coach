# Работа агентов в Dota Coach

## Назначение проекта

Игра-симулятор тренера команды Dota 2 с персональными моделями игроков по их матчам,
подготовкой команды, голосовыми приказами и временным ручным вмешательством.
Быстрый каталог 175 ролей: [Агенты.md](Агенты.md).
Полные обязанности: [docs/agents.md](docs/agents.md).

## Организация работы

- **Начинайте новую работу в библиотеке своего создателя:**
  [создатель 1](creators/creator-1/PLAN.md) — сервер, ИИ и данные;
  [создатель 2](creators/creator-2/PLAN.md) — интерфейс, карта, мышь и голос.
  Затем выбирайте папку раздела и подпункта. Исследования, исходники и проверки
  первоначально ведутся там. Порядок расширения: [правила библиотеки](creators/shared/WORKFLOW.md).
- Оба создателя равноправны. Изменение проверяет другой; после необходимых проверок
  объединить его может любой. Общие файлы и контракты имеют одного автора на задачу.
- Исходники не копируйте в обе библиотеки. Конечный аддон собирается отдельно по
  [правилам интеграции](creators/shared/INTEGRATION.md); сборочный каталог не редактируется.
- Используйте весь каталог [Агенты.md](Агенты.md) по этапам и условиям
  [реестра 175 ролей](creators/creator-2/01-foundation/01-workspace-audit/notes/agent-activation-2026-10-12.md).
  Роль и процесс различаются: один исполнитель может выполнять несколько специализаций.
  После изменения docs/agents.md обновляйте быстрый индекс; новые номера не дублируйте.
- Для каждого задания определяйте ведущую роль, область изменений и критерии приёмки.
- Делегируйте независимые задачи, когда это разрешено пользователем и текущими
  инструкциями среды. Соблюдайте доступный лимит параллельных агентов.
- До параллельных изменений согласуйте интерфейсы и распределите файлы.
- Роли с пересекающимися обязанностями консультируют ведущего исполнителя;
  не реализуйте одну функцию независимо несколькими агентами.
- Сохраняйте пользовательские изменения. Не добавляйте новые механики вне текущей задачи.
- Проверяйте результаты подходящими командами и сообщайте фактические результаты.
- Пользователь поручил продолжать самостоятельно: не перекладывайте рутинные
  команды и передачу заданий на него. Недоступный канал Windows фиксируйте как
  ограничение; независимые исходники и проверки продолжайте в доступной среде.

## Диспетчер и расход токенов

- Применяйте [порядок подключения и экономии](creators/shared/AGENT-EFFICIENCY.md) и
  [настройки](creators/shared/agent-policy.json). Последнее поручение пользователя
  от 12 октября 2026: задействовать все 175 специализаций по мере их условий,
  самостоятельно передавать полезные задачи и учиться на действиях по правилам проекта.
  Оно расширяет прежний лимит одного помощника; регулярные пять критиков не возвращаются.
- Обычные ответы и обсуждения ведите самостоятельно, без критиков и подагентов.
- Перед задачей выполняйте роль 173: выбирайте релевантные роли и полезную группу этапа.
  Самостоятельные результаты можно делегировать без повторного запроса; общие файлы
  имеют одного автора. Лимит среды сейчас четыре процесса всего, включая основной;
  используйте до трёх помощников и повторно свободные слоты, не запускайте пустые роли.
  Зависимые задачи и недоступные native/data/server действия фиксируйте отдельно.
- Критик — только после завершения подпроекта, по умолчанию один. Не запускайте
  его для планирования, каждого подпункта или вопроса пользователя.
- Роли 174/175 ведут учёт и сокращают контекст без постоянных дополнительных процессов.
  Отсутствующие token usage/стоимость отмечайте null, не придумывайте экономию.
- Не перечитывайте навыки и полные документы без новой причины; выдавайте краткие
  результаты инструментов и сохраняйте длинные логи отдельно. Проверки приёмки сохраняйте.
- После значимого действия и сбоя сохраняйте проектный урок: факт/команду, причину,
  изменение подхода и проверку. Перед похожим действием применяйте этот урок;
  не повторяйте неработающий шаг без нового основания. Это рабочие заметки проекта,
  не изменение весов модели и не запись в глобальную память Codex.

## Планирование и навыки

- Перед планированием читайте [итоговые решения](docs/decisions.md), [замысел](docs/project-brief.md),
  [дорожную карту](docs/roadmap.md), [очередь задач](docs/backlog.md) и
  [порядок применения навыков](docs/skills.md).
- Для проектирования используйте доступный `superpowers:brainstorming`,
  для технического плана после рассмотрения спецификации — `superpowers:writing-plans`.
  Перед заявлением о готовности применяйте `superpowers:verification-before-completion`.
- Пользовательские решения отделяйте от предложений. Первый путь — кастомка внутри
  Dota 2 с Workshop Tools на Windows, затем демонстрация Valve. Отдельная игра на
  основе Dota требует применимых письменных прав. Браузер был прежним предложением.
- Актуальные документы имеют приоритет над архивами. Исключённый пользователем
  настольный формат не предлагайте повторно.
- Достоверность модели реального игрока проверяйте на отложенных матчах;
  различие двух ИИ не является доказательством сходства с реальными людьми.
- Измеренные признаки, оценку модели и игровые черты характера помечайте отдельно.
- При недостатке реальных данных используйте явно обозначенные тестовые профили;
  не заявляйте о подтверждённой оцифровке.
- Цель — именно Dota 2 с собственной тренерской идеей. Не заменяйте её другой MOBA
  без решения пользователя; путь реализации исследует юридическая команда (161–172).
- Перед выводами о правах читайте [юридический план](docs/legal/plan.md) и
  [первичный разбор](docs/legal/initial-review.md). Различайте проверенный документ,
  предположение и недоступный источник; сетевой отказ не является отказом правообладателя.
- Для карты фиксируйте версию и игровую структуру отдельно от изображения.
- При реализации обеспечьте временность ручного вмешательства и возврат ИИ.

## Текущее состояние

Продуктовая игра и общая приёмка Dota ещё не реализованы. Созданы библиотеки двух
создателей, диагностические помощники и исходники панели Panorama с облачными
поведенческими проверками; их команды не являются
сборкой или тестами игры. Windows-путь — D:\AI\dota2coach; облачный Linux не означает
доступ к этому диску. Пользователь выбрал создателя 2; C2-01-foundation ещё требует
нативной приёмки. Независимо подготовлены локальные карточки C2-02-01 без серверной
интеграции и панель состояний приказов C2-02-02 с подключаемым переходником;
общий контракт остаётся зависимостью. C2-02-03 связывает выбор карточки с адресатом
через локальный координатор; общий HUD, mouse/hittest и сервер остаются открытыми.
Локальный клон подтверждён пользователем.
Для C2-03-01 подготовлен ограниченный аудит файлов карты; он не подтверждает
геометрию, обзор, патч или загрузку в Dota. Сопоставляйте build_id с установкой,
не используйте референс 7.40 как runtime evidence.
Для C2-03-02 подготовлен явный запрос фокуса живого героя своей команды.
Requested не подтверждает прибытие камеры; stable id→entity, native API/hittest,
маркеры и общий HUD открыты. Выбор/refresh не перемещает камеру и не выдаёт приказы.
Для C2-03-03 подготовлена частная проекция/панель целей с revision/local expiry.
Не объявляйте frontend filtering авторизацией, gone — смертью, ready — допустимым
приказом. Скрытые id допускаются только для ранее разрешённого знания; C1-инвариантность
наблюдений, настоящий источник/clock/identity/native обзор остаются открытыми.
Ранний C2-07-01/C2-11-02 содержит inert HUD template и exact 13 source bundle.
Не включайте demo/auto-bind в этот kind, не расширяйте probe policy. Native HUD,
интегратор/сервер и полная приёмка остаются открытыми; build output не редактируется.
Перед реализацией согласуйте локальную спецификацию функции
и технический план. Используйте текущий изолированный checkout; создание отдельного
Git worktree допустимо по явному запросу пользователя.

C2-11-01 локально связывает четыре области; camera и send/report используют общий
lifecycle guard. Entity mapping не доказывает identity, закрытие UI не отменяет
серверный запрос. Bootstrap, общий server contract и native приёмка открыты.

C2-04-01 содержит pure local team draft без panel/native/server/storage. id —
виртуальный игрок, profileVersion отдельна; complete только count 5, serverConfirmed
всегда false. Source mapping людей, персональное сходство, герои/роли открыты.

C2-04-01 panel source separate from match HUD. Explicit bind/dispose, all required
nodes checked including offpage; stale handlers expire before input getters.
Definitions/graph/VM tests are not native screen proof; no submit/start/storage.

C2-04-02 pure hero-role proposals draft: local uniqueness is preliminary policy,
not server support. Structured kind retained; origin/compatibility/coverage warnings.
Atomic conflicts preserve old choice; serverConfirmed=false, no UI/native/start.

C2-04-02: отдельная source панель предложений с explicit bind/dispose и 29 новыми
проверками. Фокус только просмотр; version change очищает его. Native/сервер/реальные
профили/навигация и второй владелец открыты, match HUD/bundle не расширен.

C2-04-03: pure draft тактики/разговора, два explicit local choices, 28 сценариев.
Изменение полного lineup/option снимает выбор; intent не означает эффект.
C1-07-02/03/панель/native/server/второй владелец открыты.

C2-04-03: отдельная explicit source панель тактики/разговора, 22VM+5graph.
Намерение/version до выбора, selected/remove/clear, separateemptyhints, технический
lineup и fixed warnings. No effect/start/HUD; C1/native/server/secondowner открыты.

C2-11-01 содержит также pure preparation flow из3private моделей. Downstream
source reset сохраняетhighwater; fullcontext сравнивается по draft, busy nestedcalls
отклоняются безDTOreads. Три existing панели подключены optionalports к одной privateflow;
522 source checks проходят. XMLcomposition/C1/server/native/secondowner открыты.

C2-11-02: third fixed preparation source kind15outputs/3canonicalXMLinputs,
generatedsharedlayout9definitions, VMactualbind/click; общий итог542. Existing13HUD/
probe policy сохранены. Bootstrap/общийпереход/native/server/secondowner открыты.

C2-05-01: purelocalrequestprojection reuseOrders snapshot(id?) readAPI.29request/
6newsnapshot,577sourcechecks. ACK≠MANUAL; mode-observed≠permission/causality.
Panel/transport/lease/native/server/ИИreturn/secondowner остаются открытыми.

C2-05-01: отдельная панель запроса с явным bind/dispose, 26 VM и 5 XML проверками;
полная регрессия 608. Таймер ACK пять секунд не является lease. Скрытый обязательный
дочерний элемент блокирует отправку. HUD/пакет, настоящий транспорт/серверное право,
ручной ввод/возврат ИИ, native и второй владелец открыты.

C2-11-01: локальная связь Roster/Requests, 27 новых сценариев и общий итог 635.
Selected card и capturedactor разделены, roster дополнительно закрывает canRequest;
сообщения учитывают общий gate. Панели/сервер/native/возврат ИИ/второй владелец открыты.

12октября native empty HUD13/12 показан при двух разрешениях; default CSS/отступы
исправлены по кадрам, отдельный visible setter cycle проверен. Следующий independent
test-only HUD binding использует15source outputs/14active compiled UI outputs:
пять TEST/synthetic карточек, selection/removal/dispose/rebind и stale handle,
пять actual кадров1280×720. Production JS/XML и fixed kinds не расширены.
Не трактуйте TEST control AI как серверное наблюдение или selectPlayer как mouse click.
Native input/hittest, C1/server/identity/lease/ИИreturn, полноценная карта/матч,
полная source регрессия и другой создатель остаются открытыми.

12октября отдельная native text-preview fixture проверила6фаз existing explicit
VoicePanels,12кадров1280×720 в двух launches. Canonical voice XML теперь anonymous
outer/inner VoiceTextRoot; TextEntry explicit readable styling. Fixed6/5 сохранён,
test-only8sources/7active compiled+retained XML compiled отдельно. Public preview
не keyboard/button/hittest; microphone/ASR/C1/сервер/реальные identity/второй владелец
открыты. Full Windows46/753/6failed/verifiedfalse; targeted56PASS.

12октября native preparation fixture проверила existing three-draft flow:6APIфаз,
12actual кадров1280×720 в двух launches. Canonical outer anonymous, inner
CoachPreparationRoot; navigation Label sizing исправлен в трёх styles. Fixed
preparation15/14 сохранён, fixture17sources/16active compiled +retained generated XML
отдельно. Local complete/serverConfirmed=false; удаление пятого игрока очищает
heroes/preparation, dispose/rebind блокирует stale DTO inspection. API scroll после
layout не physical input. Targeted45PASS, package20/21 с WinError1314; full46/753/
6failed/verifiedfalse. Общий UI transition/bootstrap, C1/server/реальные profiles,
physical input/hittest, другая resolution и human second owner открыты.

12октября native match observation проверила6existing APIфаз opponents/history в
отдельной TEST fixture1280×720. Initial5PASS/rebound failed из-за fixture ожидания
missing ready slot; исправлен только TEST assertion, final6/cycle PASS,11actual frames.
Canonical anonymous canvas/inner CoachMatchObservation, fixed10/9/2inputs/38ID
сохранены;12fixture sources/11active compiled+retained XML отдельно. Independent
invalid/recovery и dispose/rebind/stale Proxy inspection0 проверены. Targeted22PASS,
package8/9 с WinError1314; full46/753/6failed/false. accepted — presentation snapshot,
sourceAuthorizationConfirmed/nativeConfirmed=false. Input/C1/commonHUD/human owner
и map render открыты; final template minimap/голубая область не имеют установленной причины.

12октября native intervention проверила8existing APIфаз в двух TEST launches1280×720/16actual frames. Initial API PASS при невидимой request pane; scoped composition CSS исправление подтверждено fresh launch и geometry guard. Canonical anonymous canvas/inner CoachInterventionScreen сохраняет fixed13/12/2inputs/50ID. Fixture15sources/14active compiled+retained XML отдельно. Selected B/captured A, ACK≠MANUAL, actual Schedule(5) timeout unknown, stale Proxy inspections0 проверены. Targeted27PASS; package11/12 с WinError1314; full46/753/6failed/false. Local stub/uncalibrated wall clock не server authority/lease; input/C1/AI return/commonHUD/map/human owner открыты.

12октября native mouse-targeting проверила8existing coordinator APIфаз/8actual frames1280×720. Fixed7/6/7ID и production JS/XML/CSS сохранены;9fixture outputs/8active compiled+retained canonical targeting XML отдельно. Captured actor A сохраняется при смене цели; controlled TTL1000ms снимает target draft, move независим от stale source; invalid/recovery и dispose/rebind/stale Proxy inspections0 проверены. Targeted27PASS, package8/9 с WinError1314; required full46/753/6failed/false, packaging162/8WinError1314. TEST clock/actor/targets не real mouse/freshness/identity/authorization; C1/server/lease/AI return/commonHUD/map/human owner открыты.

12октября Windows source portability разделила incomplete skips и actual errors, сохранив strict verifiedfalse/exit1 и legacy failed_suites. Final46suites/1020passed/28skipped/6incomplete/0error suites. Общий test-only symlink probe пропускает только WinError1314; mixed guards/tamper/preservation разделены. Actual junction/ownedtimeout tests PASS вне разрешённой песочницы; OS/security/productionguard не изменены.25symlink/2deep-path/1FIFO cases остаются неподтверждёнными. C1-04 реализации отсутствуют; C2-05-03 cancel/lease/AI return не строится по выдуманному контракту. Humanowner/native/game acceptance открыты.

C2-06-01 bounded Windows microphone audit: explicit FIFINE3s PCM/cleanup/hash подтверждены, sandboxopen1 vs approvedoutsideopen0; OS/privacy unchanged. 4inputs/query0 не permission/ASR. Raw audio толькоignoredlocalbuild; diagnostic capture command не ordinary test/import. Speech/ASR/русский runtime/bridge/C1/human owner открыты;52/213 отражает2documentary actions, не голосовуюприёмку.

C2-06-01 localASRpilot: faster1.2.1/PyAV19decode несовместимы, отдельныйpinnedav18 overlay проверен; tiny model поexactHFrevision/LFSsizehash. Loaded+VAD quiet3s/segments[] не positive speech recognition; Python socket guard не native/OS networkproof. Actual speech/accuracy/bridge/C1/humanowner открыты. Model/deps ignoredlocal, smoke внеordinarycatalog; progress52/213неповышен.

C2-03-02 native TEST camera:7API phases/7actual frames1280×720, existing gateway
и panel unchanged. FixedHUD13, fixture15sources/14activecompiled+retainedinert1.
Выбор/refresh0focuscalls; native activation1/requested, invalidindexreject,
dispose/rebind/idgetterreads0. LookAtdistanceXY4520.37 @1.5sec, позднее исходная
позиция: arrival/realidentity/hittest/markers/realmap открыты, причина возврата
не установлена. OwnPID29544quit→gone; JSON timestamp сравнивать по точным UTCticks,
не stringvsDateTime. Full48/1031passed/28skipped/6incomplete/0errors/verifiedfalse.
Source-onlyflagsfalse; humansecondowner остаётся открытым.

C2-03-02 motion driver:20baseline/80post native samples, oneprogrammaticrequest,
4actualframes. Exactcamera/motionvariants сохраняют fixedHUD13/default; postrequest
guard доownorigin, rawprojectiontriple/thirdmeaningunknown. Baselinealreadynear18/20,
postnear2/80, activecursor/buttons/hero means uncontrolledcomparison, неcausalarrival
или edgepanfix. Native preferences/cvars unchanged; failedm2/m3 и100samples сохранены.
All3ownPIDsquitgone. Full49/1039passed/28skip/0errors/false; humanowneropen.

C2-09-02 bounded native preparation scaling:12actualPNG,6APIphases накаждомразмере.
1600×900/build25845666 reset modelPASS приscroll−695;1024×768/new25894101 scroll0.
Interrupted secondrun/causeunknown preserved; builddrift требуетfreshcompile17outputs.
Differentbuild/uncontrolledinput не causal comparison/productresolution support.
Canonical/fixedkind unchanged, ownclientsgone, full49/1039pass/28skip/0errors/false.
Physicalinput/storage/общийtransition/humansecondowner открыты; progress53/213unchanged.

13октября resettrace вonebuild25894101:4ABAB/131records/124samples/6frames,
allfinaltop0,oldfailureNOTreproduced. Immediategetteroldvalue неfinal layout,
firstsample0observations неSLA; physicalInputControlledfalse/globalcallbackunchanged.
SyntheticIrina3WAV decoderpositive при9edits11refwordsWER81.8% only3samples;
real speech/accuracy/bridgefalse,commands0. Full50/1059pass/28skip/0errors/false,
source/probe/fixedkinds productionunchanged;humanowneropen. Порученная2часассессия
13октября06:01:04–08:01:04UTC продолжаетсяпоC2PLAN/зависимостям.

C2-09-01 registry83C2src/98internalrefs/104trackedmedia/10source recipes сохраняет
datedscope/dd01f0b+progressSVGoverride, rightsnot_assessed/implicitengineexcluded.
Concept/reportPNG/generatedgraph неpromotedruntimeasset; onlyregistrycheckbox
marked54/213(25.4%).187hashes/membership/references/docs verified;humanowneropen.

13 октября подключены actual C1 коммиты 1c44da4/b1f2c48/71b20c0 (172 файла),
C2 рассмотрел pure core: Lua8/voice13 PASS, MANUAL/priority/revision/source/return/
binding guards исправлены; source каталог85/1242PASS/28skip/6incomplete/0errors/
verifiedfalse. C1progress112/181 не повышен, 69 open actions. Исторические фразы
«C1-04 отсутствует» относятся к прежнему срезу; новые pure модули доступны, но
общий контракт/actor-authority/transport/native/lease/real AI return открыты.

C2-06-02 grammar pilot13октября: exact sample_set baseline/parser_grammar,
oldreceipts/default unchanged;12purePASS. Actual3IrinaWAV→same tiny/beam1/CPUint8/
ru/VAD:6edits7wordsWER85.7% только3samples; refs3localready/hyps0readyunknown_action,
commands/nativeattempts0. RootPCM/model/metric/actualparserguards verified,
real speech/accuracy/bridgefalse, vocabulary/decoder unchanged; C254/213 unchanged.

C2 posthandoff13октября: actual3synthetic pairs черезexistingVoicePanels показывают
ready→unknown_action с Address/Action/proposal cleanup, capturedrev иstalehandle0reads.
24VM/full85/1245PASS/28skip/6incomplete/0errors/false; production unchanged.
C2-01-03 gapreview12sourcehashesLF/fields совпали, commoncontract/adapter несозданы.
Nextsharedscope: trustedidentity+snapshot/outcome+revision/epoch/sequence+lease/gameclock;
не связывать библиотеки прямым переименованиемполей. C254/213/nativehumanopen.
