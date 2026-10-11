# Отдельный source-пакет публичных соперников

[Родитель](README.md) · [Модель/панель](../../07-match-screen/02-opponent-cards/design.md).

Следующий этап существующего C2-07-02: перенос единственных исходников в отдельный
проверяемый каталог, без установки. Выбран fixed kind вместо расширения общего HUD
или универсального сборщика: интеграция игрового экрана и C1 policy ещё открыты.

Kind `panorama_source_opponent_roster`: ровно5 source→target пар из C2-07-02:
inert Hud loader, opponent_roster.xml, CSS, state.js, panel.js. Четыре resource
links; state перед panel. Loader не выполняет bind, root starts visible=false,
17 empty plain Labels+7 Panels. Exact slot ownership/order/attributes, никаких
buttons/events/extra dependencies. Trusted local Panel.visible extension через
existing parser; остальные kind/defaults не меняются.

Builder/verifier/current-source hashes/portable path и fresh output policy
переиспользуются. Новый validator проверяет только эту фиксированную топологию.
Handoff selector `opponent-roster` получает существующий companion report;
screen registry equality test охватывает все8 fixed screens. Actual packaged
XML+обаJS выполняются в одном NodeVM, включая null/empty/stale/extra getter и
dispose; это проверка исходников, не запуск Dota.

Native source2_compiled/runtime_verified=false, installation_performed=false,
native_checks=not_run. Публичный DTO не устанавливает разрешение источника:
sourceAuthorizationConfirmed=false, C1-09-02 остаётся зависимостью. Никакого
server/bootstrap/transport, общего manifest merge, Windows записи или runtime claim.
