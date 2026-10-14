# C2-11-02 — Сборка аддона из библиотек

**Техническое рассмотрение14октября:** [отдельный peer другого создателя](../../../creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.md). Выполненная передача относится к техническому объёму; полная функциональная, продуктовая и правовая приёмка не следует из этого checkbox. Более ранние статусы ниже относятся к указанному в них срезу.

**Отдел:** создатель 2. **Проверяющий:** создатель 1.
**Статус:** частично подготовлено: ранний source-пакет общего HUD с проверкой
целостности; native HUD13 установлен отдельно и скомпилирован на Windows.
Полный аддон, запуск/интерактивная приёмка и второй владелец открыты.
**Зависимости:** [C2-11-01](../01-ui-binding/README.md), [C2-10-01](../../10-user-testing/01-install-guide/README.md).
**Рабочая папка:** `creators/creator-2/11-integration/02-addon-packaging/`.

[Раздел](../README.md) · [План создателя](../../PLAN.md) · [Общие правила](../../../shared/WORKFLOW.md)

## Отдельная source-сцена тренера

[Упаковщик](tools/build_coach_scene.py) · [Проверки](tests/test_coach_scene_bundle.py).
Новый отдельный helper сохраняет прежние fixed kinds: normal 15 outputs
(8 Lua, 3 JS, canonical manual XML, derived scene XML, CSS, manifest);
`--test-fixture` 18 outputs добавляет отдельные Lua/JS/derived XML fixtures.
Normal содержит 6 active UI outputs и 1 retained layout; TEST — 7 active и
2 retained layouts. API: `prepare(repo, test_fixture=False)`,
`build_bundle(repo, output, test_fixture=False)`, `verify_bundle(repo, output)`.
CLI: `--output <fresh build/dota_coach child>`, `--test-fixture`, `--verify <bundle>`.
Проверка повторно читает canonical sources, композицию и receipt hashes;
недоступные inputs, лишние файлы и reparse paths отклоняются. Source flags
`source2_compiled/runtime_verified=false`; установка и native запуск отдельны.

## Действия

- [x] Собрать и проверить source-пакет мыши с private наблюдением целей из 7 ресурсов.

- [x] Собрать и проверить отдельный source-пакет предложений мыши из 5 ресурсов.

- [x] Собрать и проверить общую source-сцену соперников и истории из 10 ресурсов и двух canonical XML inputs.
- [x] Собрать и проверить отдельный source-пакет публичных соперников из 5 ресурсов.
- [x] Собрать и проверить отдельный source-пакет истории приказов из 5 ресурсов.
- [x] Собрать и проверить source-сцену карточек/запроса: 13 ресурсов, один контекст, fingerprints исходных XML.
- [x] Собрать и проверить отдельный source-пакет text preview из 6 ресурсов.
- [x] После локального аудита согласовать manifest исходников и конечные game/content пути. Выполнено14октября в limited manual/roster scene; physical input/полная игра отдельно открыты. [Доказательства](../../01-foundation/01-workspace-audit/reports/c2-functional-closure-recommendations-2026-10-14.md).
- [x] Собирать отдельный создаваемый каталог, сохраняя оригиналы в папках авторов. Выполнено14октября в limited manual/roster scene; physical input/полная игра отдельно открыты. [Доказательства](../../01-foundation/01-workspace-audit/reports/c2-functional-closure-recommendations-2026-10-14.md).
- [x] Создать и проверить отдельный source-пакет из 13 UI-ресурсов без установки.
- [x] Собрать и проверить отдельный source-пакет подготовки из 15 ресурсов.
- [x] Собрать и проверить отдельный source-пакет ручного запроса из 6 ресурсов.
- [x] Проверить полноту и отсутствие дублей серверных/UI исходников. Выполнено14октября в limited manual/roster scene; physical input/полная игра отдельно открыты. [Доказательства](../../01-foundation/01-workspace-audit/reports/c2-functional-closure-recommendations-2026-10-14.md).
- [x] Сопоставить фактический результат с критерием ниже и записать непроведённые проверки. Сопоставление source/native и непроведённых сценариев оформлено14октября. [Доказательства](reports/autonomous-acceptance-2026-10-14.md).
- [x] Передать изменение второму создателю для проверки, затем обновить этот статус. Техническая передача и independent peer review14октября выполнены; функциональные ограничения сохранены. [Доказательства](../../../creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json).

