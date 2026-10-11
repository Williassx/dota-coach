# custom_game C2-07-03

Pure модель без transport, timers и game API.

[Родитель](<../README.md>).

[orders_timeline_state.js](orders_timeline_state.js) — единственная pure модель истории.

[orders_timeline_panel.js](orders_timeline_panel.js) — explicit read-only binding одной
частной истории; нет handlers/timers/transport и auto-bind.
