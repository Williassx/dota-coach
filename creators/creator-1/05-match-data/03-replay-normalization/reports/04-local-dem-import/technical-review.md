# Независимый технический обзор C2: DEM importer v1

15 октября 2026. Один C2 reviewer, роли 105/102/173; без дополнительных агентов. Reviewed range: `e9e6ae9372dbd81e205f0ad33215a74405c99cf7..91555e4798b9831c716fec4ea0075653e5e6bd6d`, branch `codex/dem-import-v1`. Автор реализации — C1/root; reviewer не менял source, tests, plan, общие журналы или runtime build. Разрешённые новые диагностические файлы находятся в ignored `build/dota_coach/dem-import-v1/review-20261015/`.

Основания: [согласованная спецификация](../../telemetry-import-design.md), [технический план](../../telemetry-import-implementation-plan.md), [API audit](../../notes/dem-schema-api-audit-2026-10-15.md), [результат](result.md), Python/Java sources и tests, actual golden3 artifacts. Применены `requesting-code-review` и `verification-before-completion`.

## Оценка

**Требуются исправления: три P2.** Приёмка happy path одного DEM подтверждена локальными артефактами, но текущие барьеры output validation, classpath provenance и failed receipt не полностью выполняют согласованный fail-closed scope. P0/P1 не обнаружены. Ни одно замечание не утверждает наличие дефекта в самих golden3 state records.

## Что подтверждено

- Идентификация в emitter идёт по DEM match metadata, Steam64/account32 и actual PlayerResource reference с full handle/index/serial. Исторические slot/entity constants не используются как identity key. Неоднозначность и known illusion не становятся одним произвольно выбранным actor.
- Descriptor gate сравнивает actual leaf type, decoder class и declared serializer params; uint64 выводятся десятичными строками. `synthetic` tick callbacks не добавляют states.
- CombatLog records сохраняют `candidate_name_only`, а episode index не превращает snapshots в команды или intent. Unknown clock, raw control/position и research knowledge scope остаются явно ограниченными.
- Реализованы потоковая обработка, bounded index/windows, subprocess timeout/reaping, concurrent-writer lock и Windows no-replace rename. В source suite реально прошли Windows junction/no-replace checks; это не native Dota proof.
- Кэш проверяет digest, provenance, membership, artifact hashes и stream counts; Java environment injection variables удаляются. Ограничения ниже относятся к конкретным незакрытым случаям.

## Воспроизводимые замечания

### P2-1 — проверять полный обязательный state/clock DTO перед completed receipt

Файл: `src/dem_store.py:99–123`, особенно `114–116`.

Валидатор проверяет только `clock.game_seconds`; обязательные `server_tick`, epochs, raw start/pause fields и их типы/диапазоны не проверяются. Поэтому неправильные required clock данные могут пройти final validation и получить `completed=true`. Это ослабляет отдельно обещанный Python validation gate, даже при корректном текущем Java emitter.

**Фактическое воспроизведение:** existing `test_dem_store.StoreTests` subprocess-fake harness; заменены только выдаваемые DTO значения: `server_tick="invalid"`, `binding_epoch=-5`, `clock_epoch=-5`, `clock={game_seconds:null,start:"invalid",paused:"invalid",pause_total:-99,pause_start:-99}`. Полный `case.invoke()` завершился `status=imported`; receipt имеет `completed=true`, `capabilities.actor_resources=true`. Native/parser выполнение в этом сценарии не заявляется.

Диагностика: `review-20261015/invalid-required-state.json`.

**Исправление:** строго проверять обязательные поля frozen State v1 и их типы/диапазоны, допустимость nullable unknown clock, согласованность raw clock и computed seconds; использовать полные валидные DTO в positive fake fixtures. Добавить negative tests как для fresh import, так и для cache verification. Epoch/index/reference validation также должно соответствовать фактически сохраняемому контракту.

### P2-2 — исключить незапиненные вложенные классы из Java classpath

Файл: `src/dem_store.py:45–56`; повторная проверка `220–223` также рассматривает только уже известные root classfiles.

`prepare_runtime` перечисляет только `classes/*.class`, а в classpath весь каталог стоит перед pinned JAR. Вложенные package classes не входят в provenance/membership и могут перекрыть класс из проверенного dependency JAR. Наличие правильного SHA у JAR тогда не определяет фактически загруженный класс.

