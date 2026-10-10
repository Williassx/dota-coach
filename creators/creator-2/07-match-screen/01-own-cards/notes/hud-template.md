# Общий контекст компонентов

[Подпункт](../README.md) · [Дизайн](../design.md) ·
[Пакет и приёмка](../../../11-integration/02-addon-packaging/README.md).

Один CustomUIElement Hud загружает coach_hud.xml. Все существующие definitions
объявляются в одном контексте, без запуска bind: roster state/panels, orders
state/panels, input routing, camera native/panels, targets state/panels.
Стиль нового экрана не включает demo CSS и не копирует JS implementations.

| Root | Существующий адаптер | Что потребуется для подключения |
|---|---|---|
| CoachRoster и CoachOrders | DotaCoachInputRouting.bind | Явный gateway/roster/control snapshots |
| CoachCamera | DotaCoachCameraPanels.bind | Явный camera gateway и проверенный id→entity |
| CoachTargets | DotaCoachTargetPanels.bind | Явный clock/maxAge и разрешённые наблюдения |

Этот список не запускает интеграцию. Никаких global defaults/фикстур/переходников,
server events или автоматического camera focus нет. Без интегратора статические
пустые состояния и отключённые кнопки остаются. Наблюдение сообщает отсутствие
подключения, а не предлагает пока недоступный клик карты.

Orders model сейчас описывает контрольную точку и тестовую цель; подписи сохраняют
этот объём, не обещают произвольное движение/атаку. Реальная mouse/voice/action
адресация требует нового рассмотренного плана и серверной проверки.
Связь выбранной карточки с camera target/observed map target ещё не реализована.

Пять slots предусмотрены для локального roster adapter; покупки/намерения,
реальные персональные модели и полноценный match screen не заявляются готовыми.
Прозрачный центральный root не содержит изображение карты или чужие ресурсы.

56 уникальных id/51 labels html=false проверены в XML. Размеры five cards/right
sidebar — исходная раскладка, не native proof. Windows/Source2 compilation,
внешний вид/масштабирование/перекрытие stock HUD/hittest и второй владелец открыты.
