# План создателя 2

> Для агентной работы: используйте `superpowers:executing-plans` для согласованного подпункта. Критики рассматривают результат; расширение реализации требует соответствующей спецификации.

**Цель:** интерфейс, карта, ввод мышью и голос тренера.
**Архитектура:** рабочая библиотека этого создателя содержит единственные исходники его отдела. Каждая задача начинается в своём подпункте; общие контракты рассматривают оба равноправных владельца.
**Технологии:** Dota 2 Workshop Tools на Windows; серверные скрипты и Panorama проверяются по фактическому шаблону. Python 3 без внешних пакетов используется только для диагностического помощника.
**Спецификация организации:** [WORKFLOW.md](../shared/WORKFLOW.md). Спецификации функций создаются в соответствующем подпункте до реализации.

[Журнал выполненных действий](00-action-log/README.md) — отдельная служебная папка;
он не меняет нумерацию 12 разделов и 36 подпунктов.

[График выполнения разделов](PROGRESS.md) автоматически строится по чек-листам подпунктов.
В конце каждой задачи обновляйте чек-лист по фактам и выполняйте генератор из
[00-progress](00-progress/README.md); проценты вручную не задаются.

## Общие ограничения

- Начать с кастомки Dota 2; голос и реальные персональные модели сохраняются в целях продукта.
- Реальные пути Tools и API сначала проверить; исходники начинать внутри этой библиотеки.
- Каталоги `src/`, `tests/`, `fixtures/`, `notes/`, `reports/` создаются при появлении реальных файлов.
- Статус и критерии каждого подпункта находятся в его README; таблица ниже — навигация, а не отдельная копия статусов.
- Изменения проверяет другой создатель; после необходимых проверок объединить их может любой.
- Публикация и письма требуют отдельного поручения; независимый перенос Dota требует применимых письменных прав.

## На что смотреть при проверке

- Недоступная Windows: не заявлять выполненное клонирование, запуск Tools или Dota.
- Чужой/умерший герой и старое событие: не допускать зависшего или ошибочного управления.
- Повторный приказ/снимок: не исполнять дважды и не откатывать режим интерфейса.
- Неполные данные: синтетический ИИ и игровые черты явно отличать от измеренной модели.
- Общий файл: один автор задачи, просмотр обоими, без одновременных несовместимых изменений.

## Последовательность

Первый подпункт — **C2-01-01**. Аудит карты, микрофона и материалов можно вести параллельно; изменения сервера остаются у создателя 1.
Начальная проверка C2-01-02/C1-01-02 подготавливается параллельно в разных файлах:
серверный обработчик создаёт отдел 1, панель — отдел 2; затем соединение проверяется совместно.
Зависимости определяют готовность задачи: номер раздела сам по себе не требует завершить все предыдущие разделы.
Пока Windows недоступна, отдельно подготовлены модель и Panorama-исходники
[C2-02-01](02-coach-interface/01-roster-cards/README.md). Их облачная проверка не
закрывает C1-01-03, фундамент или нативную приёмку карточек.
В [C2-02-02](02-coach-interface/02-status-orders/README.md) подготовлены состояния
приказа и Panorama-панель с явно передаваемым переходником. Серверные команды
и нативная приёмка этого подпункта остаются открытыми.
В [C2-02-03](02-coach-interface/03-control-input/README.md) подготовлен координатор
выбора карточки и адресата. Общий HUD, клики мыши в движке, серверный переходник
и рассмотрение вторым владельцем остаются открытыми.
В [C2-03-01](03-map-view/01-map-audit/README.md) подготовлен read-only аудит
файлов карты и отдельного Steam build_id. Реальная карта/патч/геометрия ещё неизвестны.
В [C2-03-02](03-map-view/02-camera-overlays/README.md) подготовлен явный фокус живого
героя команды. Native arrival, связь цели с игроком, обозначения и HUD открыты.
В [C2-03-03](03-map-view/03-visibility-targets/README.md) подготовлены частная
проекция наблюдения и очистка выбранной цели при потере обзора/expiry. C1-03-01,
native источник/identity/clock/мышь и второй владелец остаются открытыми.
Рано подготовлены [шаблон HUD C2-07-01](07-match-screen/01-own-cards/README.md)
и [source-пакет C2-11-02](11-integration/02-addon-packaging/README.md) по правилу
ранней сцены. Это не закрывает C2-05-03/C1-07-01/C2-11-01/C2-10-01 или native HUD.

