# Использование отдельного запроса фокуса

[Подпункт](../README.md) · [Дизайн](../design.md) · [Проверки](../tests/README.md).

Reference: [ModDota api.d.ts, закреплённый commit](https://github.com/ModDota/TypeScriptDeclarations/blob/df7722b560d5c616f7b2f6be42480aa5053baec8/packages/panorama-types/types/api.d.ts).
MoveCameraToEntity объявлен как перемещение без блокировки слежения. GetLocalPlayerID,
Players.GetTeam, Entities.IsValidEntity/IsRealHero/IsAlive/GetTeamNumber используются
для проверки. Community declaration не подтверждает конкретную установленную сборку.

После загрузки скриптов интегратор явно вызывает DotaCoachCameraNative.create(),
затем DotaCoachCameraPanels.bind(root,gateway). Root содержит CameraRecipient,
CameraAvailability, CameraResult, CameraFocus. setTarget принимает null или ровно
{id,playerName,entityIndex}; id/name до64, id без пробельных краёв, index int0..2147483647.
Цель не определяет AI/MANUAL и не является сетевым контрактом. Проверка native
подтверждает только живого realhero той же команды, не правильность stable id→entity.

check возвращает {available:boolean,reason:string|null}; focus —
{requested:boolean,reason:string|null}. True требует reason=null; false — непустую
непробельную строку до160. focus проверяет цель снова перед вызовом камеры.
Отсутствующий API/игрок/spectator/неизвестная команда/мертвый или чужой герой
блокируют действие. Origin, SetCameraTarget, мышь и команды юнитам не используются.

setTarget/refresh не двигают камеру; только кнопка вызывает focus. Requested —
возврат native функции без исключения, положение камеры неизвестно. Предыдущий
результат сохраняется отдельно от выбора, сравнивая id и entityIndex при равных именах.
Стабильный id нельзя переиспользовать для другого игрока внутри экземпляра.

Один owner на root; dispose обязателен при HUD teardown. Таймеров/автоматических
подписок нет. Интегратор обновляет данные и вызывает refresh при изменении состояния.
Перед кликом доступность проверяется вновь. Поколение защищает stale callbacks и
повторный вход во время чтения данных/result. Ошибка render/result закрывает панель;
старый malformed result не закрывает уже обновлённую цель. Focus exception показывает
неподтверждённый запрос, не выполненное действие.

Открыто: общий HUD, безопасный источник/identity mapping, совместимость custom heroes,
установленный API, фактический фокус, камера/bounds/hittest/масштабирование,
допустимые обозначения и обзор, второй равноправный владелец.
