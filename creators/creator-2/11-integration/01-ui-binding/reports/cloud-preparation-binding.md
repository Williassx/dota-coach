# Облачная проверка привязки подготовки

[Подпункт](../README.md) · [План](../preparation-binding-plan.md).

**Дата UTC:** 2026-10-10. **Основа:** 9f26bdf. Проверялись исходники в Node VM/Python.

- Port: 10 RED → 10 GREEN; захват own data functions, receiver, accessor/ownership,
  guard после descriptor trap, исключения и повторное владение.
- Три адаптера: по четыре новых сценария injection/suspend/refresh/dispose-error и
  отказ accessor. Итог team25, hero28, preparation26. Исправлена передача optional
  projection в hero fixture; первый вариант helper не передавал аргумент.
- Partial preparation context: один RED → GREEN; flow теперь20 сценариев.
- Group: 18 RED missingmodule →18 GREEN. Фактические обработчики трёх адаптеров
  меняют одну цепь; полный draft, reset/invalid/old/busy, focus, private copies,
  hidden-node failure, partial foreign ownership, dispose/getter/render reentry,
  late handlers/timers и initial bind проверены. Busy test дополнительно проверяет
  общий статус «обновляется» до чтения DTO, по рекомендации UX критика.
- Пять read-only критиков рассмотрели дизайн и код: архитектура, ИИ/данные, UX,
  осуществимость, объём. В финальном коде существенных воспроизводимых дефектов
  не нашли. Повторные прогоны критиков не считаются отдельными сценариями.
- Все24 suites: 522 PASS, 0 FAIL/skip/todo. Это прежние481 +41 новых сценариев.
  Шесть изменённых/новых scripts прошли node --check. XML/graph и старый exact13
  HUD bundle проверены своими прежними suites; bundle не расширялся.

Созданы port/group source, design/plan, тесты/заметки/этот отчёт; изменены три
адаптера и flow contexts. C1/sharedcontract/probe/HUD/layouts не изменены.
Проверенный результат — локальная привязка на предоставленном тестовом дереве.
Общая XML-композиция, подключение ресурсов, native compile/scroll/hittest,
реальные каталоги, сервер/эффекты и второй владелец открыты.
Windows/Dota/Workshop Tools из облака не запускались.

Start_skill revision21 сохранён; readback остальных полей без изменений.
requires_publish=true: активация через настройки среды остаётся открытой;
install/network/secrets/runtime не менялись. Проверены1335 локальных ссылок.
