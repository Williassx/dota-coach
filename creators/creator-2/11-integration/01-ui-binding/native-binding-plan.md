# План native проверки explicit HUD binding

> Исполнение: superpowers:executing-plans, основной исполнитель; независимый помощник
> извлекает API read-only, один итоговый критик после результата.

**Goal:** проверить существующую local HUD привязку в настоящем Panorama.
**Architecture:**15-resource test-only fixture, derived canonical layout, explicit TEST
driver; fixed source kinds, C1 и production modules сохраняются.
**Tech Stack:** bundled Python3.12.14, Node24.19, Windows Source2/Dota25845666/VConsole.
**Spec:** [native-binding-design.md](native-binding-design.md), [design.md](design.md).

## Global Constraints

- Только creator2; source library first; generated build не редактировать.
- Fixed HUD13/12 не расширять;15 test outputs отдельно от fixed source kind.
- TEST/synthetic/null hero, clock0, options now/maxAgeMs1000; нет send/gateway/resolver.
- Новый отдельный addon dota_coach_c2_hud_binding_20261012; не заменять addons.
- Owned process only; ОС/привилегии/Steam/чужие процессы не менять.

## Review Focus

- Неизменённые canonical bytes и fixed manifest: тестировать до native установки.
- Missing fixture input/invalid recipe/output path: отказ до создания output.
- Layout/update delays: log predicates после layout, screenshot между фазами.
- Snapshot removal/hidden slots: реальные Labels/width/visible и actual frame.
- Dispose/rebind/stale handle: старый DTO getter не читается и fresh label не меняется.

## 1. Test-only fixture builder

Files: ../02-addon-packaging/tools/build_native_hud_fixture.py;
../02-addon-packaging/tests/test_native_hud_fixture.py;
tests/native-hud-binding/{README.md,custom_ui_manifest.xml,hud_binding_fixture.js}.
API: build_fixture(repository:Path,output:Path)→dict;
reuse prepare_assets/read_source/output_path existing bounded fixed policy.

- [x] RED: exact15/12 copied canonical inputs/derived scripts/unchanged source;
  existing/output escape/invalid fixed mapping/missing driver refuse before writes.
- [x] Implement minimal builder, source-only fixture report with false native flags.
- [x] GREEN, JS syntax and existing20package/26HUDbinding checks.

## 2. Native run

- [x] Fresh fixture output, verify all source/output hashes; copy15UI files and separate
  Valve template_map/addoninfo into absent named content/game directories.
- [x] Compile manifest/map, count actual outputs/VPK, save hashes/logs.
- [x] Launch own client with known flags/fresh log; live unique echo, PRE_GAME.
- [x] Record bound/selected/removed/disposed/rebound native predicates and screenshots
  at least2seconds after each phase, before next setter; inspect all actual PNG.
- [x] Quit owned client and verify process gone. Required guards failures stay failures.

## 3. Review and publication

- [x] Full source runner after new code; distinguish required known failed suites.
- [x] Report reports/native-hud-binding-2026-10-12.md, source/report/tests/tool indices,
  windows-resume, current UTC journal/learning/usage; product checkboxes only evidence.
- [x] One final read-only review and fixes, document/graph/diff checks.

Затем normal authorized commit/push, remote SHA/clean checkout; revision публикации
сохраняется Git history и ответом основного исполнителя.

Ruling: user explicitly authorised continuous autonomous execution; existing HUD
specification remains binding. This plan covers an isolated acceptance fixture,
not a new product architecture or fake C1 integration.
