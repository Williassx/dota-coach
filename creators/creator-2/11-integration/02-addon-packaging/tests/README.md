# Проверки пакета HUD

[Подпункт](../README.md) · [test_hud_bundle.py](test_hud_bundle.py).

20 Python-сценариев, включая Node VM definitions-only load и реальные CLI во временном
repo. Проверяют fixed policy, graph/order/IDs/empty states, сохранность bytes/output,
подмену/лишние файлы/report flags и запрет рекурсивной разметки. Не native Dota.

Новая проверка initial slots разрешает только текущие plain class CSS rules;
не моделирует полный CSS cascade. [Отдельная native setter fixture](native-css-visibility/README.md)
не входит в fixed kind и не заменяет полный HUD bind.

- [test_preparation_bundle.py](test_preparation_bundle.py)
- [test_intervention_bundle.py](test_intervention_bundle.py)
- [test_intervention_screen_bundle.py](test_intervention_screen_bundle.py)
- [test_voice_text_bundle.py](test_voice_text_bundle.py)

- [test_orders_timeline_bundle.py](test_orders_timeline_bundle.py).

- [test_opponent_roster_bundle.py](test_opponent_roster_bundle.py) — 8 сценариев
  публичного состава, включая actual packaged XML/JS в одном VM-контексте.

- [test_match_observation_bundle.py](test_match_observation_bundle.py) — 8 сценариев
  общей сцены, exact scopes/fingerprints и actual packaged group binding.

[test_mouse_proposal_bundle.py](test_mouse_proposal_bundle.py) — 8 сценариев fixed mapping, topology, strict XML, source/output integrity и actual packaged VM.

[test_mouse_targeting_bundle.py](test_mouse_targeting_bundle.py) — 8 сценариев: 6 reused guards и 2 package graph/actual context проверки.

[test_native_hud_fixture.py](test_native_hud_fixture.py) —7сценариев independent
fixture builder: canonical bytes/derived graph, repeatable assets и отказ до writes
для invalid mapping/manifest/missing driver/output escape/существующего output.
[test_native_voice_fixture.py](test_native_voice_fixture.py) —7сценариев isolated
native voice fixture; anonymous root, unchanged canonical bytes, deterministic
assets и refusal до writes для unsafe mapping/manifest/missing/output paths.

[test_native_preparation_fixture.py](test_native_preparation_fixture.py) —7проверок
17output fixture: composed canonical subtree/raw fingerprints и refusal guards.
test_preparation_bundle.py также проверяет anonymous outer/inner native topology.

[test_native_observation_fixture.py](test_native_observation_fixture.py) —7проверок
12output fixture: exact canonical subtree,12raw input hashes/2XML inputs, refusal
guards. Match observation package дополнительно проверяет anonymous outer shape.

[test_native_intervention_fixture.py](test_native_intervention_fixture.py) —7проверок
15output fixture и15raw input hashes. Screen package сохраняет50ID/root rename,
дополнительно проверяет exact anonymous outer и bind inner scope в actual VM.
