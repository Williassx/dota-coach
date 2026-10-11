# Локальная история: результат исходников

2026-10-11 UTC; база c125c4c; основной исполнитель отдела 2.
Pure модель и 20 Node VM сценариев с каноническим Orders готовы.
Первый RED20FAIL из-за отсутствия модуля; после реализации19PASS/1FAIL:
test fixture пыталась изменить имя без новой revision, правильно отклонённой Orders.
Исправлена fixture. Дополнительная проверка outcomeUnknown выявила pending=false;
после исправления все20PASS. Целевой прогон Orders+история:2suites/61PASS.

Проверены отдельные стадии pending/accepted/executing/completed, отказы и unknown,
поздний первый снимок, переключение карточки, смена эпохи/потеря отслеживания,
старые tickets/terminal stability, bounded64/drop counter, сохранение local correlation,
копии, getters/Proxy reentry/dispose и plain текст. Server game API не вызывается.

Это история выбранных UI-снимков, не server event stream. Панель, общий HUD,
game timestamps/identity/source, физический эффект, native приёмка и другой
человеческий владелец остаются открытыми.

Полный прогон единого каталога: **36suites/810PASS**, без fail/skip/cancelled/todo.
Фактический отчёт: `build/dota_coach/source-checks-20261011T090946Z-7a1880/source-checks.json`.
График библиотеки:33/201 действий (16.4%), не готовность игры. Каталог дополнен
новой suite, тест полноты всё ещё сравнивает все пути; фиксированное число35 снято.

Финальный review одним reused критиком: существенных замечаний нет.
Cloud draft revision37 сохранён/read-back, другие поля сохранены; публикация
среды требует отдельного инструмента, который здесь отсутствует.
