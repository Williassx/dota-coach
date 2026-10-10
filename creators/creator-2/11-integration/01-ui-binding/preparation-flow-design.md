# Последовательный локальный процесс подготовки

**Дата UTC:** 2026-10-10. **Основа:** 1f1b5c8.
Пользователь поручил продолжать автономно; ведущий создатель2, пять read-only критиков.

## Цель и выбранный подход

Связать private выбор5игроков → героев/позиций → плана/разговора. В этой части pure
координатор переиспользует три существующие модели без копирования их правил.
Панели пока имеют собственные модели; native navigation/shared panel binding — следующий
шаг. Не объявлять этот coordinator подключением кликов или готовым игровым сценарием.
Альтернатива прямого объединения панелей требует lifecycle/change notifications;
сначала проверить цепь контекстов отдельно. Server/start/storage здесь отсутствуют.

## Модели и reset

В hero_role_state.js и preparation_state.js добавить reset(): bool. На живой модели
снять все source data/выборы, committed revision=null, status=empty, generation++;
highwater сохранён, counter увеличивается один раз только если снят выбор.
Hero message «Состав изменён; получите новые предложения героев и позиций.»;
Preparation message «Назначения изменены; получите новые варианты подготовки.».
Closed reset=false, repeat reset=true/no bump. Нет автоматического восстановления.
Сохранённый highwater не позволяет позднему frame оживить выбор после upstream change.

## API coordinator

Новый source src/panorama/scripts/custom_game/preparation_flow_state.js в C2-11-01.
DotaCoachPreparationFlow.create() → updateTeam(frame), choosePlayer(id), removePlayer(id),
clearTeam(), updateHeroes(frame), assignHero(id,heroId,role), removeHero(id), clearHeroes(),
updatePreparation(frame), choosePlan(id), chooseTalk(id), removePlan(), removeTalk(),
clearPreparation(), view(), draft(), dispose(), isDisposed(). Модели остаются private.

Update methods принимают exact private DTO уже заданных моделей. Caller поставляет
новые предложения; coordinator не сочиняет героев/каталоги и не сохраняет raw DTO.
Сравнивать контекст по canonical copied draft из реальных моделей, не reread frame.
UpdateHeroes разрешён только при полном current team; после model parse его copied
team должен полностью совпасть с actual team draft (counters/id/version/order).
UpdatePreparation разрешён только при полном hero draft; его copied lineup должен
полностью совпасть с actual hero draft. Mismatch → corresponding reset, false.
Изменение team draft, включая counters, снимает heroes и preparation. Изменение hero
 draft, включая counters/assignments, снимает preparation. Ошибка/invalid upstream
тоже синхронизирует сброс; rejectedold/no-op при прежнем draft ничего не сбрасывает.

## Staging/reentry

Перед каждой permitted operation busy=true: view не показывает private данные,
draft=null. Все вложенные вызовы mutating API во время busy отклоняются false без
чтения нового DTO и без consumption highwater; caller может повторить после выхода.
Это deliberate coordinator policy, отличная от direct models newer-getter-win;
no public access к models. Dispose из getter закрывает все модели и побеждает operation.
Проверять closed/generation после model call и перед sync/read/commit; catch закрывает
координатор при неожиданной exception, не выдаёт partly synchronized draft.

view {status,message,team,heroes,preparation,complete}: обычные copied model views;
staging/closed private three fields null. status team/heroes/preparation/complete
указывает требуемый следующий шаг, complete только три local levels. Сообщения
не подтверждают поддержку сервером. draft=null до полной цепи; затем copied final
preparation draft со всеми nestedcontexts и serverConfirmed=false. Dispose идемпотентный.

## Проверки и границы

VM load только четыре definitions без native. Happy path real team→hero→preparation
models с тестовыми profiles/choices; readonly viewcopies/complete не означает реальных ИИ.
Проверить incomplete gates before DTO getters, exact context mismatch, samecatalog/old
noops, counters/version/herochange resets, late frames afterreset, invalid/recovery,
choose/clear/remove chain, staged views/nestedupdates rejection/dispose, independentcopies.
Панели/общийHUD/bundle/server/общийконтракт не менять в этой части. Реальные каталоги,
персональныеmodels, native screen navigation и второй владелец остаются открытыми.

## Уточнения review

Источник поддерживает строго растущие hero/preparation frame revisions на весь срок
экземпляра flow, даже после upstream reset; сброс source counters к0 не поддерживается.
В view.message показывать nextstep и заметку о сбросе: «Состав изменился; предложения
героев и подготовка сняты.» если прежние downstreamsources существовали;
«Назначения изменились; варианты подготовки сняты.» при прежней preparation source.
Failed/old/noop не стирает заметку; успешное новое действие/update без нового reset
может её убрать. Статус дополняется текущим message соответствующей модели.

contexts() выдаёт copied {team,heroes} draft для построения следующего frame,
без реконструкции counters; во время busy/dispose результат null. Модели не открываются.
