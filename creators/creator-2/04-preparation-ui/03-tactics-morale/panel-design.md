# Панель тактики и разговора

**Дата UTC:** 2026-10-10. **Основа:** a882841. [Модель](design.md).
Пользователь поручил автономное продолжение с пятью read-only критиками.

Отдельный source Panorama screen поверх единственной DotaCoachPreparation модели.
Два прокручиваемых списка по восемь вариантов, без пагинации: plan/talk catalogs bounded8.
Два выбранных варианта с явным удалением, общая очистка, private lineup summary.
Альтернативы с precomputed morale или server submit требуют C1 и общего контракта;
в этой части только local presentation/selection. Это не native приёмка.

## API и managed nodes

DotaCoachPreparationPanels.bind(root) → update(frame), choosePlan(id), chooseTalk(id),
removePlan(), removeTalk(), clear(), draft(), dispose(), isDisposed(). Все actions
используют pure модель; внешний frame повторно не читается, render только model.view.
Нет autochoice, no bootstrap/manifest/HUD/native/transport/storage/start.

Root PreparationRoot. Core labels: PreparationStatus, PreparationCount,
PreparationWarnings, PreparationPlanHint, PreparationTalkHint, PreparationLineup;
PreparationClear button. Plan/Talk option slots PreparationPlanN/PreparationTalkN,
N0..7, fields Label/Version/Intent/Action. Selected buttons PreparationChosenPlan,
PreparationChosenTalk, fields Label/Version/Intent/Action. 97 required children + root.

В каждом варианте до выбора видны label, optionVersion, intent. Action — «Выбрать план»
или «Выбрать вариант разговора»; уже выбранное отключено и подписано «Уже выбрано».
Selected Action — «Снять выбор плана»/«Снять выбор разговора». Тренер читает подпись; handler использует copied-view id/version,
не применяет gameplay effect. Count local N/2. PlanHint/TalkHint всегда отражают
состояние текущего каталога: отдельное отсутствие предложений, ещё не выбранный вариант
или выбранный local draft. Два fixed warnings модели остаются видимыми при ready.

Lineup summary обозначен как технический local draft; только private virtual id/profileVersion/heroId/позиция из model.view;
это stable identifiers, не реальные имена/портреты и не доказанное владение героем.
Без ready summary/варианты/selected/warnings очищены. Начальный XML inert/disabled,
все labels plain html=false; нет Start/Submit/Image/CustomUIElement/run/on* attributes.
XML includes CSS→preparation_state.js→preparation_panel.js definitions only.

## Lifecycle и проверки

Owner одного root резервируется до discovery. Все required nodes (включая скрытые)
валидны перед input/actions/draft/isDisposed. Generation увеличивается до DTO getters,
после каждого external UI write guard; callbacks captured copied-view id+generation; version принадлежит тому же снимку и
не оживают при ABA. Rejected old frame всё равно rebind актуальных handlers.
Dispose закрывает модель, очищает timer/labels/buttons, скрывает root до owner release.
Watcher0.25 только lifecycle; partial discovery/render/schedule failures освобождают owner.
Старая operation/getter/timer не меняет fresh bind; two roots независимы.

VM tests: explicit pick/remove/clear/unknown/noop, emptygroup/reset, selected intent,
lineup/optionversionchange/stale callbacks, getter disposal/reentry/getter readonce,
plain labels/draftcopy, hidden failure, partialfail/freshbind/timer/tworoot.
Graph проверяет98uniqueIDs/19disabledbuttons/ресурсы/definitions inert/noHUD inclusion.
CSS scroll/ширина/compile/hittest, реальные каталоги/C1/effect/server и второй владелец открыты.
