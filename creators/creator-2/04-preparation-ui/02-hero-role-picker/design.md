# C2-04-02: локальный черновик героев и позиций

## Замысел и первый независимый шаг

Пользователь выбирает перед матчем игроков, героев и роли. Уже подготовлен C2-04-01;
теперь первая часть C2-04-02 — pure ES5 draft назначений. Панель/сервер/native позже.
Применяются brainstorming/writing-plans, автономное продолжение и пять критиков.

Варианты: ждать полного C1-контракта блокирует независимый UI; встроить все данные
героев/моделей в frontend создаёт ложную поддержку. Выбрана явная частная проекция
предложений источника, без native discovery, импорта и подтверждения совместимости.

## Файл и API

`src/panorama/scripts/custom_game/hero_role_state.js` определяет
`DotaCoachHeroRoles.create()` → update, assign, remove, clear, view, draft,
dispose, isDisposed. Нет таймеров, native API, отправки, storage или bootstrap.
Ни модель, ни future screen пока не включаются в match HUD.

## Атомарная UI-проекция

`update({revision, team, proposals})`: exact три поля. Revision целое 0..9007199254740991.
Team — exact локальный draft C2-04-01: catalogRevision/draftRevision (целые),
complete:true, serverConfirmed:false, players ровно пять уникальных
{id,profileVersion}; строки 1..64 без крайних пробелов. UI не проверяет людей по id.
Подделать complete при неполном/повторном players нельзя, frame отклоняется.

Proposals — ровно пять профилей, по одному на каждый team id с той же profileVersion:
exact {id, profileVersion, playerName, kind, sourceLabel, choices}. Kind: synthetic/player_model, структурированная метка происхождения. PlayerName — непробельная
строка 1..64; sourceLabel — 1..160. Choices: до 32 уникальных сочетаний на игрока,
точная форма {heroId,heroName,role,coverage}. HeroId — строка 1..64 без крайних пробелов,
heroName — непробельная строка 1..64; role — целое 1..5; coverage — unknown/limited/reported.
Для одного heroId имя должно совпадать во всей проекции. Пустые choices допустимы:
выбор для этого игрока недоступен, поддержка не выдумывается.

Это предложенные назначения, не список серверно разрешённых сочетаний. reported
значит только сведения источника; герой/позиция/патч/качество ИИ не проверены.
Тестовые имена явно синтетические, реальные hero assets/data не загружаются.
Источник обязан сопоставить предложения с актуальным team draft; совпадение внутри
frame не доказывает свежесть источника/сервера. Такой контракт не объявляется общим.

Новый revision потребляется до body/keys. Во время decode view/draft/assign/remove/clear
не выдают старую проекцию под новой revision. Старые/duplicate frames не читают тело,
не меняют generation и не восстанавливают состояние после invalid. Newer reentry,
invalid reentry и dispose блокируют старый commit. Exact поля до/после copy,
array lengths captured/bounded и проверены после; никаких неоднозначных key joins.

## Правила локального черновика

assign(id,heroId,role) принимает только присутствующее предложение этого игрока.
В черновике один герой и одна позиция на игрока. Для этой ранней стандартной пятёрки
heroId и role также уникальны между игроками; конфликт отклоняется без изменения
assignmentRevision. Это локальная предварительная политика, не доказательство
полных правил кастомки; C1 позже сверит её с выбранным режимом.

Смена собственного назначения заменяет старое атомарно, без потери старого при
конфликте. Повтор того же назначения возвращает false без revision изменения.
remove(id)/clear снимают; clear пустого успешен без увеличения assignmentRevision.
Порядок draft совпадает с team.players. При update сохраняются назначения лишь для
того же id/profileVersion и всё ещё присутствующего heroId/role; удаление/смена
профиля/исчезновение предложения снимает выбор с объяснением, без auto reselect.
Пять назначений имеют complete:true только локально, serverConfirmed всегда false.

view(): независимые {status,message,players,assignments,complete,warnings}.
Players — полные profile proposals копии в порядке team; assignments — копии
{id,profileVersion,heroId,heroName,role}. Warnings — три {id,text} на назначение: вид профиля (synthetic/player_model с
оговорками C2-04-01), затем
«Сочетание предложено источником; совместимость модели сервером не подтверждена.»
и coverage-оговорка по модели C2-04-01. Никаких процентов или заявлений владения героем.
Status empty/ready/invalid/disposed; ready только валидный frame.

Draft при ready: {revision,assignmentRevision,team,assignments,complete,
serverConfirmed:false}, team — копия исходного локального draft, assignments только
{id,profileVersion,heroId,role}. Иначе null. AssignmentRevision монотонен при фактическом
изменении выбора (включая снятие новым frame), защищён от MAX_SAFE_INTEGER без wrap.

Отказы объясняются message: отсутствующий игрок/предложение, занятый герой/позиция,
повтор. Invalid сохраняет причину снятия после неудачной попытки. Update, снявший
назначение, сообщает об изменении профиля/предложений; обычный ready message —
«Предложения загружены; назначения не подтверждены сервером.»; complete —
«Пять локальных назначений; совместимость не подтверждена сервером.».

## Приёмка и открытое

RED→GREEN: five unique heroes/roles, atomic replacement/conflicts, source/schema/team
version, partial/invalid frames, high-water/reentry/copies/warnings/removal/dispose.
Пять критиков, полный прежний регресс, syntax/links/README/journal/config/Git.
C1-07-01, реальные profiles/heroes/patch/identity, панель/native и второй владелец открыты.

Уточнения критиков: invalid/dispose снятие учитывается assignmentRevision; counters
frame/team/assignment независимы. Ready при пустых choices сообщает
«Для N игроков нет предложенных сочетаний; назначения не подтверждены сервером.».
Kind не определяется по sourceLabel; synthetic/model origin видно до/после выбора.
