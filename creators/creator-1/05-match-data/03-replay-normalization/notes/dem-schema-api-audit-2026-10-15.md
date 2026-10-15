# Аудит API схемы DEM importer — 15 октября 2026

Автор: независимый аналитик C1-05-03. Область: read-only исследование локальных pinned источников и `javap`; исходники импортера, tests и schema profile не изменялись. Dota, downloads и полный parse не запускались. Цель — поддержать Task2 из [implementation plan](../telemetry-import-implementation-plan.md).

## Подтверждённый короткий путь

**Перечислять существующие property paths через состояние entity; nested metadata разрешать через это же состояние.** Root serializer сам по себе не разрешает актуальный target динамического pointer или размеры vector.

| Задача | Точный API в pinned Clarity 5.0.1 |
|---|---|
| Перечисление actual paths | `Iterator<FieldPath> it = entity.getState().fieldPathIterator()` |
| Имя actual path | `entity.getNameForFieldPath(fp)`; результат может быть null |
| Значение с сохранением missing | `entity.getPropertyForFieldPath(fp)`; boxed Object/Number, затем null/type check |
| Поиск по имени | `entity.getFieldPathForName(name)`; null означает, что path не разрешён в текущем состоянии |
| Nested field metadata | `((S2EntityState) entity.getState()).getFieldForFieldPath((S2FieldPath) fp)` |
| Только тип nested field | `S2EntityState.getTypeForFieldPath(S2FieldPath)` |
| Leaf metadata | `Field.getType()`, `getDecoder()`, `getSerializerProperties()` |
| Root serializer identity | `S2DTClass.getSerializer().getId().getName()/getVersion()` |
| Разрешение hero reference | `Entities.getByHandle(int)`; сохранять полный handle и serial, не только index |

Сигнатуры EntityState, S2EntityState, SerializerProperties и FloatQuantizedDecoder дополнительно сверены `javap` из локального JDK21 против **binary** clarity5.0.1.jar. Неполная извлечённая папка `clarity-source/` дополнена чтением members локального source JAR в памяти; ничего не извлекалось и не скачивалось.

## Dynamic PlayerResource binding

Фактические имена в ранее сохранённом dump: `m_vecPlayerData.<index>.m_iPlayerSteamID`, `.m_bIsValid`, `.m_iPlayerTeam`; reference — `m_vecPlayerTeamData.<index>.m_hSelectedHero`. Для выбранного аккаунта ранее наблюдался index0007, но **это значение не является правилом импортера**.

Перечислить actual пути SteamID, извлечь существующий suffix/index, найти ровно соответствующее значение account/Steam ID, затем разрешить selectedHero path с тем же index. Проверить наличие и тип каждого значения и совпадение full handle с существующей entity. Отсутствие пути, неразрешённый handle, неоднозначная привязка и изменение index/serial остаются отдельными состояниями. Отложенная проверка на tick end нужна из-за порядка создания entity в packet; найденная reference не гарантирует, что target уже создан в callback.

`getFieldPathForName` в Source2 зависит от текущих vector sizes/pointer targets. Нельзя считать однажды найденный path вечным для всех поколений entity. Iterator также описывает актуальное состояние, а не все возможные поля всех будущих pointer variants. После lifecycle/serializer change повторно проверять необходимые пути; избегать неограниченного полного dump каждого тика.

## Стабильный fingerprint без object addresses

Сохранять именованные значения:

- dt class name, property name, field type и decoder class name;
- `FieldType.getBaseType()`, `getGenericType()`, `isPointer()`, `getElementCount()` при необходимости структурного type fingerprint; `FieldType.toString()` имеет собственную детерминированную реализацию, но раздельные поля проще проверять;
- `SerializerProperties.getEncodeFlags()` → nullable Integer;
- `getBitCount()` → nullable Integer;
- `getLowValue()/getHighValue()` → nullable Float;
- `getEncoderType()` → nullable String;
- `getPolymorphicTypes()` → упорядоченные `SerializerId.getName()/getVersion()`, сохраняя исходный порядок: positions могут иметь значение для type index;
- pin/hash Clarity, protobuf и schema/config вне значений самих runtime entities.

Не использовать `serializerProperties.toString()` или `decoder.toString()` как fingerprint: object identity/address не является параметром протокола. `Field.getDecoder()==null` допустим для некоторых non-leaf контейнеров; отсутствие decoder у **required value leaf** — отдельная проверка согласно плану, а не молчаливый default.

Nullable getters и `get…OrDefault` — разные сведения. Для declared schema сохранять null, не заменять нулём. Если используется отдельная effective-input запись, она должна явно отличаться от declared params. Ключи полей можно стабильно сортировать по полному имени, но не переупорядочивать polymorphic type mapping.

### Quantization: что доступно публично

`FloatDecoderFactory` сначала проверяет encoder `coord`; иначе bit count ≤0 или ≥32 ведёт к FloatNoScaleDecoder, а quantized branch создаёт FloatQuantizedDecoder с bit count, flags&0xF и defaults low0/high1. Это factory inputs, а не окончательные private working coefficients.

