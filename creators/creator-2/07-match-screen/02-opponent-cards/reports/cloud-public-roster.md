# C2-07-02 — локальная модель и верхний ряд соперников

[Родитель](README.md) · [API](../notes/public-roster.md).

Дата UTC:2026-10-11. База:22a8362. Исполнитель:root/создатель2.
Модель exact публичного DTO и отдельная inert Panorama-панель пяти карточек.
Старый roster очищается до чтения Proxy/accessor входа; extra combat fields
не читаются. Invalid/stale closes ready, accepted highwater не откатывается.
Unknown имена/герои не нули; true empty источник отличается от unavailable.
Проекция не содержит позиции/характеристики, выбора или приказа.

До реализации:16 model RED отсутствующий JS, затем13 panel RED отсутствующий JS
и2 XML RED отсутствующий layout. После:16+13 VM и2 XML PASS. Первый полный
runner:41suites/866PASS. Финальный критик воспроизвёл обход max5 через Proxy
descriptor length с valueOf 0→6. Новый regressiontest:17model/16PASS1FAIL.
Исправление требует primitive number, целое0..5 до любых сравнений/преобразований.
Regression охватывает также string/null/NaN/Infinity/negative/fractional и
проверяет отсутствие coercions. Targeted3suites/32PASS; полный повтор после
production fix:41suites/867PASS, fail/skip/cancelled/todo=0.
Логи: `build/dota_coach/source-checks-20261011T121036Z-756d25/source-checks.json`.
source2_compiled=false, runtime_verified=false. Все три новых suite внесены в
единый каталог, его полнота проверена существующими тестами runner.

Самостоятельный просмотр проверил exact fields/getter no-read, revisions,
копии, reentry/dispose, обязательные off-slot Labels/containers, isDisposed
preflight, partial binding repair и владение при text-setter callbacks.
Root закрывается/тексты очищаются, старый closed API не изменяет новый binding.
Нет timers/handlers/transport/game API. Product hint содержит только смысл
публичных карточек; ограничения приёмки фиксируются здесь и в metadata.

Независимая финальная проверка: один повторно используемый критик,
один существенный finding исправлен и проверен основным исполнителем.
Предыдущий лимит был до11:35; запрос сделан после12:07 UTC без новых агентов.
Других существенных замечаний нет. Повторное ревью не запускалось.
Критик также завершил ранее отложенное ревью source package orders-timeline,
существенных замечаний нет. Проверка второго человеческого владельца отдельная.

График создателя2:38/205 действий(18.5%); это чеклист, не готовность игры.

Не проверены: C1 source authorization/hidden-enemy invariance, server contract,
общий HUD, fixed source package, Windows Source2 compile, внешний вид/читаемость/
hittest в Dota, настоящий состав матча и другой человеческий владелец.
sourceAuthorizationConfirmed=false; это не frontend authorization.
