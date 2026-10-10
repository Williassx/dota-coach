# Проверка локальной тактики и разговора

[Подпункт](../README.md) · [План](../implementation-plan.md).

**Дата UTC:** 2026-10-10. **Основа:** 045fb99. Node VM/ES5 source, без native запуска.

- До source 26 сценариев дали RED missing module; реализация дала 26 GREEN.
- Пять read-only критиков рассмотрели дизайн и реализацию. До кода архитектура
  уточнила assignment bijection/counters/heroId; это вошло в schema и тесты.
- UX воспроизвёл скрытую причину невозможности заменить выбор при пустом каталоге
  и предложил уточнить recovery copy. Два новых сценария дали 26 PASS/2 FAIL,
  исправление normalMessage/recovery вернуло 28 PASS.
- Тесты используют настоящие team picker и hero-role модели для получения полного
  local draft; сами профили/герои и варианты явно тестовые. Сходство ИИ не заявлено.
- Архитектура дополнительно проверила transient array-length newer reentry;
  независимые повторы критиков не считаются новыми сценариями.
- Повторены прежние403 сценария в18 suites; вместе431 PASS без skipped/todo.
  Node syntax прошёл. Complete означает два local choices, serverConfirmed=false.
- Предыдущие sources/C1/shared/HUD/bundle/probe не менялись. Панель/submit/bootstrap,
  обучение, вычисление морали, эффект тактики, сеть/storage/native отсутствуют.

Открыты C1-07-02/03, реальные каталоги и правила/исполнение, наблюдаемый эффект,
поддержка моделей и личности, панель/native/server/start и второй владелец.
Windows/Dota/Workshop Tools из этой облачной сессии не запускались.

Пять направлений финального review завершены. Проверены 1276 локальных ссылок/README
и diff --check. Start_skill дополнен выполненной командой, revision18; readback сохранил
остальные поля. requires_publish=true, активация через настройки среды открыта;
install/network/secrets/runtime не менялись.
