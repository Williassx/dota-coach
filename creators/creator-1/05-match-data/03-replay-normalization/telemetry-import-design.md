# DRAFT: сохраняемый локальный импорт телеметрии DEM

14 октября 2026. Автор спецификации C1, роли105/102; root реализует probe/калибровку, C2 проверяет результат. Пользователь разрешил продолжать направление. **Этот документ ещё требует рассмотрения архитектуры; импортёр и технический план реализации не созданы.** Нативная калибровка обновляется root отдельно.

Основания: [замысел](../../../../docs/project-brief.md), [решения](../../../../docs/decisions.md), [P04/P06](../../../../docs/roadmap.md), [DC-011/012](../../../../docs/backlog.md), [навыки](../../../../docs/skills.md), [actual spike](reports/02-local-dem-telemetry/result.md), [pin/доказательства](reports/02-local-dem-telemetry/telemetry-spike.json), [случаи проверки C2](notes/telemetry-validation-cases-2026-10-14.md).

## Цель и границы

Преобразовать локальный неизменяемый `.dem` в воспроизводимые исследовательские состояния и события выбранного игрока, с доказуемым происхождением, пропусками и отказами. Никаких скачиваний, автоподбора зависимостей, управления Dota, общего runtime-контракта, правового разрешения или обучения. Источник остаётся offline spectator telemetry; пригодность для восприятия ИИ не утверждается.

Actual spike прочитал один матч с Clarity5.0.1/protobuf7.1:34051 real packet-end records,32178 actor records; synthetic callbacks не являются samples. Binding0007/handle14926170/index346/serial911 — результаты этого реплея, **не константы импортёра**. Compatibility на других патчах ещё не проверена.

## Архитектура и альтернативы

Предложение: один Java extraction emitter поверх pinned Clarity, один локальный CLI-оркестратор для проверки входов, streaming outputs, кэша и atomic receipt. Исследовательский Java probe сначала оформляется в единственный библиотечный источник, не копируется в новый раздел. Точные файлы/API появятся после рассмотрения в implementation-plan.

Альтернатива API-only проще, но агрегаты не дают resource/control snapshots; она не заменяет DEM. Альтернатива новый независимый parser требует отдельной compatibility-проверки. Для первой версии используем проверенный стек; другая версия требует нового pin и тестов.

## Provenance и schema gate

Входы: существующий plain DEM с проверяемым заголовком, ожидаемый match_id и account_id, dependency lock, конфигурация выборки. По умолчанию сжатые/неизвестные форматы отклоняются: имя `.bz2` не определяет codec. Никаких секретов, сетевых входов или имениDendi как identity-key.

Pin включает parser/protobuf версии, SHA256 всех runtimeJAR, emitter source/build hash, JDK, lock revision и schema/clock revisions. До извлечения проверяются lock/hash; фактические class/property type/decoder сравниваются с поддерживаемым fingerprint. Отсутствующие required fields/несовместимый decoder дают отказ. Optional поля явно unknown с причиной; не заменяются нулями. Non-finite clock/resources или выход чисел за подтверждённый тип — отказ required channel; null не подменяет несовместимый decoder. Неизвестные enum/raw fields сохраняются в ограниченном диагностическом канале. Один match_id с другим DEMhash требует расследования, не перезаписи.

## Actor discovery

Обнаруживать все реальные PlayerResource bindings, искать ожидаемый account через подтверждённый Steam identifier/type. Затем получать assigned/selected hero reference с **полным handle, index и serial/generation**, class и owner provenance. Не выбирать первыйStorm, слот0007 или entity346. Несовпадение match/account/hero или неоднозначный выбор закрывает actor channel до разрешения; никакого fallback по nickname.

Deletion, replacement, index reuse и seek создают новую binding epoch. Иллюзии/клоны/призывы не становятся actual assigned hero по одному owner/class: признаки и lifecycle проверяются по schema, неоднозначность остаётся unknown. Raw `m_iPlayerID=14` не переименовывается в7 или2; причина семантики пока не подтверждена.

SteamID/uint64 state/другие uint64 сохраняются каноническими десятичными **строками** с диапазоном0..2^64−1; не JavaScript Number и не signed negative. Account32 остаётся отдельно отSteam64; conversion фиксируется только при проверенном типе.

## Время, значения и события

