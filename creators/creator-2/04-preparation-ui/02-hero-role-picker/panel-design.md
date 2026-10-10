# C2-04-02: отдельная панель предложений героя и позиции

[Модель](design.md) · [Подпункт](README.md).

## Цель и подход

Пользователь должен выбрать игрока и предложенное сочетание героя/позиции перед матчем.
Следующая независимая часть — source Panorama panel поверх проверенной pure модели.
Применены brainstorming/writing-plans, автономное поручение и пять read-only критиков.

Выбран фиксированный экран: пять игроков, пять сочетаний активного игрока на страницу,
пять назначений. Альтернативы dynamic CreatePanel и 160 строк сразу добавляют native
сложность/нечитаемость; fixed slots ограничивают tree/cleanup. До 7 страниц для32choices.
Source screen отдельно от team_picker.xml и match HUD; screen routing/сервер позже.

## Файлы и API

Добавить `src/panorama/scripts/custom_game/hero_role_panel.js`,
`src/panorama/layout/custom_game/hero_role_picker.xml`,
`src/panorama/styles/custom_game/hero_role_picker.css`. Реюз hero_role_state.js,
без его копирования/изменения и без новых зависимостей.

`DotaCoachHeroRolePanels.bind(root)` → update(frame), selectPlayer(id),
assign(id,heroId,role), remove(id), clear(), draft(), dispose(), isDisposed().
Caller явно bind/dispose; нет callbacks/submit/start/network/storage/native действий.
XML включает только two definitions и один CSS, без manifest/auto-bind/HUD подключения.

## Tree и поведение

Core IDs: HeroRoleStatus/Count/Recipient/Page, HeroRolePrevious/Next/Clear.
Пять HeroRolePlayerN buttons с HeroRolePlayer{Name,Version,Origin}N.
Пять HeroRoleOptionN buttons с HeroRoleOption{Hero,Position,Coverage,Action}N.
Пять HeroRoleAssignedN remove buttons с HeroRoleAssigned{Name,Choice,Warnings,Action}N.
Все Labels plain html=false; несуществующие slots hidden/disabled/text cleared.

Сначала активного игрока нет: «Выберите игрока для просмотра предложений»;
options пусты, без auto-assign/auto-select. Player button меняет только local focus;
player card явно «Показать предложения», отображает kind/source/version до выбора.
Recipient показывает имя/profileVersion и объясняет, если choices пусты.
Сочетание показывает heroName, «Позиция N», coverage оговорку и
«Назначить в черновике» либо «Уже назначено». Current exact choice disabled;
other-player conflicts не скрываются: click показывает причину модели и сохраняет
прежнее назначение. Роли/герои не утверждаются как поддержанные сервером.

Assigned slot показывает имя, hero/position и три model warnings, «Убрать назначение».
Clear снимает все назначения, не activeplayer. Count «Локальные назначения: N/5».
Complete message остаётся не подтверждённым сервером, Start/Submit отсутствуют.

Пагинация active choices только display, не assignmentRevision. При смене player
page=0; после update active сохраняется только same id/profileVersion. Иначе очищается,
без automatic selection. Page clamp; empty choices «Нет предложений для выбора»,
оба arrows disabled, индекс 0, никакого1/0. Update, новый focus и page делают все
старые handlers недействительными, включая removal предыдущей версии того же id.

## Lifecycle и отказ

Owner root до discovery/initial render; обязательны все nodes, включая скрытые slots.
Model одна на bind. Generation повышается перед model input getters и render, до
каждой/после каждой внешней записи проверяется. Old render/handlers/dispose/timer не
переписывают fresh bind. Из DTO сначала модель decode, только затем UI focus retention
по новой копии view; input getters не читаются повторно самим adapter.

При destroyed required node/render error/таймере dispose делает draft null, очищает
texts/buttons, скрывает owned root и отменяет watcher до release. Fresh bind может
показать его снова. Watcher 0.25s только lifecycle, без source/native polling.
Public draft проверяет root/allrequired nodes; dispose не является server cancellation.

## Проверки/открытое

VM real model+panels: focus not assignment, known/unavailable proposals, role/hero
conflict atomic, pages/32options/empty, names/plain warnings, revision/version/invalid,
oldhandlers/ABA, root owner/partial failures/allrequired checks/timercleanup/reentry.
Python graph tests exact ids/refs/order, disabled empty startup, nobootstrap/HUDinclude.
Native compilation/CSS/layout/scroll/resize/hittest и реальные profiles/data/identity/
C1-07-01/server/routing/второй владелец открыты. Node не запускает Dota.

## Уточнения до реализации

Player card имеет дополнительный managed HeroRolePlayerActionN: «Показать предложения».
Active focus — только {id,profileVersion} из model.view. После любого update, включая
false stale, выполняются focus retention и render/rebinding: stale update не оставляет
видимый screen без активных кнопок. Option callback снимает captured id/version/
heroId/role/generation и проверяет generation до обращения к модели.
