# Независимая сверка native HUD и tick: 9042986015

Дата: 14 октября 2026. Создатель 1. Аналитик клиентом Dota не управлял. Проверены **5 pilot и 6 batch PNG**, их SHA-256/размеры, actual before/after console receipts и соответствующие строки `telemetry-spike/run-3/storm-telemetry.csv`. Изображения имеют 1280×720; clock/resources/camera caption прочитаны вручную из диагностических crops исходных PNG.

**Три точки совпадают со строкой CSV ровно на стабильном native tick:** normal 21212, batch-3 41706, batch-4 45846. Это подтверждает выбранные HUD-поля и показанные часы в этих точках, не весь payload или точность полного матча.

| Точка | Часы HUD | Native tick before→after | CSV tick | HP/max | Mana/max | Статус |
|---|---|---|---|---|---|---|
| pilot | 8:12 | 21207→21208 | 21206 | 70/956 | 61/651 | moving_cursor_not_exact |
| paused | 8:13 | 21243→21243 | 21242 | 0/956 | 66/651 | bounded_previous_csv_tick_consistent |
| fixed | 7:25 | 21190→21190 | 21190 | 66/956 | 57/651 | clock_mismatch_resources_consistent |
| slow | 7:25 | 21190→21191 | 21190 | 66/956 | 57/651 | clock_mismatch_resources_consistent |
| normal | 8:12 | 21212→21212 | 21212 | 71/956 | 62/651 | exact_csv_tick_fields_consistent |
| batch-0 | 8:09 | 21113→21113 | 21112 | 94/956 | 208/651 | bounded_previous_csv_tick_consistent |
| batch-1 | 8:12 | 21223→21223 | 21222 | 72/956 | 64/651 | bounded_previous_csv_tick_consistent |
| batch-2 | 15:30 | 34359→34359 | 34358 | 945/1220 | 914/1148 | bounded_previous_csv_tick_consistent |
| batch-3 | 19:35 | 41706→41706 | 41706 | 1215/1308 | 734/1376 | exact_csv_tick_fields_consistent |
| batch-4 | 21:53 | 45846→45846 | 45846 | 782/1528 | 1335/1376 | exact_csv_tick_fields_consistent |
| batch-5 | 25:34 | 52485→52485 | 52484 | 324/1660 | 846/1484 | bounded_previous_csv_tick_consistent |

## Границы точности

- **exact_csv_tick_fields_consistent:** cursor неизменен, actual CSV row имеет тот же tick; HP/maxHP совпадают, mana/maxMana согласуются с целочисленной точностью HUD, clock равен целой секунде decoded game time.
- **bounded_previous_csv_tick_consistent:** cursor стабилен, но последний CSV tick на 1 меньше. Таковы paused и batch 0/1/2/5. Их нельзя объявлять проверкой exact payload на cursor tick.
- **moving_cursor_not_exact:** pilot 21207→21208 меняется во время захвата. HUD 8:12 и ресурсы согласуются с соседними строками, но одна точная привязка не доказана.
- **clock_mismatch_resources_consistent:** fixed и slow сохраняют отрицательный результат. Fixed cursor 21190→21190, actual CSV 491.633 сек≈8:11, а картинка показывает **7:25**. HP 66/956 иmana 57/651 совпадают. Slow cursor 21190→21191 имеет тот же mismatch. Причина не установлена; согласование ресурсов не позволяет засчитать часы.

В normal после fresh playdemo в том же собственном процессе PID 32720, нормальной скорости и pause часы8:12, HP71/956, mana62/651 согласуются с exact CSV tick21212. Эта последовательность наблюдений не доказывает, что конкретная настройка была единственной причиной восстановления clock.

Все 11 ресурсных сравнений согласуются в пределах отображаемой точности. Пример batch 2: HUD mana 914 против decoded 913.93835; batch 0: HUD 208 против 208.5627. Поэтому правило округления не объявляется одним постоянным floor/round. Maxima также проверены, а не только текущее HP/mana.

## Caption и неустановленные свойства

Pilot/paused показывают «АВТОМАТИЧЕСКАЯ КАМЕРА»; fixed/slow/normal и 6 batch — «ГЛАЗАМИ ИГРОКА v o i d». В paused HUD показывает сводку смерти и 28 секунд, HP 0; это наблюдаемый UI. Numeric life_state/unit_state остаются raw полями: полный enum mapping, control duration, соответствие POV fog, identity других сущностей и весь игровой мир не подтверждены этой сверкой.

Часы взяты с картинок, decoded game_seconds — из CSV; requested seek tick не используется вместо actual receipt. Raw cursor ticks, server ticks и game time сохраняются отдельно. Причинные выводы и полная fidelity матча не заявляются.

[Машиночитаемые наблюдения](observations.json) содержат hashes всех использованных кадров/inputs/receipts, HUDreadback, exact/prior tick, различия ресурсов и отрицательные результаты. Raw файлы и диагностические crops остаются в ignored build; чужие SteamID/сырой чат сюда не переносятся.