### 01. [Локальная среда и интерфейсная основа](01-foundation/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-01-01: Рабочая библиотека и пути Tools | Нет | [01-workspace-audit](01-foundation/01-workspace-audit/README.md) |
| C2-01-02: Минимальная проверка Panorama | C2-01-01, C1-01-01 | [02-panorama-capability](01-foundation/02-panorama-capability/README.md) |
| C2-01-03: Предложения интерфейса к общему контракту | C2-01-02 | [03-interface-contract](01-foundation/03-interface-contract/README.md) |

### 02. [Основные элементы тренерского интерфейса](02-coach-interface/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-02-01: Карточки виртуальных игроков | C1-01-03 | [01-roster-cards](02-coach-interface/01-roster-cards/README.md) |
| C2-02-02: Режимы и простые приказы | C2-02-01 | [02-status-orders](02-coach-interface/02-status-orders/README.md) |
| C2-02-03: Маршрут ввода | C2-02-02 | [03-control-input](02-coach-interface/03-control-input/README.md) |

### 03. [Карта и наблюдение](03-map-view/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-03-01: Версия и доступность штатной карты | C2-01-01 | [01-map-audit](03-map-view/01-map-audit/README.md) |
| C2-03-02: Камера и тренерские обозначения | C2-03-01, C2-02-03 | [02-camera-overlays](03-map-view/02-camera-overlays/README.md) |
| C2-03-03: Обзор и допустимые цели | C2-03-02, C1-03-01 | [03-visibility-targets](03-map-view/03-visibility-targets/README.md) |

### 04. [Предматчевая подготовка](04-preparation-ui/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-04-01: Выбор разных игроков | C2-02-01, C1-07-01 | [01-team-picker](04-preparation-ui/01-team-picker/README.md) |
| C2-04-02: Выбор героев и ролей | C2-04-01, C1-07-01 | [02-hero-role-picker](04-preparation-ui/02-hero-role-picker/README.md) |
| C2-04-03: Тактика и поддержка | C2-04-02 | [03-tactics-morale](04-preparation-ui/03-tactics-morale/README.md) |

### 05. [Мышь и возврат ИИ](05-intervention-ui/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-05-01: Запрос ручного вмешательства | C2-02-03, C1-04-01 | [01-request-ack](05-intervention-ui/01-request-ack/README.md) |
| C2-05-02: Перемещение и атака мышью | C2-05-01, C1-04-01 | [02-mouse-targeting](05-intervention-ui/02-mouse-targeting/README.md) |
| C2-05-03: Отмена, завершение и причины | C2-05-02, C1-04-03 | [03-return-feedback](05-intervention-ui/03-return-feedback/README.md) |

### 06. [Голос тренера](06-voice/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-06-01: Настоящий микрофон и допустимая интеграция | C2-01-01 | [01-microphone-probe](06-voice/01-microphone-probe/README.md) |
| C2-06-02: Распознавание и адресация | C2-06-01, C1-01-03 | [02-recognition-parser](06-voice/02-recognition-parser/README.md) |
| C2-06-03: Ответ и резервный ввод | C2-06-02, C2-02-02 | [03-voice-feedback](06-voice/03-voice-feedback/README.md) |

### 07. [Экран матча по эскизу](07-match-screen/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-07-01: Пять своих карточек | C2-05-03, C1-07-01 | [01-own-cards](07-match-screen/01-own-cards/README.md) |
| C2-07-02: Верхний ряд соперников | C2-07-01, C1-09-02 | [02-opponent-cards](07-match-screen/02-opponent-cards/README.md) |
| C2-07-03: Приказы и события справа | C2-07-02, C2-06-03 | [03-orders-timeline](07-match-screen/03-orders-timeline/README.md) |

### 08. [Разбор и объяснения](08-analysis-ui/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-08-01: Просмотр журнала | C2-07-03, C1-09-03 | [01-event-replay](08-analysis-ui/01-event-replay/README.md) |
| C2-08-02: Основания персонального профиля | C2-08-01, C1-06-03 | [02-profile-evidence](08-analysis-ui/02-profile-evidence/README.md) |
| C2-08-03: Итог и влияние тренера | C2-08-02 | [03-post-match](08-analysis-ui/03-post-match/README.md) |

