# Локальный импорт DEM — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** получить проверяемый локальный импорт состояний и исследовательских событий выбранного игрока, без обучения или подключения к игре.

**Architecture:** Python проверяет входы, запускает один Java emitter и публикует результат только после проверки EOF, содержимого и hashes. Java использует pinned Clarity, динамический PlayerResource binding и отдельную чистую модель lifecycle/clock. Потоковые outputs и компактный индекс заменяют повторные полные dumps.

**Tech Stack:** Python stdlib/unittest; Temurin21.0.12.1+1; Clarity5.0.1/protobuf7.1 и восемь JAR из существующего lock. Windows — первая поддерживаемая платформа CLI; pure tests могут работать отдельно от Windows/JDK/DEM.

**Spec:** [согласованная спецификация](telemetry-import-design.md). Пользователь14октября2026 ответил «Согласовать спецификацию». Пользователь15октября2026 поручил «продолжай» после предъявления этого плана; исполнение согласовано. Фактические результаты — reports/04-local-dem-import. Исполняет основной агент последовательно, один независимый C2 review завершённого подпроекта; не нужны отдельные процессы для планирования.

## Global Constraints

- «Никаких скачиваний, автоподбора зависимостей, управления Dota, общего runtime-контракта, правового разрешения или обучения».
- «Источник остаётся offline spectator telemetry; пригодность для восприятия ИИ не утверждается».
- «Synthetic callbacks не добавляют состояние»; «Optional поля явно unknown с причиной; не заменяются нулями».
- «Raw `m_iPlayerID=14` не переименовывается в7 или2»; uint64 — канонические десятичные строки0..2^64−1.
- «Existing output и пользовательские файлы не перезаписываются»; receipt только после завершения/validation, на том же томе.
- Текущий checkout, библиотека C1-05-03; никаких новых worktree, runtime/HUD, global Java/PATH или checklist изменений.

## Review Focus

1. Два импорта в один путь и внешнее создание пустого destination: отказ без замены, Task3.
2. Изменение DEM/JAR во время чтения: повторные hashes и отказ, Task1/3.
3. Clarity EOF или callbacks с исключением: наличие footer не заменяет успешный exit/проверку, Task2/3.
4. Одинаковое имя героя в CombatLog у нескольких сущностей: candidate, без ложной actor attribution, Task2/4.
5. Повторяющиеся/пересекающиеся windows и неизвестный game clock: без дубликатов, выбор по demo tick, Task4.

---

## Файлы и единственный источник

Все пути ниже относительно этого подпункта. Существующий `src/replay_gate.py` не принимает state snapshots; его4tests остаются регрессией. `TelemetryProbe.java` остаётся ignored историческим probe; его алгоритмы перерабатываются, он не становится второй активной реализацией.

| Файл | Ответственность |
|---|---|
| `src/dem_types.py` | dataclasses InputSpec, Limits, ImportContext, ImportResult; canonical JSON и ошибки |
| `src/dem_inputs.py` | input/lock/runtime hash, безопасные paths, cache key |
| `src/TelemetryCore.java` | чистые binding epoch, clock и unsigned преобразования |
| `src/TelemetryEmitter.java` | Clarity callbacks, schema fingerprint, streaming extraction |
| `src/dem_store.py` | staging, verified cache, limits/процесс, publication |
| `src/dem_episodes.py` | compact index и windows без интерполяции |
| `src/import_dem.py` | единственный CLI и краткий итог |
| `notes/dem-dependencies-v1.json` | восемь exact JAR pins из [spike receipt](reports/02-local-dem-telemetry/telemetry-spike.json), JDK provenance |
| `notes/dem-schema-v1.json` | versioned class/field/type/decoder/quantization fingerprint и sampling/clock policy |
| `tests/test_dem_{inputs,store,episodes,cli}.py` | pure и subprocess-fake checks через unittest |
| `tests/TelemetryCoreTest.java` | Java main/assertions без новых dependencies |
| `tests/check_dem_golden.py` | явно запускаемая реальная приёмка, не ordinary discovery |

README подпункта и отчёты обновляются по фактам. Новых вложенных папок не требуется.

## Frozen v1 интерфейс и формат

CLI: `python src/import_dem.py --input PATH --match-id ID --account-id ID --lock PATH --config PATH --output NEW_DIR`. Paths в примерах ниже — от этого подпункта; реальные команды запускаются из root с полным библиотечным путём. CLI ещё не существует.