## Результат и приёмка

Сборка использует единственные исходники и не перезаписывает установку без отдельного действия.

## Source-пакет local text preview

[Дизайн](voice-text-design.md) · [План](voice-text-plan.md) · [Recipe](voice-text-manifest.json) ·
[Policy](tools/README.md) · [Команды](notes/voice-text-package.md) · [Отчёт](reports/cloud-voice-text-package.md).

Шестой fixed kind содержит6 ресурсов/5ссылок, один context Roster→VoiceText→Panel.
Dedicated TextEntry policy сохраняет старые defaults. Actual packaged context
проверен на typed input/button→local proposal; общий итог760 source checks.
Пакет альтернативный, native/ASR/C1/runtime/второй владелец ещё открыты.

## Подготовленные материалы

- [Дизайн](design.md), [план](implementation-plan.md), [manifest](bundle-manifest.json).
- [Проверки](tests/README.md), [команды/политика](notes/build-manifest.md), [отчёт](reports/cloud-hud-bundle.md).
- [Единственные build/verify helpers](../../01-foundation/02-panorama-capability/tools/README.md).

Kind HUD разрешает ровно 13 source→target пар. Старый probe/defaultmanifest сохраняют
ограничения. Build output отдельный/исключён из Git; не редактируется вручную.
В source-only reports source2_compiled/runtime_verified=false. Никаких server/map/VPK/demo ресурсов нет.

[Нативная компиляция HUD 11 октября](reports/native-hud-2026-10-11.md): новый
отдельный addon, 13 непустых compiled outputs, 13/13 source SHA-256 совпадают,
19 package + 26 binding PASS. Runtime/bind/input/C1 этим не подтверждены.

## Source-пакет подготовки

[Дизайн](preparation-design.md) · [План](preparation-plan.md) ·
[Recipe](preparation-manifest.json) · [Composer](tools/README.md) ·
[Команды](notes/preparation-package.md) · [Отчёт](reports/cloud-preparation-package.md).

Третий fixed kind собирает15 ресурсов и вставляет три canonicalXML дерева в один
shell. Verifier сверяет повторную композицию из current rawinputs.20 новых сценариев,
общий итог542. Пакет альтернативен matchHUD; общий переход/manifest/native открыты.

## Source-пакет ручного запроса

[Дизайн](intervention-design.md) · [План](intervention-plan.md) ·
[Manifest](intervention-manifest.json) · [Команды](notes/intervention-package.md) ·
[Проверка](reports/cloud-intervention-package.md).

Четвёртый fixed kind содержит6ресурсов, one inert Hud layout и3definitions.13новых
сценариев; полный итог648. Пакет альтернативный, не общий runtime/установка/автопривязка.

## Общая source-сцена карточек и запроса

[Дизайн](intervention-screen-design.md) · [План](intervention-screen-plan.md) ·
[Recipe](intervention-screen-manifest.json) · [Композиция](tools/README.md) ·
[Команды](notes/intervention-screen-package.md) · [Отчёт](reports/cloud-intervention-screen-package.md).

Пятый fixed kind собирает 13 ресурсов и две canonical XML scopes в одном контексте
с восемью JS definitions. Raw input fingerprints и повторная композиция связывают
пакет с текущими исходниками. Общий итог 701 source-проверка; bootstrap, компиляция,
игровая геометрия, C1 authority и проверка второго владельца ещё открыты.

## Source-пакет истории приказов

[Дизайн](orders-timeline-design.md) · [План](orders-timeline-plan.md) ·
[Recipe](orders-timeline-manifest.json) · [Команды](notes/orders-timeline-package.md) ·
[Отчёт](reports/cloud-orders-timeline-package.md).

Седьмой fixed kind: пять ресурсов, два definitions, четыре resource links, exact inert
layout последних записей. Старые defaults сохраняются. Source-only alternative Hud,
без bootstrap/transport/native установки. Handoff screen: orders-timeline.

