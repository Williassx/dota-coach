# tests C2-07-03

Node VM проверки с канонической моделью Orders.

[Родитель](<../README.md>).

[orders-timeline.test.cjs](orders-timeline.test.cjs) — 20 Node VM сценариев с настоящим Orders.
[orders-timeline-panel.test.cjs](orders-timeline-panel.test.cjs) — 15 VM сценариев binding
с настоящими Orders/history; [test_timeline_layout.py](test_timeline_layout.py) — два XML checks.
Целевая команда из корня:

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-orders-timeline --suite node-orders
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-orders-timeline-panel --suite python-c2-07-03
```
