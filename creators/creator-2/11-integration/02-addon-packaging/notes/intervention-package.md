# Source-пакет ручного запроса

[Подпункт](../README.md) · [Manifest](../intervention-manifest.json).

Из корня репозитория:

```bash
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/intervention-manifest.json --output build/dota_coach/intervention-source-20261011-01
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/verify_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/intervention-manifest.json --bundle build/dota_coach/intervention-source-20261011-01
```

Команды выполнены: 6 assets, 5 XML resource links, package_verified=true;
source2_compiled/runtime_verified=false. Повтор build в тот же каталог запрещён:
выберите новый output либо опустите --output для нового автоматически созданного пути.
Исходники и существующие outputs/установки не перезаписываются.

Kind panorama_source_intervention содержит custom_ui_manifest.xml, layout, один CSS
и три определения: Orders→Requests→Panel. Manifest декларативно задаёт одну Hud-панель,
но скрипты сами не вызывают bind и не выдают прав. Явный caller подключает панель по
[инструкции C2-05-01](../../../05-intervention-ui/01-request-ack/notes/request-panel.md).
Реальный transport не входит в пакет.

Это отдельный альтернативный пакет. Его manifest автоматически не объединяется с
HUD или подготовкой; копирование поверх другого пакета заменило бы общий manifest.
Интеграция экранов требует собственного рассмотренного рецепта.
Панель/сервер/нативное управление/lease/возврат ИИ и второй владелец открыты.
Генератор проверяет source graph, не компилирует Source 2 и не устанавливает аддон.