Config `dem-import-config-v1`: explicit `java_home`, `jar_directory`, `fields`, `episode_windows`, `limits`; неизвестные/повторные JSON keys отвергаются. `fields` может быть только subset optional `raw_position`, `raw_control`; required identity/resources/server clock всегда включены. Windows задаются `{id,start_demo_tick,end_demo_tick}`, inclusive, id unique, sorted/merged для записи без дубликатов. Default windows=[] создаёт только index, не дополнительные копии state stream.

Limits/config keys v1: `max_input_bytes=2147483648`, `max_output_bytes=536870912` суммарно, `max_states=2000000`, `max_events=2000000`, `timeout_seconds=300`, `max_stderr_bytes=1048576`, `max_line_bytes=65536`, `java_heap_mib=512`, `max_windows=1000`, `max_index_entries=10000`. Это конфигурационные лимиты, не измеренный SLA. Превышение любого — exit6; значения положительные, без скрытого unlimited. Internal ephemeral emitter-summary также входит вoutputbudget, но не finaloutput.

Выход: `states.jsonl`, `events.jsonl`, `gaps.jsonl`, `episodes.json`, `receipt.json`; при windows ещё `windows.jsonl`. UTF-8/LF, sorted object keys, finite числа, последовательность records определяется input callbacks, никаких wall timestamps в deterministic streams.

State v1: `seq`, `demo_tick`, `server_tick`, `binding_epoch`, `clock_epoch`, `actor`(account32,Steam64-string,fullhandle,index,serial,class,reference_path), `resources`(hp,max_hp,mana,max_mana), `clock`(start,pause_total,pause_start,paused,game_seconds), `phase_raw`, `raw_player_id`, optional raw cell/vec/state64/life_state, `unknown_reasons`, `knowledge_scope="spectator_research"`. Header/receipt содержит match_id, schema и clock revisions; protobuf uint64match_id также decimal string, InputSpec int переводится по проверенному типу. State не содержит guessed action/intent или mapped control bits.

Event v1: `seq`, `demo_tick`, `server_tick`, nullable combat timestamp/game_seconds, raw type/name/value/illusion fields, nullable full entity references, `actor_link="full_reference"|"candidate_name_only"|"unresolved"`, knowledge scope. Name-only target/attacker не даёт full_reference. Неатрибутируемые events остаются отдельными исследовательскими кандидатами; capability verified_actor_events=false, без выдачи их за команды Dendi.

Gap: tick interval, epoch, reason (`unassigned`, `deleted`, `ambiguous`, `clock_unknown`, `discontinuity`, `optional_missing`), affected capabilities. Missing required schema/decoder — отказ, missing expected actor весь матч — exit3; начальные1873unassigned samples допустимы как объявленный gap. Missing nonzero start даёт game_seconds=null и clock_unknown, но server_tick необходим для actor sample. Raw pre/post phases сохраняются, active subset вv1 не предоставляется.

Receipt: completed=true только послеEOF+exit0+validation; input/runtime/source/classfile/lock/schema/config hashes, counts/gaps/capabilities, data hashes, cache key, non-deterministic timing отдельно. model_trained=false, player_fidelity_verified=false, perception_export_allowed=false. Calibration — список конкретных match/build/tick/fields из [native receipt](reports/03-native-tick-calibration/evidence.json), общий native_verified=false.

Exit:0complete или verified cache hit;2input/lock/schema;3identity;4required clock/data;5integrity/IO;6limit/timeout. stdout один JSON summary; details в ограниченном diagnostics sibling, исключение не завершает импорт успешно.

## Task1: Входы, canonical данные и dependency lock

**Files:** create `src/dem_types.py`, `src/dem_inputs.py`, `notes/dem-dependencies-v1.json`, `tests/test_dem_inputs.py`.

**Interfaces:** `validate_inputs(spec:InputSpec)->ImportContext`; `canonical_json(value:object)->bytes`; `uint64_decimal(value:int|str)->str`; `cache_key(context:ImportContext)->str`. `InputSpec(input:Path,match_id:int,account_id:int,lock:Path,config:Path,output:Path)`; Limits содержит именованные значения раздела Frozenv1. `ImportContext(spec:InputSpec,limits:Limits,hashes:dict[str,str],runtime:dict,config:dict)` хранит resolved paths черезspec, mutable staging не содержит. `DemImportError(code:int,reason:str)` — единственная ожидаемая категория отказа, не shadow встроенного ImportError.

