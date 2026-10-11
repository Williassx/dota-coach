# Source-пакет панели ручного запроса

**Основа:** 257b71c. Один редактор; критик только после завершения подпроекта.

Собрать альтернативный inert UI source-пакет, чтобы три существующих JS и CSS
загружались по локальным resource ссылкам. Нативная компиляция, bootstrap/transport,
связь с HUD/карточками и право ввода не реализуются этой упаковкой.

Kind panorama_source_intervention разрешает ровно шесть source→target пар:
C2-05-01 custom_ui_manifest.xml, intervention_request.xml, intervention_request.css,
intervention_request_state.js, intervention_request_panel.js; existing Orders из C2-02-02.
Custom manifest содержит один Hud element с intervention_request.xml. Definition
order: Orders→Requests→Panel; CSS один. Новый JS/bootstrap/демоданные не добавляются.

Существующие build/verify helpers остаются единственным источником. Общий bounded
read/path/symlink/reparse policy применяется и здесь. Probe/default/HUD/preparation
mapping не расширяется; новый kind требует exact mapping и все шесть ресурсов.
До создания output проверяются manifest schema, graph и UI tree.

XML: exact manifest root→Panel→CustomUIElement, никаких дополнительных атрибутов/
детей. Layout root содержит styles/scripts/Panel; include leaf и exact order.
Нет run/script/inline event/src на body/layoutfile/nested context/external resource.
Body только Panel/Label/Button, девять уникальных required IDs, все labels html=false,
единственная button disabled с required Hint. Source graph достигает всех шести файлов.

Вывод отдельный в build/dota_coach, никогда в установку игры; существующий каталог
не заменяется. Report/verifier сохраняют source2_compiled/runtime_verified=false.
Source/compiled/native доказательства отделены; альтернативные пакеты автоматически
не объединяются и не накладываются поверх HUD.

Приёмка source: build/verify сохраняют байты и 5 XML resource references, current-source
change/tamper/malformed graph отвергаются, все остальные source suites проходят.
