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
