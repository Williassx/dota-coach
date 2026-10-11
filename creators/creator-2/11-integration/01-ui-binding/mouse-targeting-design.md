# Связь наблюдения цели и предложения мыши

[Родитель](README.md). Root inline; пользователь разрешил продолжать самостоятельно.

Проблема: standalone MouseProposalPanel получает snapshot; её refresh не проверяет
TTL ранее предложенной атаки. Нужен локальный интегратор, владеющий одной existing
Targets моделью и одним existing MouseProposalPanel. Модели/панель не копировать.

`DotaCoachMouseTargetingPanels.bind(root, {now,maxAgeMs})`: existing MouseProposalRoot,
explicit clock в миллисекундах и bounded TTL из Targets. Методы captureActor(dto),
updateTargets(dto), selectTarget(id|null), proposeTarget() без входного snapshot,
proposeMove(point), refresh(), reset() возвращают bool. view() возвращает копии
`{mouse,observation,closed,evidence,canSend,nativeConfirmed,sourceAuthorizationConfirmed}`,
null во время операции. dispose()/isDisposed() закрывают обе области.

Каждый update/select до чтения caller DTO снимает прежний target draft; это
консервативная политика, включая отклонённый stale update/invalid select.
Move draft независим от цели и сохраняется. Перед новым target proposal/read/refresh
получается свежий Targets.view. Non-ready/dead/stale/invalid очищает target draft,
сохраняя actor. После создания target draft и native reads свежесть проверяется последней: если
clock продвинулся во время native callback, результат снимается и метод false.
Повторный capture не меняет actor; reset очищает actor/draft/target selection,
но не перематывает local revisions/serial. Invalid clock не закрывает группу сам
по себе: Targets снимает наблюдение; strictly newer valid update восстанавливает.

Busy ставится до child/native/clock/DTO callbacks. Nested methods reject без reads,
view busy=null; dispose во время callback прерывает операции. Invalid/missing/hidden/
replaced required UI closes both; old handle never writes new binding. Source data
supplies permitted observations; local TTL is neither server freshness nor authority.

No real mouse handlers, transport, bootstrap, watcher, lease/ACK/MANUAL eligibility,
coordinate mapping or gameplay. Flags always false. Standalone mouse bundle unchanged;
future native integration needs explicit dependencies and C1-approved source.

Финальный clock barrier: все native проверки до последнего Targets.view; после
успешного clock read никаких native callbacks. Non-ready очищает draft.
