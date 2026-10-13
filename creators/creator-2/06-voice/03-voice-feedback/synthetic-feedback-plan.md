# Проверка existing feedback на actual synthetic гипотезах

После C1 публикации root продолжает C2. Ведущая роль76, область — только
тестовые данные/VM проверки existing VoicePanels; production parser/panel,
fixed bundle, C1/transport/mic/ASR/native input не меняются.

Основание — [grammar report](../02-recognition-parser/reports/synthetic-grammar-2026-10-13.md):
refs3ready, actual tiny hypotheses3unknown_action. Проверяется риск сохранения
ранее показанного готового предложения после ошибочного decoded события.

## Приёмка

- Для каждой из трёх пар existing actual modules bound, synthetic5-own snapshot1.
  Receive reference с уникальным id даёт ready и правильный local recipient/action;
  следующий receive actual raw hypothesis с другим id даёт unknown_action,
  proposal=null, Address/Action пусты и явный статус отказа. Raw text не исправляется.
- Captured revision1 после roster2 остаётся stale_roster, не подменяется текущей.
- Dispose/rebind: stale handle с Proxy не читает DTO и не меняет fresh view;
  fresh model с новыми id принимает reference, ошибочная hypothesis снова отказ.
- Attempts native/GameEvents/commands0, watcher cleanup, TEST origin явный.
  VM/labels не реальные кадры, клавиатура/кнопка/ASR bridge и authority не подтверждены.

## План и владение

- [x] Helper owns only tests/voice-panel.test.cjs и new bounded JSON cases file;
  actual3refs/hyps сохраняются с raw result SHA/source/date, аудио не копируется.
- [x] Targeted VM proof; при unexpected failure сначала root diagnosis, не
  исправлять production по предположению и не ослаблять assertions.
- [x] Root verifies cases against raw result, source preservation, full regression,
  report/one final review/lessons/usage and publication; progress не повышается.
