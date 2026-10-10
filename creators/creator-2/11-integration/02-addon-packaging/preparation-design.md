# Source-пакет общей подготовки

**Дата UTC:** 2026-10-10. **Основа:** 6e070a5. Пользователь разрешил автономную работу.

## Цель и выбор подхода

Предыдущая привязка проверена на предоставленном дереве. Теперь собрать реальные
деревья трёх XML и девять определений в один layout/JS context без копий source.
Нативный CustomUIElement для каждой панели создавал бы отдельные контексты и не
позволяет доказать доступность одной цепи. Ручная копия XML нарушает один источник.
Выбираем детерминированную композицию при source build: shell содержит три host,
builder вставляет канонические Panel roots из текущих XML библиотек.

Работа C2-11-02: recipe/policy/tests; shell/style/manifest размещаются рядом с общей
привязкой в C2-11-01/src/panorama. Source2 compiler/native bootstrap отсутствуют.

## Ресурсы и граф

Новый manifest preparation-manifest.json kind=panorama_source_preparation/schema1:
точно15 assets source→target и layout_inputs из трёх фиксированных source/root_id/host_id.
Две XML: custom_ui_manifest.xml→coach_preparation.xml; четыре styles: три existing и
coach_preparation.css последним; девять scripts: port, teamstate/panel, herostate/panel,
preparationstate/panel, flow, binding. Никаких probe/demo/server/map или auto-bind.
Output содержит15 ресурсов+report. Исходные три XML — inputs, не дополнительные
layouts output; их scripts/styles сверяются с прежними точными зависимостями.

Shell CoachPreparationRoot содержит общий plain status и scroll stack с
CoachPreparationTeamHost/HeroHost/TacticsHost. Каждый host получает ровно один Panel
TeamPickerRoot/HeroRoleRoot/PreparationRoot. IDs всего дерева уникальны. Все Labels
html=false, buttons исходно disabled. Styles override только три root/window внутри
CoachPreparationRoot: высота fit-children, windows left/top/width100%, один внешний
вертикальный scroll. Scoped list overrides также задают height:fit-children и
overflow:squish squish для TeamPickerList/HeroRoleList/PreparationList, снимая
внутреннюю прокрутку. Это временная компоновка без новых табов/механик.

Graph требует одну manifest CustomUIElement typeHud, exact local references/ordering,
все outputs reachable, без nestedlayouts/run/script/event attrs/DTD/entities. Module
XML содержит один root Panel, его ожидаемые зависимости, без неизвестных rootsections.
Generated XML включает комментарии source/sha256 каждого input: любое изменение bytes
меняет output. Verifier заново выполняет ту же композицию, сравнивает current bytes,
metadata/report/tree; source2_compiled/runtime_verified остаются false.

## Helpers и ограничения

Существующие build/verify helpers сохраняют probe/default и exact13HUD policies.
Добавляется только точная третья policy. Общие ограничения пути/размера/Windows
casefold/symlink/reparse/exclusive child output применяются также ко всем layout_inputs.
Композиция проверяется до создания output. Policy/composer из tools/preparation_layout.py
в C2-11-02 загружается helper только для нового kind; новые build/verify wrappers не нужны.
Скопированные JS/CSS/manifest bytes сохраняются, преобразуется только shell XML.

## Проверки и открытая приёмка

Python RED→GREEN: exactpolicy/paths/inputs/graph/root/id/refs/inert/source fingerprints,
полный build+verify, tamper/currentinput/overwrite/unexpectedfile/reportstatus, CLI.
Node VM получает IDs/scripts именно generatedlayout и explicit bind/dispose: четыре
watchers, actual team click изменяет общий context; загрузка определений инертна.
Прежние522 sourcechecks повторяются, пять read-only критиков, journal/links/config.
Полный игровой аддон, installer, native compile/layout/scroll/hittest, реальные
каталоги/C1/server/effects/secondowner остаются открытыми. Windows не подключена.
