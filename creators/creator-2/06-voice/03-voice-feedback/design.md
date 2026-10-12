# Source-панель текстового разбора

[Подпункт](README.md). Самостоятельный C2 результат: явный локальный ввод текста,
его разбор существующим VoiceText, адресат/действие/причина отказа. Пользователь
поручил продолжать самостоятельно. Микрофон не подключён, приказ не отправляется;
надпись готовности относится к предложению. Никаких fake ACK/lease/game results.

Один canonical voice_text_panel.js с explicit bind(root); private existing parser.
API updateRoster(snapshot), preview(text), receive(event), clear(), view(), dispose(),
isDisposed(). preview берёт текущую локальную revision и уникальный ID этой панели;
receive сохраняет revision/ID внешнего уже распознанного event. Внешний канал не
реализуется здесь. Для имён в UI proposal VoiceText получает copied recipientNames
из того же принятого snapshot, не новый параллельный resolver.

Canonical XML: VoiceTextRoot, input VoiceTextInput, buttons VoiceTextPreviewButton/
VoiceTextClearButton и plain labels VoiceTextStatus/Normalized/Address/Action/Hint.
Определения Roster→VoiceText→Panel; без automatic bind. Кнопка «Разобрать текст»
считывает input.text только после lifecycle/busy guard. После любого source update
поле и предложение очищаются до чтения DTO: старый набранный текст не адресуется
новому составу. Невалидный update закрывает preview gate до следующего валидного
snapshot, даже если private parser сохранил прошлый snapshot. clear не сбрасывает
историю финальных ID и не отменяет серверные действия.

Резервный ввод здесь ограничен preview; общий исполняемый голос/кнопки требуют C1.
Root owner до discovery, обязательные nodes/identity/visibility, staging до DTO,
busy и generation guards для setters/старых handlers, cleanup/one0.25watcher.
Dispose при getter/renderer/scheduler нельзя сменить старым repaint; cancelled
callbacks не трогают свежую привязку. Только plaintext; без native игровых API.
Native XML требует anonymous outer Panel; explicit scope — внутренний VoiceTextRoot.
Ограниченная test-only приёмка XML/TextEntry/preview описана в [native design](native-design.md).
Физический ввод/hittest, микрофон, MANUAL и server остаются открытыми.
