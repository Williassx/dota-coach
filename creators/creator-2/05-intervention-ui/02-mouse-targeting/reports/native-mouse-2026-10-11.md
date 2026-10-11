# Windows: компиляция mouse-targeting 7/6

[Подпункт](../README.md) · [Native план](../native-plan.md) · [Recipe](../../../11-integration/02-addon-packaging/mouse-targeting-manifest.json).

Ведущая роль:C2 UI/Tools. Продолжение windows-resume step5; source foundation
не заменяется новым native sender. Основа c923dd2, Dota build25845666.

## Причина и исправление

Свежий handoff mouse-targeting7/6 успешно прошёл source verifier, но native
resourcecompiler отказал: `Found root panel with 'id' attribute, which is not permitted`.
Исходный mouse_proposal.xml имел id=MouseProposalRoot у верхней панели layout.
Это реальное расхождение между source policy и Source 2, не ошибка C1.

Canonical XML теперь имеет безымянный MouseProposalHost с hittest=false и
hittestchildren=true, занимающий viewport; внутри сохранены прежний скрытый
MouseProposalRoot и шесть пустых plain Labels. Семь ID/API не изменились.
Оба kinds используют тот же exact standalone validator; он требует ровно эту
структуру и отклоняет identified host/изменение input policy. Shared parser,
probe/HUD policy, manifests, JS и серверные контракты не менялись.
Explicit binder получает внутренний component по ID, не внешний context panel.
Нативное попадание клика этим исправлением ещё не проверено.

## RED → GREEN и native compile

Три source layout checks: новый test сначала упал на идентифицированном XML root,
две новые bundle policy проверки сначала пропустили запрещённый root. После
минимального исправления все пять прошли. Actual source/model checks в полном
runner: Targets36, MouseProposals17, MousePanel13, MouseTargeting20, layout3 —
пять успешных suites/89 сценариев. Новые две policy проверки дополнительно
проверены отдельно; они также проходят в общем packaging log.

Fresh source bundles без ручного редактирования output:

- 7/6: build/dota_coach/probe-ui-20261011T185609Z-335fc7;
- 5/4: build/dota_coach/probe-ui-20261011T185648Z-2216e7.

Их source_verified=true; immutable handoff сообщает stage=source_only,
source2_compiled/runtime_verified=false. Эти поля описывают подготовку пакета,
а последующая native компиляция фиксируется отдельно здесь.

Исходный неудачный addon dota_coach_c2_mouse_20261011 сохранён. Исправленный
7/6 скопирован в новый dota_coach_c2_mouse_r1_20261011; оба destination до
создания отсутствовали. Probe и пользовательские аддоны не перезаписывались.
Установлена только Panorama, без карты, bootstrap/auto-bind или C1 handlers.

```powershell
$taskDotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
& "$taskDotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$taskDotaRoot/game/dota" -i "$taskDotaRoot/content/dota_addons/dota_coach_c2_mouse_r1_20261011/panorama/layout/custom_game/custom_ui_manifest.xml"
```

Exit0: OK1compiled/0failed/0skipped. Семь native outputs проверены непустыми
и по SHA-256 в build/dota_coach/native-mouse-outputs-r1-20261011.json:

| Output | Байты |
|---|---:|
| custom_ui_manifest.vxml_c | 1389 |
| mouse_proposal.vxml_c | 1920 |
| mouse_proposal_panel.vjs_c | 7776 |
| mouse_proposal_state.vjs_c | 6804 |
| mouse_targeting_binding.vjs_c | 6179 |
| targets_state.vjs_c | 10200 |
| mouse_proposal.vcss_c | 1864 |

Локальный журнал native-mouse-compile-r1-20261011.log содержит финальный
Leaked KeyValues blocks:162; compile exit0. Неудачный предыдущий compile log
сохранён отдельно. Native compile не доказывает runtime bind/visibility/hittest.

## Полный source runner: не пройден

После изменения XML/validator выполнен полный existing runner на Windows с
PYTHONUTF8=1: 46suites,752passed_tests, verified=false. Отчёт:
build/dota_coach/source-checks-20261011T185649Z-71eb61/source-checks.json.

Упали python-c2-01-01, python-c2-01-02, python-c2-03-01, python-c2-11-02,
python-c2-10-01, python-c2-11-03. В логах сохраняются WinError1314 для symlink,
WinError206 для длинных путей и platform/mock/timeout расхождения. Packaging
suite выполнил116tests с8errors создания symlink; его нельзя объявлять зелёным.
Набор упавших suites совпадает с предыдущим Windows прогоном, но число/случаи
failures не объявляются неизменными: сейчас test_another_manifest_installation_cannot_assign_this_build
получил manifest_changed вместо installation_mismatch. Причина этого отдельного
map-audit расхождения не установлена; изменение XML не выдаётся за его исправление.
Symlink/security tests не пропущены и не ослаблены, ОС не перенастраивалась.

## Открытая native приёмка

Явный native bind/clock/paint/dispose, физический hittest, карта этого аддона,
реальные observations/identity, permission/lease и AI return открыты. Inert XML
сам не покажет панель; auto-bind не добавлен. Ни один checkbox native gameplay
не отмечен по compile. Дальнейшие проверки — в плане выше; human C1 review открыт.
