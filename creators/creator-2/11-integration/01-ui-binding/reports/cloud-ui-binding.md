# Облачная проверка локального координатора

[Подпункт](../README.md) · [План](../implementation-plan.md).

**Дата UTC:** 2026-10-10. **Основа:** fde45f3. Проверены только исходники и VM.

- До реализации 18 сценариев ожидаемо упали: отсутствовал coach_hud_binding.js.
- После реализации: 17 прошли; один тест ошибочно ожидал четыре startup timers.
  Исходники подтверждают три: targets, router, parent; orders timer появляется
  только после запроса. Уточнён тест, затем 18 прошли.
- Добавлены четыре проверки refresh, reentrant native check, router observer,
  строгого camera setTarget / нового setRecipient: 22 прошли.
- Критик воспроизвёл утечку initial observer failure; новая регрессия дала RED
  с одним оставшимся таймером. Исправление propagation/rollback ownership: 23 прошли.
  Осуществимость независимо повторила 23 и прежнее воспроизведение: ноль таймеров,
  повторная привязка успешна.
- Архитектура воспроизвела camera после внутреннего отказа roster до watcher
  и изменение options shape из getter. Два новых сценария дали RED, sync
  router lifecycle и повторная проверка keys дали 25 GREEN.
- Прежние 266 сценариев повторены без пропусков, вместе 292: Python 8/13/28/30/19,
  Node 16/28/35/26/27/36/26. Все завершились с кодом 0.
- Пять read-only направлений: архитектура, UX, осуществимость, границы проекта и ИИ.
  Их замечания не заменяют приёмку второго равноправного владельца.
- Общий manifest теперь содержит 13 файлов, в том числе 10 JS definitions.
  Реальные CLI build/verify нового ignored output
  `build/dota_coach/hud-binding-20261010T0920`: assets=13,
  xml_resource_links=12, package_verified=true, source2_compiled=false,
  runtime_verified=false. Старый output не изменён; после изменения source его
  нельзя считать текущим пакетом.

Открыты C2-05-03/C1-04-03, общий серверный контракт/identity/clock/observation,
реальные игроки и нативная приёмка. Dota/Workshop Tools на Windows не запускались;
статус C2-11-01 частичный, сквозная интеграция не объявляется выполненной.

Проверены 1138 локальных Markdown-ссылок без отсутствующих целей, README каталогов,
node --check трёх изменённых JS и diff --check. Они не входят в 292 сценарий.
Start_skill сохранён в draft revision 13; readback подтвердил остальные поля
без изменений. requires_publish=true: активация через настройки среды ещё открыта;
install/network/secrets/runtime не изменялись.

Критик обнаружил неоднозначное объединение keys через delimiter. Точное
воспроизведение дало RED; сравнение JSON массивов имён дало 26 GREEN.
