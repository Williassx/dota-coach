# Один source-пакет, разные библиотеки

[Подпункт](../README.md) · [manifest](../bundle-manifest.json) · [Дизайн](../design.md).

Manifest kind=panorama_source_hud описывает 13 точных source→target соответствий:
два XML и стиль C2-07-01; десять JS C2-02-01/02/03 и C2-03-02/03 и C2-11-01. Единственные JS
редактируются там, а build output только получает проверенные bytes/hash.
Ресурсы серверов, maps/VPK, demo/probe и данные игроков не входят.

Используются прежние build_probe_bundle.py/verify_probe_bundle.py. Их фиксированная
HUD policy не разрешает manifest расширять список/менять target и не расширяет probe
policy. Default foundation manifest остаётся прежним. Report kind сравнивается
с выбранным manifest; source2_compiled/runtime_verified всегда false.

HUD validation требует один entry manifest→coach_hud, десять scripts по dependency
order, один style, reachability всех 13 ресурсов, отсутствие XML on*/run/script
bootstrap и layoutfile/CustomUIElement внутри HUD. Поэтому циклы layout исключены.
Probe semantics остаются прежними. Python helper не исполняет JS; отдельный VM-тест
проверяет, что загрузка текущих definitions не читает native API/не запускает UI.

```sh
python3 -m unittest discover -s creators/creator-2/11-integration/02-addon-packaging/tests -v
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/bundle-manifest.json
```

Вторую команду агент выполняет из корня repo; output JSON сообщает новый каталог.
Проверять именно этот output, не предполагаемый или старый путь:

```sh
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/verify_probe_bundle.py --manifest creators/creator-2/11-integration/02-addon-packaging/bundle-manifest.json --bundle build/dota_coach/hud-binding-20261010T0920
```

Последний путь — фактический пакет текущего облака, не файл в другом Windows клоне.
Existing output никогда не заменяется; build/dota_coach игнорируется Git.
Новый kind по умолчанию может получить исторический prefix probe-ui: это название
каталога, type определяется manifest/report, не именем. Явный --output задаёт новый
child с удобным названием. Проверка не устанавливает и не компилирует пакет.

Foundation probe и новый HUD имеют разные custom_ui_manifest.xml в отдельных
пакетах. Их не накладывают друг на друга автоматически; конечный manifest рассматривают
оба владельца по фактическому template Tools. Установка сейчас не выполнялась.
