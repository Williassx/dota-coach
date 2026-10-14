# Нативная калибровка телеметрии 9042986015

14 октября 2026. Ведущий C2: роли40/70/132, диспетчер173; независимый аналитик C1 сверяет кадры, отдельный C2 reviewer проверяет завершённый результат. Исследование внутри C1-05-03; постоянный импортёр и обучение не реализованы.

## Подтверждённый результат

В собственном Dota Tools viewer build25894101 получены11actual game-only PNG1280×720:5pilot и6batch. Каждый PNG имеет SHA256 и console receipts чтения текущего `demo_goto` до/после экспорта; запрос перемотки не принимается за фактический tick. Источник — тот же verified DEM с SHA256 `3d647fb889e058534e85a759e405b9afad6a68878cfa20dae016c39c38234330`.

Три положительных кадра имеют одинаковый текущий tick до/после и существующую real packet запись CSV ровно на нём. Часы согласуются до отображаемой секунды; ресурсы — в пределах одной единицы целочисленного HUD. Это ограниченная калибровка одного реплея, не общая совместимость парсера.

| Кадр | Actual demo tick | HUD | HP / max | Mana / max |
|---|---:|---|---|---|
| normal |21212|8:12|71 /956|62 /651|
| batch3 |41706|19:35|1215 /1308|734 /1376|
| batch4 |45846|21:53|782 /1528|1335 /1376|

На кадрах выбран Storm Spirit, POV подписан `v o i d`. Identity определяется отдельно по PlayerResource Steam binding полного hero handle; подпись и класс сами по себе не подтверждают владельца. Raw uint64 state не получает семантику по надписи «ОГЛУШЕНИЕ». Подробная независимая сверка: [observations](observations.md), [машинные записи](observations.json).

## Отрицательные и ограниченные случаи

- pilot21207→21208 и slow21190→21191: cursor двигался, exact capture tick не принят.
- fixed21190→21190: HP66/956 и mana57/651 согласуются с CSV, но HUD7:25 расходится с decoded491.633s (8:11). Неподвижного cursor и совпадения ресурсов недостаточно для полной калибровки.
- paused21243→21243: отдельный остановленный cursor, без exact real packet строки; не добавляется к трём положительным.
- batch0/1/2/5: unchanged cursor21113/21223/34359/52485, последний real packet соответственно21112/21222/34358/52484. Разрыв один tick явно сохранён; предыдущая запись не объявлена точной записью текущего tick и не интерполирована. HUD8:09/8:12/15:30/25:34 согласуется с этим ограниченным сопоставлением. Старый эпизод25:34 получил новое bounded подтверждение, а не задним числом точный tick старого PNG.

Положительный normal получен после свежего `playdemo`, возврата обычной скорости, перемотки и явного `demo_pause`. Состояние HUD после низкой скорости и spectator pause было некорректным; причина не изолирована. Не утверждаем, что именно rate, pause API или reload устранили её. Physical input не контролировался, tick interval/pause model/rounding не доказаны для всех режимов.

## Метод и происхождение

Raw остаются local ignored в `build/dota_coach/replay-9042986015/native-calibration/`: `pilot-manifest.json`, `batch/frames.json`,11PNG, capture/readback/restore/quit receipts. Temporary script `native-calibration/capture-batch.py` не является продуктовым инструментом. Матрица [evidence.json](evidence.json) фиксирует hashes и этапы проверки. Полный CSV берётся из предыдущего [spike](../02-local-dem-telemetry/result.md), не из OCR.

Tools screenshot export требовал временного `cl_playback_screenshots=true`; fullscreen focus loss0 и POV3 использованы только для capture. Перед завершением восстановлены readbackfalse/1/mode0; `demo_timescale1` отправлен без value readback. Quit выполнен только для собственного PID32720 после exact start UTC ticks guard и проверки пути текущего replay. Первое немедленное cleanup чтение ещё видело процесс; последующее подтверждает gone, Steam13704 сохранён. Разрешение одного desktop probe использовано ранее; повторного desktop capture нет.

## Границы следующего шага

[Спецификация импортёра](../../telemetry-import-design.md) остаётся DRAFT для рассмотрения. Persistent source/CLI, implementation-plan, native schema coverage других матчей, реальные паузы, world transform, fog/доступные игроку сведения и отложенная проверка сходства Dendi открыты. Checklist не повышен, runtime игры не менялся.
