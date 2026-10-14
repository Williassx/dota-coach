# C2-02-01 — сопоставление приёмки 14 октября 2026

Автор: отдельный исполнитель C2 Task F. Это авторский технический отчёт; независимый C1 reviewer ещё не вынес решение. Чекбоксы не изменены. Основание: frozen baseline b267b5f и текущие файлы подпункта. Новый coach-scene/native outcome не включён без собственного receipt.

## Буквальный критерий README

Выбор не меняет режим; синтетический профиль явно отмечен.

Подготовка модели и демонстрации не требует сетевого контракта. Для подключения
серверных данных нужен C1-01-03; внутренние семь полей карточки не являются общим
протоколом. Компиляция Source 2, рендеринг/мышь в Dota и проверка другим владельцем
ещё не выполнены. Задача целиком не закрыта.

## Фактическое покрытие

roster_cards_state раздельно хранит playerName/heroName/role/source; выбор карточки не выдаёт приказ. Native TEST binding показал пять synthetic карточек.

## Непроведённые проверки и зависимости

Реальная player identity, measured profile fidelity и физический выбор мышью не проверены; native fixture не серверное наблюдение режима.

## Прочитанные материалы и воспроизводимость

- [src/panorama/layout/custom_game/roster_cards_demo.xml](../src/panorama/layout/custom_game/roster_cards_demo.xml) — SHA256 41c4e9ef493b84ed095d180cc25026e0e7b9ce3472767b7e23999dd6748233eb.
- [src/panorama/scripts/custom_game/roster_cards_demo_data.js](../src/panorama/scripts/custom_game/roster_cards_demo_data.js) — SHA256 293f1bf460bcb819e450b56f0af1078c447713f78365bc9bd40e6b329dfdb9b3.
- [src/panorama/scripts/custom_game/roster_cards_demo.js](../src/panorama/scripts/custom_game/roster_cards_demo.js) — SHA256 89f89beb7869b8b43c12fcfe028d9240b125cf2c370d758a0f1e676c3feb364e.
- [src/panorama/scripts/custom_game/roster_cards_state.js](../src/panorama/scripts/custom_game/roster_cards_state.js) — SHA256 8ead8e2f798d6778430e9921200b409b45cc56d7b8d0c215995fd149716094ab.
- [src/panorama/scripts/custom_game/roster_cards.js](../src/panorama/scripts/custom_game/roster_cards.js) — SHA256 a246c95ca8298b9a002585904ff40518a0e58308b3c6a0f0609bca2e0379c419.
- [src/panorama/styles/custom_game/roster_cards.css](../src/panorama/styles/custom_game/roster_cards.css) — SHA256 e3288e1b038d83ce4778a974f4dbfb75608989cf4775376a9778ddbaa0143155.
- [tests/roster-cards.test.cjs](../tests/roster-cards.test.cjs) — SHA256 8b09756180e52d443632797a6ceb6cc02f930bc4f3008ea73304fff93ec65606.
- Предыдущий отчёт: [cloud-cards.md](cloud-cards.md).

Команды этого сопоставления: чтение README/файловых списков и поиск guards/маркеров в actual JS/tests через rg; Get-FileHash для перечисленных ресурсов. Новые runtime tests, native launches, physical input и публикация этим docs-only заданием не выполнялись. PASS прошлых отчётов относится к указанному в них срезу, а не автоматически к текущему HEAD.

## Решение по границе действия

Сопоставление критерия выполнено: зафиксированы покрытая часть, открытые проверки и зависимости. Это допускает рассмотрение существующего действия «сопоставить результат», но не закрывает функциональные действия и критерий целиком. Независимый technical peer review отдельного C1 исполнителя обязателен перед действием передачи.
