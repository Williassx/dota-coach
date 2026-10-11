# tools — source layout policy и композиция

[Родитель](../README.md).

- [preparation_layout.py](preparation_layout.py) — точная policy и композиция;
  вызывается существующим build helper, не отдельный installer/CLI.

- [intervention_screen_layout.py](intervention_screen_layout.py) — точная композиция
  canonical roster/request scopes, также через существующий build helper.

- [voice_text_layout.py](voice_text_layout.py) — fixed six-resource text preview;
  использует общую strict XML policy с отдельным trusted TextEntry разрешением.

- [orders_timeline_layout.py](orders_timeline_layout.py) — fixed five-resource history; общая XML policy с local Panel.visible разрешением.
