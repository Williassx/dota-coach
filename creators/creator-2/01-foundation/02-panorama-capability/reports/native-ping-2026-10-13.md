# Native diagnostic ping: C1 sender guard и C2 Probe

13 октября2026, installed build25894101. [Дизайн](../native-ping-design-2026-10-13.md),
[Fixture](../tests/native-ping/README.md),
[Candidate diagnostic envelope](../../../../shared/contracts/diagnostic-probe-v1.md).
Ведущий146, C1 helper author validator/TEST entrypoint/candidate/tests, root C2
author builder/driver/native commands/evidence. Builder test helper завершил RED,
затем остановился из-за model capacity; root довёл GREEN. Один final review отдельно.

## Реально проверенный обмен

В двух отдельных TEST launches existing Probe state, markup/CSS и native GameEvents
прошли bound/valid/unsupported/extra/spoofed-player-id/valid-again/disposed —
по7фаз/7actual1280×720кадров. Valid получил correlated ok/none от настоящего Lua
listener. Unsupported version и extra field получили разные server rejection reasons.
Каждый callback разрешил sourceindex1→native player entity(table)/player0 и
проверил равенство PlayerResource:GetPlayer(0). Payload PlayerID не выбирал адресата.
Это фактический local diagnostic sender path на этом build; multi-client/game
authorization/identity реальных игроков этим не установлены.

Первый run не логировал engine metadata категорию; его успех не объяснял spoof case.
Второй fresh addon добавил trace-only metadata enum и pre-send snapshot. Actual
wire snapshot содержит PlayerID99999, но callback сообщил matching_native (player0),
reply пришёл ok/none. Путь native transport изменил это значение до callback; точный
внутренний механизм engine override/removal и другие версии/клиенты не измерены.
В source stub test сохранённый mismatch всё равно rejected/invalid_request только
native verified sender. Неизвестный source отклоняется до чтения payload.

Disposed callback не инспектировал stale getter (0reads). Wire IDs разные,
response IDs совпадают с captured requests. Нет game orders, MANUAL или lease.
Client timeout2s остаётся diagnostic timer, не длительностью вмешательства.

## Исходный auto-adapter

Первые две fixtures использовали TEST transport glue и исключали coach_probe.js
из active layout; оригинальный файл/canonical XML retained unchanged.
Третий fresh variant включает unchanged original auto-adapter и TEST observer:
native Activated dispatch вызывает существующий onactivate, повтор и dispose
наблюдаются отдельно. Это programmatic UI event, не физический мышиный ввод/hittest;
строка mouse в event arguments не подтверждает реальную мышь.
Третий run дал4/4PASS и4actualframes: original adapter panel_ready, два request_sent
с разными IDs, два matching ok, visible status и dispose. Всего18фаз/18кадров/
12verified callbacks; ownPID21488/4452/22204quit→gone, Steam12964 сохранён.

## Проверки и сборка

Fixed probe5/policy и canonical production XML/JS/CSS не расширены. Каждый fixture
имеет9source outputs (7Panorama+2C1Lua),7compiled UI outputs; map13compile steps,
0failed/0skipped, compile exit0. Игровой source addon не подменяется TEST entrypoint.
Все3addons fresh; build directories не редактировались после генерации.

Pure C1 TDD→14PASS (without optionalLua51: explicit skips), builder RED→9PASS,
existing Node probe+fixture VM19PASS, snapshot mutation RED→GREEN. Ordinary tests
не устанавливают пакеты и не запускают Dota. Source full125920Z-7764f3:
85suites/1271PASS/28skip/6incomplete/0errors/all85exit0/strictfalse/CLI1.
Кадры получены engine screenshot и просмотрены отдельно; template ground и белая
область minimap не являются принятием настоящей карты или объяснением её геометрии.

Native bootstrap/game HUD/real identity/actor permission/lease/ИИ return/microphone/
ASR bridge/physical input/другой размер/human second owner остаются открытыми.
Candidate diagnostic version не является утверждённой игровой wire schema.
[Metadata](native-ping-2026-10-13.json) содержит фактические run/records/hashes/frames.

Один итоговый критик не нашёл существенных замечаний; human review остаётся открытым.
Отмечен только diagnostic event/reply пункт C2-01-02: progress55/213(25.8%).
Полная foundation/game/native-input приёмка не закрыта.
