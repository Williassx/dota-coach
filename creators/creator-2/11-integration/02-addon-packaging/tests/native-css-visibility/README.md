# Нативная проверка visible setter

[Проверки](../README.md) · [План](../../native-scene-plan.md).

Это отдельная test-only native fixture, не fixed source kind и не часть HUD13
или probe. Собственные [manifest](custom_ui_manifest.xml), [layout](css_visibility.xml)
и [script](css_visibility.js) устанавливаются в отдельный тестовый addon.
coach_hud.css берётся из единственного источника C2-07-01; карты/addoninfo —
из штатных установленных Tools templates по native-scene-plan.

Скрипт использует только Panel.visible, native layoutwidth/height, $.Schedule/Msg
в собственном контексте. Он не bind игровой HUD и не выдаёт игровые действия.
Цикл initial→shown→hidden→reshown проверяет default collapse, переключение
visible=true/false и положительную ширину/высоту с видимым root после показа.
Initial ожидает false/0×0; hidden ожидает false, но cached layout может сохраниться.
Фактическое изображение каждой фазы проверяется отдельно после native layout.
[Результаты](../../reports/native-hud-scene-2026-10-12.md) не доказывают полный bind.
