# Синтетический ASR и действующая грамматика: 0/3 предложений

13 октября 2026. [Дизайн](../synthetic-grammar-design.md),
[план](../synthetic-grammar-plan.md), [метаданные](synthetic-grammar-2026-10-13.json).
Ведущая роль 76; один helper автор двух диагностических команд, отдельный helper
автор трёх новых pure tests. Root независимо проверил WAV/model/метрики и повторно
исполнил actual Roster/VoiceText исходники в NodeVM. Общие документы пишет root.

Для первой проверки выбраны тексты, которые оказались вне точной грамматики.
Теперь **до синтеза** зафиксированы три существующих parser-compatible эталона.
Словарь, production parser, decoder/model параметры и нормализация не менялись.
Диагностические команды C2-06-01 получили exact `sample_set=parser_grammar`;
default baseline и старые receipts без этого поля сохраняют прежние три эталона.
Unknown/type/corpus mismatch отклоняются до inference.

Microsoft Irina Desktop ru-RU создала три новых synthetic WAV: 16000 Hz,
PCM16/mono, 2.04 /2.46 /2.405 s. Микрофон и динамики не использовались;
raw audio остаётся в ignored build, записи людей/игроков не создавались.
Faster-whisper 1.2.1/PyAV18, tiny revision
`d90ca5fe260221311c53c58e660288d3deb8d356`, CPU int8/2 threads/ru/beam1/VADtrue.
Четыре model hashes и семь параметров равны baseline; три generators consumed.

| Эталон | Actual ASR hypothesis | Правки/слова | Local parser |
|---|---|---:|---|
| керри отступай | Кириат Ступай. | 2/2 | rejected: unknown_action |
| мидер держи позицию | Мидердерже позиции. | 3/3 | rejected: unknown_action |
| команда соберитесь | Команда Сабиритесь. | 1/2 | rejected: unknown_action |

Root заново рассчитал word Levenshtein: **6 правок /7 reference words,
WER 85.7% только этих трёх synthetic samples**. Нормализация lowercase/ё→е/
пунктуация; fuzzy matching, исправление decoded текста и подмена эталонов отсутствуют.
Ни одна гипотеза не дала local proposal. Это отрицательный результат данного
tiny/system-TTS опыта, не оценка всей русской речи или пригодности других моделей.

Actual C2 parser на том же TEST snapshot (revision1, пять own/alive synthetic
профилей) принял **3/3 эталона**: retreat→TEST-p1, hold→TEST-p2, regroup→пятёрка.
Все шесть событий имеют разные utteranceId и captured revision. Duplicate/stale/
ambiguous guards отдельно отвергают входы. Root после dispose передал stale Proxy:
0 inspections, disposed; попытки native API и отправленные команды — 0.
Ready означает локальное предложение, не authority и не начало действия.

## Проверки и исходные записи

12 pure tests PASS (старые9+новые3), grammar RED сохранён до реализации.
PS parse/AST проверены. Unknown `SampleSet` и неверный регистр отказали до создания
output. Четыре baseline входа (receipt+3WAV) сохранили прежние SHA256.
Root acceptance: `build/dota_coach/asr-grammar-root-20261013T110447Z-919c6e51`;
там сохранён повторный parser script, outcomes и independently recomputed metrics.

Свежий полный source прогон уже включает эти стабильные изменения и подключённый
C1: `source-checks-20261013T105504Z-498303`, 85 наборов /1242 PASS /28 skips /
6 incomplete /0 errors, все процессы exit0, строгий verified=false/CLI1.
Ordinary tests не открывают микрофон, не синтезируют аудио и не запускают модель/Dota.
Decoder elapsed2.045625 s /process CPU3.53125 s — конкретный процесс, не latency SLA
и не сравнительный benchmark. Python sockets[], native network trace отсутствует.

Synthetic decoder positive=true; real speech/accuracy/Dota bridge flags=false.
Микрофонная речь, независимая human разметка/командная точность, companion→Dota,
identity/authorization/lease/common contract/native input/human second owner открыты.
Новые C1 pure исходники не превращают C2 proposal в authoritative engine command.
Прогресс C2 остаётся 54/213; голосовая приёмка не отмечалась.

Один итоговый критик не нашёл существенных замечаний; это техническая проверка,
не human/native приёмка. Raw audio/model binaries не публикуются.
