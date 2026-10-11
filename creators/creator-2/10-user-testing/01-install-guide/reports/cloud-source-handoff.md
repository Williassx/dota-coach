# Облачная проверка source handoff

[Подпункт](../README.md) · [План](../implementation-plan.md).

**Дата UTC:** 2026-10-11. **Основа:** cd45ebe. Commit — в истории записи.

Один helper выбирает canonical recipe из шести fixed screens и делегирует build/
verify единственным foundation helpers. Immutable companion report вне bundle
связывает source graph/assets/digests, platform/Python и same-root Git metadata.
Existing report/output не перезаписываются; source/Steam/Tools не редактируются.
Native destination null, installation=false, all nativechecks=not_run. Report
означает источник evidence на момент source verification, не разрешение запуска.

14 тестов: сначала всеERROR из-за отсутствующего модуля, затем14PASS. Проверены
default/all six recipes/actual CLI, fixedkind/unknown/missing/large recipe,
source/recipe symlinks, existingreport/bundle, tamper/current-source/wrongscreen/
externalbundle, actual same-root Git HEAD/dirty безorigin. Full34suites/774PASS,
нулевыеfail/skip/cancelled/todo. Actual voice-text handoff:
build/dota_coach/probe-ui-20261011T084803Z-887038, companion `.handoff.json`,6/5.
Git cd45ebe/dirty=true честно отражает незафиксированную текущую задачу; источник
не объявлен clean. Один reused finalcritic не выявил существенных дефектов в
выборе recipe, путях/integrity/nooverwrite/metadata или native claims.
Full regression без нового кода не повторялся. График31/199действий (15.6%).
Windows execution/установка/Source2compile/scene/hittest/ASR/server/MANUAL/ИИreturn
и другой человеческий владелец открыты. Native checklist не закрывался.
