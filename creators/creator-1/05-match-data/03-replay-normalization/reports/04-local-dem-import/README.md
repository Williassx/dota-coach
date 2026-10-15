# 04 — локальный импорт DEM

[Отчёты](../README.md) · [спецификация](../../telemetry-import-design.md) · [план](../../telemetry-import-implementation-plan.md).

Владелец реализации C1, проверяющий C2. Постоянные исходники находятся только в `../../src/`; raw DEM, JDK/JAR, classfiles, local config и полные JSONL остаются в ignored build. Результат — offline spectator research, без обучения или runtime-интеграции.

- [Результат и ограничения](result.md).
- [Измерения, версии и доказательства](receipt.json).
- [Независимый итоговый обзор](technical-review.md).
- [Инструкция](../../notes/dem-import-usage.md).
