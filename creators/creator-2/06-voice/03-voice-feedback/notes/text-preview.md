# Explicit source text preview

[Подпункт](../README.md) · [Дизайн](../design.md).

Загрузить Roster→VoiceText→VoicePanels в одном контексте XML voice_text.xml,
затем явно вызвать `DotaCoachVoicePanels.bind(root)` для внутреннего
`VoiceTextRoot = $.GetContextPanel().FindChildTraverse("VoiceTextRoot")`.
Внешний root Panel анонимный: native compiler запрещает ему id. bind не запускает
микрофон или игру. Production bootstrap и физический ввод остаются открытыми.

```javascript
var panel = DotaCoachVoicePanels.bind(root);
// panel.updateRoster({revision: 1, players: existingCardRows});
// После принятого snapshot пользователь вводит «керри, отступай» и жмёт
// «Разобрать текст»; для внешнего caller доступно panel.preview(text).
panel.dispose();
```

`updateRoster(snapshot)` использует schema existing VoiceText: локальные revision
и карточки. Каждое обновление до чтения DTO очищает поле/preview. Отказ источника
выключает gate до следующей принятой revision; старое намерение не восстанавливается.
`preview(text)` даёт новое локальное final событие. `receive(event)` для будущего
caller сохраняет ID/revision/final из event; не обновляйте автоматически ревизию
старой фразы. Интерим/duplicate/stale/ambiguous/unavailable отражаются локально.

Методы возвращают true только для принятого snapshot или ready preview; rejected/
interim тоже обновляют отображение при валидной scope. `view()` возвращает копию
projection/result либо null во время staging/dispose. Captured recipientNames
показываются plain labels с html=false. При source change input и result пусты.
`clear()` очищает только input/preview, сохраняя final ID history. Ни clear, ни
dispose не отменяют серверное действие. После128 событий preview недоступен в
этой source-сессии; поведение нового игрового сеанса задаст будущая интеграция.

Root/required nodes/identity/visibility guard, busy до tree preflight, generation
handlers и один0.25s watcher закрывают scope при потере элементов. Старые callbacks
не трогают новую привязку. Скрытая input scope не даёт прочитать event DTO.

Из корня проверено:

```bash
node --test creators/creator-2/06-voice/03-voice-feedback/tests/voice-panel.test.cjs
python3 -m unittest discover -s creators/creator-2/06-voice/03-voice-feedback/tests -p 'test_*.py' -v
```

UI пишет «Микрофон не подключён» и «Ничего не отправлено». Это source text preview,
не уже работающий резервный путь исполнения приказа или проверенный голос.
