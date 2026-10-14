# Нативный просмотр 9042986015 — фактический итог

[Главный разбор](match-analysis.md) · [Root evidence](root-evidence.json) · [Урок и экономный порядок](efficient-analysis.md).

## Полученный результат

Valve replay действительно загружен в Dota Tools. В трёх корректных локальных наборах сохранены 114 native PNG 1280×720: 88 обзорных и 26 близких выборочных кадров. Все размеры/байты/SHA256 сверены с manifests. Root просмотрел их контактные листы и выбранные полноразмерные изображения; два независимых анализатора рассмотрели раннюю и позднюю части. Это выборочный разбор, не непрерывный просмотр всех секунд и не доказанная оцифровка Dendi.

В обзоре читаемые часы 0:14–30:00. Близкие кадры дополняют смерти и финальный отрезок до HUD31:45; API duration31:50 сохранена отдельно. Requested demo tick/скорость/UTC/index не заменяют часы изображения. Точное соответствие tick↔game time не установлено.

Установка D:/SteamLibrary/steamapps/common/dota 2 beta, app build25894101. Native demo_info подтвердил match9042986015 и целевого StormSpirit v o i d/account70388657. Header patch_version48, server build_num10939 и OpenDota patch60/7.41 family различаются.

## История диагностики, которая не засчитывается как просмотр

- По явному разрешению пользователя original Dota14764 перезапущен. Steam13704 сохранён.
- Own7276: replay загружен, VCon29004 недоступен. Own12992: normal client, -insecure/29000; VCon доступен, команды screenshot отсутствовали. Изменились две launch conditions, причина разницы не изолирована.
- Own29444 и26024: Tools зарегистрировал png_screenshot. Replay guard cl_playback_screenshots=false блокировал экспорт; после true реально получен игровой PNG. Own26024 запускался как foreground interactive viewer с Normal window style.
- Sky window graphics capture неоднократно timeout, GDI window probe — чёрный кадр. Один desktop probe сначала отклонён automatic approval review, затем отдельно разрешён пользователем и выполнен ровно один раз. В нём Codex foreground/предпросмотр taskbar, не игровое доказательство. Он только ignored local и не публикуется.
- overview-r4:88 одинаковых изображений итогового экрана. К игровому покрытию не относятся. v2/v3 остановились после трёх дубликатов. Demo ticks могли идти при неактуальном изображении; гипотеза о причине не выдаётся за факт.
- После обновления Sky state и активации окна появился актуальный кадр15:27. Затем v4 получил88 разных игровых кадров с продвижением HUD. Это наблюдаемая последовательность, не изолированный эксперимент о причине заморозки.

Native help показывал PlayerView mode3 и Dire fog mode3; PNG показывают «ГЛАЗАМИ ИГРОКА / v o i d». Историческое допустимое знание и физический ввод полностью не проверены. Direct exported native PNG не является успешным Sky mouse/hittest.

## Завершение сеанса

Временные настройки восстановлены и прочитаны обратно через VCon: cl_playback_screenshots=false; dota_video_config.setting.fullscreen_min_on_focus_loss=1. demo_timescale1 отправлен, точная скорость этим не измеряется.

Перед quit сверены имя процесса и точные StartTime UTC ticks с ownership receipt26024. Status показывал local loopback/empty spawngroup, активный replay отсутствовал. После quit own26024 отсутствует; Steam13704 присутствует. Предыдущие own7276/12992/29444 завершены ранее. Raw logs/реплей/изображения/diagnostic scripts находятся только в ignored build/dota_coach/replay-9042986015.

## Проверка другим исполнителем

API identity и обе части sparse обзора отдельно проверены анализаторами. Дополнительный ранний follow-up не выполнен из-за usage limit; его результат не придуман. Финальный [C2 technical review](technical-review.md) завершён:114files/hash, API,8sampled fullframes иcleanup;0P1/P2. Checklist, готовность модели, права, полная игровая приёмка и экономия токенов этим исследованием не подтверждаются.
