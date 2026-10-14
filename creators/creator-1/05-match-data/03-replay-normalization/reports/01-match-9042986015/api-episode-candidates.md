# Эпизоды9042986015 для нативного просмотра

14октября2026. АналитикC1-05-03. Это выборка **реальных записей OpenDotaAPI** для поиска в реплее; данный аналитик ещё не просматривал нативные кадры. [Протокол](analysis-protocol.md) · [Записи, source pointers и SHA256](api-episode-candidates.json).

Источник: [матч OpenDotaAPI](https://api.opendota.com/api/matches/9042986015), локально `build/dota_coach/replay-9042986015/match.json`. account70388657, player_slot130, индекс players7, hero_id17, Dire; API nameDendi/personaname`v o i d`. Связь identity проверяется основным исполнителем и metadata-аналитиком; этот документ не повторяет независимую identity-проверку.

## Время

В выбранных log/time и times используются секунды игрового времени. В текущем [официальном исходнике OpenDota parser output()](https://github.com/odota/parser/blob/master/src/main/java/opendota/Parse.java#L157-L174) из времени событий вычитается gameStartTime. В этомJSON times начинается0, стартовые покупки−89, duration1910(31:50). Unix start_time1791892318 — отдельная шкала. Точная deployed revision парсера не дана; version22 не выдаётся за pinned executable. До сравненияHUD времяAPI — ориентир, demo ticks/предматчевый offset не установлены.

## Очередь просмотра

| Эпизод | Окно игрового времени | ФактAPI и что проверить |
|---|---|---|
| early-resource-01 | 01:00–03:20 | LH3→8→16 на01:00/02:00/03:00; Bottle01:26, Stick02:20, Wand03:07. Проверить линию, волну и delivery. |
| mana-and-stack-02 | 04:45–05:55 | Soul Ring05:30; stack count0 в05:00→1 в06:00. Проверить лагерь и действия; точное время stack не дано. |
| first-kill-sequence-03 | 07:05–07:45 | kills_log07:29Dragon Knight и07:35Undying. Проверить цели, союзников и доступное знание. |
| first-death-04 | 07:50–08:50 | deaths_log08:13Rubick, time_dead28. Проверить предшествующий эпизод. |
| arcane-boots-05 | 09:40–10:10 | purchase_log09:54Arcane Boots. Проверить доставку/экипировку отдельно. |
| fight-kills-06 | 10:20–11:50 | kills_log10:42Rubick и11:38Dragon Knight. Это отдельные моменты, непрерывная драка не заявлена. |
| tracked-kill-07 | 12:29–13:09 | kills_log12:49Rubick имеет tracked_death/Bounty Hunter. Проверить атрибуцию перед выводом о last-hit Storm. |
| kaya-08 | 13:00–13:30 | purchase_log13:13Kaya. Проверить предмет и контекст. |
| second-death-and-teamfight-09 | 15:00–16:15 | API teamfight15:16–16:06; смерть15:32Mirana. Проверить видимость, ресурсы и фактические действия. |
| orchid-10 | 18:15–18:55 | purchase_log18:38Orchid. Проверить доставку и применение. |
| third-death-11 | 19:17–20:27 | Смерть19:37Dragon Knight, time_dead46. Проверить контекст и возврат. |
| fourth-death-12 | 21:35–22:45 | Смерть21:55Mirana, time_dead46. Не делать вывод о характере по повторению. |
| bkb-13 | 25:11–25:51 | purchase_log25:31BKB. Overall item_usesBKB1 не указывает время активации. |
| late-teamfight-14 | 29:55–31:05 | API fight30:09–30:53: Ball Lightning7, damage1978, deaths0; max_hit30:15. Проверить последовательность без вывода об агрессии. |

Показатели подтверждают наличие исходных событий для изучения. Они не раскрывают маршруты, камеру, обзор игрока, намерения или точную задержку реакции. Сегменты teamfights — извлечённые интервалыAPI, не полная запись решений. По каждому эпизоду native_verified=false, available_knowledge=unknown и intent=null до реального просмотра.

Первый матч относится к исследовательским данным и кандидату train. Его нельзя позже объявлять untouched final test. Поражение, общий фарм или число убийств не подтверждают сходство модели с игроком; мораль и дружелюбие остаются отдельными игровыми параметрами.
