# Панель предложенного действия

[Родитель](README.md) · [Спецификация](../panel-design.md).

В контексте с загруженными mouse_proposal_state.js и mouse_proposal_panel.js вызвать
`DotaCoachMouseProposalPanels.bind(root)` на MouseProposalRoot. Loader скрыт и inert,
автоматического bind нет. Методы captureActor(dto), proposeMove(point),
proposeTarget(Targets.view()), reset(), refresh() возвращают bool. view() — copy,
null во время операции, empty closed после dispose(). isDisposed() проверяет дерево.

Actor нельзя сменить до reset; это предварительно выбранный виртуальный игрок,
не доказанная identity героя. Новый клик заменяет draft, ошибочный очищает его.
Четыре подписи: движение, атака героя, добивание вражеского крипа, денай союзного.
Точка показывается как «Точка выбрана», цель — plain label. Нет native buttons,
handlers, clocks, game API или sender. Время всегда «неизвестно», действие ещё не
выполнено; canSend/nativeConfirmed/sourceAuthorizationConfirmed всегда false.

Свежий Targets.view должен подавать вызывающий интегратор. Сам refresh не проверяет
TTL ранее сформированного предложения. Сервер заново проверяет допустимость цели,
identity, death/range/deny/last_hit и lease; настоящий bridge ещё отсутствует.

Все 6 required Labels проверяются, включая скрытые/заменённые; повреждение закрывает
панель. Root зарезервирован до discovery, cleanup удерживает ownership до последней
записи; старый handle не пишет в новый bind. Команды source-проверок — в tests README.
