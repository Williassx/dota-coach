# Preparation: два native размера, неполная визуальная приёмка

13октября2026; опыт начат12октября. [Дизайн](../design.md),
[план](../implementation-plan.md), [команды](../tools/README.md),
[metadata/UTC/PNG hashes/compiled hashes](preparation-scaling-2026-10-13.json).
Ведущая роль157; root107/114/159/173/174/175, один reused readonly helper.
Это существующий synthetic TEST draft, без C1/матча/storage/physical input.

Два завершённых запуска дали12actual engine кадров и по6existing API predicates.
Actual размеры PNG совпали с launch flags. На осмотренных кадрах блоки укладываются
по ширине, доступные колонки и подписи читаются; navigation label predicates
подтвердили семь непустых labels с положительными dimensions. Filled hero proposals
во всех трёх колонках одновременно не сняты. Complete после API ScrollToBottom
показывает оба выбранных намерения, нижнюю кнопку и все пять строк сводки.
Удобство человеческого чтения и попадание физических кликов ещё не проверены.

| Наблюдение |1600×900,12октября|1024×768,13октября|
|---|---|---|
| Runtime build_id |25845666|25894101|
| Own PID |33548|18192|
| Bound: content/viewport/scroll |866/801/0|746/682/0|
| Team: content/viewport/scroll |1496/801/0|1301/682/0|
| Complete: content/viewport/scroll |2475/801/−1674|2155/682/−1473|
| Reset: content/viewport/scroll |1496/801/−695|1301/682/0|
| Rebound: content/viewport/scroll |992/801/0|857/682/0|
| Reset вернулся к началу |**Не подтверждён**|Видно4/5 и начало состава|
| Dispose/rebind |Pane hidden/свежий TEST каталог|Pane hidden/свежий TEST каталог|

**Reset1600×900 не проходит визуальный критерий возврата кверху:** при model
predicate PASS и вызове ScrollToTop остался−695, кадр показывает TEST4/середину
состава. В1024×768 scroll0 и начало4/5 видны. Ни root, ни helper не фиксировали
контроль ввода в обоих опытах; причиной могут быть input/layout/runtime differences,
она не установлена. Не объявлять исправление или различие соотношений сторон:
между опытами обновилась Dota. Для причинной проверки нужен отдельный controlled
опыт с before/after geometry; существующий driver/source не менялся ради PASS.

## Кадры

Все12PNG осмотрены. Engine capture UTC/hashes находятся в JSON; здесь фазы:

| Фаза |1600×900|1024×768|
|---|---|---|
| bound |[кадр](preparation-1600x900-bound-2026-10-12.png)|[кадр](preparation-1024x768-r2-bound-2026-10-13.png)|
| team |[кадр](preparation-1600x900-team-2026-10-12.png)|[кадр](preparation-1024x768-r2-team-2026-10-13.png)|
| complete |[кадр](preparation-1600x900-complete-2026-10-12.png)|[кадр](preparation-1024x768-r2-complete-2026-10-13.png)|
| reset |[кадр](preparation-1600x900-reset-2026-10-12.png)|[кадр](preparation-1024x768-r2-reset-2026-10-13.png)|
| disposed |[кадр](preparation-1600x900-disposed-2026-10-12.png)|[кадр](preparation-1024x768-r2-disposed-2026-10-13.png)|
| rebound |[кадр](preparation-1600x900-rebound-2026-10-12.png)|[кадр](preparation-1024x768-r2-rebound-2026-10-13.png)|

HUD Dota просвечивает сквозь preparation, TEST banner остаётся после dispose.
На disposed1024×768 белый многоугольник частично закрывает minimap; причина
неизвестна. Template world/TEST Axe не настоящая геометрия карты/identity/матч.
Кадр верхней части не должен одновременно показывать нижнюю часть scroll content.

## Версии, изоляция и сбой возобновления

12октября совпали17installed source payloads/18current raw inputs/17compiled
и map hashes прежней fixture; она была скомпилирована ранее, повтор compile
для1600×900 не выполнялся. Addon preparation_r1_20261012, map3033460bytes.
После6фаз quit exact PID/start ticks→gone, Steam12336 сохранён.

Запуск1024×768/PID34752 от12октября остановился до первого preparation predicate;
на возобновлении13октября old tool session недоступна и PID отсутствует. Cause
не установлена, log/receipt и герой selection commands сохранены, frames0.
Это незавершённый запуск, не положительная проверка разрешения.

Preflight13октября отказал historical build_id25845666: actual25894101.
Fresh builder `native-preparation-20261013T054508Z-d20b6f` создал17outputs,
source2/runtime flagsfalse. Fresh addon `dota_coach_c2_preparation_scale_r2_20261013`
не перезаписал старый. Native compiler UI1/canonical1/map13/0failed/0skipped,
все exit0;17compiled UI files/map3033508bytes, hashes в JSON.
Template compiler также содержит missing test resources/steamaudio warnings;
их причина отдельно не исследована, успешный compiler summary не полный матч.
OwnPID18192 phase-scoped hero commands/6phases/quit→gone, finalDota clients0,
Steam12964 сохранён. Без forcekill и изменений OS/security/cvars/default preferences
в командах диагностики; автоматические записи конфигурации самой Dota не аудированы.

## Проверки и открытые критерии

Capture helper импортируется inert; explicit CLI имеет exact size/addon allowlist,
validated date/attempt, fresh outputs и PID/name/UTCticks перед каждой query.
Для invalid size/attempt/date/addon refusal выполнены4проверки до receipt access;
AST PASS. Query subprocess timeout10s, phase polling420s. Actual capture не в
ordinary source catalog, canonical fixed15/14 и matchHUD13/probe policy сохранены.

Первыйfull12октября183455Z-3b1602 имел cp1251/owned sandbox termination errors:
root не перенёс PYTHONUTF8 в новую shell. Он сохранён. ПовторUTF8/approved
owned taskkill183655Z-d91974:49/1039passed/28skip/6incomplete/0errors/false.
Fresh full13октября054618Z-b3595e: те же counts, все49process exits0, CLI1/
strictverifiedfalse. Source checks не являются этими native запусками.

Supported product resolutions, попадание кликов/physical wheel, настройки/storage,
полный C2-07-03, C1/общий UI transition и human second owner остаются открытыми.
Progress53/213(24.9%) не увеличен. Следующий шаг — воспроизвести reset scroll с
контролем input/geometry на одном build; не добавлять storage или mouse authority
без согласованных интерфейсов. Один reused final technical critic существенных
замечаний не нашёл; это AI review, человеческая приёмка остаётся открытой.
