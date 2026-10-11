# План подключения общей модели запроса

[Спецификация](intervention-port-design.md). Выполнение inline, журнал в 00-action-log.

1. Написать intervention-port-binding.test.cjs: actual JS VM и дерево required nodes,
   существующие models/port helper/panel. Команда node --test этого файла: ожидается
   RED из-за отсутствия requestPort и поведения общей панели.
2. В intervention_selection_state.js добавить cached узкий requestPort; в canonical
   intervention_request_panel.js — optional adoption, refresh и stale screen guard.
   Expected: новый suite GREEN; старые request/selection/port suites GREEN.
3. Проверить все source suites один раз после завершения кода, recipes/package,
   ссылки и diff whitespace. Один итоговый критик после готового подпроекта.
4. Документировать данные проверок/открытые зависимости, отметить локальную
   приёмку в README, обновить PROGRESS генератором и --check, commit/push main,
   проверить remote SHA/чистоту checkout. Native/authority не отмечать выполненными.

Файлы: два существующих JS; один новый integration test; design/plan, notes/report
и индексы в C2-11-01, journal, generated progress. Existing XML/recipe не расширять.

Выполнено: шаги 1–3, 19 новых RED→GREEN и полный итог667. Замечание итогового
критика исправлено в одной pass с повторной регрессией. При публикации выполняется
шаг4; подтверждённый commit находится в Git-истории отчёта и журнала.
