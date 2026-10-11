# План local text parser

[Дизайн](design.md). Inline execution; журнал C2-00-action-log.

1. Добавить README в src/Panorama и tests, один canonical voice_text_state.js.
   Сначала RED Node VM suite с existing roster dependency и запрещёнными native API.
2. Реализовать bounded own-descriptor copying, atomic monotonic snapshot, finite
   vocabulary, строгие адресаты/группу, final-only history и copied proposal.
   Проверить ambiguity/unavailable, stale/duplicate/interim, input bounds/getters,
   reentrancy/dispose и отсутствие отправки. Targeted suite RED→GREEN.
3. Полная source regression с новым suite; один итоговый критик по готовому
   подпроекту, необходимый fix pass. Отчёт/журнал/учёт/progress, ссылки/whitespace,
   startup draft и normal main push с SHA/clean verification.

Общий command contract, реальный ASR/микрофон, transport и native acceptance
остаются открытыми; соответствующие checklist items не закрываются parser тестами.
