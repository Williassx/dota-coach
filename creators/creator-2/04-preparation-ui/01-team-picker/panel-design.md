# C2-04-01: панель локального выбора состава

[Модель](design.md) · [Подпункт](README.md).

## Замысел и выбранная часть

Пользователь хочет выбирать состав перед матчем. Проверенная модель уже поддерживает
пять виртуальных id с версиями; следующий шаг делает этот выбор доступным через UI.
Используются brainstorming/writing-plans и пять read-only критиков, автономное
продолжение поручено пользователем. C1-07-01 и native Windows недоступны для приёмки.

Варианты: один список из 64 строк слишком велик; динамическое создание panel вносит
лишний native API и cleanup; выбран фиксированный экран с пятью кандидатами на страницу
и пятью местами локального выбора. Максимум 13 страниц, без dynamic CreatePanel.

## Исходники и включение

Добавить `src/panorama/scripts/custom_game/team_picker_panel.js`, отдельные
`src/panorama/layout/custom_game/team_picker.xml` и
`src/panorama/styles/custom_game/team_picker.css` в эту же библиотеку.
Модель не копировать. XML включает две definitions и один стиль, без auto-bind/данных.
Не включать предматчевый экран в текущий match HUD/manifest: совместная маршрутизация
экранов будущая задача, native вывод не подтверждён.

`DotaCoachTeamPickerPanels.bind(root)` → update(snapshot), choose(id), remove(id),
clear(), draft(), dispose(), isDisposed(). caller явно вызывает bind и dispose.
Без callback/export/send/storage/ready/server/native действий.

## Пять кандидатов и пять выборов

IDs: TeamPickerStatus/TeamPickerCount/TeamPickerPage, TeamPagePrevious/TeamPageNext/
TeamClear; по пять TeamCandidateN кнопок с TeamCandidate{Name,Version,Source,Coverage,Hint}N;
по пять TeamSelectedN кнопок удаления с TeamSelected{Name,Version,Warnings}N.
Все Labels html=false; поля недоступных slots стираются и кнопки hidden/disabled.
Список кандидатов по каталогу, selected в порядке выбора. Кандидат уже выбран —
disabled с пометкой; при пяти выбранных остальные disabled с объяснением лимита.
Выбранная запись удаляется собственной кнопкой; clear снимает весь черновик.

Пагинация только отображение, не меняет draftRevision. Страница ограничена валидным
каталогом; update сохраняет страницу если существует, иначе clamp. Invalid/empty
сбрасывает страницу и отключает выбор/clear/пагинацию. Старые кнопки не должны
выбрать ранее показанный id после перехода или нового snapshot.

PlayerName/sourceLabel/version — plain text. Synthetic/player_model и coverage
отображаются как предоставленные свойства с оговорками, не точность моделей.
SelectedWarnings объединяет два уже сформированных моделью предупреждения в plain text.
Счётчик «Локальный выбор: N/5», title «Черновик состава». У complete текст модели
указывает не подтверждённый сервером draft; кнопки запуска/подтверждения отсутствуют.

## Lifecycle и отказ

Один владелец root, резерв до initial render. Модель единственная для bind.
Каждый render получает generation, перед/после внешней записи проверяет её; старый
render или handler после reentry/dispose/rebind ничего не меняет. Dispose скрывает
свою область/кнопки и очищает таймер ДО release root. Сохраняется другая живая привязка.
Watcher 0.25s проверяет lifecycle, не обновляет каталог и не собирает native данные.
Перед update/handlers/draft проверяется root и все обязательные panels; failed renderer
закрывает привязку, draft null, очищает слоты, отменяет watcher. Свежий bind после
ошибки/закрытия может использовать тот же root и повторно показывает свои controls.
После dispose старый callback никогда не скрывает/не пишет новую привязку.

## Проверки и открытое

Тесты Node VM используют реальную модель и mocked panels: pagination/slot clearing/
max five/duplicate/source warnings/version removal/stale handlers/plain text/ownership/
partial render+schedule errors/teardown/reentrant fresh bind. XML/CSS resource references
и ids проверяются отдельно без native compilation.

Нативный внешний вид, resolution/hittest, реальные профили/identity/контракт/сервер,
постоянное сохранение, герои/роли/тактика и второй владелец открыты. Эта панель ещё
не подтверждённый рабочий предматчевый экран Dota.

## Уточнения критиков

Выбранный slot дополнительно имеет TeamSelectedActionN с «Убрать из черновика».
CandidateHint: «Добавить в черновик», «Уже в черновике» либо объяснение лимита.
CandidateSource показывает kind-оговорку вместе с sourceLabel, до выбора;
CandidateCoverage показывает unknown/limited/reported оговорку, не bare code.
Страницы: «Страница X из Y»; при нуле записей «Нет записей для выбора», arrows
отключены и индекс остаётся 0 (никогда -1 или 1/0). Clear доступен лишь при count>0.
