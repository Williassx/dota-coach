# План source-пакета подготовки

> Для исполнителя: superpowers:executing-plans/TDD, один редактор, пять read-only критиков.

**Goal:** один generated layout с actual module trees и определениям общей цепи.
**Architecture:** fixed recipe + composer, прежние build/verify сохраняют свои guards.
**Stack:** Python3 stdlib/ElementTree, ES5/NodeVM. **Spec:** [preparation-design.md](preparation-design.md).

## Ограничения и review focus

Не копировать source modules, не менять старые kinds/default, только15 exact outputs.
Неправильный input root/dependencies/IDs → отказ до output; accessor/native не нужен.
Symlink/oversized input → отказ; nestedlayouts/event attrs → отказ; сырые input bytes
в fingerprints; current source mismatch/false runtime/foreign outputs сохраняются.

## 1. Recipe и детерминированная композиция

**Create:** preparation-manifest.json, tools/README.md, tools/preparation_layout.py,
tests/test_preparation_bundle.py. Shell/style/manifest в C2-11-01/src/panorama с README.
**Modify:** foundation build_probe_bundle.py для fixedthirdkind/lazycomposer;
verify_probe_bundle.py использует прежний prepare_assets API без новой логики.

- [x] Python exactpolicy/composition/build/failures tests RED.
- [x] Implement prepare(repository,manifest,shared_helpers) → list(source,target,bytes).
- [x] GREEN; current canonical source fingerprints/graph/inert structure проверены.

## 2. Проверка и публикация

- [x] Actual CLI build+verify нового child build/dota_coach; existing outputs preserved.
- [x] NodeVM load generated dependency order, actual generated tree bind/click/dispose.
- [x] Пять критиков; конкретные defects RED→GREEN; previous522 +new suites PASS.
- [x] Notes/report/README/планы/журнал, syntax/links/diff, только start_skill/readback.
- [x] Commit/fast-forward main/remoteSHA/clean; native/сервер/второй владелец открыты.

Опубликован d5066a2; remoteSHA/clean проверены.
