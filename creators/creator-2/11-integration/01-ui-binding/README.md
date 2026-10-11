# C2-11-01 — Связь UI с сервером

**Отдел:** создатель 2. **Проверяющий:** создатель 1.
**Статус:** частично: локальный координатор четырёх областей проверен; связь с реальным сервером открыта.
**Зависимости:** [C2-05-03](../../05-intervention-ui/03-return-feedback/README.md), [C1-04-03](../../../creator-1/04-intervention/03-lifecycle-guards/README.md).
**Рабочая папка:** `creators/creator-2/11-integration/01-ui-binding/`.

[Раздел](../README.md) · [План создателя](../../PLAN.md) · [Общие правила](../../../shared/WORKFLOW.md)

## Действия

- [x] Связать source-панель мыши с собственной проекцией Targets и снимать предложения для устаревшей цели.

- [x] Связать публичных соперников и историю приказов в одну read-only source-сцену с общим lifecycle.
- [x] Подключить панель запроса к единой локальной модели выбора через owned port и проверить source lifecycle.
- [x] Связать карточки и запрос в одну source группу с единым выбором, staging и lifecycle.

- [ ] Сверить каналы событий с общим контрактом.
- [ ] Проверить поздний снимок, смену героя и старое подключение.
- [ ] Передать результаты создателю 1 для общей интеграции.
- [ ] Сопоставить фактический результат с критерием ниже и записать непроведённые проверки.
- [ ] Передать изменение второму создателю для проверки, затем обновить этот статус.

## Результат и приёмка

Одна версия контракта работает с реальным сервером, без локального ложного подтверждения.

## Где размещать материалы

- `tests/` — проверки поведения и отказов.
- `reports/ui-binding.md` — фактические результаты и ограничения.

Это назначение будущих файлов, а не заявление, что все они уже созданы.
Новый вложенный каталог получает README с назначением и ссылкой из этого файла.
API, сигнатуры, конкретные файлы и команды проверки закрепляются в локальном
техническом плане после исследования входов; не подменяйте их выдуманными командами.

## Подготовленная локальная часть

[Дизайн](design.md) · [План](implementation-plan.md) · [Исходники](src/README.md) ·
[Тесты](tests/README.md) · [Заметки](notes/README.md) · [Отчёты](reports/README.md).

Явная привязка без bootstrap/data соединяет выбор игрока, адресата приказов,
камеру и наблюдение цели. Общий lifecycle guard блокирует transport и camera
при закрытии любой области; unknown mapping сохраняет имя и отключает камеру.
26 новых сценария проходят. Source HUD и облачные VM не доказывают native работу.

## Локальная цепь подготовки

[Дизайн цепи](preparation-flow-design.md) · [План цепи](preparation-flow-plan.md) ·
[Заметки](notes/preparation-flow.md) · [Отчёт](reports/cloud-preparation-flow.md).

19 сценариев координатора проходят; 4 новых reset сценария добавлены двум private
моделям, вместе481 source checks. Изменение предыдущего шага снимает зависимый выбор,
старые frames послеreset не оживают. Первый этап проверял pure модель процесса; текущая привязка описана ниже. Критерий реального сервера C2-11-01 остаётся открытым.

## Общая привязка трёх панелей

[Дизайн привязки](preparation-binding-design.md) · [План](preparation-binding-plan.md) ·
[Использование](notes/preparation-binding.md) · [Отчёт](reports/cloud-preparation-binding.md).

Одна частная цепь управляет тремя существующими адаптерами. Optional projection,
refresh/suspend, общий lifecycle и статус проверены реальными обработчиками в VM.
18 сквозных, 10 port, 12 injection и один context сценарий добавлены; общий итог522.
Общий XML/ресурсы, native, сервер/реальные данные и второй владелец открыты.

Shell/style/manifest общей подготовки теперь собираются через
[пакет C2-11-02](../02-addon-packaging/notes/preparation-package.md).
Generatedlayout содержит3canonicalroots/9definitions; native/автопривязка открыты.

## Локальная связь карточки и запроса

[Общий порт панели](intervention-port-design.md) · [План](intervention-port-plan.md) ·
[Подключение](notes/intervention-port.md) · [Проверка](reports/cloud-intervention-port.md).

[Экран из двух областей](intervention-screen-design.md) ·
[План](intervention-screen-plan.md) · [Подключение](notes/intervention-screen.md).
[Проверка](reports/cloud-intervention-screen.md):20 групповых и3 таймерных сценария,
полный итог690; native/C1 открыты.

[Дизайн](intervention-selection-design.md) · [План](intervention-selection-plan.md) ·
[Подключение](notes/intervention-selection.md) · [Проверка](reports/cloud-intervention-selection.md).

Один private Roster/Requests, общий gate и сохранение capturedactor: 27 сценариев,
полный облачный итог 635. Панели ещё не подключены; серверный критерий остаётся открытым.

## Общая сцена наблюдения матча

[Дизайн](match-observation-design.md) · [План](match-observation-plan.md) ·
[API](notes/match-observation.md) · [Отчёт](reports/cloud-match-observation.md).

Один родитель владеет двумя существующими панелями: соперники сверху и история
справа. Источники обновляются независимо, недоступность одного не приписывается
другому. Повреждение обязательного элемента закрывает группу; повторное открытие
создаёт новые private instances. Explicit bind/dispose, без handlers/timers/transport.
[Пакет](../02-addon-packaging/notes/match-observation-package.md) собирается из
единственных канонических XML/JS/CSS. Это ещё не полный игровой HUD или приёмка Dota.

## Локальная свежесть цели мыши

[Дизайн](mouse-targeting-design.md) · [План](mouse-targeting-plan.md) ·
[API](notes/mouse-targeting.md) · [Отчёт](reports/cloud-mouse-targeting.md).

Один private Targets и existing MouseProposalPanel. Explicit update/select до DTO
снимают старый target draft; expiry/dead/hidden при refresh/view снимают его,
сохраняя actor. Move независим. Нет native hook, clock scheduling, authority/send
или серверного эффекта; общий C1/native критерий и второй владелец открыты.
