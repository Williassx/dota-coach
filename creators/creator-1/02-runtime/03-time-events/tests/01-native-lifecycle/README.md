# TEST lifecycle probe

[Parent](../../README.md) · [Actual Lua 5.1 tests](../../../../11-integration/01-ui-contracts/tests/test_coach_scene.py)

[Verification and project lesson](verification-2026-10-14.md) records RED/GREEN, commands, and native limits.

`coach_scene_fixture.lua` is the addon entrypoint only in the separate TEST coach-scene recipe. It requires the single `coach_scene_game_mode` source and captures/delegates its `Activate`, once. Normal recipes must not include it.

Event `dota_coach_scene_test` accepts exactly `protocol_version=1`, `request_id`, `kind` (`caps/report/pause/unpause/kill/respawn`). Only matching engine `PlayerID` metadata is removed from a copy. Original native sender resolution precedes DTO reads; after the first valid request the player handle and selected owned real hero are pinned. Replacement player/hero cannot inherit authority.

Addressed reply `dota_coach_scene_test_state` contains exactly 13 fields: protocol_version/request_id/kind/status/reason/game_time/wall_time/paused/alive/entity_index/cap_pause/cap_kill/cap_respawn. Boolean observations/capabilities use 0/1. `caps/report` never mutate. Missing native effects are `unsupported`; kill/respawn while paused are rejected. Native exceptions report `native_effect_failed`, without pretending rollback. Game time and Time are separate raw engine observations, not a calibrated clock or proof of causality.

Lua 5.1 engine-stub tests exercise the real wrapper/modules; native availability/effects/input/game acceptance remain separate experiments. No automatic activation, normal import side effects, production transport, or permission claim.