### 09. [Оформление и доступность](09-presentation/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-09-01: Происхождение графики и звука | Нет | [01-assets](09-presentation/01-assets/README.md) |
| C2-09-02: Настройки и масштабирование | C2-07-03 | [02-settings-layout](09-presentation/02-settings-layout/README.md) |
| C2-09-03: Читаемость и локализация | C2-09-02 | [03-accessibility-localization](09-presentation/03-accessibility-localization/README.md) |

### 10. [Проверка игроками](10-user-testing/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-10-01: Установка и запуск кастомки | C2-01-02 | [01-install-guide](10-user-testing/01-install-guide/README.md) |
| C2-10-02: Сценарии нового тренера | C2-09-03, C2-10-01 | [02-user-scenarios](10-user-testing/02-user-scenarios/README.md) |
| C2-10-03: Исправления по наблюдениям | C2-10-02 | [03-usability-fixes](10-user-testing/03-usability-fixes/README.md) |

### 11. [Интеграция и сборка](11-integration/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-11-01: Связь UI с сервером | C2-05-03, C1-04-03 | [01-ui-binding](11-integration/01-ui-binding/README.md) |
| C2-11-02: Сборка аддона из библиотек | C2-11-01, C2-10-01 | [02-addon-packaging](11-integration/02-addon-packaging/README.md) |
| C2-11-03: Сквозная проверка интерфейса | C2-11-02, C2-07-03, C2-08-03 | [03-end-to-end](11-integration/03-end-to-end/README.md) |

### 12. [Материалы демонстрации и выпуска](12-release/README.md)

| Подпункт | Зависимости | Рабочая папка |
|---|---|---|
| C2-12-01: Условия и атрибуция | C2-09-01, C1-12-01 | [01-rights-display](12-release/01-rights-display/README.md) |
| C2-12-02: Презентация тренерской идеи | C2-11-03, C2-12-01 | [02-valve-presentation](12-release/02-valve-presentation/README.md) |
| C2-12-03: Руководство выбранного выпуска | C2-12-02 | [03-release-guide](12-release/03-release-guide/README.md) |

## Добавление новых частей

1. Выберите раздел по ответственности. Для нового подпункта используйте следующий свободный номер `NN-purpose` и ID `C2-SS-NN`.
2. Создайте README с целью, зависимостями, файлами, приёмкой и проверяющим; добавьте ссылку в README раздела и эту таблицу.
3. Для нового крупного раздела выделите следующий свободный номер; не перенумеровывайте существующие задачи и ссылки.
4. Разбивайте подпункт глубже только по самостоятельной ответственности. Не переносите чужую реализацию и не дублируйте общий контракт.
5. Сохраняйте единственные исходники в исходной папке; сборочный вывод публикуется отдельно по [правилам интеграции](../shared/INTEGRATION.md).

Частично подготовлен [локальный координатор C2-11-01](11-integration/01-ui-binding/README.md):
общий выбор и lifecycle четырёх областей без bootstrap/server. Проверены 292
облачных сценариев и source-пакет из 13 ресурсов. Полная серверная/native приёмка открыта.

[C2-04-01](04-preparation-ui/01-team-picker/README.md): локальный черновик состава
проверен отдельно (28 сценариев); общий облачный итог 320. UI/реальные модели/сервер
и приёмка второго владельца ещё открыты.

C2-04-01: исходники отдельной панели и 26 новых проверок подготовлены;
вместе 346 облачных сценариев. Панель не включена в match HUD; native/server открыты.

[C2-04-02](04-preparation-ui/02-hero-role-picker/README.md): pure local hero-role
proposal draft (28 сценариев), общий итог 374. C1/native/real source и UI открыты.

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

C2-11-02: source-пакет ручного запроса из6ресурсов,13новыхсценариев,648PASS.
Проверка source graph не означает native compile/runtime или право ручного ввода.

C2-11-01: общий owned port связывает existing selection flow с панелью ручного
запроса; 19 новых сценариев, общий итог667. Explicit refresh и atomic displayed-view
guard предотвращают dispatch к невидимому адресату. Общий экран/recipe/native/C1 открыты.

C2-11-01: source группа карточек/запроса с private flow, staging и общим lifecycle;
20 новых групповых и3 таймерных сценария, полный итог690. Layout/recipe группы
следующий шаг; native/C1 открыты.

C2-11-02: source-сцена карточек/запроса из 13 ресурсов, двух canonical XML inputs
и восьми JS definitions в одном контексте. 11 новых проверок, полный итог 701;
actual build/verify 13/12. Native/C1 и приёмка второго владельца открыты.

