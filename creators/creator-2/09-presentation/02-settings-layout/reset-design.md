# Reset scroll: tracing одного runtime

13октября2026, leading157/root107/114/173/174/175.
[Исходное расхождение](reports/preparation-scaling-2026-10-13.md): model reset PASS
при native scroll−695. Пользователь поручил2часа самостоятельной работы с06:01:04
до08:01:04UTC (08:01–10:01 Europe/Berlin). Root ведёт исполнение и общие файлы.

Bounded diagnostic, не production fix: fresh existing preparation fixture получает
exact variant `reset`, fixed kind15/14 и default driver не меняются. Native driver
в C2-09-02/tests создаёт5synthetic profiles/assignments/2choices через существующий
explicit public API. Четыре independent bind cycles на одном build/размере1600×900
сравнивают immediate/0.5s delayed ScrollToTop после removePlayer(TEST-p4), ABAB.

Перед reset дождаться layout и API bottom. Записывать operation boundaries и
samples Schedule0.1s: scroll/content/viewport, UI context counts, cursor/buttons,
Alt/Ctrl/Shift, Date.now elapsed. Ни одной origin/foreign data read, game order,
server/storage/lease/AI claim. AfterReset predicate проверяет model4/5; top отдельно.
Каждый опыт завершить через2s после remove. Banner/read-only logs сохраняют исходы.

Global SetMouseCallback не устанавливать: восстановление предыдущего callback
и события wheel/keyboard не подтверждены local native dump1026/1031/1034–1040;
официальная wiki403 не доказывает отсутствие API. PhysicalInputControlled=false;
sampledInputQuiet только bounded observations, inputTainted при observed activity.
Краткие события между samples и полный keyboard/wheel остаются ненаблюдаемыми.

Source-level tests pin exact variant/refusal/default preservation и driver scheduling/
malformedinput/dispose guards. Native compile/fourtrials/actualscreens наодномbuild;
самые интересные стадии снять кадрами. Причину объявлять только по фактической trace,
не по ожидаемому0.5s. Human owner/C1/input/product acceptance остаются открытыми.
