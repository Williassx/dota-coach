# Проверяемый пакет публичных соперников

[Родитель](README.md) · [Recipe](../opponent-roster-manifest.json) ·
[API панели](../../../07-match-screen/02-opponent-cards/notes/public-roster.md).

Из корня репозитория:

```text
python3 creators/creator-2/10-user-testing/01-install-guide/tools/prepare_ui_handoff.py --screen opponent-roster
```

Команда создаёт свежий каталог под `build/dota_coach`, делегируя единственным
build/verify helpers. Рядом создаётся неизменяемый companion report с исходными
хешами, Git/platform metadata и флагами source-only. Существующие output/report
сохраняются. `--bundle` проверяет уже созданный пакет и создаёт новый companion
только если соответствующего отчёта ещё нет.

Ровно пять ресурсов: inert Hud loader, XML, CSS, state.js, panel.js. Четыре ссылки;
сначала state, затем panel. Точная топология: 24 ID, root/strip/5 cards и 17 пустых
plain Labels. Root скрыт до explicit bind; нет кнопок, обработчиков, таймеров,
автоматического binding или game API. Отдельный Hud loader альтернативен другим
пакетам и не объединяется с ними этой командой.

```text
python3 creators/creator-2/11-integration/03-end-to-end/tools/run_source_checks.py --suite python-c2-11-02 --suite python-c2-10-01 --suite python-c2-01-02
```

Это частичные source-проверки. Полный прогон — та же команда без `--suite`.
Проверяются exact mapping, XML schema/order/slot ownership, отсутствие DTD/events,
current source bytes, linked paths, сохранность output, запуск actual packaged
контекста с неизвестными данными, stale revision, hidden getter и dispose.

Установка в Windows, Source 2 compilation и настоящий состав Dota не проверены.
В отчёте installation_performed=false, native_checks=not_run. Сервер обязан
предоставить разрешённую проекцию; sourceAuthorizationConfirmed=false.
Этот пакет не добавляет общий HUD, транспорт, контракт, permission policy или
автоматическую установку в пользовательские папки.
