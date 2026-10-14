# Локальный parser spike: первичный аудит 14 октября 2026

Автор: независимый аналитик библиотеки создателя 1, роли 40/105. Область: read-only источники/API; clone/install/build/local dem parsing этим аналитиком не выполнялись. Корневой исполнитель владеет кодом и запуском. Прочитаны проектные legal plan/initial review; лицензия parser не означает права Valve/игрока или разрешение выпуска.

## Рабочий путь сегодня

Использовать небольшой отдельный collector для Java 21+ с **`com.skadistats:clarity:5.0.1`**, без полного сервиса OpenDota. [Официальный README](https://github.com/skadistats/clarity/tree/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa) и [build](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/build.gradle.kts) подтверждают Java 21 и эту версию. Core commit `bd37eab0a572cd963dcfeaeaf9afb195f12c43aa`; examples commit `fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0`.

[Published Maven metadata](https://repo1.maven.org/maven2/com/skadistats/clarity/maven-metadata.xml) фактически HTTP 200, содержит 5.0.1; [POM 5.0.1](https://repo1.maven.org/maven2/com/skadistats/clarity/5.0.1/clarity-5.0.1.pom) HTTP 200. [Jar 5.0.1](https://repo1.maven.org/maven2/com/skadistats/clarity/5.0.1/clarity-5.0.1.jar) HEAD 200, Content-Length 666198; полный jar этим аналитиком не загружался/нехэшировался.

POM содержит **динамический диапазон** `clarity-protobuf:[7.0,8.0-SNAPSHOT)`, snappy-java1.1.10.7 и slf4j-api2.0.17. Для воспроизводимости pin только Clarity недостаточен: отдельно зафиксировать фактически разрешённый protobuf. [protobuf Maven metadata](https://repo1.maven.org/maven2/com/skadistats/clarity-protobuf/maven-metadata.xml) сейчас публикует 7.1; [POM 7.1](https://repo1.maven.org/maven2/com/skadistats/clarity-protobuf/7.1/clarity-protobuf-7.1.pom) получен и содержит также transitive dependency `it.unimi.dsi:fastutil-core:8.5.12`. Сохранить полный resolved graph и jar hashes при установке основным исполнителем; отсутствующие binary hashes не придумывать.

Самый короткий build path: зависимость Clarity 5.0.1 + explicit protobuf pin в отдельном collector на Gradle/Maven, Java 21, `MappedFileSource`→`SimpleRunner.runWith(collector)`. [Examples build](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/build.gradle.kts) использует Clarity как API и как annotationProcessor. При сборке/shading сохранить `META-INF/clarity/providers.txt`; это отражено и в [odota POM](https://github.com/odota/parser/blob/5934586999f8799e4ea1ffa6b3773028b26df5bf/pom.xml). Build approach проверен по исходникам, не заявляется уже собранным.

## Точные primary API и ограничения

| Требование | Фактически прочитанный первичный пример/API | Что проверить на нашем dem |
|---|---|---|
| Tick/state sampling | [tick/Main.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/tick/Main.java): `@OnTickStart/@OnTickEnd(Context, boolean synthetic)`, `Context.getTick()` | Synthetic tick означает промежуток без replay data; не выдавать interpolated state за новый packet |
| Dynamic properties | [Entity.java](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/model/Entity.java): `hasProperty`, `getFieldPathForName`, `getPropertyForFieldPath` | Отсутствующий FieldPath → null/incomplete. `getProperty` missing field throws; не подставлять0 |
| Hero mapping/position | [position/Main.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/position/Main.java): `m_vecPlayerTeamData.<four-digit-index>.m_hSelectedHero`, `Entities.getByHandle`, deferred assignment в TickEnd; CBodyComponentcell/vec | Entity handle включает serial; entity index не является stable identity. После create/update/replacement проверять полный handle и привязку 70388657 |
| Mana | [dumpmana/Main.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/dumpmana/Main.java): `m_flMana`, `m_flMaxMana`, созданное Entity + changedFieldPaths | Сначала проверить наличие property paths в конкретном patch; реальные float values, unknown при неуспехе |
| HP | Тот же Entity API позволяет читать поля с проверкой наличия; отдельный HP collector здесь не проверен | `m_iHealth/m_iMaxHealth` только кандидаты для обнаружения, не утверждение их наличия или семантики. Подтвердить class/type и HUD |
| Alive/death | [propertychange/Main.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/propertychange/Main.java): `@OnEntityPropertyChanged(classPattern,propertyPattern)` с `m_lifeState` | Записать raw enum; meaning сопоставить с подтверждённой смертью, без default alive |
| Control/modifiers | [modifiers/Main.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/modifiers/Main.java): `@OnModifierTableEntry(CDOTAModifierBuffTableEntry)` из ActiveModifiers | Callback может дать incomplete message. Наличие modifier не подтверждает stun/root duration без owner/start/end/state proof; это не input orders |
| Ability state | [cooldowns/Cooldowns.java](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/examples/src/main/java/skadistats/clarity/examples/cooldowns/Cooldowns.java): `m_fCooldown`, owner `m_hOwnerEntity`→getByHandle | Cooldown end/change не означает full cast intent или successful effect. Пример использует старое GameTime field; его отсутствие в новом patch требует fallback |

Пример position собирает мировую координату по оси как cell × 128 + vec. Формат проверен по исходнику примера; его наличие и точность для dem 9042986015 должен доказать actual probe. Принимать только entity реального владельца; illusion, replacement и respawn не отождествлять по имени героя.

## Game clock: не constant offset из длительностей

[odota Parse.java](https://github.com/odota/parser/blob/5934586999f8799e4ea1ffa6b3773028b26df5bf/src/main/java/opendota/Parse.java) реально прочитан: tick-derived time корректируется `m_nPauseStartTick/m_nTotalPausedTicks/m_bGamePaused`, `m_flGameStartTime` читается из GameRules proxy, затем output() вычитает gameStartTime. Старый `m_fGameTime` — optional route. Runner tick и serverTick не объявлять тождественными без message proof.

Для нашего матча получить фактические GameRules fields и server tick/clock anchor, затем сверить clock, HP и mana с подтверждёнными native кадрами. Разность header 2270 sec − API duration 1910 sec = 360 sec — **непроверенный offset**. Сохранять raw ticks, raw clock fields, parsed clock и calibration status отдельно. API match field version=22 не устанавливает точную deployed OpenDota parser revision.

OpenDota alternative pinnedcommit `5934586999f8799e4ea1ffa6b3773028b26df5bf`: готовый combat/event extractor, но больше сервисных зависимостей; не нужен как первый bounded HP/mana/position probe. Его[repository](https://github.com/odota/parser/tree/5934586999f8799e4ea1ffa6b3773028b26df5bf) и POM прочитаны; он не объявляется установленным.

## Лицензия и reproducibility

Прочитанные [Clarity LICENSE](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/LICENSE), [examples LICENSE](https://github.com/skadistats/clarity-examples/blob/fd82493d9c278a48ea9b3bb572caeb93ee5ccfd0/LICENSE) и [protobuf LICENSE](https://github.com/skadistats/clarity-protobuf/blob/master/LICENSE) — тексты BSD 3-clause: при source/binary redistribution сохраняются copyright, conditions и disclaimer; endorsement именем автора требует отдельного письменного основания. Полный аудит лицензий всех transitive jars пока не выполнен. Это technical dependency review, не разрешение Valve или использования образа Dendi.

Фактически полученные источники (SHA-256; bytes):

- Clarity POM 5.0.1: `f0241239b1e7352ace3004a5a4b8ef1b766c93f742cf17a03f12ef54fc348489`;2109.
- Maven Clarity metadata: `505e53704a225a0e758e057d254ec0fd6ab1643448a8ec74ab65f454c11d235d`;1579.
- protobuf metadata: `9a6844640e07dd2cb413eda019ad036aa33f5c5205fc8e577d49f2d29bcd9a45`;1625.
- protobufPOM 7.1: `0541af1cc742b27d67ae603b5e418bc97e33871b310414361e79502a4ee1a1f4`;1842.
- Clarity build: `f5d2de9575094cc19bec05ed1c7a4300c9b5bff295e464adef119f8d28ca9361`;10046.
- Examples position: `102926b548dafbf9b86a4522f68d28a9f703f55874d744cc9cbcce7373bf4a57`;10381.
- Examples dumpmana: `4e4e52f788176b1d70de2494c56e0c3358fca9a58d5943e44ec81fe4db2145d7`;3749.
- Examples tick: `cfdaad9d4f2d6a621c8d3d28b8117bb5c1afb0a73f41db6203191870d6f46e6b`;4316.
- Examples modifiers: `4242bd4a6e2b13451705235649c60e5f0bdf76382e9933c81958e50664803ada`;2174.
- odota Parse: `406d0b6bae12812c4103b533375f206ee5f93f61ca3249ddabcacb34225139d1`;55531.
- Clarity LICENSE / protobuf LICENSE: `069d82574a725bc5b6171478727a399af77ac1a4c84ec91284e7a9898320c9e0`;1504.
- Examples LICENSE: `4e9bb1ea77b8b36ec6a5499bf151d65019dab18981a0cc95a61592fac66fcd03`;1504.

Актуальность: public GitHub commit API и HTTPS source/POM/metadata получены 14 октября 2026; финальная проверка Maven jar HEAD/metadata — 16:52:00 UTC. Repo.maven.apache.org отказал по TLS (CERTIFICATE_VERIFY_FAILED, certificate expired); fallback repo1.maven.org с обычной проверкой TLS успешен. TLS не отключался, сторонний mirror не применялся.

Критерийspike: реальныеdecodedrecords+matchingheroidentity+доказанныйclock/fields/missing fields, boundedlogs иявныеlimitations. Не обучающаямодель, не fog-authorizedнаблюдения и неполныйпрофильличности.


## Узкая проверка расхождения m_iPlayerID: run-1

Дата проверки: 2026-10-14T17:12:54.586799+00:00. Фактически перечитан ignored dump `telemetry-spike/run-1/CDOTA_Unit_Hero_StormSpirit-346-911-tick3750.txt`: 45144 байта, SHA-256 `a7c6bcd598fad02876a935031856f5745f83bbf646705f91bb6ff804e87443d7`. В нём hero raw `m_iPlayerID=14`, team 3, HP 670, mana 399.00037. Предоставленный основной пробой independent путь identity — PlayerResource SteamID64 76561198030654385 (account_id 70388657) → selected hero handle 14926170, entity 346/serial 911 — используется для выбора игрока. Dump player ID14 не меняет эту привязку автоматически.

### Что показывает primary source

На pinned Clarity commit `bd37eab0a572cd963dcfeaeaf9afb195f12c43aa` [S2DecoderFactory.java](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/io/s2/S2DecoderFactory.java) выбирает signed decoder для int8/int16/int32/int64; неизвестный type получает default unsigned varint decoder. В списке есть HeroID_t со signed decoder, но **PlayerID_t отдельно не перечислен**. Это возможность, а не доказательство типа конкретного поля в нашем replay.

[FieldGenerator.java](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/processor/sendtables/FieldGenerator.java) передаёт base type и serializer properties в factory. [IntVarSignedDecoder](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/io/decoder/IntVarSignedDecoder.java) читает readVarSInt, [unsigned decoder](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/io/decoder/IntVarUnsignedDecoder.java) — readVarUInt. В [BitStream.java](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/io/bitstream/BitStream.java) signed reading применяет ZigZag преобразование. Поэтому raw unsigned14 мог бы соответствовать signed7, **если** именно это поле имеет signed wire encoding и попало в unsigned fallback. Одна арифметика14=2×7 этого не доказывает.

[Исторический issue194](https://github.com/skadistats/clarity/issues/194) показывает, что ошибки entity decoding ранее действительно давали неверные player IDs; maintainer тогда исправил Vector4D. [Issue283](https://github.com/skadistats/clarity/issues/283) содержит сообщение о переходе CDOTAPlayer→CDOTAPlayerController и m_iPlayerID→m_nPlayerID. Эти старые обсуждения не устанавливают причину нынешнего значения14 и не заменяют actual schema.

### Минимальная проверка перед любым исправлением

1. Зафиксировать на actual hero поле полный FieldPath, serializer ID/version, **field.getType()**, serializer encoder и выбранный decoder class. Проверенные APIs: [S2DTClass.getSerializer()](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/model/s2/S2DTClass.java), [Serializer.getFieldIndex/getField](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/model/s2/Serializer.java), [Field.getType/getDecoder/getSerializerProperties](https://github.com/skadistats/clarity/blob/bd37eab0a572cd963dcfeaeaf9afb195f12c43aa/src/main/java/skadistats/clarity/model/s2/Field.java). Если имя отсутствует в root serializer, исследовать фактическую вложенность; не подставлять предполагаемый индекс.
2. Сопоставить raw IDs всех десяти selected hero handles с PlayerResource slots и отдельным owner/controller field, при его наличии. Записать missing/illusion/replacement отдельно. Систематический doubled pattern усиливает гипотезу, но ещё не доказывает bug.
3. На отдельном known-byte fixture сравнить official signed/unsigned decoders: byte0x0e соответствует unsigned14 и ZigZag signed7; byte0x01 — unsigned1 и signed−1. Это подтверждает decoder семантику; отдельно требуется доказать реальный type/encoder поля и правильность wire bytes нашего replay.
4. Только после actual schema/wire подтверждения допустим узкий fix или quarantined interpretation с regression fixture. **Не делить все player IDs на2**, не патчить общий int decoder и не считать raw14 новым player slot.
5. До разрешения расхождения identity сохраняется по SteamID→selected full handle. m_iPlayerID остаётся raw diagnostic unknown-domain. Если обнаружится более общая ошибка декодирования, остальные поля тоже требуют cross-check, а не доверия только потому, что parser завершился без исключения.

Дополнительные source bytes/SHA: S2DecoderFactory4978/`6444252a41b77156d0053cae396d9ae0120d3055407d281f95b950864fea232f`; IntVarSigned637/`688a4d5d3cadea65ae39643fa4e6b00c22a1e0d1a2f952f3b954e88d225917db`; IntVarUnsigned639/`2811a3db49e440ae4c484572920e5d196e166e87ce20740233a0d0de1bc1cad5`; BitStream13649/`b053165feb9901f571f3a35779d0e295ee6eb36a76e2352c6facc1c3f61a5106`; FieldGenerator10218/`aa64a72b3792fd07155463bc6d2ef0c80b992d575073c20ae830a56591c5ac49`. Источники реально получены public HTTPS; этой проверкой runtime код, зависимости и Dota не изменялись.
