# C2-04-03 — локальный черновик тактики и разговора

**Дата UTC:** 2026-10-10. **Основа:** 045fb99.
Пользователь хочет подготовку команды перед матчем и поручил работать автономно
с пятью критиками. Новый компонент проектируется в библиотеке создателя 2.

## Выбранный подход и граница

Pure ES5 модель поверх полного local hero-role draft C2-04-02, затем отдельная панель.
Это позволяет проверить сохранение намерений тренера до native/server интеграции.
Альтернативы: заранее прошитые бонусы морали требуют несуществующих C1 правил;
прямой server submit требует общего контракта. В этой части реализуется только модель.
Не вычислять мораль, личность, качество ИИ, победу или исполнение тактики.

## Private frame

`update({revision,lineup,plans,talks})`: exact object, revision safe nonnegative integer.
Lineup exact предыдущий draft: revision, assignmentRevision, team, assignments,
complete=true, serverConfirmed=false. Team exact catalogRevision/draftRevision,
complete=true/serverConfirmed=false/players; пять unique virtual id/profileVersion.
Assignments пять exact id/profileVersion/heroId/role; совпадение team pair, unique
hero и позиции 1..5; assignment id уникальны и покрывают каждый team id ровно один раз.
Lineup revision/assignmentRevision и team counters safe nonnegative integers; heroId
1..64 без краевого пробела. Сортировать assignments в team order, без угадывания real identity.
Это структурный вход локального UI, а не аутентификация источника или поддержка сервера.

Plans и talks массивы 0..8; каждый элемент exact {id,optionVersion,label,intent}.
Unique id внутри своей группы, совпадение ids разных групп допустимо. Identifier/version
1..64 без краевого пробела, label1..80, intent1..240, все непустые plain strings.
Intent — намерение/описание предложенного игрового правила, не наблюдаемый результат.
Реального каталога пока нет: fixtures обозначаются тестовыми; модель не задаёт механику.

## API и выбор

`DotaCoachPreparation.create()` → update, choosePlan(id), chooseTalk(id), removePlan(),
removeTalk(), clear(), view(), draft(), dispose(), isDisposed(). Вначале нет выбора.
Выбирать можно только полученный option id в ready состоянии; повтор false без bump.
Пустой каталог допустим и объясняется, complete только plan+talk. В будущем каталог
может дать явный вариант «без разговора», он выбирается как обычный option; сейчас
ничего не подставлять автоматически. Отдельные remove и clear не создают новых выборов.

view {status,message,lineup,plans,talks,plan,talk,complete,warnings}; полные независимые
копии, выбранные plan/talk содержат id/optionVersion/label/intent. Lineup null до ready.
Draft {revision,preparationRevision,lineup,plan,talk,complete,serverConfirmed:false};
выборы сокращены до id/optionVersion или null. Inactive draft=null/скрытые view данные.
Complete — локальная полнота, не готовность настоящего матча. Поддержка и отказ от
разговора не оказывают побочных эффектов; это сохранение намерения.

## Обновления и отказы

Frame highwater независим от counters lineup; old revision отклоняется до body/ownKeys.
Новый frame staging скрывает view/draft и запрещает выбор до полной атомарной проверки.
При invalid все private данные/выборы снимаются, highwater не откатывается.
Полный canonical lineup (с counters и assignments) изменился — снимаются оба выбора;
даже изменение одного героя требует пересмотра всей подготовки, без auto restore.
При том же lineup сохраняются только options с совпадающими всеми четырьмя полями.
Изменение label/intent при той же version тоже снимает соответствующий выбор.
Каждый реальный change выбора/reset bump preparationRevision один раз, no-op не bump.
Подтверждённая причина снятия выбора должна оставаться в message после отказа/no-op.

Exact schema checks before/after reads; after EACH external read/ownKeys/array length
проверять generation. Newer update/invalid/dispose из getter побеждает старую операцию;
view/draft во время staging скрыты, mutations rejected. Arrays captured bounded length
и неизменная финальная length. Safe integer overflow закрывает модель без wrap.
Copies без исходных ссылок, никаких native/network/storage/bootstrap/clock/observers.

## Маркировка и приёмка

Два fixed warnings при ready: «Подготовка локальная; исполнение и эффект сервером
не подтверждены.» и «Мораль и доверие — игровые допущения; это не сведения о характере
реального человека.» Источник не выдаётся за real player proof. Emptyplans/talks
показываются в message, сохранённый выбор доступен отдельно и может быть удалён.

Node VM использует реальный draft team/hero models с тестовыми profiles/героями.
Проверить explicit/no-autopick, copies, conflicts in lineup, версия/контекст/изменение
intent, invalid/highwater, getter newer/invalid/dispose/ownKeys/length и pending locks.
C1-07-02/03 правила, персональная совместимость, effect/наблюдение, panel/native/server,
постоянное сохранение, запуск и равноправный второй владелец остаются открытыми.
