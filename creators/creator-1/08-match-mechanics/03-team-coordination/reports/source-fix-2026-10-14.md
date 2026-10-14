# Atomic team target conflict source fix — 14 October 2026

Independent C2 review reproduced two roles receiving the same sole target despite the declared unique-resource rule. C1 author repaired existing `src/team_orders.py`: reject insufficient targets atomically as `None/resource-conflict`, then index targets without wraparound. No target search/engine orders or additional coordination mechanic. Existing unreachable/policy/confirmation semantics remain.

Actual `tests/test_team_orders.py`: RED 6 tests/4 failed subtests (all four declared orders), then GREEN 6 PASS/0 skips. Logs `build/dota_coach/c1-team-conflict-{red,green}-20261014.log`. Command: bundled Python executable `C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` with this test path, `PYTHONUTF8=1`.

New actual-source test checks attack/retreat/farm/gather shortage yields no partial assignments and preserves all inputs. Project lesson: unique input targets do not guarantee unique assigned targets when modular indexing repeats them; validate cardinality and remove wraparound. Independent C2 regrade/native acceptance remain separate.
