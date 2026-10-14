# TEST lifecycle source verification — 14 October 2026

Lead role: C1 server lifecycle/clock guard; scope C1-only TEST entrypoint and its Lua 5.1 tests. Acceptance: exact request/reply schema, original sender before DTO reads, owned player/hero pin, capability inspection before effects, once-only activation delegation. Independent C2 review remains required. No progress flags changed.

Actual RED: `test_coach_scene.py` ran 6 tests, 2 failures `TEST lifecycle fixture missing`; log `build/dota_coach/coach-scene-fixture-red.log`.

Actual GREEN after adding the real fixture and three failure-path tests: same suite ran 9 tests, 0 failures/skips, exit 0; log `build/dota_coach/coach-scene-fixture-green.log`. Related actual controller/adapter/roster/scene regression ran 41 tests, 0 failures/skips, exit 0; log `build/dota_coach/coach-scene-fixture-regression.log`.

Runtime: `C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; `PYTHONUTF8=1`; `PYTHONPATH=D:/AI/dota2coach/build/dota_coach/c1-review-lua-20261013/deps;D:/AI/dota2coach/build/python-deps`; import `lupa.lua51.LuaRuntime`. Tests execute actual production controller/native adapter/scene wrapper and actual fixture, without runtime copies in tests.

Targeted command:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONPATH='D:/AI/dota2coach/build/dota_coach/c1-review-lua-20261013/deps;D:/AI/dota2coach/build/python-deps'
& 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' creators/creator-1/11-integration/01-ui-contracts/tests/test_coach_scene.py
```

Verified: caps has no effects; pause/unpause reflected by stub observation; paused kill rejected; kill/respawn scoped to pinned hero; native effect exception explicit; extra fields/version/metatable/mismatched engine metadata rejected; foreign source and replacement owner/hero cause zero raw DTO reads; original input metadata preserved; addressed 13-field reply; report keeps game time and wall time separate; activation once.

Unverified: actual engine availability/signatures/effects, game-clock pause/lease causality, death/generation transitions, full/native scene, physical input, real profiles, product/legal acceptance. An effect that throws may already have partially happened; rejected `native_effect_failed` does not claim rollback. No native client launched here.

Project lesson: the pre-existing six scene tests exposed an absent TEST entrypoint (cause: the saved implementation stopped before Task D fixture). Supply the single-source fixture under C1-02-03, preserving normal scene wrapper and separate TEST recipe, then execute actual Lua 5.1. The missing-file RED and nine-test GREEN establish the repair without treating engine stubs as native proof.
