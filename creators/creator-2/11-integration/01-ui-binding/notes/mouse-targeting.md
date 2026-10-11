# Локальная связь цели и мыши

[Родитель](README.md) · [Спецификация](../mouse-targeting-design.md).

Загрузить canonical Targets, MouseProposals, MouseProposalPanel и
mouse_targeting_binding.js в одном контексте. Вызвать
`DotaCoachMouseTargetingPanels.bind(root,{now,maxAgeMs})` на MouseProposalRoot.
Clock — явная функция локальных monotonic milliseconds; TTL 1..60000 по Targets.
Нет auto-bind/scheduling; интегратор вызывает refresh/view при нужной проверке.

captureActor(dto), updateTargets(dto), selectTarget(id|null), proposeTarget(),
proposeMove(point), reset(), refresh() → bool. proposeTarget не принимает caller
snapshot, получает его от private Targets. view → copied mouse/observation + closed,
evidence=local_mouse_targeting, false canSend/nativeConfirmed/sourceAuthorizationConfirmed.
Во время операции view=null; закрытый view содержит null child views. dispose и
isDisposed относятся ко всей группе. Private children наружу не предоставляются.

Любой update/select консервативно снимает прежнее target предложение до DTO reads,
даже отклонённый stale update. Выделение новой цели не переиздаёт действие. Non-ready
наблюдение снимает target draft на явных проверках, сохраняя actor; move независим.
Clock проверяется также после target paint и всех native reads: после успешной
финальной проверки времени native callbacks уже не вызываются. Если TTL истёк,
target draft снимается; это не watcher или серверная гарантия. Reset снимает actor/draft/selection, сохраняет high-water
revision и serial. Плохое время снимает наблюдение, newer valid source позволяет
восстановить его. Это local source policy, не серверная identity/свежесть/право ввода.

Missing/hidden/replaced/destroyed UI закрывает private модели. Busy до clock/DTO/
native callbacks; old closed API не читает новые входы и не пишет новый bind.
В разрушенный root не пишут native свойства; остальные живые Labels очищаются.
Нет реальных click handlers, bridge, game API, lease, cancel/AI return или игровых
гарантий last_hit/deny. Standalone mouse recipe пока включает только model+panel;
координатор требует отдельной явной упаковки, не подменяет её неучтёнными JS.
