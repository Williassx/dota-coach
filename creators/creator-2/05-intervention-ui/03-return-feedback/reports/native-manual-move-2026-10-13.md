# Первый игровой сценарий: временное перемещение одного героя

Пользователь согласовал внедрение 13 октября 2026. Реализован отдельный ограниченный
аддон Dota 2 для одного **TEST / синтетического** героя: сервер выдаёт разрешение,
исполняет перемещение, завершает вмешательство и выдаёт новый приказ synthetic ИИ.
Это частичная приёмка C2-05-03, не готовая игра или персональная модель игрока.

[Дизайн](../native-move-design-2026-10-13.md) · [План](../native-move-plan-2026-10-13.md) ·
[Контракт v1](../../../../shared/contracts/manual-move-v1.md) ·
[Данные, хеши и границы доказательства](native-manual-move-2026-10-13.json).

## Что реализовано

Карточка выбирает адресата без команды. Отдельная кнопка запрашивает MANUAL у сервера.
UI принимает строгий versioned snapshot и использует левый world callback только
после grant. Отмена отправляется серверу; после cancel/arrival/expiry сервер делает
Stop, заново наблюдает героя и выдаёт фактический новый synthetic AI move.
Issued order не подписывается прибытием, а timeout UI показывает unknown и sync.
Смена выбранной карточки не меняет захваченного адресата.

Сервер разрешает sender через native source entity, GetPlayerID и равенство
PlayerResource player handle. TEST actor привязан к исходному player handle,
своему текущему живому герою и команде. Client не выбирает entity/owner/game clock.
Позиция проверяется по finite/bounds/distance и GridNav. Приказы клиента герою
ограничивает scoped order filter; собственные серверные orders проходят его guard.
Новая move не продлевает срок; duplicate ID/body не повторяет эффект, changed body
отклоняется, bounded dedup не вытесняет уже принятые ID.

Пауза и неизвестное состояние паузы запрещают эффекты. New acquire/move/cancel в
паузе возвращают paused; sync доступен. Close/disconnect/clock failure в паузе
откладывают одну остановку до подтверждённого unpause, повторно проверяя исходного
владельца, живое состояние, generation/entity. Replacement не получает старый Stop.
После close/disconnect ИИ не возобновляется. Эти ветви проверены исполнением Lua,
нативная death/pause/replacement приёмка остаётся открытой.

Переподключение UI делит token владения callback через CustomUIConfig. Новый bind
отключает прежний; поздний dispose из прежнего JS context не отключает новый.
Dispose закрывает обработчики до чтения DTO, не отменяет lease на сервере.

## Нативное доказательство

Windows Dota build **25894101**, template_map, **1280×720**. Восемь собственных
запусков; ещё r4/r5 были скомпилированы, но не запущены. Сохранены ранние отказы и
сборки, они не переименованы в положительную приёмку.

| Запуск | Результат | Реальные PNG |
|---|---|---:|
| r1/r2 | UI не принимал bool/number wire; диагностические неуспехи сохранены | 0 |
| r3 | 9 программных API-фаз PASS: grant/move/движение/expiry/cancel/arrival/dispose | 8 |
| r6 | Повтор тех же 9 фаз PASS | 8 |
| r7 | bound/world position API PASS; physical input отсутствует | 2 |
| normal final | Обычная панель и server AI state, без TEST драйвера | 1 |
| r8 | Текущий controller/adapter: те же 9 фаз + world API PASS | 8 |
| normal final2 | Текущая обычная сборка: server AI state, без TEST драйвера | 1 |

Итого **28 настоящих кадров**. Full-cycle driver вызывает существующие state API
программно: это transport/engine effect proof, не mouse/hittest. В r7 driver после
world-only захвата продолжал свой сценарий; отсутствие input не означает отсутствие
программных orders во всём запуске.

В r3/r6/r8 перемещение героя между началом и фазой moving составило соответственно
327.69 / 336.14 / 342.38 единиц XY. После возврата новые actual native order traces
и изменившиеся actual hero origins подтверждают движение synthetic ИИ. Это не
доказательство сходства с реальным игроком.

Logical lease настроен на **5 игровых секунд** от grant. Expiry/AI return наблюдались
через **5.0333 / 5.0667 / 5.0667** игровых секунд: сервер проверяет срок на следующем
Think tick. Строгая остановка ровно к 5.000 без задержки тика **не подтверждена**.
Arrival отдельного near-target цикла подтверждён transition arrived; успешный
ExecuteOrderFromTable сам по себе arrival не доказывает.

Native GetScreenWorldPosition([640,360]) дал finite XYZ
[-128,-137.90081787109375,128] в r7/r8. Это проверка API проекции, не настоящий клик.

