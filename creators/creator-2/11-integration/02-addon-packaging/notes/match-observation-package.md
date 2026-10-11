# Source-пакет общей сцены наблюдения

[Родитель](README.md) · [Recipe](../match-observation-manifest.json) ·
[API binding](../../01-ui-binding/notes/match-observation.md).

Из корня репозитория:

```text
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen match-observation
```

Fresh output под build/dota_coach и companion снаружи, никакой установки. Пакет
собирает canonical opponent/history scopes в два пустых shell hosts: 10 assets,
9 resource links, 38 ID. State/panel пары перед общим binding, всего пять JS
definitions. Raw XML input hashes зафиксированы в generated layout; verifier
повторяет композицию с текущими источниками. Output вручную не редактировать.

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite node-match-observation --suite python-c2-11-02 --suite python-c2-10-01 --suite python-c2-01-02
```

Это partial прогон; полный runner вызывается без --suite. Проверки не компилируют
Source2 и не запускают Dota. Существующие output/report защищены от перезаписи,
linked paths/extra dependencies/неверная topology отклоняются до создания output.

Loader альтернативен другим пакетам, автоматического bind нет. Caller создаёт
одну группу, доставляет два независимых источника и dispose. Полное объединение
с собственной командой/приказами/голосом/камерой остаётся отдельным этапом.
sourceAuthorizationConfirmed=false; native_checks=not_run, installation=false.
