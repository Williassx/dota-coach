# Native text preview — 12 октября2026

[Подпункт](../README.md) · [Дизайн](../native-design.md) · [План](../native-plan.md).
Windows checkout D:/AI/dota2coach, исходный HEAD55e59a9, native build_id25845666.
Ведущий — creator2 UI executor; C1/source contracts не изменяются. Это отдельная
acceptance fixture existing explicit VoicePanels, не production bootstrap/голос.

## Результат и исправления

Canonical voice_text.xml теперь имеет anonymous outer Panel и внутренний
VoiceTextRoot. Exact fixed recipe остаётся6resources/5links; mapping, scripts,
public API, inert loading и probe policy сохранены. Strict voice_text_layout.py
проверяет точную новую outer topology. Binding caller получает inner scope.

Первый addon dota_coach_c2_voice_text_20261012: UI exit1, native сообщение
`Found root panel with 'id' attribute, which is not permitted.` Карта exit0.
Derived wrapper и canonical XML имели одинаковое native ограничение. Новые
root regressions сначала RED; после anonymous outer GREEN. Defect addon сохранён.

R1 addon dota_coach_c2_voice_text_r1_20261012: UI/canonical/map exit0;
шесть фаз PASS, shots0035–0040 осмотрены. Поле без рамки и красный default text
обнаружены именно на кадрах. Default skin причина не установлена. Canonical CSS
получает explicit color/font-size/background/border/padding. R2 свежий owned launch
показал рамку пустого поля и светлый текст; hot reload не предполагался.

## Изоляция сборки и native compile

[Builder](../../../11-integration/02-addon-packaging/tools/build_native_voice_fixture.py)
читает fixed six canonical inputs через existing guarded policy, копирует five
canonical outputs кроме manifest, затем test Hud manifest/driver/derived layout:
8sources. Seven outputs принадлежат active derived graph; retained canonical
voice_text.xml компилируется отдельно. Anonymous wrapper содержит canonical subtree
и отдельный TEST label, поэтому dispose скрывает только проверяемую scope.

Builder не перезаписывает existing output, отклоняет escape/missing driver/changed
mapping/executable manifest до writes. Strict manifest tags/attrs/text/DTD guards,
bounded reads и reparse policy reused; fixture не добавлена к fixed kinds.
6canonical hashes и8bundle→installed payloads совпали. Source fixture/handoff flags
source2_compiled/runtime_verified=false сохранены: native evidence в этом отчёте.

Final fixture: build/dota_coach/native-voice-text-20261012T085132Z-8a0949.
Final native addon: dota_coach_c2_voice_text_r2_20261012; absent dirs проверены
до copy. Valve template_map.vmap и workshop_testbed/addoninfo.txt скопированы
в отдельный addon. Lua/server/bootstrap отсутствуют.

```powershell
$dotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot = "$dotaRoot/content/dota_addons/dota_coach_c2_voice_text_r2_20261012"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/custom_ui_manifest.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/panorama/layout/custom_game/voice_text.xml"
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/maps/template_map.vmap"
```

Final compile: UI1/0, canonical1/0, map13/0, exits0. Eight compiled UI files
45442bytes; seven active + separately compiled retained canonical layout.
Leaked KeyValues blocks162 сохранено, причина не установлена. -novpk не используется.

| Объект | SHA-256 |
|---|---|
| canonical XML | 4ddb604790706c9ccad52f53d008f846339b98f2a476d54b761d4f5837b74324 |
| canonical CSS | 3db1765b6af377d5fbcb594bfdc7668caa20dd379aebade5640d209b24dcdd46 |
| map VPK3033460bytes | 5e6215ee5070dfdc8a3feb1bb0338c9a7ca0435bbb550bbf914167b3b11e6e76 |

## Native phases и кадры

Launch uses -game/-steam/-addon/-novid/-windowed/-w1280/-h720/-console/-dev/
-insecure/-vconsole/-vconport29000/-con_logfile and +dota_launch_custom_game.
Owned PID18976 R1 и24436 R2; live VConsole random markers подтверждены.
На HERO_SELECTION test-only sv_cheats1/dota_pick_hero0npc_dota_hero_axe дали
штатный Axe; он не связан с synthetic player IDs. R2 PRE_GAME08:54:57UTC.

