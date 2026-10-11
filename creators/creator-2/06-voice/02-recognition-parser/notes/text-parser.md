# Явное подключение local parser

[Подпункт](../README.md) · [Дизайн/API](../design.md).

Загрузить existing `DotaCoachRoster` перед `DotaCoachVoiceText`; новый definition
сам ничего не создаёт. Caller явно создаёт parser, принимает полный локальный
snapshot `{revision,players}` и обновляет его. `players` использует семь полей
canonical карточек C2-02-01. Это local input adapter, не server command contract.

```javascript
var parser = DotaCoachVoiceText.create();
// После parser.update({revision: 1, players: ownSnapshotRows}):
var preview = parser.ingest({
    utteranceId: "example-final-1", text: "керри, отступай",
    rosterRevision: 1, final: true
});
// preview.status === "ready" означает лишь локальное предложение.
parser.dispose();
```

Caller захватывает rosterRevision при начале utterance. Изменение состава требует
новой финальной фразы с новым ID; нельзя автоматически подставлять последнюю
ревизию в старый event. Интерим не исполняется и не резервирует ID. Ошибочные
финальные фразы резервируют ID; исправленная фраза получает новый ID. До128 ID,
затем history_full. Пересоздание экземпляра сбрасывает только локальную историю,
поэтому эта защита не является серверной дедупликацией. Текст/аудио не сохраняются.

`normalizedText` — plain text; будущая UI должна назначать его plain Label с html=false.
Не интерпретировать его как markup или JavaScript. `proposal` нельзя напрямую
отправлять как игровой приказ: C1 должен определить авторизацию/версии/дедупликацию,
конфликты/цель/срок и действие персонального ИИ. Парсер не угадывает coordinates,
атаку/покупку, адресата выбранной карточки или сведения вне своего snapshot.

Проверка из корня:

```bash
node --test creators/creator-2/06-voice/02-recognition-parser/tests/voice-text.test.cjs
```

Это проверка уже распознанного текста. Реальный микрофон, ASR/задержка/качество и
разрешённый канал Dota проверяются в C2-06-01; панель обратной связи — C2-06-03.
