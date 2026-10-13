# Native diagnostic ping между библиотеками

Продолжение автономной C2 работы; C1 исходники подключены и рассмотрены. Цель —
проверить настоящий client event и адресный diagnostic reply существующей модели
Probe. Это не игровые команды, MANUAL, identity реального игрока или lease.

## Выбранный ограниченный путь

Отдельный TEST addon вместо изменения production bundles или C1 movement сцены.
Fixed probe5 остаётся прежним. Fixture содержит9 outputs: five canonical resources
(manifest substituted by TEST manifest), derived layout, TEST driver и два C1 Lua.
Derived layout использует existing state/markup/CSS, исключает auto adapter из
active scripts; native glue TEST driver вызывает existing DotaCoachProbe.create.
Canonical auto adapter retained unchanged; programmatic request не physical click.

Клиентский envelope: exact protocol_version=1 и request_id1..64, response version1,
тот же id/status ok|rejected/reason none|unsupported_version|invalid_request.
Сервер сначала проверяет callback sender: source entity разрешается через native
EntIndexToHScript, GetPlayerID и равенство PlayerResource:GetPlayer(id). Payload
PlayerID никогда не выбирает получателя; engine metadata strip/mismatch проверяется.
Unknown sender — no reply. Не вводить fallback по присланному PlayerID ради успеха.
Native source semantics измеряется; отсутствие подтверждения не становится authority.

C1 helper — единственный автор pure diagnostic validator, TEST native entrypoint
и candidate diagnostic contract document. Root/C2 — author fixture builder/driver,
native command и документации. Другой helper — только builder tests после interfaces.
Один итоговый технический критик; human second owner и общая игровая версия открыты.

## Приёмка

Pure RED→GREEN: exact shape/types/id/version/extra fields; malformed-with-valid-id
rejection; no usable id→nil response; no engine calls in pure validator. Entry point
никогда не создаёт unit/order, не меняет OS/game settings и не шлёт broadcast.
Builder preflight/escaping/tamper/fresh outputs и fixed policy проверяются.

Native compile+fresh launch на текущем installed build; real valid request→server
trace→client response/visible status. Direct unsupported/extra/spoofed PlayerID,
repeated valid request и client dispose проверяются отдельными TEST фазами.
Не менять root UI самостоятельно в ответ на придуманный server result. Logs/screens/
PID+exactticks/receipt сохраняются, quit через VCon только своего процесса.
При source-resolution отказе сохранить evidence и продолжить независимые проверки.

## План реализации

1. Согласованный интерфейс: C1 diagnostic_ping.evaluate(payload)→response|nil;
   C1 ping_game_mode.lua→game/scripts/vscripts/addon_game_mode.lua.
2. C1 pure tests RED→GREEN; C2 build_fixture(repository,output) exact9 outputs,
   TEST driver и XML, separate builder tests.
3. Targeted/VM/source проверка, fresh install/compile/owned launch, bounded capture.
4. Root evidence/one review/full regression/lesson/usage/progress scope/publication.
5. Довести active work accounting до7200s; interrupted wall time не считать работой.

## Уточнение после первых наблюдений

r1неопределялметаданные, r2добавилmetadataenum/presendcopy; r3variantadapter
сохраняет activecoach_probe.js и использует TESTobserver. NativeActivateddispatch
вызывает originalonactivate без physicalmouse/hittest. All3freshbuilds completed,
18phases/18frames, Lua14/VM19/builder9/full85/1271/28skip/0errors/false.
