# Общий HUD: шаблон и ранний пакет исходников

**Дата:** 10 октября 2026 года. **База:** 3564ab586a7ae365464095e552e802dce41c26f4.
**Среда:** Linux `/workspace/dota-coach`, Python3.12.14, Node24.19.0.
Windows/Dota/Workshop Tools не запускались.
[Пакет](../README.md) · [Дизайн](../design.md) · [План](../implementation-plan.md) ·
[Шаблон HUD](../../../07-match-screen/01-own-cards/README.md).

## Изменения

В C2-07-01 созданы общий coach_hud.xml, custom_ui_manifest.xml и coach_hud.css.
Разметка даёт четыре scoped root и пять скрытых собственных slots, прозрачный центр,
секции приказов/камеры/наблюдения справа. Проверены56 уникальных id и51 plain-text labels.
Девять существующих ES5 definitions загружаются в порядке зависимостей; JS не копировались
в другую исходную библиотеку и не менялись. Нет bootstrap/bind/data/demo/server events.

В C2-11-02 создан bundle-manifest.json для12 точных source→target пар. Существующие
foundation helpers расширены fixed HUDpolicy; probe/defaultmanifest прежние.
Build/verify проверяют complete graph, manifest→HUD, девять scripts/один style,
достижимость всех ресурсов и отсутствие XMLbootstrap/повторной загрузки layout.
Report kind сравнивается с manifest; compiled/runtime всегдаfalse.

## Проверки

```sh
python3 -m unittest discover -s creators/creator-2/11-integration/02-addon-packaging/tests -v
```

15, затем17 сценариев RED до manifest/source. После template и manifest17 тестов
дали4errors/1failure из-за неподдержанного kind; негативные проверки уже отклоняли
неподдержанный пакет. После новой policy/graph17/17 GREEN и foundation28/28 GREEN.
UX regression method дал3failures RED: generic order labels скрывали test intent,
а target prompt предлагал неподключённый map input. Explicit point/testtarget и
«Наблюдение целей не подключено» дали18/18 GREEN.
Архитектура воспроизвела циклическую layout-ссылку: две subcases RED. Запрет
layoutfile/CustomUIElement внутри HUD дал19/19 GREEN, также проверен отказ verifier.

| Набор, заново выполненный в этой задаче | Результат |
|---|---|
| Аудит среды C1 | 8/8 |
| Аудит UI C2 | 13/13 |
| Foundation упаковка/проверяющий | 28/28 |
| Ping, Node VM | 16/16 |
| Карточки, Node VM | 28/28 |
| Приказы, Node VM | 35/35 |
| Координатор ввода, Node VM | 26/26 |
| Аудит карты | 30/30 |
| Камера, Node VM | 27/27 |
| Наблюдение целей, Node VM | 36/36 |
| HUD/упаковка | 19/19 |

Всего 266 различных сценариев без пропусков. Новый набор выполняет реальные CLI
во временном repo и Node VM загрузки всех definitions с запрещёнными native API.
Реальные данные/права/приказы/компиляция этим не подтверждаются. PythonAST разобрал
два helper и новый testfile; native CSS compiler не запускался.
Проверены 1108 локальных Markdown-ссылок, README новых каталогов и git diff --check;
отсутствующих целей и ошибок нет. Служебные проверки не входят в число сценариев.

## Фактическая упаковка

Из корня repo выполнены build/verify с новым --manifest и отдельным --output
build/dota_coach/hud-ui-20261010T0825. Каталог исключён из Git; исходники сохранены.
Report generated_at_utc: 2026-10-10T08:21:11.095921+00:00.
Manifest SHA256: `36fa933bb293d7f3b45764fee3f57e8b9f12e2cee4d2db317e24dbf53537d422`.
Verify: package_verified=true, assets12, xml_resource_links11,
source2_compiled=false, runtime_verified=false. Установка/компиляция не выполнялись.

Проверены пути/bytes/hash, unchanged source, отсутствие дополнительных outputfiles,
ресурсный graph. Это проверенный source-пакет, не работающий HUD.

## Ревью и открытая приёмка

Пять read-only направлений рассмотрели дизайн и результат:

- Объём: ранняя подготовка допустима по INTEGRATION.md; полные зависимости сохранены.
- Архитектура: exactfilepolicy вместоprefixes и connectedgraph до кода;
  cycle defect воспроизведён/исправлен, независимо19new+28old GREEN.
- ИИ: честные unknown/disconnected states, noautobind/hidden reads; target prompt исправлен.
- UX: восстановлены fixed test intent labels и disconnected target status;
  повторный прогон18/18 до cycle regression, native geometry/hittest открыты.
- Осуществимость: API/ES5/resource scopes проверены,17new+28old до исправлений;
  полная загрузка definitions не вызывает native startup. Компиляция не заявляется.

Start_skill сохранён с новой командой/ограничениями. Readback подтвердил только
это изменение, revision11, requires_publish=true. Install_script, зависимости,
репозитории, сеть, секреты и runtime-переменные не менялись. Активация требует
рассмотрения, сохранения и публикации в настройках среды.

C2-07-01 всё ещё требует C2-05-03/C1-07-01, реальные карточки/покупки/намерения.
C2-11-02 требует C2-11-01/C2-10-01 и рассмотрение manifest вторым владельцем.
Открыты интегратор/clock/camera identity/server observation/control, mouse/voice,
native Source2/HUD appearance/overlap/hittest/масштабирование и второй владелец.
Противники/голос/карта/сервер/персональные модели не добавлены этим пакетом.
