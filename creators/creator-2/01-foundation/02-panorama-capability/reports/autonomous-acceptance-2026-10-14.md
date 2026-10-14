# C2-01-02 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

В реальном клиенте работают панель, событие и подтверждение; текстовый макет не считается запуском.

UI подготавливается параллельно C1-01-02.
До локального доступа автономно подготовлены исходники и отдельная упаковка;
это не закрывает аудиты и нативную приёмку. Минимальный серверный
обработчик делает создатель 1 в своей папке; оба совместно проверяют соединение.
Готовое серверное подтверждение в штатном шаблоне заранее не предполагается.

## Фактическое покрытие

coach_probe разделяет отправку и addressed reply; native-ping 13 октября содержит три запуска, включая unchanged auto-adapter.

## Непроведённые проверки и зависимости

Программная активация не проверяет physical mouse/hittest; этот diagnostic exchange не игровой протокол приказов.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/coach_probe.xml](../src/panorama/layout/custom_game/coach_probe.xml) — SHA256 d62f0e478a73253ec19f9320c85130160975e96bc2879c9cfb16039accd4a6f2.
- [src/panorama/layout/custom_game/custom_ui_manifest.xml](../src/panorama/layout/custom_game/custom_ui_manifest.xml) — SHA256 3719e4d29330ded724bdd39d3efd45d25510323992a4170f601fa24e31a80582.
- [src/panorama/scripts/custom_game/coach_probe_state.js](../src/panorama/scripts/custom_game/coach_probe_state.js) — SHA256 29c2ecf466a39b8c0d8ea4b83962a9cd17b37fb52bece1f43a993fe5a79a9cea.
- [src/panorama/scripts/custom_game/coach_probe.js](../src/panorama/scripts/custom_game/coach_probe.js) — SHA256 5f9097c0d5429466c3d9c0baec14d8d22af871f46ded80ff89b0e2ec60b72773.
- [src/panorama/styles/custom_game/coach_probe.css](../src/panorama/styles/custom_game/coach_probe.css) — SHA256 b3895055f7c7b911f0f38980fedfad1a22a6edf02db2e07860cecb3bdaef2c84.
- [tests/probe.test.cjs](../tests/probe.test.cjs) — SHA256 394584d8b7eaf5f4dc75534a0cce3a2839a8a2ce3605366f4638c73661e49a94.
- [tests/test_build_probe_bundle.py](../tests/test_build_probe_bundle.py) — SHA256 43040687595134cc62d1ba5a4eb74fdae4a3b0a12e3eb02a0a50fcb34e7a8608.
- [tests/test_native_ping_fixture.py](../tests/test_native_ping_fixture.py) — SHA256 8af8949e64c1244f30793e89900c44d969c8159aa18feaf2d7fc18022112c65c.
- [tests/test_verify_probe_bundle.py](../tests/test_verify_probe_bundle.py) — SHA256 6f4e7bb87f5be4d12147cc79a26513c8f7e22b238db4f072959d999d1a4a1f3b.
- [tests/native-ping/capture-command.py](../tests/native-ping/capture-command.py) — SHA256 6080ce2970c6f0955bb476d15488c7e8d868b6e0bbba9185a6f12ffe8ba34dec.
- Предыдущий отчёт: [bundle-verification.md](bundle-verification.md).
- Предыдущий отчёт: [cloud-behavior.md](cloud-behavior.md).
- Предыдущий отчёт: [native-ping-2026-10-13.md](native-ping-2026-10-13.md).
- Предыдущий отчёт: [source-bundle.md](source-bundle.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
