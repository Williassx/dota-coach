# Автономная работа двух создателей: границы и результат

Пользователь 13 октября поручил обследовать весь репозиторий, составить план обоих
создателей, сразу выполнять его и закрыть **+30 процентных пунктов у каждого**.
Он отдельно разрешил независимую проверку технических подпунктов C1↔C2 агентами.
Проектные/юридические основания и реальные игровые результаты это не заменяет.

## Зафиксированное основание

[Baseline](autonomous-30pp-baseline-2026-10-13.json): HEAD b267b5f,
1180 tracked files, 72 подпункта, 36 у каждого; каждый tracked файл хеширован.
Исходный C1 112/181 содержит склеенный уже выполненный пункт C1-01-02: после
исправления baseline **113/182**, без нового результата. Нужно **55 новых пунктов**,
цель **168/182**. C2 baseline **56/213**, нужно **64 новых**, цель **120/213**.
План и новые отчёты не увеличивают знаменатель; архивы и .freebuff не меняются.
Процент означает выполнение существующих действий, не готовность игры.

У C1 33 функциональных и 36 review пунктов открыты. У C2 90 функциональных,
31 сопоставление/отчёт и 36 review пунктов. Review теперь допустим отдельным
исполнителем другого создателя для технической части; он не превращает TEST
профиль в реальный, smoke в матч или unknown license в разрешение.

## Выбранное направление

Развивать существующую нативную сцену одного TEST героя, связывая настоящие C1
observation/synthetic policy/arbiter/journal и server-confirmed TEST roster с C2.
Это сохраняет первый путь Dota Workshop, позволяет проверять engine effects,
паузу, смерть, generation/rebind и поздние ответы без реальных персональных данных.
Полный 5×5 и обучение на отложенных реальных матчах остаются следующей зависимой
веткой. Расширять их только отдельной спецификацией, не ради числа чекбоксов.

Альтернативы: преимущественно source-аудит даст много формальных пунктов, но не
улучшит нативную сцепку; сразу полный 5×5 добавит неподтверждённые карту/патч/ИИ.
Выбран интеграционный сценарий плюс независимая техническая приёмка всех библиотек.

## Изменения поведения

1. Existing manual v1 сохраняет events, strict 17-field wire, sender/owner/life,
lease5 game seconds и admission≠arrival. Нормальный fixed7 и TEST9 kind сохраняют
состав. Native adapter получает однократно устанавливаемые server-only hooks до
Activate; default mechanical patrol остаётся для старого kind.
2. Новый coach scene wrapper использует actual C1 projection→policy→arbiter и
fresh engine order, а journal получает действительный server game time/transitions.
Никаких hidden/future channels; input из клиента не выбирает owner/engine entity.
3. C1 production roster validator подтверждает фиксированные пять TEST профилей
с hero/role compatibility и weak coverage warnings. Read-only native roster sync
передаёт server-confirmed assignments в новую C2 панель. Это не старт 5×5 или
подтверждение сходства людей; существующий private preparation draft не переписывается.
4. Новый versioned roster wire отдельный от manual v1: request exact
{protocol_version:1,request_id}; response exact protocol_version/request_id/session_id/
revision/status/reason/synthetic/assignments. assignments — object string slots1..5;
entry exact id/hero/role/coverage/warning. synthetic=1; status confirmed либо rejected,
при rejected assignments пуст. Session/read-only revision выдаёт сервер; consumer
strict/highwater/timeout/dispose; server confirmation не означает старт матча.
5. Новый normal kind **15 outputs**, native TEST kind **18 outputs**: source map
до реализации фиксируется в плане. Существующие fixed recipes/policy не расширяются.
6. Нативный TEST driver отдельно проверяет pause freeze/no effects, expiry after
unpause, death/rebind/old lease и roster receipt. Engine capability сначала измеряется;
если pause/death API отсутствует, сценарий остаётся непроведённым. Physical input
требует рабочего supported capture/input канала, координаты не подставляются.

## Что можно отмечать выполненным

Функциональный пункт закрывается собственным result/command receipt в его подпункте.
Сопоставление критерия можно выполнить честным report с частично удовлетворённым
критерием и точным перечнем непроведённого; оно не закрывает соседний functional.
Technical review имеет отдельного автора/reviewer другого создателя, findings и
regrade. Отчёт/передача не означают завершённость всего подпроекта.

C1 кандидат19: 01-02(1),01-03(3),02-03(2),03-01/02/03(3),04-01 grant(1),04-02 cycles(1),
07-01 roster(1),11-01(2),12-01 registry(1),12-02 early bounded unsent demo(3),
12-03 technical package/install/version(1). Вместе с36technical review это55.
Early demo/package — только проверенная сцена прототипа по отдельному текущему плану,
не полная демонстрация продукта/общая приёмка/публичный выпуск; права не утверждаются.
Если буквальный критерий какого-либо кандидата не выполнен, он не отмечается ради55.

C2 выполняет минимум64 действительных actions: contract/ownership, server grant/input
admission/reject, feedback/lifecycle, producer-consumer integration, exact packaging,
prototype presentation/transfer плюс сопоставление31критерия и independent technical
reviews. Подробный action delta остаётся в evidence ledger; нельзя зачесть старое [x].

## Автономность и ограничения

Диспетчер173 выбирает готовые задачи по зависимости и выдаёт scoped ownership.
Root — единственный автор общих документов/контрактов/каталога/сводки. C1 исполнитель
владеет новыми серверными файлами, C2 — панелью/упаковкой и отчётами. До native
операций один исполнитель owns process; установка только fresh addon/receipt,
PID+startUTC, quit только собственный. Build output не место разработки.

Не меняются Windows privacy/security, Steam login, credentials, user addons,
.freebuff; нет писем, workshop upload или внешнего выпуска. Источники/лицензии
реестром отмечаются assessed/unavailable/unknown, не становятся разрешёнными.
Нет обещания real player fidelity/real voice/fullmap/fullmatch.
Token usage/cost при отсутствии данных null. Глобальная память не редактируется.
