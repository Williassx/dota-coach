# План source-пакета журнала

Основание: [design](orders-timeline-design.md).

1. Добавить canonical inert Hud manifest и fixed recipe пяти ресурсов. Написать
   roundtrip/recipe/graph/plain topology/path/current-source/actual packaged VM tests;
   получить RED до production dispatch/validator.
2. Добавить только trusted kind dispatch + validator, переиспользуя общую policy.
   Получить GREEN; прежние kind/default restrictions не менять.
3. Добавить экран в handoff registry и его existing all-screen проверку, пройти
   actual CLI, затем полный canonical каталог.
4. Один final critic готового подпроекта; исправления подтверждать RED→GREEN,
   повторять full только при новом коде. Отчёт/журнал/график/cloud draft и normal push.
