# Пакет общей подготовки

[Подпункт](../README.md) · [Recipe](../preparation-manifest.json) · [Дизайн](../preparation-design.md).

Из корня используйте прежние build/verify helpers с отдельным manifest:

```sh
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/preparation-manifest.json
```

Полученный JSON сообщает новый output. Передайте его проверяющему:

```sh
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/verify_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/preparation-manifest.json --bundle build/dota_coach/preparation-source-20261010-01
```

Показанный output существовал в этой облачной проверке. В новом checkout используйте
путь своего JSON, не перезаписывайте существующий output. Облачный результат не
устанавливает аддон в Windows. Build output исключён из Git, вручную не редактируется.

Recipe фиксирует15 outputs и3 inputs. Shell XML преобразуется: три canonical Panel
trees вставляются в hosts, raw input SHA сохраняются в комментариях. Остальные14
ресурсов копируются без изменения bytes. Verifier заново композирует ожидаемый XML,
проверяет outputs/report/current sources; source2_compiled/runtime_verified=false.

Исходный shell из C2-11-01 не содержит вставленных модулей и сам по себе не экран:
нативному интегратору нужен именно generated coach_preparation.xml из output.
Внутри него9 JS definitions в одном контексте. При загрузке нет bind или данных.
Явный caller должен вызвать DotaCoachPreparationBindings.bind(root), где root —
CoachPreparationRoot, и подавать actual frames согласно copied contexts.
Bindings/API описаны в [заметках](../../01-ui-binding/notes/preparation-binding.md).

Preparation manifest загружает только этот HUD. Он не объединяется автоматически
с прежним match HUD/custom_ui_manifest.xml: два альтернативных source-пакета нельзя
слепо наложить друг на друга. Общий переход подготовки→матч и manifest/серверный
контракт, native compile/scroll/hittest и второй владелец пока не приняты.
