# Проверки пакета HUD

[Подпункт](../README.md) · [test_hud_bundle.py](test_hud_bundle.py).

19 Python-сценариев, включая Node VM definitions-only load и реальные CLI во временном
repo. Проверяют fixed policy, graph/order/IDs/empty states, сохранность bytes/output,
подмену/лишние файлы/report flags и запрет рекурсивной разметки. Не native Dota.

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
