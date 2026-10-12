# Native mouse targeting — 12 октября 2026

[Родитель](../README.md) · [Дизайн](../native-mouse-targeting-design.md) ·
[План](../native-mouse-targeting-plan.md) · [Fixture](../tests/02-native-mouse-targeting/README.md).
Windows D:/AI/dota2coach, baseline aa6fb49/main/clean, Dota build_id25845666
проверен в appmanifest_570.acf. Ведущая роль76; root единственный автор.
Read-only windows_learning сверил DTO/API. Production JS/XML/CSS, C1 и shared
контракты не изменены. Проверка existing binding, не реализация mouse input.

## Source fixture и проверки

Fixed kind panorama_source_mouse_targeting сохраняет7assets/6links/7ID и четыре
канонических определения. Builder использует существующую guarded prepare_assets:
derived layout добавляет пятый TEST driver и literal status вне MouseProposalRoot.
Девять outputs: canonical six без manifest, own manifest/driver/derived layout.
Два generated layouts: retained canonical targeting XML и TEST derivative.
Seven raw canonical inputs fingerprint отдельно от seven canonical output hashes.
Canonical targeting XML SHA25637d5d7b23d36c6ccebcd1ec7563cd1eb4a0122d39d40d3b0f099c4b33743ec7b.

RED7missing builder→первый прогон6PASS/1FAIL: generated canonical XML ошибочно
помечен copied, проверка обнаружила отличие от raw standalone XML с двумя JS.
Исправлены metadata derived и assertion exact fixed-policy bytes; source unchanged.
Final7PASS: canonical bytes/subtree/dependencies/fingerprints/determinism и отказ
до writes для existing/escape/missing driver/changed mapping/executable manifest.
Existing coordinator20VM PASS, driver syntax PASS; targeted27PASS.

Required full source-checks-20261012T133855Z-3b442f:46suites/753passed_tests,
6failed/verified=false. python-c2-01-01/01-02/03-01 invalid_summary при expected
Windows skips; python-c2-11-02/10-01/11-03 process_exit при WinError1314 symlink.
Packaging162tests:154PASS/8WinError1314; новые7fixture PASS. Existing targeting
package8/9 с прежним WinError1314. Full не green; skips/OS/security не изменены.
Source-only handoff134114Z-00b8f6 verified7/6, source2_compiled/runtime_verified=false,
native checks not_run сохранены.

## Установка и native run

Fresh bundle native-mouse-targeting-20261012T133704Z-7fa4b5 и новый addon
dota_coach_c2_mouse_targeting_20261012. До установки content/game directories
отсутствовали; девять bundle/install hashes совпали. Valve addon_template map и
workshop_testbed addoninfo скопированы отдельно, existing addons сохранены.
Resourcecompiler -v -nop4 -game game/dota -i: own manifest1compiled/0failed,
retained mouse_proposal.xml1/0, template_map.vmap13/0; всеexit0, без -novpk.
Leaked KeyValues blocks162 сохранён, причина неизвестна.

Девять compiled UI files48258bytes =8active dependencies +retained canonical XML.
Map VPK3033475bytes/SHA25652aa243cbafa239501157a703f1c3d33ef098580d95f5f6ec6ffbb5ec8819eea.
Raw source/compiled fingerprints сохранены локально в
build/dota_coach/native-mouse-targeting-hashes-20261012.json.
Собственный PID27104/window1280×720, fresh HERO_SELECTION проверен перед каждой
cheats/hero командой; PRE_GAME13:41:58UTC. Actual кадры содержат штатного Axe;
TEST actor A/B и entityIndex10 не являются его идентификацией или mapping.

Все восемь фаз/cycle PASS, native pane253×167 на открытых фазах. Проверены
положительные dimensions Actor/Lease/Hint; остальные подписи осмотрены на кадрах.

1. bound: empty source/no actor/proposal; unknown intervention time.
2. attack: TEST A, enemy hero t, serial1, literal `<b>TEST t</b>`/html=false.
3. captured-switch: intermediate enemy creep last_hit/serial2/caption проверены
   assertion; затем select ally creep u снимает draft без auto action, явное
   propose даёт deny/serial3. captureActor B отвергнут; actor остаётся A.