- [x] RED: `test_inputs_reject_codec_truncation_duplicate_keys_and_tampered_jar`, `test_paths_reject_reparse_escape`, `test_uint64_canonical` проверяют PBDEMS2 magic, отсутствующие/повторные8pins, hashes, unknownconfigkeys,0/2^53+1/2^64−1 strings и отказ−1/overflow/noncanonical. `test_cache_key_changes_for_each_provenance_input` меняет каждое поле ключа по одному.

```python
assert canonical_json({'state64': '18446744073709551615'}) == b'{"state64":"18446744073709551615"}\n'
assert uint64_decimal(9007199254740993) == '9007199254740993'
with self.assertRaises(DemImportError):
    canonical_json({'mana': float('nan')})
```

- [x] Запустить `python -m unittest discover -s tests -p test_dem_inputs.py -v`; ожидаемый RED — отсутствующий модуль, затем реальные failing assertions, не случайная ошибка окружения.
- [x] Реализовать интерфейсы stdlib; зависимость/runtime используются только из explicit local paths. Lock переносит literal SHA/bytes всех8JAR; release/JDKjava+javac hashes измеряются перед фиксацией, не придумываются. Проверять все существующие path components на reparse, разрешённый local volume и наличие; immutable input hashes повторяются перед publication.
- [x] Та же команда GREEN; lock сверить с8actualJAR и записанным Temurin release, сохранить результат. Commit `feat: validate local DEM import inputs`.

## Task2: Generic emitter, lifecycle и schema gate

**Files:** create `src/TelemetryCore.java`, `src/TelemetryEmitter.java`, `notes/dem-schema-v1.json`, `tests/TelemetryCoreTest.java`.

**Interfaces:** `TelemetryCore.updateBinding(BindingObservation)->BindingResult`; `TelemetryCore.clock(ClockObservation)->ClockResult`; `TelemetryCore.uint64(long)->String`. Core records: `HeroReference(long accountId,String steamId,long fullHandle,int index,int serial,String className,boolean existent,Boolean illusion,boolean authoritativeReference)`; `BindingObservation(int demoTick,List<HeroReference> candidates)`; `BindingResult(long epoch,HeroReference actor,String reason)` сnullableactor; `ClockObservation(int demoTick,int serverTick,Double startSeconds,int pauseTotalTicks,Integer pauseStartTick,boolean paused,double tickSeconds)`; `ClockResult(long epoch,Double gameSeconds,String reason)`. `TelemetryEmitter.main(String[] args)` принимает `--input/--account-id/--match-id/--schema/--staging/--limits-json`; пишет streams и отдельный `emitter-summary.json` сEOF/counts, не receipt.

- [x] RED Java assertions: `testIndexReuseExpiresOldSerial`, `testAmbiguousAndIllusionCannotReplaceAssignedHero`, `testStartUnknownAndPauseClock`, `testUnsignedBoundary`, `testSameHeroNameIsNotIdentity`. Fixtures передают observed references, не hardcoded slot/entity. Death/raw life_state change запрещает interpolation, не создаёт угаданный enum. Emitter actual negatives synthetic/missingdecoder/truncatedEOF проверяются Task5, исключение процесса Task3.

```java
assert TelemetryCore.uint64(-1L).equals("18446744073709551615");
assert core.clock(new ClockObservation(0,463,null,0,null,false,1.0/30)).gameSeconds() == null;
```

- [x] Компилировать `& "$taskJavaHome/bin/javac.exe" --release 21 -d "$taskBuild/classes" src/TelemetryCore.java tests/TelemetryCoreTest.java`; выполнить `& "$taskJavaHome/bin/java.exe" -ea -cp "$taskBuild/classes" TelemetryCoreTest`, RED затем GREEN после core implementation.
- [x] Emitter: Clarity `infoForFile(...).getGameInfo().getDota()` presence/matchid/roster checks, затем SimpleRunner; перечислять существующие PlayerResource paths, account по Steam64low32 при подтверждённом Steam type, выбранный полный hero reference/index/serial. Нет fallback firstStorm/0007/346 или ID14/2. Serial/deletion/reference change создают epoch и gaps; ambiguity закрывает actor channel. Единственная authoritative full reference допускает assignedhero binding приunknowncloneclassification, сохраняя unknownreason/capabilityfalse; это не доказательство clone/illusion semantic enum. Knownillusion или конфликт references не принимаются.
- [x] Schema сначала fail-closed audit: получить actual type/decoder и стабильные numerical quantization parameters required identity/resources/clock и optional fields. Сравнить с versioned profile; runtime `toString()` object addresses изspike не fingerprint. Фиксировать только реально измеренные entries; unknown profile возвращает2 и observed diagnostic, не auto-allow. Required hp:int32/signed, mana:float32/quantized, state64:uint64/unsigned подтверждены spike; остальные значения проверить, не экстраполировать.
- [x] Compile emitter с exact8JAR classpath; running schema audit не завершает receipt. После фиксации профиля реальный parse обязан успешно завершиться и generic identity получитьaccount70388657/fullhandle14926170. Политика clock поactualCNETMsg_Tick/currentnonzero start/observed pause fields, tick interval изruntime; не464offset. Тестпауза synthetic, actual pause acceptance остаётся false. Commit `feat: extract generic replay telemetry with schema gates`.

