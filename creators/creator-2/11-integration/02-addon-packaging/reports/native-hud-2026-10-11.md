# Нативная компиляция инертного HUD на Windows

**Дата:** 11 октября 2026 года, наблюдение 2026-10-11T20:30:26.2603100Z.
**База исходников:** `9f01155b4cb6ad64f537c9e007acd8500bbea840`.
**Ведущая область:** C2-11-02 / C2-07-01, Panorama и проверка пакета.
[Пакет](../README.md) · [Шаблон](../../../07-match-screen/01-own-cards/README.md) ·
[Возобновление](../../../01-foundation/01-workspace-audit/notes/windows-resume.md).

## Критерий и фактический результат

Проверить существующий fixed HUD kind: 13 ресурсов / 12 XML resource links,
установить в новый отдельный addon и скомпилировать настоящим Source 2 compiler.
Не менять исходники, policy probe, порядок scripts, generated bundle или bootstrap.
Это выполнено; запуск и интерактивная приёмка HUD в этой задаче не проводились.

Windows 10 / PowerShell, Python 3.12.14, Node 24.19.0; установленная Dota build_id
25845666. Корень Dota:
`C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta`.
Новый addon `dota_coach_c2_hud_20261011`; content/game каталоги отсутствовали до установки.
Существующие probe/mouse addons сохранены.

Свежий handoff `build/dota_coach/probe-ui-20261011T202634Z-bdc78b` создан штатным helper:
`prepare_ui_handoff.py --screen hud`. Ошибочный первый `--package hud`
отклонён argparse с exit 2 до создания пакета; исправленная команда exit 0.
Единственные исходники остаются в библиотеке создателя 2. Все 13 SHA-256
сопоставлены между текущим source, generated bundle и установленным content.
Установлены только ресурсы рецепта: два XML, один CSS, десять JS definitions.
Карты, addoninfo, Lua, сервер, bind или demo не добавлены.

## Реальная команда компиляции

```powershell
$dotaRoot = 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
& "$dotaRoot/game/bin/win64/resourcecompiler.exe" -nop4 -game "$dotaRoot/game/dota" -i "$dotaRoot/content/dota_addons/dota_coach_c2_hud_20261011/panorama/layout/custom_game/custom_ui_manifest.xml"
```

Exit 0, `OK: 1 compiled, 0 failed, 0 skipped, 0m:00s`.
Число 1 — compile entry manifest, а не число ресурсов: recursive graph дал
ровно 13 непустых файлов в новом game addon, всего 88754 байт.
Compiler также сообщил `Leaked KeyValues blocks: 162`; это сообщение сохранено,
причина/последствия отдельно не исследованы. В логе нет compiler failure.

## Проверенные compiled outputs

Относительно game addon. Хеши относятся к полученным bytes, а не к source.
Повторная компиляция на другой версии Tools может дать другие хеши.

| Файл | Байт | SHA-256 |
|---|---:|---|
| custom_ui_manifest.vxml_c | 1369 | `ef93e353d55c4d7f79114d5f9a8ab27c56680f5100be7b090ae09539f979bb16` |
| coach_hud.vxml_c | 3681 | `53d51b5194d6e75d60553f9b2febdbfd5c373ae47a19944300b7d58622b51652` |
| coach_hud.vcss_c | 4028 | `e48db0fd8aa5d61f44273b9df29e790f60d59f69a7b57fa1e458a416997c88a7` |
| roster_cards_state.vjs_c | 6348 | `7efad4bdbe882be9041230c61d69aa613573d2f1e1c1d40886f8c2aef2b2f7e5` |
| roster_cards.vjs_c | 10528 | `5d22625891cdec5c94ee640ab8e613be0c9bcde42e2f7666d3c1bfdd40580d9e` |
| orders_state.vjs_c | 11711 | `66857551ff1efa2aec0684285f956052bed0868a071d7996d84e44f5a2f77547` |
| orders_panel.vjs_c | 7145 | `b07c3f77ca7ec78aa7ba993a84d010d29e85e063f20ce4667a6657217a3265d3` |
| input_routing.vjs_c | 4251 | `8a052ddabfb6aa16713dfa8627cd8b22f5c36d88f2ba96405810441bf4da0b14` |
| camera_native.vjs_c | 3804 | `a2b17bcb0bc216bc12d68f0dca8145cf6a5c453d5074099de19afb38e60f53ec` |
| camera_panel.vjs_c | 9057 | `669caa684b862dbdfd1a99781e6b4e5aa4428a3dd760b514638fbd08dba130bc` |
| targets_state.vjs_c | 10184 | `d91e8f07dffd63effaa7f1a2bcdf40e8532c5983352a8c8d3202b060a9cfa7d9` |
| targets_panel.vjs_c | 5603 | `f9b94cd7aea776deff466e4f38591f3cdecf1f30a2b5d5b174bcaa2b002d2fe3` |
| coach_hud_binding.vjs_c | 11045 | `299d26ccbc2ddc292c734607ec9c93fbcd25e6cbe9227ebdbb04cf5e21135ea5` |

## Проверки и локальное evidence

- HUD source tests: 19/19 PASS, без skips/errors.
- HUD binding Node VM tests: 26/26 PASS, без skips/errors.
- Повторный source verifier: package_verified=true, assets=13,
  xml_resource_links=12, source2_compiled=false, runtime_verified=false.
- Actual installed source hashes: 13/13 совпадают; compiled files: 13/13 непусты.

Source-only report и handoff намеренно сохраняют native=false/not_run:
сам helper не устанавливает и не компилирует. Нативное подтверждение хранится
отдельно в этом отчёте и ignored `build/dota_coach/native-hud-evidence-20261011.json`.
Другие локальные файлы: `native-hud-compile-20261011.log`,
`native-hud-source-tests-20261011.log`, `native-hud-binding-tests-20261011.log`,
`native-hud-source-verify-20261011.json` в build/dota_coach.
SHA-256 compiler log: `49e7849f163ca4c0661d973df05e0c75b0a094f8509385ffc9add247b91d4781`.

Исходники/тесты не менялись; полный source runner не повторялся.
Последний полный Windows результат остаётся 46 suites / 752 passed tests /
6 failed suites, verified=false, из-за existing symlink privilege errors и
strict skip-summary policy. [Подробности](../../03-end-to-end/reports/windows-reparse-2026-10-11.md).
45 целевых PASS не добавляются к этому агрегату как новая полная регрессия.

## Следующие границы приёмки

1. Согласовать отдельную native fixture scene и её manifest с интегратором;
   пакет HUD остаётся инертным, без автоматического bind и выдуманных данных.
2. Запуск/изображение HUD, разрешения и реальные UI размеры, input/hittest,
   reload/dispose требуют отдельного evidence. Успех compiler этого не доказывает.
3. C1 bootstrap/ping, реальный server contract/identity, lease и возврат ИИ
   ещё открыты. Проверка другого человеческого владельца не заменяется critic.

Нативные игровые чекбоксы не отмечаются; готовность полного аддона не заявляется.
