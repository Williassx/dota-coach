# План локального координатора вмешательства

> Исполнитель: superpowers:executing-plans/TDD; один редактор и пять read-only критиков.

**Цель:** согласованный выбор карточки и контрольного снимка, сохранение capturedactor.
**Архитектура:** один private Roster + Requests; DTO каждого вида читается одной моделью.
**Дизайн:** [intervention-selection-design.md](intervention-selection-design.md).

## 1. Модель и проверки

Создать src/panorama/scripts/custom_game/intervention_selection_state.js и
 tests/intervention-selection.test.cjs. API и gate из дизайна; pure ES5 без эффектов.

- [x] Реальные модели в VM: сценарии выбора/доступности/корреляции RED.
- [x] Минимальная реализация GREEN, copies/busy/dispose/closed проверены.
- [x] Не меняются панели, HUD/пакет, shared contract, C1 и нативные API.

## 2. Проверка и публикация

Создать notes/intervention-selection.md и reports/cloud-intervention-selection.md;
добавить ссылки в существующие README, статусы и отдельный журнал действий.

- [x] Пять read-only критиков; конкретные дефекты RED→GREEN.
- [x] Полная регрессия прежних 608 плюс новые, syntax/links/README/diff.
- [x] Только start_skill сохранён/readback; main push/remote SHA/clean проверены.

Панели/пакет, транспорт/authority/lease/возврат ИИ и native/второй владелец открыты.

Проверки пяти критиков выполнены до изменения рабочего порядка пользователем.
Для следующих задач применяется [экономный порядок](../../../shared/AGENT-EFFICIENCY.md).