Скриншот запрашивается после найденного маркера, VCon добавляет задержку. Поэтому
файл с именем move_issued может показывать уже moving. JSON хранит время захвата и
последнюю предшествующую logged phase; атомарное соответствие phase/frame не заявлено.
Все 28 PNG проверены по размеру/хешу и просмотрены через contact sheet; normal final2
и r8 granted также просмотрены в полном размере. Панель читается, MANUAL/AI различны.
Белая область штатной minimap template присутствует; её причина и полноценная карта
не установлены. Герой после дальней команды может выйти из исходного кадра.

[Обычная панель](native-move-ui-20261013t174639276-ready-2026-10-13.png) ·
[Полученное разрешение](native-move-r8-granted-2026-10-13.png) ·
[Ручное движение](native-move-r8-move_issued-2026-10-13.png) ·
[Отмена / новый приказ ИИ](native-move-r8-cancelled_return-2026-10-13.png).

## Исходники, упаковка и проверки

[C1 controller/adapter](../../../../creator-1/04-intervention/01-manual-actions/src/scripts/vscripts/README.md) ·
[C2 state/panel](../src/README.md) · [Тесты](../tests/README.md) · [Сборка](../tools/README.md).
Обычный kind имеет exact **7 outputs / 5 compiled UI**, TEST fixture —
**9 outputs / 7 compiled UI** (6 active + retained canonical XML). Source receipts
проверяют exact graph/hash/schema, новые пути и отсутствие reparse/extra files.
Обычная сборка не содержит TEST driver. Старые fixed HUD/probe bundles не расширены,
build output и установленная сборка не редактировались.

Текущие исходники: native r8 и normal final2, свежие bundles
`native-move-20261013T174214Z-d70b55` и `manual-move-20261013T174214Z-f5ce54`.
Compile/PID/console/capture receipts лежат в ignored `build/dota_coach`; raw console
с account metadata не публикуется. В JSON сохранены только отобранные безопасные данные.

**26 исполняемых Lua5.1**, **26 Node state/panel**, **11 bundle/fixture** проверок PASS.
RED→GREEN сохранены для paused disconnect, clock unknown, shared callback ownership,
native alive=1, видимого child Label, highwater и результата после refresh.
Полный каталог: **88 suites / 1334 PASS / 28 skipped / 6 incomplete / 0 error suites**,
все 88 процессов завершились exit0; strict verified=false / runner exit1 из-за skips.
Свежий full report: `build/dota_coach/source-checks-20261013T175338Z-451750/source-checks.json`.
Sandbox отказ owned timeout cleanup сохранён отдельно; повтор вне песочницы проверил
собственные child processes без изменения security/source guards.

Два помощника оставили RED/tests и частичный controller до ограничения ёмкости;
root завершил принадлежащие им задачи. Один итоговый критик нашёл два P2:
Stop при неизвестной паузе и поздний dispose callback. Оба исправлены и воспроизведены
тестами; повторная оценка cross-context/deferred cleanup/original owner — без
существенных замечаний. ИИ-критик не заменяет другого человеческого владельца.

Все восемь собственных Dota PID завершены через VCon с проверкой PID/startUTC;
Steam PID12964 сохранён. Чужие клиенты и настройки ОС/игры не изменялись.
Точное token usage/стоимость недоступны и отмечены null. C2: **56/213 (26.3%)**
после одного подтверждённого пункта cancel; C1 **112/181** без повышения.

## Что посмотреть и продолжить

Установлена обычная актуальная сборка `dota_coach_c2_move_final2_20261013`.
Локальный запуск из PowerShell:

```powershell
& 'D:/AI/dota2coach/creators/creator-2/05-intervention-ui/03-return-feedback/tools/launch_manual_move.ps1'
```

Launcher сохраняет existing Dota client и пишет ownPID receipt; с закрытым клиентом
запускает отдельную сцену. Карточка → запросить управление → левый world click;
cancel/expiry возвращают synthetic ИИ. Физический путь реализован, но его
нативная приёмка ещё не подтверждена.

Computer Use не смог захватить окно: initial `FrameArrived timed out: timed out
waiting on channel`, recovery `window capture timed out: timed out waiting on
channel`. UIA показал только window index0 / Raise, без карточки или мира.
Coordinate input не выполнялся. Согласно прочитанному computer-use guidance,
после отказа захвата старые координаты не применяются; повтор на свежем окне
также завершился тайм-аутом. Это ограничение доступного канала, причина не установлена.

Следующие проверки: настоящий mouse/hittest через рабочий канал, нативные
pause/death/respawn/replacement/reload/late-event сценарии, точное измерение границы
остановки и человеческий второй владелец. Общий HUD, атака, voice bridge, 5×5,
реальная карта и персональные модели остаются отдельными зависимостями.
