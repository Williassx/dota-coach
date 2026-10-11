# План source-пакета ручного запроса

[Дизайн](intervention-design.md). Выполнение: основной агент, TDD; один итоговый критик.

1. Создать tests/test_intervention_bundle.py, реальные canonical inputs в temp checkout.
   RED: exact six resources, roundtrip/no runtime proof, dependency graph, failures
   before output, byte tamper/current-source change, unchanged default/HUD policies.
2. Добавить intervention-manifest.json и C2-05-01 source custom_ui_manifest.xml.
   В существующем build helper добавить exact mapping и strict XML validator нового kind.
   GREEN, не изменять verifier/canonical JS/CSS/layout или старые policies.
3. Actual CLI build/verify в новом ignored output; один итоговый critic, concrete fixes
   RED→GREEN, полная регрессия и синтаксис. notes/report/README/journal по фактам.
4. Обновить checklist упаковки и график C2, сохранить compact start_skill/readback,
   diff checks до commit, fast-forward main, remote SHA/clean.

Native installation/compilation/hittest/bootstrap/C1 authority/lease/возврат ИИ,
совместная проверка вторым владельцем остаются открытыми.

Реализация и полная регрессия завершены: 648 PASS. Публикация/итоговая проверка
фиксируются в отчёте и журнале; native/второй владелец остаются открытыми.
