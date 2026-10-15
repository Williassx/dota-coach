# Реализованный локальный импорт DEM v1

15 октября 2026. C1-05-03; ведущие роли105/102, основной исполнитель последовательно выполнил [согласованный план](../../telemetry-import-implementation-plan.md). Независимый исследователь проверил APIs вложенных полей; итоговый C2 reviewer рассматривает завершённый подпроект отдельно. [Использование и локальная сборка](../../notes/dem-import-usage.md), [измерения/хэши](receipt.json).

## Что работает

Постоянный Python CLI проверяет plainDEM, match/account, локальные8JAR/Temurin, исходники/classfiles/схему/config; запускает один Java extractor; проверяетEOF, exitcode, JSONL, identity, clocks, counts и hashes; публикует completedreceipt через Windows no-replace. Existing output принимается только как полностью совпадающий проверенный кэш, без повторного запускаJava. Неудачные/незавершённые stages сохраняются отдельно и не становятся completed output.

Java использует actual PlayerResource paths и полную ссылку героя сindex/serial. Slot0007,entity346,handle14926170 иrawID14 не являются константами алгоритма. Root identity/account/heroClass discovery общий, но schema v1 измерена только для одного match/Storm: другой actor/class/patch может быть неподдержан. Поля type/decoder/nullable declared serializer params фиксируются вместе сJARhash; это не заявление о доступе кprivate adjusted quantizer coefficients.

Наблюдаемые состояния, именованные события-кандидаты, пропуски и индекс сохраняются раздельно. Полные ground-truth enemy dumps/chat не публикуются. CombatLog имени недостаточно дляstableentityidentity: все11341records имеютcandidate_name_only. `replay_gate` не принимает этиstates и не превращает их ввыдуманныеactions/intent. uint64 сохраняется строками, rawcontrol/lifestate не превращены вsemanticbits.

## Фактическая приёмка

Final golden3 — два freshoutput импорта exactDEM SHA `3d647fb889e058534e85a759e405b9afad6a68878cfa20dae016c39c38234330`, match9042986015/account70388657:

| Проверка | Результат |
|---|---|
| Два импорта |48.375s и46.766s; одинаковые hashes всех5dataoutputs|
| Кэш |1.343s, statuscache_hit, всеbytes существующегоoutput сохранены|
| State/packet |32178actorstates,34051real callbacks,34050synthetic исключены,1873unassigned|
| Events/gaps |11341name-candidateevents;3221rawgaprecords (unassigned иunknownclock)|
| Compactindex/windows |3549entries,335records в4запрошенныхwindows, overlap бездубликатов|
| Nativepoints |21212/41706/45846: HP/mana/maxima within1HUDunit, clockfloor согласуется|
| Неверные IDs |actual CLI wrongmatch/wrongaccount exit3, безcompletedoutput|
| ОбрезанныйDEM |actual CLI exit2, безcompletedoutput|
| Несовместимая схема |изменённое decoder expectation далоactual extractor exit2/noEOFsummary|
| Локальные checks |30Pythonchecks (26новых+4existing), JavaCore assertion main PASS|
| Общий каталог |89suites/1417passed/28skipped/0error suites;6incomplete, strictverified=false|

Времена — отдельные локальные прогоны, без SLA или обещания скорости на других машинах. Во время приёмки были дополнительные прогоны после исправления Pythonstore; их артефакты сохранены. Final runtime interval берётся из `Context.getMillisPerTick()` и записывается вclock; малое отличие от исторической exact1/30 аппроксимации не подгонялось подHUD.

Три nativepoint — ограниченная проверка конкретных полей/DEM/build25894101, не fullpayload/nativefidelity. Старые prior1tick иclock7:25negativecases остаются в[report03](../03-native-tick-calibration/result.md). Source/cfghash входят вcachekey; изменениеorchestrator/Java/schema invalidatesoldcache.

## Отрицательные тесты и исправления

Tests наблюдались RED→GREEN: missing modules/Core; truncated/invalid inputs/JAR/JSON; indexreuse/ambiguous/knownillusion/seek; synthetic clockpause; EOF+exit failure; timeout/output/stderr/line limits; concurrentwriters; actual Windowsjunction иno-replace; tamperedcache/counts/EOF; incorrectactor/nonfinitevalues; overlap/streaming input. Fixtures процессов явноPython-emitterfake, неDota. JavaCore pause testsynthetic; реального pause вэтомматче не было.

Дополнительные REDtests закрыли receipt/diagnostic budget, метаданные cache и Javaenvironment inheritance. Дочернему процессу не передаются JAVA_TOOL_OPTIONS/JDK_JAVA_OPTIONS/_JAVA_OPTIONS/CLASSPATH. Это контролируемая childenvironment, не доказательствоOSnetworkisolation. Receipt digest защищает отнесогласованного измененияметаданных, не является signature/authentication.

Первый общий каталог безнаследуемогоUTF8/optionalLua ивпесочнице дал4error suites/82skip, включаяcp1251decode иownprocess-tree failures. Он сохранён какnegative setup run. Повтор сprocess-localPYTHONUTF8/PYTHONPATH existingLua иразрешённым запускомвнепесочницы:0errors,28skip,6incomplete. Privilege/path/FIFO пропуски не превращены вPASS, policy/OS не изменены.

## Границы

Пока открыты: actual pause/death/replacement/illusion lifecycle всехреальныхматчей, другиеschema/patch, мировые координаты, causal control/стратегическое качество решений, fog/playerknowledge, обучение/heldoutfidelity, права, runtime5×5 ипродуктовая приёмка. Actualреплей уже исследован и не является untouchedtestset. Model/perception export отсутствует; model_trained/player_fidelity_verified/native_verified=false.

RawDEM/JDK/JAR/classfiles/localconfig/fullJSONL иlogs остаются ignoredbuild. Исходники вбиблиотекеC1, игровыхHUD/аддон/OSsettings не менялись. Новые progresscheckbox не засчитывались. Независимая итоговая оценка: [technical-review.md](technical-review.md).
