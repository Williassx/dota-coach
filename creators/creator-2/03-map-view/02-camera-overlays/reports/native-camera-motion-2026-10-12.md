# Motion/input: 100 замеров, причина прежнего возврата не установлена

12 октября2026, C2-03-02, leading76/root107/114/173/174/175.
[Дизайн](../motion-design.md), [план](../motion-plan.md),
[metadata/hashes/UTC](native-camera-motion-2026-10-12.json),
[100 исходных образцов](native-camera-motion-samples-2026-10-12.jsonl).
[Прежний failed arrival](native-camera-2026-10-12.md) сохранён без изменения.

В исправленном TEST-драйвере получены20baseline/80post samples вокруг ровно одного
native panel Activated→gateway.focus. Actual elapsed20016ms, nominal Schedule0.2s;
это не подтверждение точности clock или latency SLA. Own hero123/native guard
проверялся перед origins и повторно после request. Production panel/gateway,
fixedHUD13 и probe policy не изменены; builder допускает только camera/motion.

| Показатель | Наблюдение |
|---|---|
| Начальный lookAt/ownOrigin XY | Оба−128/−64: камера уже у героя до request |
| Near≤64 в baseline | 18 из20 |
| Near≤64 в post | 2 из80: index20=0, index23=8.66938 |
| Минимальная post distanceXY | 0 |
| Последняя distanceXY | 312.744306 |
| Cursor distinct values | 68, raw диапазоны x153–1279/y0–719 |
| Own origin distinct values | 8; герой двигался |
| Mouse button readings | 14samples с хотя бы одним true; index2=true при request |
| Read-only cvars | dota_camera_edgemove=true, dota_camera_speed=3000 |

Эта серия **не является управляемым сравнением**: изменялся ввод и герой, а исходная
камера уже совпадала с целью. Near0 после запроса не доказывает причинное прибытие;
нет доказательства удержания фокуса или причины прежнего возврата к позиции
в7528units от героя.
Гипотеза edge pan остаётся гипотезой. Индексы кнопок записаны без неподтверждённой
расшифровки; sampled pressed state не доказывает C2 mouse/hittest/ручное право/ИИ return.
Настройки/cvars/положение указателя не менялись. Новый опыт с одной переменной имеет
смысл после определения контроля native input и отдельного rollback-плана.

## Реальный формат API и исправления диагностики

- Builder RED: три новых cases получили unexpected variant argument; GREEN10.
- VM RED выявил origin read после потери guard во время native request; повторный
  guard закрыл чтение, GREEN5. Первый compiled m1 не запускался; сохранён отдельно.
- m2/PID26612: ошибка Invalid native vector до sample0/request0. Ошибка не называла
  поле; root добавил только name/raw instrumentation и сохранил failed run.
- m3/PID29240: `clampedProjection=[0.5,0.45477646589279175,0]`. Exact2 было догадкой,
  локальный зарегистрированный API говорит js_array без точной длины. Новая VM
  fixture с actualtriple сначала RED, затем GREEN5 после raw3 correction.
- m4/PID18356:100samples/5status phases/fourframes PASS. Третий projection component
  не интерпретируется; raw3 и units не являются доказательством visibility/hittest.

Read-only API helper107 подтвердил ограничения локального native dump
`build/dota_coach/native-api-details-20261011.txt` (1031/1043/1044/1059).
Valve wiki pages были недоступны403; их содержимое не использовано как evidence.
Конкретная форма установлена runtime, не по имениXY. Diagnostic failure не permission
failure. Повтор install с занятым Run теперь отказывает до writes; preservation
проверена на m1 с fresh unused addon name — каталог не создан.

## Native кадры и сборка

Все четыре engine TGA→PNG1280×720 осмотрены. Own hero виден на плоской TEST-карте;
слева внизу minimap частично закрыта белым многоугольником, причина неизвестна.
Это изменение картинки относительно предыдущего black minimap не доказывает
геометрию настоящей карты/полноценный матч или исправление renderer.

| Фаза | Capture UTC | Кадр |
|---|---|---|
| baseline |18:03:53.743|[actual](native-camera-m4-baseline-2026-10-12.png)|
| early |18:03:59.303|[actual](native-camera-m4-early-2026-10-12.png)|
| settled |18:04:02.689|[actual](native-camera-m4-settled-2026-10-12.png)|
| returned |18:04:09.715|[actual](native-camera-m4-returned-2026-10-12.png)|

`returned` — имя временной фазы, не assertion возврата камеры к прежней точке.
Metadata layoutWidth1280/height720/uiScale≈0.666667 — фактические свойства панели;
дополнительно умножать layout dimensions на scale для объявления viewport не следует.

Build_id25845666. Final bundle `native-camera-20261012T180101Z-4d29b5`, addon
`dota_coach_c2_camera_motion_vectors_20261012`.15source outputs; UI1/canonical1/map13
compiled/0failed/0skipped, exits0.14active+1retained inert outputs,100363bytes;
map3033508bytes/SHA25663042460edc3eccd3686be77c909a7aeff90f34a1ea1a950aa77bedf2cddd310.
Source-only builder flagsfalse. Raw logs/bundles m1–m4 сохранены в ignored build.
Все три own launched PIDs закрыты черезquit→gone, exact UTCticks guard; Steam12336
сохранён. Без forcekill, preference/OS/security/server/sharedcontract изменений.

Required full `source-checks-20261012T180207Z-e4cd16`:49suites/1039passed/28skipped/
6incomplete/0error suites, strictverified=false/CLIexit1, все49process exits0.
Source tests не запускают native capture/Dota/microphone. Полная карта/real identity/
physical input/markers/scaling/C1 и human second owner остаются открытыми.

Один итоговый reused technical critic существенных замечаний не нашёл. AI review
не заменяет рассмотрение вторым человеческим создателем.
