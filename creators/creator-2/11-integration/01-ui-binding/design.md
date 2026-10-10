# Единый локальный контроллер HUD

Пользователь поручил продолжение до остановки. Общая разметка и source-пакет уже
подготовлены, но компоненты не привязаны. Готовим явный координатор их UI lifecycle
и выбора игрока, без серверной интеграции или нового общего протокола.

## Объём и архитектура

Отдельные привязки потребовали бы от интегратора повторять обработку выбора,
ошибок и освобождения ресурсов. Автоматический bootstrap сейчас не имеет реальных
данных/clock/переходников. Выбираем definitions-only DotaCoachHudPanels.bind,
который явно получает caller options и переиспользует существующий input routing,
camera и target adapters. Нет native мыши/подписок/фикстур/default sender/clock.

Новый source: src/panorama/scripts/custom_game/coach_hud_binding.js этого подпункта.
Расширения исходных модулей: input_routing.bind четвёртым optional onSelection;
camera panels setRecipient для известного игрока с неизвестной entity. Реализации
не копируются. Общий layout/include и fixed source-пакет получают новый script:
10 definitions,13resources, один дополнительный общий status label.

## API

DotaCoachHudPanels.bind(root,options) → replaceRoster,updateControl,selectPlayer,
clearSelection,updateTargets,selectTarget,refreshCamera,dispose,isDisposed.

Root содержит CoachRoster/CoachOrders/CoachCamera/CoachTargets и CoachHudStatus.
Options: обязательные now/maxAgeMs по targets; optional send(function),
cameraGateway(check/focus), resolveCameraEntity(function id→int index|null).
Неизвестные собственные поля/неверные типы options отклоняются. Нет implicit native
gateway или fallback clock. Индексы0..2147483647; false/NaN/throw/неверный resolver
результат трактуются как неизвестная entity, без сохранения прежней цели камеры.

replaceRoster/updateControl делегируют existing router; selectPlayer/clearSelection
меняют только локальный выбор. updateTargets/selectTarget делегируют target pane,
не превращают наблюдаемую цель в приказ. refreshCamera повторяет явное сопоставление
текущего выбранного игрока, не перемещает камеру. Gateway получает только явный
клик existing buttons; без gateway кнопки отключены. send/report обёрнуты общей
проверкой четырёх компонентов: уничтоженная camera/target/root закрывает группу
до отправки/позднего ответа, не ждёт следующего watcher.

## Выбор и камера

Router сначала обновляет адресата приказов, затем передаёт copied selection optional
observer. Обратная совместимость трёхаргументного bind сохраняется. Нет повторной
реализации card/order routing или вмешательства AI/MANUAL.

Координатор сохраняет копию {id,playerName}, не человек→hero authority. При выборе
он явно вызывает resolveCameraEntity, если передан; проверяет поколение после
callback. Новая выборка/закрытие во время resolver не позволяет старому результату
переключить камеру к предыдущему игроку. Resolver не вызывается без выбора.

Camera.setTarget сохраняет строгий прежний shape/index. Новый setRecipient принимает
null либо ровно {id,playerName}; внутри camera target entityIndex=null, доступность
«Герой выбранного игрока ещё не определён». Игрок показывается по имени, кнопка
отключена, gateway.check/focus не вызываются. Полная entity из resolver используется
только для того же выбранного id/name. Native gateway по-прежнему проверяет
живого realhero команды; достоверность id→entity остаётся открытой серверной приёмкой.

Выбор/обновление/разрешение entity никогда не отправляют приказ и не двигают камеру.
Чужая/мёртвая entity блокируется native gateway. Персональные модели не создаются.
Late resolver/reply, old roster callback и старый watcher защищены closed/generation.

## Владение и отказы

Один parent owner на root; резервирование до чтения options/привязок. Четыре
компонента привязываются явно; partial bind rollback освобождает только созданные
этим координатором адаптеры/таймеры. Чужой уже привязанный child не закрывается и
не скрывается. Не смешивать прямые child bindings с parent на тех же scope.

Закрытие/сломанный child отменяет parent watcher0.25с и child timers/handlers,
скрывает только принадлежащие ему scope до освобождения parent root. Новый bind
может показать их снова. Status plain text; перед каждым paint проверяется владение.
Старые callbacks не затирают fresh binding. Watcher только отслеживает lifecycle,
не разрешает entity/native focus и не отправляет heartbeat/приказы.

Сбой child/action/update закрывает группу с объяснением. Resolver failure оставляет
карточки/приказы/наблюдение, отключая лишь camera target. Invalid DTO сохраняет
семантику соответствующего existing adapter; returns bool не подтверждают native
действие. После reload unresolved server requests/clock/epoch ещё требуют общего
контракта и восстановления; dispose не считается серверной отменой приказа.

## Приёмка исходников

Node VM исполняет все реальные модули вместе: startup без данных/приказов/native,
выбор адресата/известный unmapped recipient, explicit focus/order, invalid resolver,
selection reentry/copies, dead/opponent guards, disappearance/expiry, root failure,
late report после camera/target teardown, partial bind/options reentry/ownership,
cleanup/fresh bind. Tests обозначают synthetic data, не реальные профили.
Прежние suites и source-пакет13resources повторяются; actual build/verify новый child.
Общий контракт/C1-04-03/C2-05-03, server/clock/identity, native HUD/hittest/мышь/голос,
Windows/Dota и второй владелец остаются открытыми. Auto-bootstrap не добавляем.

## Уточнения пяти критиков перед кодом

Сначала сброс камеры через setRecipient и новая generation, затем внешний resolver.
Общий guard оборачивает camera check/focus, transport и reports; методы gateway
снимаются один раз в фазе options. Начальный null observer разрешён в binding phase,
когда camera/targets уже готовы, но router ещё не вернул handle.
Статусы: статический «Данные и переходники не подключены.»; активный
«HUD связан локально. Исполнение в Dota не подтверждено.»; отказ
«Общий HUD недоступен. Локальная привязка закрыта.». Дочерний результат приказа
не переписывается общим статусом.
