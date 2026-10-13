# Actual synthetic ошибки безопасно показаны existing source панелью

Продолжение C2 после публикации C1. [План](../synthetic-feedback-plan.md),
[TEST cases](../tests/synthetic-grammar-cases-2026-10-13.json),
[ASR происхождение](../../02-recognition-parser/reports/synthetic-grammar-2026-10-13.md).
Helper изменил только cases и три теста; production sources и прежние helpers/tests
сохранены. Это regression proof действующего поведения, а не новое поведение/RED bugfix.

Три raw hypotheses, включая исходные пробелы, сверены root с actual decoder JSON
SHA256 `5620cd78d3fb53de278e4c9c198eb2c5fbee4d88ba14399a52ecca4dd7968416`.
Context — пять TEST/synthetic own/alive профилей, revision1, не реальные игроки.

Existing Roster/VoiceText/VoicePanels исполнены вместе в NodeVM. Для каждой пары
reference сначала даёт local ready с правильным адресатом и действием, затем
actual decoded hypothesis даёт unknown_action/proposal=null и очищает **Address
и Action**. Статус явно «Действие не распознано», normalized text сохранён.
Предыдущее предложение не остаётся на экране как будто новое распознавание принято.

Captured revision1 после source2 остаётся stale_roster; событие не переписано.
Dispose/rebind закрывает old handle до чтения Proxy DTO (0 inspections), прежние
callbacks не читают input и не меняют fresh view. Новый owner снова принимает
reference и отвергает hypothesis; watcher cleanup завершает все local timers.
Attempts native API — 0. Панель только preview и не содержит транспорт/исполнение.

Targeted Node: **24 PASS**, включая ровно3 новых сценария; каждый проходит три
case pairs. Root проверил rawtext/context/hash, неизменность production и byte
prefix старых тестов после LF-нормализации. Full `source-checks-20261013T111628Z-231765`:
**85 наборов /1245 PASS /28 skips /6 incomplete /0 errors**, все85 процессов exit0,
строгий verified=false/CLI1. Logs ignored; ordinary tests не синтезируют аудио,
не открывают микрофон, не запускают ASR или Dota.

Одновременно C2 рассмотрел [границы подключённого C1](../../../01-foundation/03-interface-contract/notes/c1-gap-review-2026-10-13.md):
12 current source hashes совпали с published LF, поля/enum сверены с actual source.
Различия identity/epoch/revision/action/outcome/clock записаны; общая версия
contracts и runtime переходник не создавались. Это вход к согласованию, не wire schema.

VM labels/callbacks не реальные кадры, кнопки, клавиатура или voice bridge.
Real speech/command accuracy/native input/authority/C1 transport/lease/AI return/
human second owner остаются открытыми; C2 progress54/213 не повышен.

Один итоговый критик не нашёл существенных замечаний в feedback/gap review;
human/native и полное серверное рассмотрение остаются открытыми.
