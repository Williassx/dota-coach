# API локальной истории

`DotaCoachOrdersTimeline.create()` создаёт частную историю для **одного** Orders.
Она не требует загрузки Orders для работы, но принимает его exact 11-field view.
Один источник сохраняет собственную local ticket последовательность. Новый Orders
в новой сцене требует новой истории; это не server epoch/actor identity.

- `record(orderView)` → `{status, added}`. status: recorded/unchanged/invalid/busy/closed.
  Вход читается через own data descriptors; getters не вызываются. Повторы не
  создают событий. Actor/action фиксируются для ticket и не меняются при выборе
  другой карточки. Строго более новый ticket может заменить старое отслеживание.
- `view()` → копия `{events,capacity,droppedEvents,lastTicket,closed}`; во время
  входного чтения — null. events идут от старых к новым; максимум64, вытеснения
  явно учитываются. Последняя correlation сохраняется независимо от вытеснения.
- `dispose()` закрывает и удаляет историю/имена. Закрытый Orders.view закрывает
  её также. Закрытые/reentrant вызовы не читают чужой DTO.

Event: eventIndex, ticket, kind, actorName/actionText, stage/stageText/reasonText,
lastReportedStage, outcomeUnknown, evidence и nativeConfirmed. `eventIndex` — местный
счётчик событий, не server sequence и не timestamp. outcomeUnknown относится к
сообщённой стадии; completed содержит сообщение источника, не проверенный игровой
эффект. evidence всегда presentation_snapshot; nativeConfirmed всегда false.
Перед отображением используйте Label(html=false), а не HTML-разметку имён/причин.

Если ticket исчезает либо заменяется до terminal, добавляется tracking-ended.
Это конец UI-отслеживания с неизвестным итогом, не отмена/победа/эффект. Промежуточные
стадии между record вызовами теряются: polling не является полным журналом сервера.
Терминальный результат одного ticket не перезаписывается. История не выдаёт приказы,
не разрешает повтор, не меняет selected card и не восстанавливает полномочия.