Хранить demo_tick, actual CNETMsg_Tick, real/synthetic marker, clock epoch, raw start/pause fields и nullable game_seconds. Tick interval, pause adjustment и game-start источник имеют версии и доказательства. Не применять постоянный offset464: spike имел первое отличие463. Start неизвестен — game_seconds=null; не путать start0 с доказанным игровым временем0. Synthetic callbacks не добавляют состояние.

Pre/postgame и phase unknown сохраняются отдельно; active-game subset возможен только с проверенным phase mapping. Паузы/пропуски/deletions отмечаются интервалами. Нет interpolation через discontinuity, смерти или новую entity. Указываются packet sampling interval и необработанные интервалы;15Hz replicated states не являются реакцией человека30Hz.

HP/mana и maxima остаются decoded значениями с type/decoder, без подгонки подHUD. Raw cellXYZ/vecXYZ не называются мировыми координатами или скоростью до transform calibration. State64/raw life_state и именованные CombatLog modifiers сохраняются раздельно: event-add/remove не гарантирует полный state snapshot. Root/leash/stun/death enum нельзя угадывать по caption, имени поля или соседнему герою.

Replicated snapshot — **состояние**, не выдуманное действие. [replay_gate.py](src/replay_gate.py) применяется только к совместимым event records с известным observed action, отдельно от state stream. Он разделяет action/intent и фильтрует заданные hidden/future flags, но не доказывает visibility. Intent не создаётся автоматически. Ground truth врагов/future outcomes хранится исследовательским каналом; model/perception export запрещён, пока unknown fog/authorization не разрешены отдельным контрактом.

## Предлагаемый CLI и результаты

Будущий локальный CLI: `import-dem --input PATH --match-id ID --account-id ID --lock PATH --config PATH --output NEW_DIR`. Это предложение интерфейса, **не существующая команда**. Конфигурация явно задаёт поля, episode windows, лимиты времени/bytes/records и sampling policy; параметры входят в receipt.

Результаты: manifest/receipt с hashes/counts/capabilities/gaps; streaming JSONL states/events; compact episode index и только запрошенные windows. Полный raw dump выключен по умолчанию. Память ограничена текущим bindings и bounded buffers; stdout — краткий итог, длинные diagnostics отдельно. Любые downsampling/aggregation версии записаны; сохранение событий/death discontinuities не обещается произвольным resampling.

Кэш keyed by DEMhash+actor+parser/lock/emitter/schema/clock/config hashes; cache hit требует проверки всех output hashes и завершённого receipt. Повторный импорт не создаёт дублей; повреждённый/неполный кэш отклоняется. Прогресс и wall timestamps не меняют deterministic data hash.

Запись в новый sibling staging на том же томе; receipt публикуется последним после EOF, hashes и validation, затем atomic promotion в NEW_DIR. Existing output и пользовательские файлы не перезаписываются. Reparse/escaping paths, незавершённый parse, timeout/лимит или hash mismatch не оставляют completed receipt. Удалять можно только созданный этим запуском проверенный staging; failure diagnostics сохраняются отдельно.

Exit0 означает завершённое извлечение required capabilities, не native fidelity. Ненулевые категории: input/lock/schema, identity, required clock/data gap, integrity/IO, limit/timeout. Optional unknown допускается со scope в receipt; required mismatch не маскируется partial-success. Calibration_status ссылается на отдельный доказательный receipt с полями match/build/tick/fields/scopes; три проверенные точки одного реплея не превращают весь импорт или другие матчи в native_verified. [Нативная калибровка](reports/03-native-tick-calibration/result.md) завершена отдельно; userpersonality/model flags всегда false.

## Приёмка перед реализацией

Тесты: invalid/truncated DEM и non-finite values; match/account mismatch; дубликат/изменённый lock; uint64>2^53/границы/overflow; actor absent/ambiguous/illusion/reused index; start unknown/epoch/pause/gap/synthetic tick; unsupported decoder/control; pre/postgame; interrupted atomic write; tampered cache; bounded streaming; deterministic replay. Реальный golden DEM проверяется отдельно поhash, не запускается автоматически каждым unit test.

СверкаHUD следует протоколуC2: exact tick/readback отдельно от requested seek consistency; новый25:34 имеет только prior real-row gap1tick, clock mismatch fixed/slow и неизвестные control/coords сохраняются. Перед code нужны архитектурное рассмотрение, frozen schema/ошибки/лимиты и технический план. Никакой цифровой моделиDendi или готовности5×5 этим результатом не заявляется.
