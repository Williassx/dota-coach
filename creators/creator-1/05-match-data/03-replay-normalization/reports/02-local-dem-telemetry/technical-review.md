# Независимый C2 technical review локальной DEM-телеметрии

14 октября 2026. Один итоговый reviewer после завершения research spike C1-05-03. Read-only рассмотрены result/JSON, experiment README, actual ignored `TelemetryProbe.java`, parser audit и validation cases; независимо прочитаны run-2/run-3 samples, CSV и combat events. Dota, runtime игры, зависимости и общие документы reviewer не менял; единственная запись — этот отчёт. Повторный запуск Java/parser и широкие продуктовые тесты не выполнялись.

**После исправления указанной ниже документальной неточности P1/P2 замечаний в ограниченном исследовательском результате не найдено.** Принимается technical feasibility одного локального реплея; validation_complete и strict_HUD_alignment_complete остаются false.

## Независимые проверки actual output

- Из run-3 непосредственно прочитаны **34051 samples.jsonl records**, **32178 CSV actor rows**, **11341 combat records**; последний demo tick68100. Все samples synthetic=false, ticks уникальны. Synthetic callbacks34050 отражены только в summary/code skip, не выданы за новые packet-end состояния.
- Независимый фильтр по actual PlayerResource SteamID0007 и selected full handle даёт ровно32178 eligible ticks; множество совпадает с CSV, остальные1873 не подставлены как состояния игрока. В каждой CSV строке verified SteamID76561198030654385 соответствует account70388657 и selected handle14926170; actual Storm identity=index346/serial911/active/existent. Index отдельно не использован как постоянная identity.
- Все32178 CSV строки сверены с raw JSONL: HP/maxHP/mana/maxmana/life state, full identity, raw cell/vec XYZ и clock formula — **0 mismatches**. Life histogram0:29833,1:81,2:2264 совпал. Raw player ID14 сохранён; семантика неизвестна, деление14/2 не применено.
- Actual clock fields: start0.0 и230.16667, paused=false; старое m_fGameTime=null. `(CNETMsg_Tick−pause_total_ticks)/30−current_nonzero_start` совпадает с CSV. При отсутствии ненулевого start1348 уже привязанных actor rows имеют пустое game_seconds_raw. Настоящая пауза не наблюдалась: ветка pause-start не получает положительную приёмку этим матчем.
- Server−demo delta histogram действительно463:1 и464:34050. Единственная463 — **первая** запись demo0/server463; последняя68100/server68564 имеет464. Это provenance реальных сообщений, не fitted HUD offset.
- Все32178 state64 значения сравнены **точно как integer→decimal string**, без float/JavaScript Number; mismatches0, максимальное observed значение72057594046316800. Семантика битов не выводилась. CSV coordinates совпали с raw cell/vec, но world/map transform не принят.
- Девять HUD candidate cases пересчитаны из actual CSV на declared requested ticks: decoded fields/absolute differences/state64 совпали с report. Их статус корректно `CONSISTENT_AT_REQUESTED_SEEK_TICK_NOT_EXACT_CAPTURE_PROOF`; это не exact native calibration/PASS. Для25:34 сохранены все15 candidates `[1534,1535)` секунд, множество actual ticks совпало; статус UNRESOLVED. Два финальных кадра NOT_RESOURCE_COMPARISON. Ранее просмотренные HUD изображения используются как явные golden observations; новых image batches этот reviewer не запускал.
- Actual combat log содержит ровно четыре target Storm non-illusion death записи относительно raw start:493.00003,932.13333,1177.20003,1314.83343. API integer493/932/1177/1315 не заменён этими дробями.
- Actual target modifier-add: `modifier_slark_pounce_leash`, attacker Rubick,929.80003s; затем `modifier_stunned`, attacker Mirana,930.86673s. Это подтверждает конкретные имена/порядок событий, без переименования leash в root и без вывода об ошибке игрока/предвидимости/допустимых знаниях.

## Версии, provenance и воспроизводимость

Input DEM SHA256, current probe source SHA256, bytes/SHA256 всех6 declared run-3 artifacts и8 locked runtime JAR независимо совпали с telemetry-spike.json. Local POM содержит explicit Clarity5.0.1 и protobuf7.1; JDK release подтверждает Temurin21.0.12.1+1, Maven core artifact3.9.11. Хэши local JDK ZIP/Maven ZIP совпадают с записанными actual/published receipts. Это проверка локальных файлов/receipts, не новый network provenance audit.

Run-2/run-3 samples SHA256 одинаковы побайтно. Добавленные combat/schema observers не изменили эти snapshots; claim ограничен repeatability одного parser/version/input, **не независимым decoder implementation**. Времена10.607/18.218s обозначены как отдельные local parse measurements, не полное время исследования или token saving.

Actual schema artifact подтверждает PlayerID_t→IntVarUnsignedDecoder, mana→FloatQuantizedDecoder, state64→LongVarUnsignedDecoder. Pinned S2DecoderFactory из local5.0.1 source JAR не регистрирует PlayerID_t и имеет unsigned fallback. Это не доказывает реальную signed wire encoding, причину raw14 или корректность всех остальных полей. Field serializer-properties output является opaque object.toString; он не превращён в якобы исследованный encoder metadata.

`git check-ignore` подтверждает ignored Java source и JAR; `git ls-files` не содержит их/raw telemetry. В Git остаются выводы/хэши, а не библиотечные бинарники/полные spectator dumps. Probe использует реальные parser JAR, но не импортирован в игру и не объявлен production importer.

## Исправленный факт и оставшиеся границы

При первоначальном рассмотрении result.md ошибочно называл единственную delta463 EOF записью. Reviewer сообщил actual first/last evidence; root исправил текст на first demo0/server463 и last68100/server68564. **Повторное чтение исправленной строки подтвердило исправление**. Расчёт clocks и output не менялись; иных P1/P2 findings не обнаружено.

Не принимаются: обобщённый actor mapping/illusion/replacement/seek lifecycle вне данного fixed-slot probe; строгий tick↔PNG readback; реальная pause handling; schema compatibility всех patch/build; coordinate transform/скорость; semantic enum state64; fog/исторически доступное знание; качество решений/устойчивые черты; training/heldout fidelity; права/распространение. `learned_player_model=false`, `player_fidelity_verified=false` соответствуют результату. Hardcoded0007 и modifier parent346 допустимы только в обозначенном throwaway one-match эксперименте и требуют новой спецификации перед сохраняемым importer.

Итог: техническая передача ограниченного feasibility и воспроизводимого extracted output подтверждена. Общие checklist/product gates этим review не закрываются. Token usage/cost reviewer недоступны: null.
