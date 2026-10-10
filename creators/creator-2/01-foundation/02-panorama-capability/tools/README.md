# Упаковка исходников Panorama

[Подпункт](../README.md) · [Дизайн](../packaging-design.md) · [План](../packaging-plan.md).
`build_probe_bundle.py` читает [manifest](../bundle-manifest.json), создаёт новый
пакет только под build/dota_coach и не устанавливает/не компилирует его в Dota.

`verify_probe_bundle.py` отдельно проверяет готовый пакет по текущим manifest и
источникам. Обязательный `--bundle` получает путь output из JSON сборщика.
Не изменяет пакет, источники или bytecode в checkout; не запускает JS.
Код 0 и package_verified=true означают совпадение файлов и внутренних XML-ссылок;
source2_compiled/runtime_verified остаются false. Код 2 сообщает причину в stderr.
Устаревший пакет пересобирают в новом каталоге; проверяющий его не исправляет.

Пример из текущей облачной среды, выполняемый агентом из корня:

```sh
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/verify_probe_bundle.py --bundle build/dota_coach/probe-ui-20261009T165700Z-a3ce0b
```

[Результаты проверки](../reports/bundle-verification.md). В другом checkout агент
сначала создаёт пакет сборщиком и использует его фактический output.

Теперь те же helpers поддерживают второй явно выбранный manifest
[общего HUD](../../../11-integration/02-addon-packaging/bundle-manifest.json).
Kind panorama_source_hud разрешает только13 закреплённых source→target пар и
проверяет один связный inert HUD graph. Добавьте --manifest с этим файлом и к build,
и к verify. Probe kind/defaultmanifest сохраняют прежний source prefix; HUD не
расширяет их разрешения. [Команды и ограничения](../../../11-integration/02-addon-packaging/notes/build-manifest.md).

Третий kind panorama_source_preparation использует точную
[recipe](../../../11-integration/02-addon-packaging/preparation-manifest.json),15outputs/3inputs.
Тот же boundedreader проверяет все copied/composed inputs; lazycomposer bytecode-free.
[Команды и ограничения](../../../11-integration/02-addon-packaging/notes/preparation-package.md).
