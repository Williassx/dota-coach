# Native test-only HUD binding fixture

[Тесты](../README.md) · [Спецификация](../../native-binding-design.md) · [План](../../native-binding-plan.md).

[Manifest](custom_ui_manifest.xml) и [driver](hud_binding_fixture.js) используют
canonical HUD inputs через [fixture builder](../../../02-addon-packaging/tools/build_native_hud_fixture.py).
Generated15outputs — отдельная test-only fixture, не fixed source kind.
Явные TEST/synthetic данные; no transport/gateway/entity/real profiles/native input.
Пять фаз проверяют существующие модули, не дублируют их реализацию.