## Task3: Потоковый store, процесс, кэш и CLI

**Files:** create `src/dem_store.py`, `src/import_dem.py`, `tests/test_dem_store.py`, `tests/test_dem_cli.py`; update `src/dem_inputs.py` только для итоговых classfile hashes.

**Interfaces:** `run_import(context:ImportContext)->ImportResult`; `verify_cache(path:Path,context:ImportContext)->ImportResult|None`; `promote_no_replace(staging:Path,output:Path)->None`; CLI `main(argv:list[str]|None)->int`. ImportResult: status/cache_key/counts/data_hashes/output, без model claims.

- [x] RED: subprocess fixture с EOF+nonzeroexit, безEOF+exit0, truncatedJSONL, changedDEM/JAR, timeout, overbytes/records/stderr; все дают ненулевой код и no completed output. `test_cache_tamper_refused`, `test_two_writers_and_external_empty_destination_preserved`, `test_staging_escape_refuses_cleanup` проверяют hashes/ownership/отсутствие replacement.

```python
destination.mkdir()
with self.assertRaises(DemImportError):
    promote_no_replace(staging, destination)
assert destination.is_dir() and not list(destination.iterdir())
assert staging.exists()
```

- [x] Run `python -m unittest discover -s tests -p test_dem_store.py -v` и `test_dem_cli.py`; зафиксировать RED.
- [x] Реализовать один bounded subprocess без shell, `-Xmx512m`, streaming writer/validator, timeout/reaping own child, sibling staging и exclusive output lock. Cache — только существующий explicit output с совпадающим cache_key/completed/hashes; неполный/чужой output отказ5, не overwrite. Windows promotion `MoveFileExW` без REPLACE_EXISTING; unsupported platform отказ5 вместо недоказанной atomicity. Повторно проверять path/input/dep hashes непосредственно перед promotion; failure diagnostics отдельно, удалить только owned проверенный staging.
- [x] GREEN обеих команд и существующих4 `test_replay_gate.py`; actual no-replace race и reparse guard проверить на Windows, недоступный случай оформить NOT RUN, не skip=PASS. Commit `feat: publish verified bounded DEM imports`.

## Task4: Экономный индекс эпизодов и окна

**Files:** create `src/dem_episodes.py`, `tests/test_dem_episodes.py`; wire `dem_store.py`.

**Interfaces:** `build_episodes(states:Iterator[dict],events:Iterator[dict],gaps:Iterator[dict],windows:list[dict],output_dir:Path,limits:Limits)->EpisodeResult`; `EpisodeResult(index_count:int,window_record_count:int,data_hashes:dict[str,str])`, не полный state list. Пишет episodes/windows вownedstaging Task3 доreceipt. Merge streams поdemo_tick+source sequence, bounded current epoch/window; input ужеvalidated Task3.

- [x] RED: `test_overlap_and_duplicate_windows_no_duplicate_records`, `test_unknown_clock_uses_demo_ticks`, `test_death_gap_and_epoch_not_interpolated`, `test_candidate_event_not_promoted_to_action`, `test_index_limit_aborts`, `test_streaming_does_not_materialize_all_states`. Проверить ordinary control windows наряду с candidate control/death episodes, не отбирать только ошибки игрока.

```python
# Проверить записанный windows.jsonl при двух пересекающихся окнах.
assert len(records) == len({(r['stream'], r['seq']) for r in records})
assert all('observed_action' not in r for r in candidate_index_entries)
assert all(r['game_seconds'] is None for r in unknown_clock_records)
```

