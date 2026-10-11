# Source-панель и пакет предложений мыши

[Родитель](README.md) · [План](../panel-plan.md).
2026-10-11, Linux cloud, creator 2. Root самостоятельно; один reused final critic
после обеих фаз, существенных воспроизводимых дефектов не обнаружено.

13 Node RED (отсутствующий panel) → 13 PASS. 2 Python source XML проверки.
8 packaging tests: RED 4 unsupported-kind errors, 4 guard PASS → 8 PASS.
Targeted 5 suites / 163 PASS. Full canonical 45 suites / 938 PASS, без
fail/skip/cancel/todo; source-checks-20261011T141517Z-1d0f32.

Actual handoff: probe-ui-20261011T141517Z-fe063e, kind panorama_source_mouse_proposal,
5 assets/4 links/7 IDs/6 plain Labels. Current-source bytes и hash verification,
exact topology/dependencies/loader/DTD/symlink/output preservation проверены.
Упакованные XML + оба JS проверены в одном VM context с запрещённым native API.
Handoff helper теперь имеет 10 альтернативных fixed screens; прежние ограничения
и default probe сохраняются. Generated output не является canonical исходником.

Панель показывает фиксированного игрока, действие/цель, неизвестное время и отсутствие
исполнения. Invalid proposal очищает draft, дерево/ownership/reentry/dispose проверены.
Не проводились Source2 compile, native layout/hittest, реальные клики/геометрия,
entity identity/source authorization, lease, игровой эффект/возврат ИИ и приёмка
второго человеческого владельца. installation_performed=false, native checks not_run.
