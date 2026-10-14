# C2-06-03 — Ответ и резервный ввод

**Техническое рассмотрение14октября:** [отдельный peer другого создателя](../../../creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.md). Выполненная передача относится к техническому объёму; полная функциональная, продуктовая и правовая приёмка не следует из этого checkbox. Более ранние статусы ниже относятся к указанному в них срезу.

**Отдел:** создатель 2. **Проверяющий:** создатель 1.
**Статус:** частично подготовлена source-панель local text preview; native/голос/C1 открыты.
**Зависимости:** [C2-06-02](../02-recognition-parser/README.md), [C2-02-02](../../02-coach-interface/02-status-orders/README.md).
**Рабочая папка:** `creators/creator-2/06-voice/03-voice-feedback/`.

[Раздел](../README.md) · [План создателя](../../PLAN.md) · [Общие правила](../../../shared/WORKFLOW.md)

## Действия

- [x] Проверить локальную source-панель текста, адресата/действия, причин отказа и lifecycle.
- [ ] Показать услышанное, адресата, принятие и результат.
- [ ] Подключить кнопочный/текстовый эквивалент к той же команде.
- [ ] Проверить отказ микрофона, задержку и MANUAL.
- [x] Сопоставить фактический результат с критерием ниже и записать непроведённые проверки. Сопоставление source/native и непроведённых сценариев оформлено14октября. [Доказательства](reports/autonomous-acceptance-2026-10-14.md).
- [x] Передать изменение второму создателю для проверки, затем обновить этот статус. Техническая передача и independent peer review14октября выполнены; функциональные ограничения сохранены. [Доказательства](../../../creator-1/11-integration/03-joint-acceptance/reports/c2-technical-review-2026-10-14.json).

## Результат и приёмка

Голос и кнопки имеют одинаковую семантику, отказ записи не ломает матч.

## Где размещать материалы

- `src/` — единственные исходники данного подпункта.
- `tests/` — проверки поведения и отказов.
- `reports/voice-ui.md` — фактические результаты и ограничения.

Это назначение будущих файлов, а не заявление, что все они уже созданы.
Новый вложенный каталог получает README с назначением и ссылкой из этого файла.
API, сигнатуры, конкретные файлы и команды проверки закрепляются в локальном
техническом плане после исследования входов; не подменяйте их выдуманными командами.

## Source text preview

[Дизайн](design.md) · [План](implementation-plan.md) · [Исходники](src/README.md) ·
[Проверки](tests/README.md) · [Явное подключение](notes/text-preview.md) ·
[Отчёт](reports/cloud-text-preview.md).

Поле и кнопка разбирают текст существующим private VoiceText. Видны local proposal
или причина отказа; никакой отправки/серверного результата. Source update очищает
поле до DTO reads; invalid source закрывает gate. Нативная запись, ASR/transport,
MANUAL/эффект, общий контракт и второй человеческий владелец остаются открытыми.

[Native design](native-design.md) · [Native plan](native-plan.md) ·
[Test-only fixture](tests/native-text-preview/README.md) ·
[Native report](reports/native-voice-text-2026-10-12.md).
Canonical layout получает anonymous outer Panel для Source2; fixed пакет остаётся6/5.
Text preview через public API не подтверждает физический ввод или работающий голос.

[13 октября: actual synthetic decoded feedback](reports/synthetic-feedback-2026-10-13.md): threepairs ready→reject очищают предложение; capturedrevision/dispose guards подтверждены source VM, production/grammar unchanged.
