# Карточки и запрос на одном локальном экране

[Подпункт](README.md). Основа3306834. Пользователь: продолжать без остановки.
Исполнитель C2 самостоятельно; итоговый критик один после завершения подпроекта.

Общий экран связывает existing Roster panel и Requests panel с одним private
InterventionSelection. Не копируем состояние/исходники. Сервер/native/lease/возврат
ИИ остаются зависимостями; no auto-bootstrap. Source recipe — следующий подпроект.

1. flow.rosterPort() — stable owned объект replace/select/clearSelection/view/
   dispose/isDisposed; операции используют тот же flow. Его dispose закрывает flow.
2. RosterPanels.bind(root,onSelection?,projection?) принимает порт через existing
   PanelPorts. Standalone семантика сохранена, включая старый handler по stable ID.
   Интегрированный handler привязан к generation отрисовки. Reserve root до discovery,
   все nodes проверяются, busy/staging не позволяет getter-triggered selection;
   refresh/suspend поддерживают внешнюю транзакцию, очистку и безопасный repaint.
3. InterventionScreenPanels.bind(root,send?) владеет flow и двумя child panels.
   distinct scopes CoachInterventionRoster/ManualRequestRoot, общий plain status.
   replaceRoster/updateControl/selectPlayer/clearSelection staging обеих областей
   ДО чтения DTO, затем обновляют flow и обе панели. Parent busy/generation guard;
   guard порта не вызывает child.isDisposed рекурсивно. Click карточки обновляет
   manual pane через onSelection. Request click отправляет только через caller send.
4. Любая потеря required node закрывает group/flow/таймеры/children до новых DTOreads;
   partial bind не прячет чужую independently bound scope. Один root — один owner.
   Старые callbacks после dispose/rebind не влияют на новую группу.

Group view наружу — copied flow.view() или null при busy/closed. Новый layout пока
не обещается: caller предоставляет существующее дерево; отдельный inert composition
будет собран после этого подпроекта. Это UI source acceptance, не запущенная Dota.

Групповой watcher также обновляет plain сводку каждые0.25сек, чтобы локальный
ACK timeout отображался без новой команды. Этот timer не является игровым lease.