C2-06-02: ограниченный local text parser использует existing Roster, четыре
действия, точные имя/роль/группу и final-only bounded ID history. 23 RED→GREEN,
полный итог724. Proposal не server contract; ASR/микрофон/transport/C1 открыты.

C2-06-03: отдельная source text preview UI с input/кнопками, guarded private
parser и plain адресатом/действием/отказом. 21VM+3XML+1captured-names сценарий;
исполнение, микрофон/native/packaging/C1 и второй владелец остаются открытыми.

C2-11-02: отдельный source recipe text preview —6 canonical ресурсов/5ссылок,
три definitions, exact inert TextEntry policy и actual packaged VM click.11 новых
сценариев; full33suite760PASS. Native/ASR/общий runtime/C1/второй владелец открыты.

C2-10-01: source handoff helper делегирует existingbuild/verify и создаёт отдельный
immutable report для6fixedscreens; native поля явноnot_run/null/false.14RED→GREEN,
full34suite774PASS. Маршрут локальномуCodex создан; Windows installation открыта.

В [C2-11-03](11-integration/03-end-to-end/README.md) реализован единый каталог
и запуск source checks: полный прогон 35suites/790PASS, partial явно обозначается,
логи отдельно. Это вспомогательная source-проверка; клиентская сквозная цепочка,
сервер и нативная приёмка обоими владельцами остаются открытыми.

В [C2-07-03](07-match-screen/03-orders-timeline/README.md) подготовлена pure история
отображаемых приказов: захваченный адресат, отдельные стадии, explicit потеря
отслеживания, bounded64/drop counter. 20 новых сценариев; full36suites/810PASS.
Панель справа, общий HUD, согласованный источник/server и native приёмка открыты.

Для [C2-07-03](07-match-screen/03-orders-timeline/README.md) добавлена explicit source
панель последних6 записей с отдельными hiddenStored/droppedEvents и lifecycle guards.
14VM+2XML новых сценария; full38suites/826PASS. Watcher/transport нет; source package,
общий HUD, читаемость/scroll/hittest в движке и другой владелец остаются открытыми.

После финального review исправлена проверка дерева в isDisposed панели C2-07-03;
добавлен regression case. Итоговый full38suites/827PASS.

В [C2-11-02](11-integration/02-addon-packaging/README.md) подготовлен седьмой fixed
source-пакет истории приказов:5assets/4links, actual packaged VM и handoff экран
orders-timeline. Full38suites/835PASS. Независимый final review недоступен из-за
usage limit; выполнен самостоятельный просмотр изменений, review остаётся открытым.
Native/common HUD/server/другой владелец также открыты.

C2-07-02: минимальная публичная проекция и отдельная верхняя панель пяти соперников.
Unknown отличается от0, invalid/stale очищают источник до более новой revision.
Нет боевых полей/выбора/приказа; sourceAuthorizationConfirmed=false.
17model+13panel+2XML PASS; finalfull41suites/867PASS. Один финальный критик выявил
Proxy length coercion: воспроизведено regressiontest, исправлено без coercions.
[Отчёт](07-match-screen/02-opponent-cards/reports/cloud-public-roster.md).
Sourcepackage/commonHUD/C1/native/другой владелец открыты. График38/205(18.5%).

C2-11-02: восьмой фиксированный source-пакет публичных соперников, 5 ресурсов / 4
ссылки и handoff selector `opponent-roster`. Exact slot ownership и actual packaged
контекст проверены. 8 новых сценариев, полный итог 41 suites / 875 PASS; один
финальный критик без существенных замечаний. [Отчёт](11-integration/02-addon-packaging/reports/cloud-opponent-roster-package.md).
График 39/206 (18.9%). C1/common HUD/Windows/native/второй владелец открыты.

C2-11-01/02: общая read-only сцена соперников и истории; один parent и два
канонических private child bindings, отдельные источники/готовность, общий lifecycle.
Fixed пакет: 10 ресурсов / 2 canonical inputs / 9 links / 38 ID и fingerprints.
15 Node и 8 packaging сценариев; итог 42 suites / 898 PASS. Один финальный критик
выявил failed-acquisition visibility, воспроизведено и исправлено с сохранением
независимого child/status. [Отчёт](11-integration/01-ui-binding/reports/cloud-match-observation.md).
График 41/208 (19.7%). Full игровой HUD, C1/native/второй человек открыты.