4. expiry: controlled ms999 сохраняет draft, ms1000+explicit refresh снимает
   target proposal/Action/Target; actor A сохранён. Никакого automatic watchdog.
5. move: reset/capture A, hidden source, point100/200/0; controlled ms3000 делает
   source stale, explicit refresh сохраняет move/point и «Точка выбрана.».
6. recovery: malformed visible source revision5 отвергнут, observation invalid,
   target cleared/actor retained; valid revision6 восстановил attack. Промежуточный
   invalid state проверен assertion; отдельного invalid screenshot нет.
7. disposed: root hidden, labels cleared, closed view/null children.
8. rebound: fresh actor B/empty source/no proposal. Old capture/update/move/select/
   propose/reset/refresh false; Proxy get/ownKeys/descriptor inspections0.

Controlled clock0/999/1000/2000/3000/4000 — TEST input. Native Schedule только
разносит фазы; TTL проверяется explicit API. Это не измерение actual freshness,
native wall clock, lease, deadline accuracy или серверного срока вмешательства.
Group и mouse canSend/nativeConfirmed/sourceAuthorizationConfirmed всегда false.

| Фаза | UTC engine screenshot | TGA | Actual PNG |
|---|---|---|---|
| bound | 2026-10-12T13:42:02.605Z | shot_0086.tga | [PNG](native-mouse-targeting-bound-2026-10-12.png) |
| attack | 2026-10-12T13:42:17.583Z | shot_0087.tga | [PNG](native-mouse-targeting-attack-2026-10-12.png) |
| captured-switch | 2026-10-12T13:42:32.575Z | shot_0088.tga | [PNG](native-mouse-targeting-captured-switch-2026-10-12.png) |
| expiry | 2026-10-12T13:42:47.529Z | shot_0089.tga | [PNG](native-mouse-targeting-expiry-2026-10-12.png) |
| move | 2026-10-12T13:43:02.513Z | shot_0090.tga | [PNG](native-mouse-targeting-move-2026-10-12.png) |
| recovery | 2026-10-12T13:43:17.491Z | shot_0091.tga | [PNG](native-mouse-targeting-recovery-2026-10-12.png) |
| disposed | 2026-10-12T13:43:32.500Z | shot_0092.tga | [PNG](native-mouse-targeting-disposed-2026-10-12.png) |
| rebound | 2026-10-12T13:43:47.471Z | shot_0093.tga | [PNG](native-mouse-targeting-rebound-2026-10-12.png) |

Все восемь actual frames просмотрены. Pane видна справа снизу, literal label и
unknown time читаются; disposed скрыта, fresh TEST B виден. Штатный HUD остаётся
под pane; TEST banner частично перекрыт XP tooltip. Общая компоновка/другой размер
экрана не приняты. Minimap чёрный, основная карта без проверенных структур, голубая
нижняя область; причина render не установлена. Map geometry/visibility не доказаны.
Driver не перемещает героя/камеру. Engine TGA преобразованы в RGB PNG, не generated.

После кадров quit через fresh VConsole marker; PID27104 отсутствует при проверке.
Steam сохранён, force kill не применялся. Physical clicks/hittest/world mapping,
real identity/authorized observations, server actions/permissions, intervention
lease/ИИ return/common HUD/bootstrap и human second owner остаются открытыми.

Один reused final technical critic не выявил существенных замечаний: guards/raw-vs-generated, captured actor/controlled TTL/move/recovery/stale APIs и отчёт проверены. Это AI review; human second owner остаётся открытым.

Финальная проверка:16changed Markdown/320local links,27полных пятичастных уроков,39unique usage tasks. Семь текущих raw inputs,9bundle/install и9compiled hashes/map VPK подтверждены;8PNG просмотрены. График50/213(23.5%) и diff --check проходят. Product checklist не повышен. Публикация/remote SHA определяются Git history и последующей проверкой.
