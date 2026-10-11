# Source-проверка text preview пакета

[Подпункт](../README.md) · [План](../voice-text-plan.md).

**Дата UTC:** 2026-10-11. **Основа:** b555a3b. Commit — в истории записи.

Добавлены canonical source manifest в C2-06-03, fixed six-resource recipe/validator/
11 сценариев в C2-11-02; existing builder подключает шестой kind. Strict XML parse,
dependency и Hud loader policy переиспользуются из existing composer; optional
trusted TextEntry разрешение не меняет default для старых видов. Существующий
verifier/source/path/output policy сохранён. Никаких копий JS в библиотеках нет.

Первый RED запуск: пять ERROR, включая ошибочный test import. Исправлен import
существующего load helper без production изменения: четыре ERROR/семь защитных
PASS из11 до поддержки kind. Затем все11 PASS. Packaging74/foundation28 PASS.
Проверены byte roundtrip/5links, fixed complete mapping, dependencyorder/reach,
required IDs/topology/plaintext, leaf/disabled/empty TextEntry, DTD/entities/text/
events/tags, one-parent Hud manifest, symlink/current-source/tampered output,
existingoutput и сохранение старого запрета TextEntry. Actual packaged XML tree
и три JS definitions в одном VM: explicit bind/snapshot/input/button→proposal A,
без игровых API; dispose очищает таймер.

Actual CLI output `build/dota_coach/probe-ui-20261011T083247Z-fcfde1`:
6assets/5links/package_verified=true; source2_compiled/runtime_verified=false.
Полная регрессия: **33 suites/760 PASS**, нулевыеfail/skip/cancelled/todo.
Один reused итоговый read-only критик не выявил существенных дефектов в mapping,
XML/пути/топологии, default oldkind safety и current-source byte validation.
Без нового кода full regression не повторялся. График30/198действий (15.2%).
Native compile/TextEntry/layout/hittest, общий runtime/переходы, микрофон/ASR,
server transport/authority/эффект и другой человеческий владелец открыты.
