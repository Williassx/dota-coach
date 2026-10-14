# Nested save ownership source fix — 14 October 2026

Independent C2 review reproduced nested payload aliasing despite the declared fresh-structure boundary. C1 author repaired existing `src/save_compat.py`: deep-copy payload when saving and when loading. Save version1, keys and compatibility reasons unchanged. No file persistence, serializer, migration or engine behavior added.

Actual `tests/test_save_compat.py`: RED 6 tests/2 failures, then GREEN 6 PASS/0 skips. Logs `build/dota_coach/c1-save-copy-{red,green}-20261014.log`. Command: bundled Python executable `C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` with this test path, `PYTHONUTF8=1`.

New actual-source tests mutate nested original/save data in both directions, mutate nested saved/restored data in both directions and verify current state untouched. Project lesson: a fresh wrapper is insufficient when its nested payload retains aliases; copy at each ownership boundary and verify mutations independently. Independent C2 regrade and native persistence acceptance remain separate.