**Фактическое воспроизведение:** в отдельный scratch build скопированы existing classes и compile receipt. Локальным pinned javac скомпилирован безвредный `com.google.gson.Gson` с единственным marker method в `scratch/classes/com/google/gson/Gson.class`. `prepare_runtime` успешно принял runtime до и после добавления; cache key остался прежним, класса в provenance нет. Отдельный Java reflection probe с тем же порядком classpath загрузил Gson именно из scratch classes и вывел `UNPINNED_CLASS`. Основной `BUILD/classes`, JAR, source и imports не изменялись; Dota/сеть не запускались.

Диагностика: `review-20261015/classpath-shadow-result.json`, исходники/классы probe — `review-20261015/classpath-shadow/`.

**Исправление:** для default-package v1 fail-closed разрешать только точный заявленный набор root classfiles и отклонять вложенные каталоги/лишние файлы. Либо полностью пиновать допустимое рекурсивное classpath содержимое. Проверять membership и hashes повторно до promotion, включая добавление нового файла, а не только изменение известного.

### P2-3 — не сохранять принимаемый completed receipt после failed publication/лимита

Файл: `src/dem_store.py:269–284`, связанный `verify_cache` в `139–178`.

Receipt записывается как `completed=true` до последней проверки общего output budget и promotion. При последующем отказе stage переименовывается в `.failed-*`, сохраняя этот receipt. `verify_cache` не проверяет общий byte limit, поэтому такой failed artifact может затем быть принят как успешный cache output.

**Фактическое воспроизведение:** existing subprocess-fake harness с `max_output_bytes=2500` дал код 6 / `receipt_output_limit`, original output отсутствует. Сохранённый `.out.failed-*` содержит 4197 bytes и receipt с `completed=true`. `verify_cache(failed_path, same_context)` вернул `status=cache_hit`. Output path не входит в cache key, поэтому выбор retained failed directory как explicit output также не представляет отдельного provenance mismatch.

Диагностика: `review-20261015/failed-receipt-cache-result.json`.

**Исправление:** failure после receipt creation должен инвалидировать completed receipt в проверенном owned stage; итоговый byte budget следует проверить до признания completion. Кэш также должен соблюдать текущие лимиты и принимать только результат с полным доказательством успешного завершения. Сохранять failure diagnostics допустимо, сохранять принимаемую completed-квитанцию для отказавшего импорта — нет. Добавить regression для failed budget и promotion race после записи receipt.

## Свежие проверки reviewer

| Проверка | Фактический результат |
|---|---|
| Bundled Python `-m unittest discover -s creators/creator-1/05-match-data/03-replay-normalization/tests -p 'test_*.py' -v` | 30/30 PASS, 4.351 s; 0 skipped; includes four existing replay_gate tests |
| Pinned Java `-ea -cp build/dota_coach/dem-import-v1/classes TelemetryCoreTest` | PASS: lifecycle/ambiguity/illusion/pause/unsigned/unknown/seek |
| Independent SHA-256 всех пяти data artifacts в actual `golden3/first` и `golden3/second` | Оба набора совпали между собой и с declared hashes |
| Реальные output counts | states 32178, events 11341, gaps 3221 |
| Независимые negative reproductions | Все три выше воспроизведены; это guard FAIL, а не новые successful acceptance cases |
| Fresh full DEM extraction / full catalog / Dota / network | NOT RUN reviewer; существующие golden outputs проверены непосредственно, source full-catalog status не расширялся |

Сумма пяти data outputs одного golden3 результата: 34616658 bytes (episodes 784035, events 4326749, gaps 455985, states 28804394, windows 245495). Fresh artifact hash details: `review-20261015/golden-artifact-check.json`. Остальные времена reviewer не измерялись единым интервалом; elapsed total, token usage и cost — null. Показатель 89/1417/28 skipped/6 incomplete/0 errors/strict false — результат root, не новый reviewer full run. Skips/incomplete не считаются успешной общей приёмкой.

## Рассмотрено и оставлено вне этого verdict

- Реальная pause/death/replacement/illusion lifecycle across matches: один golden replay и synthetic Core assertions не доказывают весь native lifecycle; не расширять scope по этому обзору.
- Hero metadata/class mismatch при испорченном DEM: возможный дополнительный negative case, но отдельное подтверждённое воспроизведение не получено; в findings не включён.
- Fog/player authorization, world transform, model fidelity, heldout evaluation, rights и runtime 5×5: явно исключены согласованным offline research scope и требуют отдельных доказательств.
- Подпись receipt/защита от пользователя с правом произвольно переписать source, lock и весь receipt: digest не заявлен аутентификацией. P2-2 относится к незаявленной загрузке файлов при **неизменённых** pin/receipt/key.
- Права Windows, path/FIFO и прочие skips общего каталога: этот обзор не меняет OS policy и не подменяет их локальными unit PASS.

