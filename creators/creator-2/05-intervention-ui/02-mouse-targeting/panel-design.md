# Панель локального предложения действия

[Родитель](README.md) · [Модель](design.md).
Следующий этап — показать captured игрока, тип действия и точку/цель без
вымышленного исполнения или обратного отсчёта. Выбрана read-only панель вместо
native mouse hooks или кнопок отправки: C1 permission/lease ещё отсутствуют.

`DotaCoachMouseProposalPanels.bind(root)` владеет одной существующей MouseProposals.
Explicit captureActor/proposeMove/proposeTarget/reset/refresh → bool; view → copied
model snapshot либо null while busy; dispose/isDisposed. Модели/handlers/clock/
transport не добавлять. Все действия создают лишь локальные предложения.

Root MouseProposalRoot initial visible=false, шесть пустых plain Labels в порядке
MouseActor/MouseAction/MouseTarget/MouseState/MouseLease/MouseHint. Всего 7 ID.
Нативное уточнение 11 октября: XML layout имеет внешний безымянный
MouseProposalHost (hittest=false, hittestchildren=true), единственный ребёнок —
прежний MouseProposalRoot. Source 2 запрещает id у корневой панели layout.
Host занимает viewport; explicit bind получает внутренний компонент по ID,
не $.GetContextPanel() напрямую. Наличие hittest атрибутов не доказывает ввод.
Перед DTO parent скрыт, все тексты пусты; busy до native/traps. Required nodes
проверяются на missing/hidden/replaced/invalid, включая isDisposed. Distinct nodes,
root ownership до discovery, cleanup до освобождения, старый binding не пишет
в нового владельца. Caller доставляет события/refresh/dispose; watcher отсутствует.

Текст: назначенный игрок или «Адресат не назначен», четыре human action captions,
«Точка выбрана»/имя цели, предложение сформировано либо отсутствует. Lease всегда
«Время вмешательства неизвестно». Hint объясняет, что действие ещё не выполнено.
Не показывать технический serial/entityIndex/epoch или источник как право ввода.
canSend/nativeConfirmed/sourceAuthorizationConfirmed=false в metadata.

В этом же подпроекте подготовить отдельный fixed source kind из 5 assets/4 links:
loader/XML/CSS/state/panel. Validator exact topology/dependencies на existing parser,
local Panel.visible extension, старые defaults неизменны. Handoff mouse-proposal,
10 фиксированных вариантов в registry. Actual packaged VM не native runtime.
Native mouse/UI geometry/lease/server/ИИ return/другой владелец остаются открытыми.