У **FloatQuantizedDecoder нет публичных getters** для внутренних adjusted bitCount/min/max/encodeFlags/multipliers. Constructor меняет рабочие параметры; поэтому raw SerializerProperties нельзя называть всеми окончательными quantization coefficients. Для v1 достаточно честно обозначить fingerprint как declared/post-field-generator serializer params + decoder class + pinned binary hash. Не использовать reflection на private fields или повторно реализовывать quantizer ради получения якобы тех же чисел. Наличие float decoder не доказывает соответствие HUD: это отдельная native calibration.

## Отсутствующие значения, uint64 и clock

Boxed чтение нужно не только ради удобства. В S2FlatEntityState primitive getInt/getLong/getFloat при отсутствующем значении, out-of-range vector или несовместимом primitive layout может дать0. Это уничтожает различие missing и реального нуля. Для critical fields сначала проверить actual field path, boxed value, Java type и decoder/schema, затем читать число. Missing optional → unknown reason; missing required → установленный планом отказ.

SteamID/reference/clock — разные domains. SteamID64 сравнивать и сериализовать без JavaScript Number/double; сохранять unsigned64 как canonical decimal string. Hero handle должен оставаться полным reference value; entity index и raw hero m_iPlayerID не заменяют его. Для unit_state64 применять тот же unsigned64 transport, не объявляя meanings enum bits.

Protobuf7.1 binary `CommonNetworkBaseTypes$CNETMsg_Tick` имеет **hasTick()/getTick()** (javap). Проверять hasTick до принятия default0. Context.getTick() — demo callback tick; network message tick хранить отдельно. Отсутствие clock anchor `m_flGameStartTime` нельзя маскировать вычислением по длительности файла. Из ранее исследованного матча доступны names GameRules `m_nTotalPausedTicks`, `m_nPauseStartTick`, `m_bGamePaused`, `m_flGameStartTime`; фактические leaf types/decoders/importer gate должен получить новым actual state metadata, не по названию поля.

Наличие активной/существующей entity и все перечисленные metadata не доказывают player fog-authorized knowledge. Экспорт остаётся offline spectator telemetry по согласованной спецификации.

## Воспроизводимость исследования

- `clarity-5.0.1-sources.jar`: 259064 bytes, SHA-256 `01b043a617745ba749dd792a5749b5a7e1b7831038de7581a162d637e11b6287`.
- `deps/clarity-5.0.1.jar`: 666198 bytes, SHA-256 `8d42d78f383b25bd23ed2d1f61d6efe06866b14f98e0a4852163022b44320bd9`.
- `deps/clarity-protobuf-7.1.jar`: 8884549 bytes, SHA-256 `7a17d3d97189482319a65337bf7e65ad3c2d8c6162d2c26115acb8419c497c8d`.

Локальные source members, фактически прочитанные (SHA-256):

- `skadistats/clarity/state/EntityState.java`: `d9fa353202230865c11012ef1feed4a8744df6a34ec26eed6c781b943c5891c5`.
- `skadistats/clarity/state/s2/S2EntityState.java`: `07880d926c3149f32a4b9dc01edd28fe7ccd7a44cee901cf1f1269d1cba9077b`.
- `skadistats/clarity/state/s2/S2FlatEntityState.java`: `235f6cfe992bb45254bc970643be206ef8d6963f8f467922e00a4b0fa31071e1`.
- `skadistats/clarity/model/Entity.java`: `0d0ff8e08e3d69a55de841c609db579170d47eec1b686361736d46c8ffbfe514`.
- `skadistats/clarity/model/s2/SerializerProperties.java`: `eb6b89011de63613cd04dfb65f0b592089a41afb6a61e964dbb8fa7d88396f05`.
- `skadistats/clarity/model/s2/Field.java`: `25d173a983d87f1624f186c076d8862a8da54d492d270a11db9c0df6000d5673`.
- `skadistats/clarity/model/s2/FieldType.java`: `3d452b03bb5f52012c456ec8913711bf7d471e61987bb3610aa4d4f686202a56`.
- `skadistats/clarity/model/s2/SerializerId.java`: `42714ad0f52ad51350f1661aee47ef500c5a8197cd637ce741e1c250312bdd65`.
- `skadistats/clarity/io/decoder/factory/s2/FloatDecoderFactory.java`: `832b22d4f988b5f4e215964fc243a95977f05d777894c96c6a802e90bc42d92e`.
- `skadistats/clarity/io/decoder/FloatQuantizedDecoder.java`: `a93f3e3c81e7542142c3d80c0ce383cceb7093bb3e07b576fce5061bf7aac04a`.

Primary provenance: source JAR Clarity5.0.1 и binary pins выше; предыдущее [исследование публичного API/лицензий](local-parser-audit-2026-10-14.md) содержит upstream commit/URLs. Эта заметка не означает successful importer run или приёмку Task2.
