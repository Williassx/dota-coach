# Проверка исходников панели выбора

[Подпункт](../README.md) · [План](../panel-plan.md).

**Дата UTC:** 2026-10-10. **Основа:** 3b9840c. Native Dota/Tools не запускались.

- 21 VM-сценарий сначала RED (missing adapter), затем GREEN. Две ошибки самого теста
  уточнены: assert.throws(message совпадал с Error.message) и plain-label predicate
  ошибочно включал navigation Button. Product assertions не отключались.
- Пять XML/sourcegraph сценариев RED (missing XML) → пять GREEN: unique required ids,
  local resources/order, plain labels/no bootstrap, disabled empty controls,
  inert definitions load и отсутствие screen в match HUD manifest.
- Пять read-only направлений рассмотрели дизайн/adapter. До code закреплены stable
  generation на входе update и old remove ABA. Кандидаты показывают source/coverage
  до выбора, выбранные slots явно предлагают удаление. XML/CSS рассмотрены отдельно.
- Прежние 320 сценариев повторены (13 suites), с панелью/графом общий итог 346,
  без skipped/todo. Node --check adapter прошёл. VM не подтверждает native API/layout.
- Модель не копировалась/не менялась. Match HUD/package/probe/server/creator1/shared
  contract не изменены. Добавлен отдельный source screen, не установленный аддон.

Открыты реальные данные/identity/C1-07-01, серверное подтверждение/роли/герои,
навигатор экранов, постоянное сохранение, native compile/CSS/scroll/разрешения/hittest
и равноправный второй владелец. Полная C2-04-01 приёмка ещё не выполнена.

Проверены 1194 локальных Markdown-ссылок без отсутствующих целей и README
каталогов; эти служебные проверки не входят в 346 сценариев.

Start_skill дополнен двумя проверенными командами: revision 15, readback подтвердил
сохранение остальных полей. requires_publish=true: активация через настройки среды
открыта, install/network/secrets/runtime не менялись.

Для заключительного архитектурного review недоступный прежний критик заменён
разрешённым пользователем Sol 6. Независимо повторены 21+5 сценариев и transient VM
для двух roots/offpage failure/fresh rebind/stale callbacks; блокеров не обнаружено.
Tree содержит 61 required node плюс root, всего 62 unique ids.
