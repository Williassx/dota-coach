# Связанная локальная цепь подготовки

[Подпункт](../README.md) · [Дизайн](../preparation-flow-design.md).

DotaCoachPreparationFlow.create() владеет тремя private моделями и не копирует их
правила. UpdateTeam/choosePlayer/removePlayer/clearTeam ведут состав; updateHeroes/
assignHero/removeHero/clearHeroes — назначения; updatePreparation/choosePlan/chooseTalk/
removePlan/removeTalk/clearPreparation — намерения. view/draft/dispose/isDisposed завершают API.

Сравниваются копии полного canonical draft. Смена teamcontext снимает героев/подготовку,
смена herocontext снимает подготовку. Героев нельзя загрузить без пяти игроков, а
подготовку — без пяти назначений: gate не читает DTO. Input старого контекста после
parse снимается reset, не становится новым составом. Root message показывает сброс
и следующий шаг; failedaction detail может измениться, resetnotice сохраняется.

reset моделей hero/preparation снимает источник и выбор, сохраняя highwater и
увеличивая localcounter только на actualremoval. Caller должен монотонно повышать
frame revisions весь срок flow. Busy скрывает views/draft, nestedupdates/mutations
отклоняются до DTO чтения без потребления ревизии; повтор возможен позже. Dispose
закрывает всю цепь и побеждает inputgetter. Это deliberate facade policy, direct
модели сохраняют свой прежний newer-getter-win порядок.

Final draft выдаётся только при полной цепи, copied/serverConfirmed=false. No native,
server/start/catalog invention/storage. Existingpanels пока владеют отдельными
моделями: coordinator ещё не подключён к их кнопкам и навигации. C1/sharedcontract,
реальные данные/эффект и второй владелец остаются открытыми.

contexts() выдаёт copied {team,heroes} draft для построения следующего frame,
без реконструкции counters; во время busy/dispose результат null. Модели не открываются.
