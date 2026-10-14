# C2-11-02 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Сборка использует единственные исходники и не перезаписывает установку без отдельного действия.

## Фактическое покрытие

Fixed source recipes используют единственные canonical XML/JS/CSS, hash/graph checks, отдельные TEST kinds. Сборка отделена от авторских src и guarded output.

## Непроведённые проверки и зависимости

Source build не устанавливает полный аддон. Windows WinError1314 skips сохраняют strictfalse; новый15/18 recipe/native compile проверяет root отдельно, здесь не утверждается успех.

## Прочитанные материалы и воспроизводимость

- [tests/test_coach_scene_bundle.py](../tests/test_coach_scene_bundle.py) — SHA256 eb470c76b951d204d5c5a0ca528d5e13864c548f48a0956e450db19dcd2c8cb9.
- [tests/test_hud_bundle.py](../tests/test_hud_bundle.py) — SHA256 82ef6a79c2caf731c35fed3d0ebd9a20f1bf078f2e9a164596ef637230c1231a.
- [tests/test_intervention_bundle.py](../tests/test_intervention_bundle.py) — SHA256 865760dc483638ea3ab93fe279abc1b7a98cc0ca3f32dc26d71aeca9608a5fd2.
- [tests/test_intervention_screen_bundle.py](../tests/test_intervention_screen_bundle.py) — SHA256 5a2aed9a334540ce034201658bb08cf83819a5f4b6fdad318c1ef4ca5187a9f9.
- [tests/test_match_observation_bundle.py](../tests/test_match_observation_bundle.py) — SHA256 76f89eb31538433a4db83d86e7851ea27203695fc78cca866a2d4830f0c4a283.
- [tests/test_mouse_proposal_bundle.py](../tests/test_mouse_proposal_bundle.py) — SHA256 6babfde0191c069e9195da5671774fecbf952f0af15bdd9966f4ed6373c2773c.
- [tests/test_mouse_targeting_bundle.py](../tests/test_mouse_targeting_bundle.py) — SHA256 b6fd22d8a3a082a4983f44eef6b5b3c93569b90f95bce9f6bddd47f7379416ed.
- [tests/test_native_hud_fixture.py](../tests/test_native_hud_fixture.py) — SHA256 76183da19424b6f22351ddd4ab2d98b29c83b2d158e034c1adf5187250ba84ed.
- [tests/test_native_intervention_fixture.py](../tests/test_native_intervention_fixture.py) — SHA256 2b215ebf0d13a06343d31c00aeebe42fca34e154d0081fb71e192843b9b10fb5.
- [tests/test_native_mouse_targeting_fixture.py](../tests/test_native_mouse_targeting_fixture.py) — SHA256 ed7a200a547ed77eca8304fb1e4c1c53e5a09ba4f29e9b15415bf619bcdf6972.
- [tests/test_native_observation_fixture.py](../tests/test_native_observation_fixture.py) — SHA256 4558f26d701c9386b1f1e105cf840748c02651ac613e188a6e959836999a2b11.
- [tests/test_native_preparation_fixture.py](../tests/test_native_preparation_fixture.py) — SHA256 65d8d5a41dd23b88fac23116db5c39854d176800e81825d8166eb3d36e049ca0.
- [tests/test_native_voice_fixture.py](../tests/test_native_voice_fixture.py) — SHA256 7276a87e80c8b59b3945abd7cfa953ac99d0933b86ab7361f4b10a645f5ff405.
- [tests/test_opponent_roster_bundle.py](../tests/test_opponent_roster_bundle.py) — SHA256 c329e3774445f38aa919c0e18c6cde972f1eb38327136a073b2886d7d8f9e33a.
- [tests/test_orders_timeline_bundle.py](../tests/test_orders_timeline_bundle.py) — SHA256 3bfeaea7ca67af084f43006704bda237705eb0ca602e0ba7720d7da2f0b02b61.
- [tests/test_preparation_bundle.py](../tests/test_preparation_bundle.py) — SHA256 d8600045924b9c2d48dc36014d24e1f61bd7c42d8b29cdd2c4fa2996609e29a2.
- [tests/test_voice_text_bundle.py](../tests/test_voice_text_bundle.py) — SHA256 a741eb5397a1911e929f0743df8aa11cb830cfee220fe79f78aab2153f495d4d.
- [tools/build_coach_scene.py](../tools/build_coach_scene.py) — SHA256 51c851a52217e7b1cf39ef12c75b5c23e5cac9584fb762b702bddd8074ca5cac.
- [tools/build_native_hud_fixture.py](../tools/build_native_hud_fixture.py) — SHA256 b11414cc273fb329f0cfafd6acbc1dfdc219a97a49b1e5f2f01fe3785a93a721.
- [tools/build_native_intervention_fixture.py](../tools/build_native_intervention_fixture.py) — SHA256 75d975844cf6aa962303502e3671e0549426534314ad772e130caec2066d7c71.
- [tools/build_native_mouse_targeting_fixture.py](../tools/build_native_mouse_targeting_fixture.py) — SHA256 14b400548d75101501c0d0cea24cab3c29fbeb8e1fa2bb53eea422641310ff68.
- [tools/build_native_observation_fixture.py](../tools/build_native_observation_fixture.py) — SHA256 dfce6ac03326381494fc4a6f1b2dc630ff4f86b957b9394988f70bd4ebf08aca.
- [tools/build_native_preparation_fixture.py](../tools/build_native_preparation_fixture.py) — SHA256 0ef2892ffc03f7dd1c1b6ef2402f20b15d71403abd8fe6b79048a32c1723f385.
- [tools/build_native_voice_fixture.py](../tools/build_native_voice_fixture.py) — SHA256 84f1a16d9768aba6655dea6c62ed97a617a28c02ac0126096d6c7840ee34082b.
- [tools/intervention_screen_layout.py](../tools/intervention_screen_layout.py) — SHA256 119e9ecef7906c473526080cf7b9810372185480310d80ca521a80f80989f34d.
- [tools/launch_coach_scene.ps1](../tools/launch_coach_scene.ps1) — SHA256 a5eeb3f5d0eaebb74d8fec8c4e2c9100f27549a10c49d1c6c5c9c4d9c3ea48f9.
- [tools/match_observation_layout.py](../tools/match_observation_layout.py) — SHA256 0ac1b482379d1c5e7f3a3085e5db262cbc1188b7e92b57f124803725a4f5c4ee.
- [tools/mouse_proposal_layout.py](../tools/mouse_proposal_layout.py) — SHA256 909ce194f6a33c8958922b096793871a0564479a2ebf74733b5ead880d61a646.
- [tools/mouse_targeting_layout.py](../tools/mouse_targeting_layout.py) — SHA256 5587024b961ce5b6df5a29216080293b03757510088b81ae53b8c64ee627660f.
- [tools/opponent_roster_layout.py](../tools/opponent_roster_layout.py) — SHA256 ad136248a4f87e5c39afc6a8ec008747c1a2001b6075d22d89cadcea45fdc468.
- [tools/orders_timeline_layout.py](../tools/orders_timeline_layout.py) — SHA256 6eb6dfcd6816dfc872a4901173364c5c128096d55c0e92cbabdd21673fdd37d7.
- [tools/preparation_layout.py](../tools/preparation_layout.py) — SHA256 a036172c4ab086ec603f8dc574543d2981f2e60414b24324320ec7aa2e3c4145.
- [tools/voice_text_layout.py](../tools/voice_text_layout.py) — SHA256 060889e57b043aac32354b1bac3f78c097c3bc505a0b5e198dfe36c6e5126df5.
- Предыдущий отчёт: [cloud-hud-bundle.md](cloud-hud-bundle.md).
- Предыдущий отчёт: [cloud-intervention-package.md](cloud-intervention-package.md).
- Предыдущий отчёт: [cloud-intervention-screen-package.md](cloud-intervention-screen-package.md).
- Предыдущий отчёт: [cloud-mouse-targeting-package.md](cloud-mouse-targeting-package.md).
- Предыдущий отчёт: [cloud-opponent-roster-package.md](cloud-opponent-roster-package.md).
- Предыдущий отчёт: [cloud-orders-timeline-package.md](cloud-orders-timeline-package.md).
- Предыдущий отчёт: [cloud-preparation-package.md](cloud-preparation-package.md).
- Предыдущий отчёт: [cloud-voice-text-package.md](cloud-voice-text-package.md).
- Предыдущий отчёт: [native-hud-2026-10-11.md](native-hud-2026-10-11.md).
- Предыдущий отчёт: [native-hud-scene-2026-10-12.md](native-hud-scene-2026-10-12.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
