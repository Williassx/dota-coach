# Независимый итоговый C2 review нативной tick-калибровки

14 октября 2026. Рассмотрен завершённый исследовательский подпроект: result.md, evidence.json, observations.md/json и соответствующие local raw источники. Reviewer не управлял Dota, не запускал parser/игру повторно, не менял общие файлы или runtime. Единственная запись — этот отчёт.

**P1/P2 замечаний не найдено в заявленной ограниченной калибровке.** Подтверждены три конкретные точки одного реплея и сохранённые отрицательные/ограниченные случаи; полная native fidelity или готовый импортёр не приняты.

## Прямые проверки

- Все11 PNG независимо перечитаны: bytes/SHA256 совпадают с observations, размеры1280×720. Все22 before/after receipts также совпали по bytes/SHA256; actual `Currently playing … of68100 ticks` соответствует записанным ticks и правильному пути `9042986015.verified.dem`.
- UTC экспорта каждого PNG находится между actual before/after query timestamps. Это подтверждение recorded bracket, не контроль всего физического ввода или доказательство каждого внутреннего renderer state.
- Independently rehash snapshot **101 declared artifacts**: drift0. Это датированный manifest указанных файлов, не claim полного множества последующих diagnostic crops/raw files.
- Verified DEM и CSV SHA256 совпали с evidence. Все11 observation decoded field sets найдены в actual `run-3/storm-telemetry.csv` и совпали буквально. Native request tick не использован вместо readback; CSV не создан из OCR.
- Полноразмерно reviewer просмотрел normal, batch3, batch4, fixed и batch2. Выбран Storm Spirit, POV label `v o i d`, HUD часы и HP/mana соответствуют указанным observations. Остальные6 PNG проверены криптографически/по dimensions и raw readbacks; их visual readout остаётся явно результатом независимого C1 analyst.

## Принимаемые и отклонённые случаи

| Случай | Actual before→after | CSV tick | Итог reviewer |
|---|---|---|---|
| normal |21212→21212|21212|HUD8:12, HP71/956,mana62/651 согласуются с exact real CSV row; ограниченный positive.|
| batch3 |41706→41706|41706|HUD19:35, HP1215/1308,mana734/1376; ограниченный positive.|
| batch4 |45846→45846|45846|HUD21:53, HP782/1528,mana1335/1376; ограниченный positive.|
| fixed |21190→21190|21190|HP66/956,mana57/651 согласуются, но HUD7:25 против decoded491.633s≈8:11; negative clock case сохранён.|
| slow |21190→21191|21190|Clock mismatch7:25 и moving cursor; exact capture calibration не принята.|
| pilot |21207→21208|21206|Moving cursor; не positive exact point.|
| paused |21243→21243|21242|Предыдущая real row, gap1; bounded comparison.|
| batch0/1/2/5 |21113/21223/34359/52485 stable|21112/21222/34358/52484|Все gap1; exact real row на cursor tick отсутствует, interpolation не выдана за наблюдение.|

Три positive точки имеют совпадающий tick и floor(decoded game seconds)=показанная HUD секунда; HP/maxHP совпадают, mana/maxmana отличаются менее чем на1. Из этого не выводится постоянное правило округления или совпадение всего payload. В частности batch2 HUD mana914 против913.93835 и batch0 HUD208 против208.5627 не сведены к единому floor/round.

Identity этих decoded rows сохраняет account70388657/full handle14926170; caption/class отдельно не считаются доказательством владельца. Clock provenance предыдущего spike остаётся CNETMsg_Tick/GameRules start/pause fields, а не fitted HUD offset. Новая воспроизводимая bracket-проверка не исправляет задним числом old PNG capture tick. Надписи stun/leash не устанавливают enum meanings raw uint64, fog или знание игрока.

## Завершение и границы

Actual restore readbacks: cl_playback_screenshots=false, fullscreen_min_on_focus_loss=1, spectator mode0. demo_timescale1 имеет отправку без value readback и не считается измеренной скоростью. Ownership receipt хранит PID32720/startUTC; cleanup-cursor указывает правильный DEM, quit trace и immediate/final cleanup сохранены раздельно. Read-only текущая проверка: own32720 отсутствует, Steam13704 присутствует. Историческая exact StartTime guard перед quit не воспроизводилась reviewer после завершения процесса.

Raw PNG/capture script остаются ignored; desktop capture не выполнялся reviewer и не используется этим набором. model_trained=false, physical_input_controlled=false и runtime_source_changed=false корректны для заявленного исследовательского результата.

Не принимаются: причина прежнего clock mismatch; causal роль speed/pause/reload; реальная pause model матча; общий sampling/rounding/schema compatibility; world transform; uint64 bit semantics; trusted fog/доступное знание; trained player model/fidelity; общая игровая приёмка. `telemetry-import-design.md` прочитан только по DRAFT/calibration scope: спецификация не является implementation, три конкретные точки не становятся общим native_verified.

Итог — независимая technical acceptance указанного ограниченного research результата, без расширения checklist/product gates. Token usage/cost reviewer недоступны: null.
