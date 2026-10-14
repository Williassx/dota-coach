# Независимые случаи проверки decoded telemetry ↔ HUD

14 октября 2026. C2 — проектирование проверки; C1/root — автор локального DEM spike и его output. Область этого документа: ограниченная техническая воспроизводимость, без установки парсера, управления Dota, обучения модели или вывода о персональном сходстве.

Основание: [root-evidence.json](../reports/01-match-9042986015/root-evidence.json), матч **9042986015**, account **70388657**, Storm Spirit **hero_id 17**. Шесть указанных ниже PNG независимо сверены по SHA256; полноразмерно просмотрены close samples 8, 11, 14. Остальные числовые значения взяты из явно указанного root visual record, а не названы новым самостоятельным просмотром. Source/parser schema и clock mapping нового spike ещё не приняты.

## Опорные кадры

| Запись | Фактический HUD | HP/max HP | Mana/max mana | Видимое состояние |
|---|---|---:|---:|---|
| episode-samples-r4/4 | 08:08 | 88/956 | 205/651 | Actor жив; KDA 2/0/1 |
| episode-samples-r4/5 | 08:11 | 66/956 | 57/651 | Отображаемая стоимость Ball Lightning 73; доступность команды этим не доказана |
| episode-samples-r4/8 | 15:30 | 947/1220 | 915/1148 | Над Storm подпись «ПРИВЯЗКА» |
| episode-samples-r4/11 | 19:35 | 1217/1308 | 736/1376 | Над Storm подпись «ОГЛУШЕНИЕ» |
| episode-samples-r4/14 | 21:53 | 786/1528 | 1337/1376 | Над Storm подпись «ОГЛУШЕНИЕ» |
| episode-confirm-r4/0 | 08:16 | 0/956 | Не прочитано в root record | Death summary, respawn 25, KDA 2/1/1 |

«ПРИВЯЗКА» сохраняется буквальным caption. **Не переименовывать его в rooted=true:** root, leash и иные ограничения могут быть различными состояниями. Нужны отдельные raw fields и подтверждённое mapping для применимой версии. «ОГЛУШЕНИЕ» — визуальный положительный случай для проверки decoded stun; само название поля/бит ещё не подтверждены.

## Clock и числовые допуски

1. Сохранить отдельно replay tick, tick interval/источник, engine game time, match-start epoch, API game time и capture UTC. Epoch выводить из документированного поля/события, не подгонять по смертям, HP или желаемому совпадению. Для integer HUD clock записать правило отображения; пока оно неизвестно, окно кандидатов [t−1, t+1] с — только поиск соответствия, не доказательство exact alignment.
2. Сохранять запрос seek и фактический HUD clock отдельно. Известное отличие примерно +4 с не превращать в универсальную поправку; оно не является clock mapping. UI 1x/8x, wall-time interval и порядковый номер кадра не заменяют game time.
3. Для совпадающего decoded tick и кадра current HP/mana: допустимо не более **1 единицы** из-за целочисленного отображения, с явно указанным rounding/truncation rule. Max HP/max mana: ожидать точное совпадение целых показанных значений; альтернативный допуск требует заранее документированного преобразования. Не использовать проценты или широкие допуски для сокрытия mismatch.
4. Для кадра с неизвестным subsecond tick не выбирать удобный tick только по совпадению ресурсов. Вывести **все** кандидаты в clock window и диапазон значений. При стабильном интервале можно заявить интервальную совместимость. Во время удара/cast/resource change секундная сетка обычно не позволяет доказать exact correspondence: статус unresolved, а не PASS или nearest-value match.
5. Если есть подтверждённая regen и измеренная погрешность времени Δt, отдельный анализ возможен с bound `1 + abs(regen) * Δt`; это не покрывает неизвестные повреждения/касты/изменение максимума. При discontinuity требует tick/event sequence. Regen не выдумывается из одной картинки.
6. При replay seek/restart создать новый playback epoch; старые entity handles и cursor checkpoints не переносить. Внутри эпохи game time/ticks упорядочены по подтверждённому правилу. В паузе wall/network ticks могут идти иначе, чем game time: не смешивать эти часы. Проверка freeze делается только при настоящем pause evidence; API pauses=[] здесь не создаёт положительный pause test.