Driver явно bind внутренний VoiceTextRoot. Два synthetic TEST own/alive профиля,
role1/2, heroName Synthetic; public preview получает текст из программно заданного
TextEntry.text. Это не keyboard input и не вызов настоящей кнопки/hittest.

- bound: roster revision1 принят, input/buttons enabled, native TextEntry geometry>0.
- ready: «КЕРРИ, отступай» → TEST-a / TEST Альфа / retreat; normalized «керри отступай»,
  UI явно пишет «Предложение готово. Ничего не отправлено.».
- ambiguous: два TEST Альфа при revision2 → expected false/ambiguous_address;
  прежние адресат/действие пусты, предложение отсутствует.
- reset: fresh role preview, затем revision3; input/result/labels cleared, history
  consumed3 сохранена. Это новая local snapshot revision, не серверная.
- disposed: root hidden, все labels/input пусты, кнопки disabled, handle closed.
- rebound: fresh revision1/consumed0; old updateRoster/receive/preview/clear false,
  Proxy ownKeys/getOwnPropertyDescriptor/get reads0; fresh state не повреждён.

Все шесть predicates и cycle PASS в обоих launches; все12 actual frames осмотрены.
Ни plain label, ни result ready не подтверждает permission/execution.
Engine screenshot снят через≥2сек после phase, TGA→RGBPNG, без модификации сцены.

| Фаза R2 | UTC кадра | Native TGA | Кадр |
|---|---|---|---|
| bound | 2026-10-12T08:55:02.015Z | shot_0041.tga | [PNG](native-voice-text-r2-bound-2026-10-12.png) |
| ready | 2026-10-12T08:55:16.993Z | shot_0042.tga | [PNG](native-voice-text-r2-ready-2026-10-12.png) |
| ambiguous | 2026-10-12T08:55:31.967Z | shot_0043.tga | [PNG](native-voice-text-r2-ambiguous-2026-10-12.png) |
| reset | 2026-10-12T08:55:47.186Z | shot_0044.tga | [PNG](native-voice-text-r2-reset-2026-10-12.png) |
| disposed | 2026-10-12T08:56:02.153Z | shot_0045.tga | [PNG](native-voice-text-r2-disposed-2026-10-12.png) |
| rebound | 2026-10-12T08:56:17.140Z | shot_0046.tga | [PNG](native-voice-text-r2-rebound-2026-10-12.png) |

[Предыдущий ready кадр с дефектом default text](native-voice-text-ready-2026-10-12.png).
Остальные R1 кадры сохранены рядом как native-voice-text-{phase}-2026-10-12.png.
После последнего кадра quit через VConsole; оба owned PID проверены absent,
Steam сохранён. Quit response сам по себе не заменял process check.

## Проверки и границы

RED7builder missing→GREEN7; root RED1graph/1builder→GREEN. Final builder7,
VoicePanels21, parser24, graph4 проходят:56targeted checks. Voice package11:
10passed,1WinError1314 symlink creation; suite целиком не green.
Final source-only handoff probe-ui-20261012T085415Z-c43a32 verified fixed6/5;
installation/native_checks остаются source-only not_run. Source reports не переписаны.

Required full runner085259Z-1dac4b:46suites,753passed_tests,6failed,verified=false.
Те же три invalid_summary с skips и три process_exit suites; packaging131tests,
8WinError1314,123остальных прошли (включая7новых fixture tests). Никаких skip,
OS/security changes или ложного полного PASS. Graph50/213=23.5% сохранён.
Локальные raw logs/hashes/install/owner/captures в ignored build/dota_coach/native-voice-text-*;
full logs — build/dota_coach/source-checks-20261012T085259Z-1dac4b.

Микрофон/ASR/transport/C1/серверные приказы, физические клавиши/мышь/hittest,
MANUAL/lease/возврат ИИ, реальная identity/profile, production bootstrap и второй
человеческий владелец открыты. Native TextEntry styling/локальный lifecycle доказаны
только на1280×720 в template scene. Сходство игроков не измерялось. Это ещё не игра.

Один final technical AI review foundation_report_review завершён без существенных
замечаний; это не проверка другого человеческого создателя. Local file links,
19полных пятичастных уроков и diff check проверены перед публикацией.
