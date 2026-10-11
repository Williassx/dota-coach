# Облачная проверка text preview UI

[Подпункт](../README.md) · [План](../implementation-plan.md).

**Дата UTC:** 2026-10-11. **Основа:** 355c194. Commit — в Git-истории записи.

Добавлена отдельная canonical source-панель с input/двумя кнопками/пятью plain
labels, CSS и XML Roster→VoiceText→Panel. Explicit bind/private parser; text/button
preview, receive уже распознанного event, clear/view/dispose. Никакого игрового
send/микрофона/ASR. Source updates очищают input/result до DTO reads; invalid source
закрывает gate. Root owner до discovery, required identity/visibility, busy и
generation guards, plaintext, cleanup и один0.25s watcher с поддержкой handle0.

Existing parser proposal дополнен copied recipientNames из того же snapshot для
UI, без второго resolver. Один новый RED→GREEN; прежний exact proposal test обновлён
по расширенному local design. Первые18VM/3XML дали RED из-за отсутствующих source
files, затем PASS. Self-review: два RED→GREEN для busy nested API/tree preflight;
busy резервируется до native discovery. Hidden root — отдельный GREEN control.
Итого21VM+3XML+1parser новый сценарий. Проверены actual button/input callbacks,
адресат/действие/отказы, staging/source reset/gate, interim/duplicate/stale, clear
с history, plaintext/copies, hidden/invalid/replaced nodes, stale callbacks,
partial failures/duplicate owner/watchers/reentry/dispose и capacity.

Полная регрессия: **33 suites / 749 PASS**, нулевые fail/skip/cancelled/todo.
Один reused итоговый read-only критик не выявил существенных дефектов в адресации,
source reset, busy/generation, identity/visibility, cleanup/stale callbacks.
Повтор полной регрессии без изменений кода не запускался. График29/197 (14.7%).
Native XML/TextEntry/компиляция/layout/hittest, packaging/manifest, ASR/реальный
микрофон/задержка, transport/общий контракт/MANUAL/эффект и второй владелец открыты.
