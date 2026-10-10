# Единая привязка трёх панелей подготовки

**Дата UTC:** 2026-10-10. **Основа:** 9f26bdf. [Цепь моделей](preparation-flow-design.md).
Пользователь поручил продолжать самостоятельно с пятью критиками.

## Цель и подход

Связать реальные existing adapters с одной private preparation flow: клики выбора
состава/героев/подготовки обновляют все три pane, dependent reset сразу очищает UI.
Это explicit local binding source/VM, без native compilation/navigation/start/server.
Новый group layout и source package остаются следующим шагом, здесь caller уже даёт
root с тремя областями из прежних XML. Не создавать Panels через native API.

## Optional model port

Три existing bind(root) сохраняют defaultmodel; optional bind(root,projection) принимает
owned model-compatible port. New DotaCoachPanelPorts.adopt(projection,required,isCurrent)
в preparation_panel_port.js: required собственные data properties function, getters
методов не исполнять; capturedfunctions сохраняют receiver. Один projection не может
быть усыновлён двумя liveports. Dispose идемпотентный/exception safe, чистит ownership
после captured dispose; isDisposed throw закрывает порт. Guard проверяется после
каждого descriptor trap и перед возвратом. Unknown optional methods не читаются.
Если adoption partialfailed, captured dispose вызывается безопасно, owner снимается;
если projection уже owned, не dispose первого владельца. No native work.

В каждом adapter добавить refresh():bool для render currentcopiedview/generation без
mutation, suspend():bool и second projection parameter. Suspend снимает handlers/labels
и скрывает pane, но сохраняет local focus/page; после refresh версия проверяется
прежним render. Так temporary staging не теряет focus при успешном назначении. Optionalpath требует явно loadedporthelper;
default standalone XML/testgraph resources не меняются. Paneldisposal не оставляет
owner при исключении injectedmodel. Guard adoption проверяет root/всеnodes/closed без
требования уже существующего model. Portmethods ловят lifecycleexceptions и закрывают
projection. Existing requirednode/watch/staleguards/backcompat сохраняются.

## Group API и private facades

DotaCoachPreparationBindings.bind(root) из preparation_binding.js создаёт один flow
и три model-compatible facades. Root содержит TeamPickerRoot, HeroRoleRoot,
PreparationRoot и CoachPreparationStatus; все scopes distinct/root не совпадают.
API flow mutators/contexts/draft плюс selectHeroPlayer(id), refresh(), dispose(),isDisposed().
External flow/childhandles/facades наружу не возвращаются.

Facades map team update/choose/remove/clear → flow team methods, heroes update/assign/
remove/clear → hero methods, preparation соответствующие API. view каждого возвращает
copied flow.view section; facade draft — copied соответствующая секция contexts(): team/heroes/preparation.
Частичная preparation доступна для панели, final draft gating остаётся прежним.

Для facade draft нужен partial draft подготовки, добавить contexts().preparation,
не меняя final draft gating; existing contexts team/heroes остаются. Guard busy/dispose
по-прежнему null. Tests обновить copied/contextshape без guessed counters.

Facade.isDisposed = ownclosed || groupclosed || flow.isDisposed; без groupavailable
во избежание recursion. Facade.dispose отмечает ownclosed, group watcher/availability
закрывают остальные. Mutation facade вызывает groupinvoke, который проверяет каждый
pane до flowchange. После permitted flowoperation refresh всех panels и общий status.
Общий status flow.message+localunconfirmed, no Start/Submit. Unknown DTO не reread.

## Reentry/lifecycle

Groupgeneration до inputгеттеров. На время mutation все facade mutators reject busy;
flow.view ужескрывает данные. Перед DTO getter suspend всех panels: generation истекает, private labels очищены,
root скрыт, но focus/page сохраняются до финального render. Facadeview при busy
не используется для suspend; actualmodel busy сам скрывает data. После flowoperation
busy=false и refresh всех actualviews; focus сохраняется только при прежней id/version.
Во время grouprefresh reentrant API может supersede generation: новаяoperation wins,
старый цикл не перерисовывает её. Busy mutations отвергаются до input reads.

Presentation focus/page не mutationflow: selectHeroPlayer явно отдельный UI выбор.
Он также должен быть groupguard/busy/generation gated. Panel-localcallbacks focus/page
не проходятfacade: sourceoldhandler текущийpanelgeneration до refresh делает их inert.
Groupavailable validates root/status/threepanes including allrequiredchild nodes,
catch closesallflow/ports/panels; failures beforetimer закрывают ownedresources.
Bindingphase owner сохраняется до latehandle cleanup, что предотвращает freshbind
поверх unwindinginitialbind. Fourwatchers (3pane+group) lifecycleonly0.25.
Dispose clearschildpanes/timers/flow/status before rootownerrelease. Partialfailedbind
не скрывает чужой independentlyboundpane: track ownership onlysuccessfulhandles.

## Проверки/границы

Port tests receiver/data-only/getterdisposal/duplicateowner/partialfailure/throwcleanup.
Default panel suites должны пройти; injectedport/refresh failure tests meaningful.
Group VM uses actual three pane adapters/flow/models with trees derived from original
XML IDs (fixtures parse source IDs without compiled/native claim). Click through5players,
update actual contexts hero proposals, click each hero, preparation pick/talk; deleting
player immediately clears others, invalid/staleversion/latehandlers/groupnodefailure,
reentrant DTO/render/dispose/freshbind/timer/partialowner tested.
No duplicated module/real catalogs/auto-bind/XMLbootstrap/HUDbundle. RealC1/identity/
effect/native layout и второй владелец остаются открытыми.

## Уточнения review

Во время initialbinding facade.view/isDisposed работают без требования уже созданных
siblinghandles; group mutation запрещена до полного bind. Portguard проверяет текущий
lifecycle, а не однажды захваченное groupgeneration. После grouprefresh originating
panel invoke может вернутьfalse из-за новойgeneration при принятом flow change;
clickcallback void, публичныйgroup API возвращает результат flow с current guard.
Нативная resource/layout composition не заявлена этой частью.
