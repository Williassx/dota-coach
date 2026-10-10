# Экран локальной подготовки

[Подпункт](../README.md) · [Дизайн](../panel-design.md).

DotaCoachPreparationPanels.bind(root) использует единственную pure модель подготовки.
API: update(frame), choosePlan(id), chooseTalk(id), removePlan(), removeTalk(), clear(),
draft(), dispose(), isDisposed(). Входы читает только модель; render использует view.

Два каталога до8 вариантов без пагинации; до выбора видны label/version/intent.
Действия «Выбрать план»/«Выбрать вариант разговора», selected отдельно снимаются.
Clear — «Снять выбранные варианты», доступен при одном или двух выборах. Count localN/2.
Отдельные hints показывают emptycatalog/unselected/selected; warnings не обещают эффект
или характер человека. Lineup — технический local draft с внутренними id/version.

97 required children проверяются включая скрытые. Generation до DTO getters и
после external writes исключает старые callbacks при version/intent/context/ABA.
Rejected old update rebind актуальных действий. Dispose закрывает model, очищает
labels/buttons/timer, скрывает root до releaseowner. Lifecycle watcher0.25 не опрашивает
Dota. Definitions inert; bind и permitted input передаются только явным интегратором.

Отдельный XML/CSS не включён в HUD/manifest. Fixed1280px окно, два360px списка,
100px summary с прокруткой и selected fit-children: native fit/scroll/compile/hittest
ещё не проверены. C1 realcatalog/effect/server, screen navigation, native и второй
владелец открыты. Нет native/bootstrap/transport/start/storage/gameplay effects.
