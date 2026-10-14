# Независимая C2 technical peer review — матч 9042986015

14 октября 2026. Проверяющий — отдельный C2 исполнитель после завершения исследовательского подпроекта C1-05-03. Область: `match-analysis.md`, `root-evidence.json`, `efficient-analysis.md`, `native-status.md`, metadata/API и ранний/поздний визуальные отчёты. Проверка read-only; Dota не управлялась, исходники/общие документы/checklist не менялись. Единственная явная запись reviewer — этот отчёт.

**P1/P2 замечаний не найдено в рассмотренной исследовательской области.** Допускается техническая передача выборочного анализа с указанными ниже границами. Это не приёмка обученной модели, полной игры, прав или непрерывного просмотра реплея.

## Проверенные данные

Actual cached `match.json` относится к9042986015. Целевой account70388657 — `/players/7`, Storm Spirit17/player_slot130/Dire. Все aggregate fields из `metadata.json` совпали с actual API; в частности5/4/3,343LH/2denies,551GPM/487XPM,16602networth,12448hero_damage/84tower_damage. Match start1791892318 соответствует2026-10-13T11:51:58UTC; duration1910=31:50, Radiant36:12 и radiant_win=true совпали.

Actual kills_log содержит449/455sec для DK/Undying; deaths_log493/932/1177/1315sec соответствует8:13/15:32/19:37/21:55. Purchase log содержит black_king_bar1531sec=25:31. Main report не превращает эти API моменты в часы соседних изображений и не утверждает native BKB activation/TP success. neutral_kills164/lane_kills166 сохраняются отдельно от343LH.

Bytes/SHA256 всех пяти cached API sources match/proPlayers/heroes/patch/profile совпали с metadata receipts. Public proPlayers сопоставляет account70388657 с Dendi; target profile SteamID совпадает с metadata. Native `demo_info` source2957bytes/SHA256 совпал; matchid/targetSteamID/Storm/name `v o i d` присутствуют. Другие SteamID не выводились reviewer. Это сопоставление источников, не независимая аутентификация человека или согласие на использование образа.

Cached patch constants60 содержит7.41; numeric domains APIpatch60/nativeheader48/serverbuild10939/clientbuild25894101 отчёт не смешивает. Точный suffix и compatibility остаются неизвестными. Source compressed replay37843886bytes/SHA256 совпал и имеет magic28b52ffd; verified demo64095154bytes/SHA256 совпал и имеет PBDEMS2 magic. Reviewer не запускал демопарсер и не декодировал всю телеметрию заново.

## Кадры и выборочная визуальная сверка

Независимо перечитаны manifests и каждый PNG трёх наборов: overview-r4-v4=88, episode-samples-r4=21, episode-confirm-r4=5. Все114 файлов имеют1280×720, ожидаемые bytes/SHA256; manifest SHA256 совпали с root evidence. Все114 хэшей уникальны.12 root observation records также совпали по bytes/SHA256 со своими файлами. Хэш подтверждает файл, а не интерпретацию его содержания.

Reviewer непосредственно просмотрел8 полноразмерных native PNG:

| Source | HUD | Сверенное наблюдение |
|---|---|---|
| overview-r4-v4/frame-013 | 4:41 | Storm level5 у нейтралов; LH26/2. |
| episode-samples-r4/frame-005 | 8:11 | HP66/956,mana57/651; Ball Lightning displayed cost73. |
| episode-confirm-r4/frame-000 | 8:16 | Death summary0/956,respawn25,KDA2/1/1. |
| episode-samples-r4/frame-008 | 15:30 | HP947/1220,mana915/1148; «ПРИВЯЗКА» над Storm. |
| episode-samples-r4/frame-011 | 19:35 | HP1217/1308,mana736/1376; «ОГЛУШЕНИЕ» над Storm. |
| episode-samples-r4/frame-014 | 21:53 | HP786/1528,mana1337/1376; «ОГЛУШЕНИЕ» над Storm. |
| overview-r4-v4/frame-074 | 25:34 | HP322/1660,mana844/1484; TP channel«Применяется1.9с». |
| episode-samples-r4/frame-020 | 31:45 | KDA5/4/3,LH343/2,score36:12. |

POV label `v o i d` видна; подпись не доказывает историческую полноту доступного игроку знания. В close кадрах видно1x, в overview8x: это UI label/requested condition, не измеренная точная скорость симуляции. UTC/index/requested tick не использовались reviewer для чтения игровых часов.

Root отдельно обозначил final confirm/frame-004 как `postgame_camera_black_letterbox`; число114 — native screenshots трёх проверенных наборов, не114 непрерывных игровых решений. Старые88 одинаковых postmatch кадров остаются negative capture evidence и не включены в эти114. Sparse early/late reports сохраняют фактическую ограниченную выборку; новые26close кадров не приписаны двум прежним аналитикам.

## Очистка и границы доступа

Actual restore receipts содержат readback `cl_playback_screenshots=false` и `dota_video_config.setting.fullscreen_min_on_focus_loss=1`. `final-demo-state` содержит отсутствие активного demo; final status/quit подтверждают local loopback и shutdown/disconnect trace. Ownership receipt26024 содержит original startUTC. Read-only текущая проверка процессов:7276/12992/29444/26024 отсутствуют, Steam13704 присутствует. Историческую точную StartTime-сверку перед quit reviewer заново воспроизвести не может после завершения процесса; native-status не подменяется новым native экспериментом.

`git check-ignore` подтвердил ignored desktop probe/replay/PNG; `git ls-files -- build/dota_coach/replay-9042986015` пуст. Desktop image reviewer не открывал; оно не используется как gameplay proof и не публикуется текущим tracked report. Raw/account logs не копировались в отчёт.

## Сохранённые ограничения

- Accepted scope — public API facts и выборочные реальные кадры, не continuous every-second viewing. Подтверждение114bytes/hash не означает, что reviewer визуально проверил все114 сцен.
- Tick↔HUD alignment остаётся false; API31:50 и last observedHUD31:45 сохранены отдельно.360секунд разницы header/API не принимаются как доказанный offset.
- Наблюдаемое ресурсное истощение/контроль — контекст кандидатов признаков. Причины входов, альтернативы, вина в поражении, мораль, дружелюбие и устойчивый стиль не установлены.
- Actual training/runtime/heldout player fidelity отсутствуют; personal_model_trained=false/player_fidelity_verified=false корректны. Изученный матч не назван untouched final test.
- Native fog/help/POV не заменяют trusted historical knowledge reconstruction или controlled physical input.
- Efficient-analysis — документированный порядок кеша/пилота/ограничения повторных ошибок/компактных эпизодов. Измеренная token economy не заявлена; tokens/cost=null. Неприменённый follow-up из-за usage limit не выдан за результат.
- Reviewer не принимает права, выпуск, самостоятельную игру, новые механики, производительность модели или общую игровую приёмку. Runtime source данным подпроектом не изменялся; product regression tests здесь не запускались.

Итог: ограниченный исследовательский результат технически рассмотрен отдельным C2 исполнителем; указанные числовые и выборочные визуальные утверждения имеют проверяемые локальные источники. Обновление авторского review_status и итоговых общих документов остаётся у root. Token usage/cost этого review: null.
