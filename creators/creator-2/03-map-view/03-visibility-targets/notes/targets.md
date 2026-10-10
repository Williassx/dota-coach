# Частная проекция допустимого наблюдения

[Подпункт](../README.md) · [Дизайн](../design.md) · [План](../implementation-plan.md).

После загрузки targets_state.js и targets_panel.js интегратор явно вызывает
DotaCoachTargetPanels.bind(root,{now,maxAgeMs}). Root содержит TargetTitle,
TargetDetails, TargetStatus. now — конечное монотонное число миллисекунд;
maxAgeMs int1..60000. Нет default clock, источника данных или автоматического bind.

update(snapshot) принимает ровно {revision,targets}; revision int0..9007199254740991,
targets array<=32 уникальных id. Visible запись ровно
{id,visibility:"visible",label,team,kind,alive,entityIndex}, team ally|enemy,
kind hero|creep, alive boolean, index int0..2147483647. Id/label<=64 непустые,
id без пробельных краёв. Hidden/gone/unknown — ровно {id,visibility}; дополнительные
поля отвергаются без чтения их значений. Координаты не принимаются.

Revision читается раньше тела; old/duplicate не читают targets и не продлевают TTL.
Новая допустимая revision потребляется даже при invalid body: high-water не
откатывается после ошибки/expiry. Для восстановления нужна более новая проекция.
Новый матч требует новый model/controller. Локальная freshness отсчитывается от
приёма, без обещаний server freshness/heartbeat/reconnect.

select(id|null) выбирает только видимую запись. Full snapshot заменяет предыдущий;
hidden/gone/unknown/removal снимает выбор и удаляет label/index из view. Причина
сохраняется до explicit select/null; появление цели не выбирает её автоматически.
Gone означает отсутствие наблюдения, не уничтожение. Dead означает видимую мёртвую
цель, не допустимую атаку. UI никогда не объявляет действие выполненным/разрешённым.

Модель create/update/select/view/dispose/isDisposed возвращает view
{status,message,target}, target null или независимую копию шести visible полей
без visibility. Status empty/ready/dead/unavailable/stale/invalid/disposed.
При age>=maxAgeMs, clock throw/rollback/nonfinite цель исчезает синхронно в
update/select/view. View нельзя менять для изменения модели.

Panel update/select возвращают boolean операции+рендеринга, refresh — рендеринга.
Watcher0.1с обновляет текст без следующего пользовательского действия; dispose
отменяет его и освобождает root. Ownership резервируется до чтения options getters;
ошибка create/bind/render/schedule откатывает ресурсы. После повторного входа
getters/clock старый model/callback не затирает новое состояние или fresh binding.
Схема учитывает все собственные строковые поля, включая non-enumerable; изменившаяся
visibility отвергается до чтения label/index. Между записями UI проверяется generation.
Закрытие очищает и скрывает старые подписи до освобождения owner; watcher после
повторного входа продолжает expiry, если тот же адаптер остаётся открытым.

Сервер C1-03-01 должен передавать только разрешённое знание. Tombstones — только
для ранее разрешённых id; не перечислять неизвестные скрытые сущности и не выводить
gone из скрытой смерти. Одинаковое разрешённое наблюдение при изменённых скрытых
объектах должно давать одинаковую UI-проекцию. Эта приёмка переходника открыта.
Frontend filtering не является авторизацией или границей безопасности.

Открыто: источник/общий контракт, native видимость/identity/clock/HUD/map mouse,
игровые действия/серверная проверка, рендеринг/hittest и второй владелец.
