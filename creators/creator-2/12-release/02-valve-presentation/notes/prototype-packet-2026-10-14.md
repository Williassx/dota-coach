# Dota Coach — ранний технический прототип, пакет для рассмотрения

Дата 14 октября 2026. Автор технической упаковки: исполнитель C2; передача C1
предназначена для независимого технического рассмотрения. **Не отправлено**.
Проект не представляет себя официальным продуктом Valve. Оператор, юридическое
лицо, территории, монетизация и основания внешнего распространения не установлены.

Замысел: тренер готовит команду, отдаёт приказы и временно вмешивается в управление;
после ограниченного срока управление возвращается ИИ. Показ ниже ограничен одним
TEST героем в Dota и пятью синтетическими назначениями состава. Полная игра,
персональные модели реальных игроков, голосовые приказы и матч 5×5 не показаны.

## Проверенная последовательность

Основа — [нативный отчёт](../../../11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.md)
и [JSON фаз/хешей](../../../11-integration/03-end-to-end/reports/native-coach-scene-2026-10-14.json).
R2: build 25894101, 1280×720, 12 API фаз PASS, 10 реальных PNG. Ниже указаны
фазы журнала, а не монтажные таймкоды. Screenshot после logged phase может быть
позже события: атомарная синхронизация кадра и snapshot не подтверждена.

| Порядок | Реальный кадр | Что говорить | Граница доказательства |
|---|---|---|---|
| 1 | [ready](../../../11-integration/03-end-to-end/reports/native-coach-r2-ready-2026-10-14.png) | Сервер подтвердил пять TEST назначений, слабое покрытие видно отдельно. | Не реальный roster, не подтверждённое сходство с людьми, не старт матча. |
| 2 | [manual moving](../../../11-integration/03-end-to-end/reports/native-coach-r2-manual_moving-2026-10-14.png) | Одному герою выдано временное управление и движение. | Programmatic API, физический клик не проверен. |
| 3 | [paused](../../../11-integration/03-end-to-end/reports/native-coach-r2-paused-2026-10-14.png) | За 2.202 s wall interval game time/remaining/counters не изменились. | Это измеренный один TEST сценарий. |
| 4 | [expired return](../../../11-integration/03-end-to-end/reports/native-coach-r2-expired_return-2026-10-14.png) | После истечения срока сервер вернул ИИ и выдал новый synthetic order. | Наблюдалось 5.033336639 игровых секунд от grant; не ровно 5.000. |
| 5 | [cancelled return](../../../11-integration/03-end-to-end/reports/native-coach-r2-cancelled_return-2026-10-14.png) / [arrived return](../../../11-integration/03-end-to-end/reports/native-coach-r2-arrived_return-2026-10-14.png) | Отмена и прибытие имеют собственные переходы и возврат ИИ. | Не общий набор coach commands. |
| 6 | [dead](../../../11-integration/03-end-to-end/reports/native-coach-r2-dead-2026-10-14.png) / [rebound](../../../11-integration/03-end-to-end/reports/native-coach-r2-rebound-2026-10-14.png) | Смерть закрывает управление; после respawn generation меняется. | Только own TEST hero, не полный матч. |
| 7 | [stale rejected](../../../11-integration/03-end-to-end/reports/native-coach-r2-stale_rejected-2026-10-14.png) / [reloaded](../../../11-integration/03-end-to-end/reports/native-coach-r2-reloaded-2026-10-14.png) | Старое поколение отклонено; после rebind приходит актуальное состояние. | Dispose stale DTO reads=0 в API probe; human input acceptance открыта. |

Кадры содержат штатные материалы Dota/template, поэтому это внутренние доказательства,
а не разрешённые рекламные/runtime assets. Белая minimap/край template не приняты как
полноценная карта. В R2 найден невидимый roster Sync; исправление generated XML и
отдельный normal UI3 рассматриваются в исходном нативном отчёте, R2 не переписан.
[Финальный normal кадр UI3](../../../11-integration/03-end-to-end/reports/native-coach-ui3-ready-2026-10-14.png)
показывает видимый Sync, пять назначений и weak warning без TEST driver; это отдельная
native source сцена 15/7. Physical input и продуктовая приёмка этим не подтверждены.

## Что работает и что следует дальше

Actual C1 observation→synthetic policy→arbiter→event log связан с existing manual
controller. Сервер владеет grant, пятью игровыми секундами, identity/generation и
TEST roster. C2 показывает snapshot, предупреждения и переходы. Normal source
recipe содержит 15 ресурсов; TEST — 18. Source reports сохраняют false runtime flags.

Следующий продуктовый этап требует отдельных доказательств: physical mouse/hittest,
map/visibility/patch, реальные данные и heldout fidelity, real speech/ASR, общий
preparation submit, тренерские команды, матч 5×5/result, performance и применимые права.
Эти функции являются планом, а не обещанием уже готового продукта.

## Буквальная приёмка C2-12-02

«Презентация показывает реальное управление и ограничения модели; пакет не отправлен
автоматически». Реальные server/API переходы и ограничения представлены конкретными
кадрами/JSON. Физическое управление пользователем и сходство реальных моделей не
проверены; полный критерий продуктовой демонстрации остаётся открытым. Пакет несент;
сам факт подготовки не подтверждает права, одобрение Valve или готовность выпуска.

[Руководство повторения](../../03-release-guide/notes/prototype-local-guide-2026-10-14.md) ·
[Два черновика запросов](../../../../creator-1/12-release/02-valve-demo/notes/rights-requests-2026-10-14.md) ·
[Технический архив](../../../../creator-1/12-release/03-release-package/reports/technical-packet-2026-10-14.md).
