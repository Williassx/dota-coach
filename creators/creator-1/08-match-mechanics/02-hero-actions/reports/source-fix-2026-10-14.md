# Capability kind source fix — 14 October 2026

Independent C2 review reproduced an item accepted as an ability and the converse. C1 author repaired only the existing pure `src/hero_actions.py` gate: supported action membership uses the requested kind's pool. Unavailable action remains `ability-unavailable`; bad kind remains `bad-kind`; patch/cooldown/profile guards remain. No engine invocation or measured hero capability claim.

Actual `tests/test_hero_actions.py`: RED 5 tests/1 failure, then GREEN 5 PASS/0 skips. Logs `build/dota_coach/c1-hero-kind-{red,green}-20261014.log`. Command: bundled Python executable `C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` with this test path, `PYTHONUTF8=1`.

New actual-source test checks blink/ability and call/item reject, and corresponding correct kinds accept. Project lesson: combining allowed pools erased the kind boundary; select one declared pool before membership admission and test both crossover directions. Independent C2 regrade remains separate; native/product criteria unchanged.
