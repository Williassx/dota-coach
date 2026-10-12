# Native smoke существующей явной привязки HUD

12 октября 2026. C2-11-01 / C2-11-02, ведущие роли: интеграция Panorama и
поведенческая проверка UI; диспетчер173, учёт174 и контекст175 — основной исполнитель.
[Исходная спецификация](design.md) · [Предыдущий native результат](../02-addon-packaging/reports/native-hud-scene-2026-10-12.md).

Пользователь поручил продолжать самостоятельно без остановок. Проверяем уже
реализованный DotaCoachHudPanels.bind в движке после успешного empty HUD/setter smoke.
Новый игровой bootstrap или общий контракт не проектируются. Этот bounded test
продолжает согласованную проверку native UI; рутинное повторное согласование не требуется.

Варианты: изменить inert HUD bootstrap; подставить данные через чужой native UI;
собрать отдельную явную test-only fixture из canonical inputs. Выбран последний:
fixed HUD13/12 остаётся definitions-only, все игровые модули имеют один источник.
Fixture builder отдельно читает и проверяет13 canonical inputs, сохраняет12 из них
без изменения bytes, формирует test manifest и derived layout и добавляет test script:
15 outputs. Inert canonical manifest не используется для запуска этой fixture.
Canonical layout сохраняется также как неизменённый input/output; derived layout
получает последний script include и plain TEST label, не копию новой реализации.

Данные: пять виртуальных TEST карточек с source=synthetic, heroName=null,
без связи с людьми или entity. Clock — явно заданное локальное nowMs=0.
Options только now/maxAgeMs1000; send, cameraGateway и resolveCameraEntity отсутствуют.
Тест вызывает публичные replaceRoster/selectPlayer/updateControl/updateTargets/dispose,
не имитирует клики мышью. Режим AI в TEST DTO — тестовое значение, не наблюдение ИИ Dota.

Фазы после native layout: пять карточек → selected TEST0 с тем же адресатом
приказов/камеры → удаление выбранного TEST0 и четыре карточки без адресата →
dispose скрывает четыре scope → новый bind с TEST-FRESH, старый handle отвергает
методы и не читает переданный DTO getter. В каждой фазе кнопки приказов и фокуса
отключены. Лог predicates плюс устойчивый actual engine кадр; положительный getter
или phase label отдельно не доказывает видимое изображение.

Приёмка: bytes/graph/guards builder, unchanged fixed kind, compile UI/map,
fresh owned launch/live echo/PRE_GAME, phase logs и actual PNG, quit/PID gone,
targeted checks/full runner, один итоговый read-only critic, журнал/урок/usage.
Если compile или native assertions выявляют дефект существующих модулей, сначала
установить причину и создать meaningful RED/GREEN; generated output не редактировать.

Открытые границы: real server/clock/visibility/identity, полный продуктовый bootstrap,
мышь/hittest/голос, карта с белым участком fixture minimap, lease/возврат ИИ,
полная Windows source регрессия и рассмотрение другим создателем. Fixture не выдаёт
приказов, не перемещает камеру и не подтверждает качество реальных профилей.