## Случаи приёмки

| ID | Проверка | Условие технического PASS / отказа |
|---|---|---|
| T01 | Provenance и воспроизводимость | DEM SHA256/bytes, parser executable/package version или commit, dependency версии и output schema записаны; повторный extract тех же полей/интервала даёт одинаковые значения после исключения объявленных технических timestamps. Никаких invented parser version. |
| T02 | Match/actor | Выход match_id 9042986015; player-resource account 70388657 связан с assigned hero Storm/17 и Dire. Persona `v o i d` сама по себе недостаточна. Описать преобразование Steam identifiers, если оно нужно, по действительному входному типу. Несовпадение — отказ, не fallback на слот7. |
| T03 | Entity lifecycle | Хранить entity identity/index **и serial/generation**, class и owner mapping. При deletion/replacement старый handle истекает; reuse index с другим serial не наследует actor state. При seek проверить восстановление заново. Кодирование handle/маски не угадывать. |
| T04 | Illusion / clone / summon | Одинаковых account/hero class недостаточно. Actual assigned hero связывается через подтверждённый player-resource/entity reference и признаки illusion/clone по schema. Иллюзия того же игрока не замещает HP/mana настоящего героя; при неоднозначности actor unresolved. |
| T05 | Clock | Epoch и conversion установлены независимо от golden resource values; сохранены raw tick/game_time и HUD clock. До этого ресурсы/состояния отмечаются interval-only или unresolved. API last time 31:50 и HUD 31:45 не исправляются подгонкой. |
| T06 | 08:08 → 08:11 | Сверить HP 88→66, mana 205→57, maxima 956/651 по правильному actor и времени. Dynamic max HP между другими эпизодами может меняться: не фиксировать956 на весь матч. Output не округляет, не backfill и не копирует HUD вручную. |
| T07 | Death | 08:16 — HP0 + death summary; decoded life state/death flag сравнивается с sourced enum semantics. Positive alive 08:08 и dead 08:16 различимы. Сам по себе HP0, запись killed_by или API life_state dictionary не доказывает значение engine bit. Missing property ≠ alive. |
| T08 | «ПРИВЯЗКА» 15:30 | Сверить947/1220 и915/1148; сохранить raw control field(s), enum/mask definition и caption. rooted/leashed выводятся раздельно только после source/schema proof. Строка caption не автоматически ground truth для rooted enum. |
| T09 | Stun 19:35 / 21:53 | Сверить actor привязку и ресурсы1217/1308,736/1376 и786/1528,1337/1376. Проверить raw stun field/бит по документированному mapping. Отдельные положительные кадры не измеряют длительность stun или latency. |
| T10 | False positives / неизвестное | Соседний герой с надписью stun не делает Storm stunned. Missing/unsupported bool/enum даёт unknown, а не false; неизвестные enum значения сохраняются. Негативный случай требует подтверждённого actor state, отсутствие подписи на одном кадре недостаточно. |
| T11 | Sampling и переходы | Вывести sample interval, clock uncertainty и пропуски. Проверить состояние до/после смерти без interpolation через death, pause, entity recreation, discontinuity. Общий факт transition может быть принят без заявления exact timestamp. |
| T12 | Knowledge и применение | Omniscient DEM telemetry — ground-truth исследовательский канал, не доступное игроку знание. Enemy state, camera и future outcomes помечены отдельно; неизвестный fog не проходит в perception/model input как visible. Заключение о возможности cast/escape не следует только из HP/mana/control. |

## Что считается завершённым spike

Получены provenance, корректная actor identity, clock mapping и несколько воспроизводимых извлечений resources с объявленным уровнем совпадения. State fields могут остаться unsupported/unknown: это честная частичная feasibility, не приёмка death/stun/root. Сводка показывает каждый случай PASS / FAIL / UNRESOLVED / NOT RUN и причину. Значения и допуски не меняются после просмотра output без новой ревизии протокола и сохранения исходного mismatch.

Отдельно остаются полный parser compatibility для патча/сборки, observation authorization/fog, все эпизоды матча, train/validation/test разбиение и проверка персональной модели на отложенных матчах. Этот матч уже исследуется и не является нетронутым final test. Здесь ни одного такого результата не заявлено.
