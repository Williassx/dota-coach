# C2-02-02 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Обе команды меняют действие того же героя; отказ остаётся читаемым.

Этот критерий ещё не проверен в Dota. Подготовлены два локальных намерения через
явно передаваемый переходник, без GameEvents и игровых приказов. Внутренние
snapshot/ticket/report не задают общий wire-контракт. Нужны C1-01-03, интеграция
карточек, настоящие цели/серверная сцена, Windows/Source 2 и второй владелец.

Смена карточки не снимает блокировку незавершённого приказа. Тайм-аут означает
неизвестный результат; accepted не означает completed. Режим меняется только
входящим снимком. Причина результата и доступность новой команды показаны отдельно.

## Фактическое покрытие

orders_state различает pending/report/snapshot; accepted не completed, timeout unknown. Смена карточки не освобождает pending запрос.

## Непроведённые проверки и зависимости

Два действия move/attack одного героя с реальным сервером не показаны. Ограниченный native manual move не реализует attack через эту панель.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/orders_demo.xml](../src/panorama/layout/custom_game/orders_demo.xml) — SHA256 f5a21989a9585cd459816a32555d0ea1c97d1067d95ddcd7a5d4fdf8e08768a3.
- [src/panorama/scripts/custom_game/orders_demo_data.js](../src/panorama/scripts/custom_game/orders_demo_data.js) — SHA256 a657ea17111fcf5ce320984bdec629e13629a1bc1426307ba105afe662a2524f.
- [src/panorama/scripts/custom_game/orders_demo.js](../src/panorama/scripts/custom_game/orders_demo.js) — SHA256 151f4f97b5facc8f52ad6604568331ba095f3070c9f23fad28c22b608115476e.
- [src/panorama/scripts/custom_game/orders_panel.js](../src/panorama/scripts/custom_game/orders_panel.js) — SHA256 b5cf2e8eb7724bc1e43042619ad5b0f535fe69c1e214a37f2441998316f330aa.
- [src/panorama/scripts/custom_game/orders_state.js](../src/panorama/scripts/custom_game/orders_state.js) — SHA256 d93502069eb14b18696ffdca9674a4bbf74efa4d3a42a4d836a2ccbdba720868.
- [src/panorama/styles/custom_game/orders.css](../src/panorama/styles/custom_game/orders.css) — SHA256 5ea6c1b698e7bf0989eaaa6bf9d9811a0d8e8ebdc0d435f57916526aa1b0f0ef.
- [tests/orders.test.cjs](../tests/orders.test.cjs) — SHA256 778d31a3a925b5feeb61d7cefb0773f8205accde73e0ad9bc01382c800f964e3.
- Предыдущий отчёт: [cloud-orders.md](cloud-orders.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
