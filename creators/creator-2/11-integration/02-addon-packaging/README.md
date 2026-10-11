# C2-11-02 — Сборка аддона из библиотек

**Отдел:** создатель 2. **Проверяющий:** создатель 1.
**Статус:** частично подготовлено: ранний source-пакет общего HUD с проверкой
целостности; полный аддон, установка/компиляция/runtime и второй владелец открыты.
**Зависимости:** [C2-11-01](../01-ui-binding/README.md), [C2-10-01](../../10-user-testing/01-install-guide/README.md).
**Рабочая папка:** `creators/creator-2/11-integration/02-addon-packaging/`.

[Раздел](../README.md) · [План создателя](../../PLAN.md) · [Общие правила](../../../shared/WORKFLOW.md)

## Действия

- [x] Собрать и проверить отдельный source-пакет публичных соперников из 5 ресурсов.
- [x] Собрать и проверить отдельный source-пакет истории приказов из 5 ресурсов.
- [x] Собрать и проверить source-сцену карточек/запроса: 13 ресурсов, один контекст, fingerprints исходных XML.
- [x] Собрать и проверить отдельный source-пакет text preview из 6 ресурсов.
- [ ] После локального аудита согласовать manifest исходников и конечные game/content пути.
- [ ] Собирать отдельный создаваемый каталог, сохраняя оригиналы в папках авторов.
- [x] Создать и проверить отдельный source-пакет из 13 UI-ресурсов без установки.
- [x] Собрать и проверить отдельный source-пакет подготовки из 15 ресурсов.
- [x] Собрать и проверить отдельный source-пакет ручного запроса из 6 ресурсов.
- [ ] Проверить полноту и отсутствие дублей серверных/UI исходников.
- [ ] Сопоставить фактический результат с критерием ниже и записать непроведённые проверки.
- [ ] Передать изменение второму создателю для проверки, затем обновить этот статус.

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
source2_compiled/runtime_verified=false. Никаких server/map/VPK/demo ресурсов нет.

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
