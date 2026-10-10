# Панель запроса ручного режима

**Дата UTC:** 2026-10-10. **Основа:** 36845f6. Автономная работа разрешена пользователем.

## Цель и область

Подключить [pure request state](design.md) к отдельной Panorama source panel.
Один selectedplayer, один capturedactor, observedmode и requeststage видны отдельно.
Одна кнопка «Запросить ручное управление» посылает intent только явно injected send.
Нативное управление героем, lease/возвратИИ, commonwirecontract/HUD integration открыты.

## Дерево и API

ManualRequestRoot содержит семь plainlabels ManualRequestRecipient/Mode/Actor/State/
Reason/Message/Hint и одну ManualRequestButton. Source XML включает существующий
orders_state.js, intervention_request_state.js, intervention_request_panel.js и
один новый intervention_request.css; definitions inert/no run/onload/demo/bootstrap.
Каждый ID required, все включая hint проверяются перед action. XMLbutton disabled.

DotaCoachInterventionRequestPanels.bind(root, send?): update(frame), select(id|null),
request():bool, dispose/isDisposed. send только function/undefined/null; иной тип
reject до sideeffects. model=create(typeofsend==function). Своей копии source rules нет.
send(copiedintent, reply) принимает локальное предложение request_manual; reply tied
к originating instance/ticket, никогда к текущему selection. No automatic network/API.
Caller must validate source identity/epoch/authorization on actual server.

Mode label «Снимок: ИИ/MANUAL/неактивен» не говорит «права выданы». Requeststate labels
разделяют pending, accepted (получение, без MANUAL), unknown, rejected/cancelled,
not-sent и mode-observed (не причина/право ввода). Capturedname[id] отдельно от selected.
ManualRequestMessage = model.message; reason отдельна; dynamic text html=false.

## Запрос, ожидание и ошибки

request before send: check allnodes, begin; render pending, register ACKwait timer5s.
Deadline только UI ожидание, не manuallease/time limit/server cancellation. Если timer
не создался, send не вызывается и notSent применим. После каждого external call/write
guardgeneration/lifecycle. Dispatch only while currentticket pending/valid root.
Если send throws, outcome ambiguous: expirepending→unknown, никогда notSent/retry.
Синхронныйaccepted перед throw сохраняется accepted, позднийreply может уточнять unknown.
First accepted/reject/cancel/mode-observed/new epoch отменяет ACKtimer; accepted остаётся
ожиданием observedmode без lease clock. Reply живёт после смены карточки, но закрытая
instance/terminal/newticket отвергают его до DTOreads. Older cancelledtimer callback
не трогает новую instance/новый timer. UI dispose не отменяет серверный запрос.

## Staging и владение

One liveowner perroot reserved before discovery; cleanup labels/button/model/timers
доrelease. На время update/reply DTO чтения panelbusy=true/generation++, labelsblank,
buttonhandlers сняты/root скрыт; busy public mutations reject до DTOreads. Рендер после
modelcall снимает busy и permits newer renderer reentry: старый token не перерисовывает
новый state/instance. Select тоже меняет generation; capturedrequest остаётся.
Modelbusy действует внутри private pure model; panelguards не используют DTO twice.
Watcher0.25 проверяет lifecycle только. Hiddenrequirednode fail закрывает panel before
send; partial discovery/render/schedule failure releases ownership for retry.

## Проверки и открытая приёмка

Node RED→GREEN: real private model, click intent/pending/ACK≠mode, sourceupdate/selection,
5s unknown/no retry, definitive timerfailure-notSent/no dispatch vs ambiguous sendthrow,
late reply/epoch/ticket/timer, busy/private labels, invalidsource, failurecleanup,
renderer/getterdispose/rebind and stalehandlers. PythonXMLgraph IDs/dependencies/inert/
plainlabels/disabledbutton/CSS; no compiler proof. Прежние577 repeated +new checks,
пять critics, journal/links/config/fastforwardmain. Native geometry/hittest/actualsource/
transport/authority/manualinput/lease/C1/server/secondowner остаются открытыми.