- [x] `python -m unittest discover -s tests -p test_dem_episodes.py -v`: RED.
- [x] Реализовать index поraw state/lifecycle changes, gap boundaries и named event candidates; label сохраняет source/type/uncertainty. Нет игровых команд/intent и нет подачи states вreplay_gate. Model export отсутствует; raw entitydump/rawchat/offactorresources не включаются. События/состояния каждого запроса попадают вwindows не более одного раза с list windowids.
- [x] GREEN; повторный deterministic output hash безwalltimestamps. Commit `feat: index replay episodes without inferred actions`.

## Task5: Реальная приёмка, независимый обзор и публикация

**Files:** create `tests/check_dem_golden.py`; update README; new report `reports/04-local-dem-import/README.md`, `result.md`, `receipt.json`, `technical-review.md`; индекс reportsREADME. Raw outputs/compiler/config/JDK остаются ignored BUILD.

- [x] Создать golden check: exactDEMhash изspike,account70388657,match9042986015,mis-match IDs, preserve existing output; actual synthetic callbacks не увеличивают realcount, truncatedDEM и несовместимыйdecoder дают отказ. Два freshoutput импорта должны иметь одинаковые deterministic data hashes; cachehit не запускает Java. Parsecounts объяснить относительно34051real/32178actor/1873unassigned, не менять критерий под output без сохранённого исследования.
- [x] Run Python `unittest discover -s tests -p test_dem_*.py -v`, existing replaygate и Java main suite. Затем explicitly `python tests/check_dem_golden.py --dem VERIFIED_DEM --lock notes/dem-dependencies-v1.json --config LOCAL_CONFIG --output BUILD/golden-import`; команды будущие, сейчас не выполнены.
- [x] Compare21212/41706/45846 HP/mana/maxima/gameclock сexact native receipt. Межпакетные1tick и fixed/slowclock7:25 остаются отдельными отрицательными случаями. Actual pause/otherpatch/fog/controlbit/worldtransform/model/5×5 не становятся проверенными от unit fixtures.
- [x] Один independent C2 reviewer после завершения всехзадач: код+realoutputs+guard negatives+limits/cache/atomicity, исправления и повтор затронутых checks. В отчёте actualPASS/FAIL/NOTRUN и elapsed/bytes; tokens/costnull при отсутствииметрики. Нет критика каждого test/подпункта.
- [x] JSON/links/gitdiff checks, project lesson/actionlog/oneusage entry; staged только библиотечные источники/малыеtests/locks/compactreports. Commit/push по поручению пользователя, verifyremote SHA; .freebuff/сыройDEM/Java toolchain/assets не публиковать.

## Самопроверка плана и передача

Для команд исполнения использовать bundled Python, а не системныйJava8/Pythonalias. В PowerShell перед futurechecks (не выполнено сейчас):

```powershell
$taskPython = 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskJavaHome = 'D:/AI/dota2coach/build/dota_coach/replay-9042986015/telemetry-spike/jdk/jdk-21.0.12.1+1'
$taskBuild = 'D:/AI/dota2coach/build/dota_coach/dem-import-v1'
Set-Location -LiteralPath 'D:/AI/dota2coach/creators/creator-1/05-match-data/03-replay-normalization'
```

Все команды `python ...` вшагах означают `& $taskPython ...` вэтомworkingdirectory. Emitter compile использует проверенный configjar directory, pathсписок строится изlock, не wildcardстороннихJAR. `BUILD`/`LOCAL_CONFIG`/`VERIFIED_DEM` вgoldencheck — значения изactualignoredlocal config/ownedoutput, их разрешает checker и пишет вreceipt; не команда скачивания или текущая выполненная проверка.

Speccoverage: provenance/schema→1/2, identity/lifecycle/clock/uint64→2, streaming/limits/cache/atomic→3, episodes/knowledge/actionboundaries→4, native evidence/independentreview→5. Все пять ReviewFocus имеют отдельные namedtests; интерфейсы совпадают междузадачами. Профиль неизвестных required decoder параметров получается actualaudit, не подгоняется кHUD. Новые лимиты/формат — предложения именно технического плана.

План исполняет основной агент в этой сессии с существующим разрешением на полезные независимые специализации; выбранная здесь схема соответствует требованию экономии и одного итогового C2review. План рассмотрен; исходники реализованы, приёмка и итоговый обзор фиксируются отдельно.