Рекомендуемая следующая проверка: один связанный fix pass с RED→GREEN для трёх замечаний, затронутые local suites, затем fresh deterministic golden imports/cache, поскольку source hashes входят в key. До этого итог review — **With fixes**, без утверждения полной готовности импортёра или игры.

## Resolution: повторная проверка исправлений 15 октября 2026

Один связанный fix pass C1/root рассмотрен тем же C2 reviewer, без нового критика. Исходные три P2 выше сохранены как история подтверждённых дефектов. Проверен working-tree diff поверх `91555e4`, только `src/dem_store.py` и `tests/test_dem_store.py`; reviewer не редактировал эти файлы. Проверенные SHA-256: source `b3d13224bb4281daa12cbecfddbc1d0c26c1cd558d59dde2d3b5a6e0a76008f2`, tests `26a12e98836164855f0c749e7ff3a1787784eb000cf593a246daae83895ac09c`.

**Итог повторного обзора: три P2 закрыты в проверенном scope; технических blockers для этого локального импортёра не осталось.** Это заменяет начальный verdict `With fixes` после внесённых исправлений и не расширяет native/model/product scope.

| Finding | Реализация и независимая проверка | Статус |
|---|---|---|
| P2-1 | `validate_state` проверяет typed server tick, epochs, phase, actor identity, complete clock, finite values, pause bounds и формулу game seconds; positive fake DTO дополнен. Первоначальный invalid DTO повторно отвергнут кодом 4 `required_integer_range`, completed output отсутствует. | CLOSED |
| P2-2 | `class_snapshot` разрешает только точные root classfiles, отклоняет вложенные каталоги/не-class entries. `assert_unchanged` повторяет full runtime snapshot перед publication. Первоначальный scratch с реальным benign Gson shadow class повторно отвергнут кодом 2 `unexpected_classpath_entry`; добавление nested class во время child run покрыто новым regression. | CLOSED |
| P2-3 | Полный бюджет с encoded receipt проверяется до записи receipt; при последующем publication failure completed receipt удаляется только из staging с подтверждённой identity. Internal failed/staging/diagnostics пути не принимаются как cache; кэш проверяет текущий byte budget. Повтор исходного overbudget: код 6, failed receipt отсутствует; failed cache даёт код 5. Отдельный post-write publication-failure regression прошёл. | CLOSED |

Независимые повторные reproductions: `build/dota_coach/dem-import-v1/review-20261015/resolution-reproductions.json`. Изучен root RED log `review-fixes-red.log`: 15 failures (включая десять clock subcases), затем GREEN. Reviewer заново выполнил полный локальный discover: **37/37 PASS, 6.835 s, 0 skips**, и pinned JavaCore main: **PASS**. Новые regressions проверяют требуемый отказ и отсутствие completed output/receipt, а не только наличие новой функции. `git diff --check` прошёл; предупреждение Git о будущем LF→CRLF не является failure.

Fresh **golden4** выполнен root с исправленным source; reviewer непосредственно проверил итоговые файлы, пять hashes обоих fresh outputs и записи отрицательных запусков. Результат: first 45.093 s, second 51.610 s; все пять deterministic data hashes совпадают друг с другом и с golden3. Counts сохранились: states 32178/events 11341/gaps 3221. Cache 1.704 s, `cache_hit`; final checker подтвердил сохранение всех existing output bytes. Wrong match/account: 3/3; truncated: 2; все три completed output directories отсутствуют. `golden4/golden-check.json` содержит завершённый scoped PASS, а `review-20261015/golden4-artifact-check.json` — независимую проверку данных. Последние проверки выполнялись после завершения всех golden4 subprocesses.

Receipt/cache key сменились из-за source provenance; сами deterministic data outputs остались прежними. Scope flags по-прежнему false. Reviewer не повторял full catalog и не запускал Dota/сеть/download. Actual pause, другие patch/schema, fog/identity semantics в native игре, heldout fidelity, права и продуктовая приёмка остаются за границами этого technical verdict. Elapsed total/token usage/cost не доступны и остаются null.
