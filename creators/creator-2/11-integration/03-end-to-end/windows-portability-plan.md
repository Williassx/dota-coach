# План Windows portability

[Дизайн](windows-portability-design.md).

1. RED tests: consistent Python/Node skips, impossible/duplicate counts, all-skipped,
   incomplete report classification/strict exit; symlink probe known/unknown errors.
2. Root: test-only probe, runner additive counters/classification; разделить runner
   file/directory link cases от available output/path checks. Helper агент: только
   packaging/handoff mixed cases с тем же require_symlink API.
3. Targeted helper/runner/packaging/handoff checks. Полный required source run вне
   sandbox: owned taskkill test permission уже диагностирован; OS не менять.
4. Проверить accurate totals, skip reasons, все native/source flags и new report
   preserved paths; финальный critic после завершённого результата.
5. Report/README/resume/lessons/action log/usage/graph/links/diff; разрешённая Git
   публикация и remote SHA/clean. Incomplete security coverage не объявлять PASS.
