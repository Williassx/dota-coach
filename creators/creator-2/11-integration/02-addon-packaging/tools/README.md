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

- [mouse_targeting_layout.py](mouse_targeting_layout.py) — reuse standalone mouse prepare/validate, generated four-script dependency order, raw fingerprint, exact7/6.

- [build_native_hud_fixture.py](build_native_hud_fixture.py) — отдельный test-only
  builder15outputs из existing fixed HUD inputs. Не расширяет fixed kinds/probe policy;
  strict/bounded guards и source-only flags сохранены. [План](../../01-ui-binding/native-binding-plan.md).
- [build_native_voice_fixture.py](build_native_voice_fixture.py) — отдельный test-only
  builder8outputs из6canonical voice inputs; exact non-executable manifest,
  strict mapping и preserved bytes. Не расширяет fixed kind/probe policy.

- [build_native_preparation_fixture.py](build_native_preparation_fixture.py) —17outputs
  отдельной TEST сцены;15canonical composed outputs/18raw input hashes с3XML inputs,
  strict manifest/path policy и retained generated layout, fixed15/14 без auto-bind.

- [build_native_observation_fixture.py](build_native_observation_fixture.py) —12outputs
  TEST scene opponents/history;10canonical composed outputs/12raw input hashes,
  strict manifest/path policy и retained generated layout, fixed10/9 без auto-bind.

- [build_native_intervention_fixture.py](build_native_intervention_fixture.py) —15outputs
  TEST scene карточек/запроса;13canonical outputs/15raw inputs с2XML inputs,
  strict manifest/path guards, fixed13/12 и preserved source-only flags.
