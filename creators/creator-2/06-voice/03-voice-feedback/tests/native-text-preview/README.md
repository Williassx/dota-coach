# Native test-only text preview

[Дизайн](../../native-design.md) · [План](../../native-plan.md).
Этот driver не входит в fixed voice kind. Explicit public API exercises use
synthetic TEST profiles; нет microphone/ASR/transport/server/input callback.
preview(text) не является физическим вводом. Engine screenshot подтверждает
только отображение и lifecycle фаз. Report и native compilation отдельно.
