# tools — source layout policy и композиция

[Родитель](../README.md).

- [preparation_layout.py](preparation_layout.py) — точная policy и композиция;
  вызывается существующим build helper, не отдельный installer/CLI.

- [intervention_screen_layout.py](intervention_screen_layout.py) — точная композиция
  canonical roster/request scopes, также через существующий build helper.

- [voice_text_layout.py](voice_text_layout.py) — fixed six-resource text preview;
  использует общую strict XML policy с отдельным trusted TextEntry разрешением.

- [orders_timeline_layout.py](orders_timeline_layout.py) — fixed five-resource history; общая XML policy с local Panel.visible разрешением.

- [opponent_roster_layout.py](opponent_roster_layout.py) — пять фиксированных ресурсов
  публичного состава; проверяет точный порядок карточек и принадлежность их подписей,
  использует прежний XML parser с локальным разрешением Panel.visible.

- [match_observation_layout.py](match_observation_layout.py) — фиксированная
  композиция двух canonical scopes в shell; использует validate_layout прежних
  opponent/history policies, raw fingerprints и проверку generated topology.

- [mouse_proposal_layout.py](mouse_proposal_layout.py) — fixed 5/4, exact 7 IDs и 6 plain Labels; shared XML parser, отдельное разрешение root.visible.
