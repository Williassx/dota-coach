# Проверка source-пакета ручного запроса

[Подпункт](../README.md) · [План](../intervention-plan.md).

**Дата UTC:** 2026-10-11. **Основа:** 257b71c.

12 сценариев дали RED при отсутствии recipe. После реализации 11 PASS / 1 ERROR:
тест неверно ожидал ValueError для существующего output; правильный FileExistsError
сохраняет исходный файл. Тест исправлен без изменения output policy.

Самопроверка обнаружила недостаточную проверку иерархии manifest: плоский перечень
root/Panel/CustomUIElement допускал loader рядом с Panel. Отдельный 13-й тест дал RED;
добавлена проверка родителей/числа детей, затем 13 PASS.
Проверены exact mapping/full six assets, byte roundtrip/5links, отказ до output при
ошибках, dependency order, plain labels/disabled button/9IDs, inert exact tree,
DTD/entities/text/events/src/nestedcontext, current-source/tamper, сохранение output.

Полная регрессия: **28 suites / 648 PASS**, без ошибок, пропусков, cancelled/todo.
Existing foundation 28, packaging 52 (HUD19 + preparation20 + intervention13) проходят.
Actual CLI build/verify создали build/dota_coach/intervention-source-20261011-01:
6assets/5links/package_verified=true, source2_compiled/runtime_verified=false.

Добавлены recipe, один canonical source XML manifest и strict validation нового kind
в существующем build helper. Verifier/default/probe/HUD/preparation policy не изменены;
source JS/CSS/layout тоже не менялись. Нативная загрузка/компиляция/layout/hittest,
bootstrap/transport/C1authority/lease/возврат ИИ и второй владелец остаются открытыми.

Один итоговый read-only критик после завершения подпроекта не обнаружил дефектов
или обходов политики. Повторные полные тесты не запускались без новых изменений кода.
Повторяемая CLI-команда с автоматически выбранной новой папкой также проверена:
probe-ui-20261011T071353Z-4f29ab, те же 6 ресурсов/5 ссылок и false для native/runtime.

График обновлён: 22/192 действий (11.5%); раздел 11 — 3/18 (16.7%).
Исправлена сериализация SVG с удалением пробелов в концах строк.
Стартовые инструкции среды сохранены/read-back revision27; остальные поля сохранены.
Публикация черновика среды недоступна через текущие инструменты.