## Source-пакет публичных соперников

[Дизайн](opponent-roster-design.md) · [План](opponent-roster-plan.md) ·
[Recipe](opponent-roster-manifest.json) · [Команды](notes/opponent-roster-package.md) ·
[Отчёт](reports/cloud-opponent-roster-package.md).

Восьмой фиксированный вариант: пять ресурсов и четыре ссылки, 17 пустых plain
Labels и 7 контейнеров. Отдельная панель пяти соперников сохраняет канонические
исходники C2-07-02. Проверены порядок, принадлежность полей карточкам, целостность
и поведение упакованного контекста. Handoff selector: `opponent-roster`.
Серверная политика доступа, общий HUD, установка, запуск Dota и второй владелец открыты.

## Общая source-сцена наблюдения

[Спецификация](../01-ui-binding/match-observation-design.md) ·
[План](../01-ui-binding/match-observation-plan.md) · [Recipe](match-observation-manifest.json) ·
[Команды](notes/match-observation-package.md) · [Отчёт](../01-ui-binding/reports/cloud-match-observation.md).

Девятый fixed kind: 10 ресурсов / 2 canonical XML inputs / 9 links / 38 ID.
Верхний ряд соперников и история справа управляются одним parent binding;
поддерживается отдельная готовность источников. Source fingerprints и повторная
композиция сохраняют единственные исходники. Selector: `match-observation`.
Это read-only вариант; весь игровой HUD, bootstrap/C1 ещё открыты. Отдельный
[native smoke](../01-ui-binding/reports/native-observation-2026-10-12.md) проверил
existing explicit API/render; fixed10/9 сохранён, source flags не повышены.

[Mouse proposal recipe](mouse-proposal-manifest.json) ·
[Инструкция](notes/mouse-proposal-package.md).

[Mouse targeting recipe](mouse-targeting-manifest.json) ·
[Дизайн](mouse-targeting-design.md) · [План](mouse-targeting-plan.md) ·
[Инструкция](notes/mouse-targeting-package.md).

## Нативная сцена пустого HUD

[План](native-scene-plan.md) · [Фактические кадры и проверки](reports/native-hud-scene-2026-10-12.md).
HUD13/12 загружен в отдельной Dota fixture при1280×720 и1920×1080; исправлен
canonical CSS initial slots и отступов от штатного UI. Kind/JS/bootstrap не расширены.
Полная регрессия, input, bind, C1 и рассмотрение другого создателя остаются открытыми.

[Отдельный explicit native binding smoke](../01-ui-binding/reports/native-hud-binding-2026-10-12.md)
проверяет TEST/synthetic bind/selection/removal/dispose/rebind. Test-only builder15
source outputs даёт14active compiled UI outputs; fixed kind13/12 не меняется.
[Native text preview evidence](../../06-voice/03-voice-feedback/reports/native-voice-text-2026-10-12.md)
проверяет отдельную сцену и existing explicit VoicePanels. Canonical voice XML
исправлен под native anonymous root; fixed6/5 сохранён. Test-only8sources/7active
compiled dependencies; canonical inert XML также компилируется отдельно.

[Native preparation report](../01-ui-binding/reports/native-preparation-2026-10-12.md)
проверяет existing три private drafts в отдельной TEST сцене. Source kind15/14
сохранён,17fixture resources/16active compiled +retained layout отдельно. Native
визуальные подписи и API scroll исправлены; production переход/C1/input/owner открыты.

[Native intervention smoke](../01-ui-binding/reports/native-intervention-2026-10-12.md): fixed13/12 и50ID сохранены,15fixture sources/14active compiled +retained canonical XML. Восемь API фаз и16frames проверяют выбранного B/captured A, actual ACK timer и dispose/rebind. Scoped CSS исправил pane visibility; TEST stub, source checks и screen evidence не подтверждают server/input authority.

[Native targeting smoke](../01-ui-binding/reports/native-mouse-targeting-2026-10-12.md): fixed7/6/7ID не расширен. Девять TEST outputs/8active compiled +retained canonical XML отдельно. Raw inputs и composed output fingerprints разделены, required full verified=false сохранён.
