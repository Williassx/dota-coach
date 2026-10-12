# Проверки камеры

[Подпункт](../README.md) · [camera.test.cjs](camera.test.cjs).

27 сценариев node:test/vm: native guards, отсутствие автоматического движения,
явный клик, повторная проверка смерти, жизненный цикл, повторный вход, устаревшие
callbacks/results и одинаковые имена. API позиции/приказов/слежения запрещены mock.
Набор не подтверждает actual camera arrival, native hittest или связь игрока с entity.

[7 Python builder checks](test_native_camera_fixture.py): canonical hashes/subtree,
determinism, fresh output/escape/missing/recipe/executable manifest refusals.
[Явный native smoke](01-native-camera/README.md) не запускается ordinary catalog.
