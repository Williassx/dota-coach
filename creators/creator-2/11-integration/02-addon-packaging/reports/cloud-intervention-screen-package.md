# Проверка общей source-сцены

[Подпункт](../README.md) · [План](../intervention-screen-plan.md).

**Дата UTC:** 2026-10-11. **Основа:** 0b746eb. Commit — в истории этой записи.

Добавлены canonical parent XML/manifest/CSS в C2-11-01, фиксированный recipe и
composer в C2-11-02; регистрация kind в существующем foundation builder.
XML карточек и manual панели не дублируется в библиотеке: generated layout содержит
извлечённые scopes и fingerprints двух полных raw inputs. Проверка всех 13 outputs,
12 ссылок и порядка восьми определений сохраняет единственный source graph.

Первые 11 тестов: пять ERROR до поддержки recipe, шесть защитных сценариев уже PASS.
После реализации все 11 PASS. Проверены точное отображение ресурсов, canonical
subtrees, fingerprint изменений вне выбранной scope, зависимости, inert XML,
DTD/entities/attributes, hosts/required IDs/slots, symlink, tampered output и
сохранение существующего каталога. VM-сценарий грузит фактические восемь JS из
generated дерева: explicit bind, карточка A, один запрос A, dispose без таймеров.

Packaging: 63 PASS; foundation: 28 PASS. Полная регрессия: **30 suites / 701 PASS**,
нулевые fail/skip/cancelled/todo. Actual CLI output:
`build/dota_coach/probe-ui-20261011T080134Z-33e902` — 13 ресурсов/12 ссылок,
package_verified=true, source2_compiled/runtime_verified=false.

Нативная компиляция, геометрия/hittest, bootstrap, микрофон, transport, C1 authority,
lease/возврат ИИ и приёмка другого человеческого владельца остаются открытыми.
Итоговый read-only критик после завершения реализации не обнаружил существенных
дефектов. Он проверил fixed mapping, scope extraction, raw fingerprints, XML/пути,
топологию и старые ветки. Полную регрессию без нового изменения кода не повторяли.
График: 26/196 действий (13.3%); это заполнение библиотеки, не готовность игры.
