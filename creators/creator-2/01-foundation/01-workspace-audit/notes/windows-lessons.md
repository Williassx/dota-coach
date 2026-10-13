# Windows: уроки из выполненных действий

[Заметки](README.md) · [Отчёт foundation](../reports/windows-foundation-2026-10-11.md) ·
[Журнал 11 октября](../../../00-action-log/2026-10-11.md).

Ведущая роль: создатель 2, диагностика Windows и проверка evidence. Область этой
записи — повторяемые рабочие решения; игровые механики и критерии приёмки не меняются.
Перед применением сопоставляйте версии, пути и режим запуска. Подтверждённый
результат ниже относится к указанному прогону, а не ко всем будущим установкам.
Полные native logs остаются в игнорируемом `build/dota_coach`; ссылки на них
предназначены для локального checkout и могут отсутствовать после очистки build.

## 1. Сначала проверять схему handoff, затем создавать addon

- **Действие:** установщик попытался прочитать `source_verified` на верхнем уровне
  handoff JSON и остановился до создания каталогов.
- **Причина:** краткая stdout-сводка и сохранённый JSON имеют разные поля;
  в handoff подтверждение находится в `source_verification.package_verified`.
- **Исправление:** проверять фактическую схему и вложенный boolean, kind, asset
  inventory и hashes до любой записи; не угадывать поле по тексту CLI.
- **Проверка:** [handoff](../../../../../build/dota_coach/probe-ui-20261012T062416Z-7e7d92.handoff.json)
  содержит `stage=source_only`, `package_verified=true`, 13 assets/12 XML links;
  [отдельный verify](../../../../../build/dota_coach/native-hud-scene-source-verify-20261012.json)
  сохраняет `source2_compiled=false`, `runtime_verified=false`.
- **Следующий раз:** любой переход CLI → JSON → установка; source verification
  не повышать до native runtime verification.

## 2. ERROR_FILEOPEN: проверять GAME search paths

- **Действие:** сборка template_map с `-novpk` не находила базовые ресурсы.
- **Причина:** verbose log показывал только addon в GAME; флаг исключал штатные
  dota/core VPK. `resourceinfo` прочитал error material внутри установленного VPK.
- **Исправление:** в этой установке убрать `-novpk`, оставить проверенный
  абсолютный `-game` и штатный resourcecompiler; не подменять базовые материалы.
- **Проверка:** [foundation report](../reports/windows-foundation-2026-10-11.md),
  раздел «Продолжение: карта собрана»: exit 0, 13 compiled/0 failed/0 skipped,
  VPK 3033412 bytes с записанным MD5; карта затем загрузилась в клиенте.
- **Следующий раз:** отсутствующий штатный ресурс при сборке карты; прежде
  исправления ассетов сравнить search paths с успешным native прогоном.

## 3. Exit 0 компилятора не доказывает обновление CSS

- **Действие:** после изменения CSS повторно скомпилирован manifest entry.
- **Причина:** [лог](../../../../../build/dota_coach/native-hud-scene-final-ui-compile-20261012.log)
  содержал 0 compiled/0 failed/1 skipped: обновлённый CSS не был скомпилирован.
- **Исправление:** явно передать изменённый canonical CSS resourcecompiler;
  generated `.vcss_c` вручную не редактировать.
- **Проверка:** [CSS compile log](../../../../../build/dota_coach/native-hud-scene-final-css-compile-20261012.log)
  — 1 compiled/0 failed/0 skipped; [inventory](../../../../../build/dota_coach/native-hud-scene-final-compiled-20261012.json)
  содержит `.vcss_c` 4171 bytes и SHA-256, совпадение всех 13 source hashes.
- **Следующий раз:** любая правка зависимого XML/JS/CSS; читать compiled/skipped
  counts и проверять фактический output, даже при exit 0.

## 4. Обновлённый ресурс нужно увидеть в новом native кадре

- **Действие:** CSS с новым отступом roster скомпилирован при работающем клиенте;
  кадр shot_0018 сохранил прежнее расположение.
- **Причина:** этот клиент не применил обновлённый CSS live; механизм или причина
  отсутствия reload отдельно не установлены.
- **Исправление:** штатно завершить свой клиент, проверить завершение и запустить
  новую собственную сессию; не считать compile сигналом перерисовки.
- **Проверка:** [shot_0018 evidence](../../../../../build/dota_coach/native-hud-scene-final-css-shot-20261012.jsonl)
  предшествует [новому owned run](../../../../../build/dota_coach/native-hud-scene-final1280-owner-20261012.json);
  [shot_0019](../../../../../build/dota_coach/native-hud-scene-final1280-shot-20261012.jsonl)
  и [итоговый кадр 1280×720](../../../11-integration/02-addon-packaging/reports/native-hud-scene-2026-10-12.png)
  подтверждают новое расположение.
- **Следующий раз:** расхождение нового source/compiled hashes со старым видом;
  native live reload считать отдельной проверкой, не предположением.

## 5. Inert HUD: XML visible=false не закрыл пустые карточки

- **Действие:** исходный HUD13 загрузился без bind, но показал пять пустых slots
  и наложение статуса на штатную статистику.
- **Причина:** в этом кадре XML `visible=false` не обеспечил требуемую начальную
  видимость. Почему XML-атрибут не сработал, отдельно не установлено. Native
  `dump_panorama_css_properties` определяет CSS `visibility: collapse` как
  невидимость с исключением из layout.
- **Исправление:** в canonical CSS задать default collapse; roster margin-left
  320px, status margin-top 120px и читаемый фон. HUD13 остаётся definitions-only.
- **Проверка:** [native CSS help](../../../../../build/dota_coach/native-hud-scene-css-help-20261012.jsonl);
  [RED](../../../../../build/dota_coach/native-hud-scene-css-red-20261012.log)
  — один default-collapse failure, [GREEN](../../../../../build/dota_coach/native-hud-scene-css-green-20261012.log)
  — 20/20; [до](../../../11-integration/02-addon-packaging/reports/native-hud-scene-before-2026-10-12.png),
  [после 1280×720](../../../11-integration/02-addon-packaging/reports/native-hud-scene-2026-10-12.png)
  и [1920×1080](../../../11-integration/02-addon-packaging/reports/native-hud-scene-1920-2026-10-12.png)
  показывают исчезновение пяти пустых slots. Это проверка начального inert вида.
- **Следующий раз:** изменение default visibility проверять без запуска JS и в
  движке. Совместимость будущего `Panel.visible=true` с CSS collapse требует
  отдельного native setter evidence; эти кадры её не подтверждают. Полный bind,
  hittest, сервер и визуальная приёмка всей карты остаются отдельными критериями.

## 6. Engine screenshot сохранять без внешнего абсолютного пути

- **Действие:** `screenshot` с абсолютным путём вне Game/Content вызвал abort.
- **Причина:** native dump сообщил `Invalid screenshot path ...: D`; это
  установленная ошибка команды, отдельно от более раннего DXGI crash.
- **Исправление:** штатный `screenshot` без аргумента; проверить новый TGA в
  `game/dota/screenshots`, затем подготовить PNG для отчёта.
- **Проверка:** [foundation report](../reports/windows-foundation-2026-10-11.md)
  отделяет два сбоя; свежие native [shot_0019](../../../../../build/dota_coach/native-hud-scene-final1280-shot-20261012.jsonl)
  /[shot_0020](../../../../../build/dota_coach/native-hud-scene-final1920-shot-20261012.jsonl)
  содержат новые live markers и штатные screenshot paths.
- **Следующий раз:** экспорт native evidence; сверять новый timestamp и размер,
  просматривать оригинальный кадр, не выдавать старый файл за новый.

## 7. WGC timeout: фиксировать ограничение канала, не придумывать причину

- **Действие:** sky capture Dota/Asset Browser и контрольного Блокнота дал
  FrameArrived timeout; UIA Dota показывал рамку, не игровую кнопку.
- **Причина:** не установлена. Проверка Блокнотом и запуск через sky не
  подтвердили гипотезу о Hidden; повтор после reset также не дал кадра.
- **Исправление:** для визуальной проверки использовать рабочий engine
  screenshot; независимые source checks продолжать. Не менять ОС/драйвер и
  не кликать по предполагаемым координатам.
- **Проверка:** [foundation report](../reports/windows-foundation-2026-10-11.md)
  описывает контроль, error `coordinate input geometry is unavailable` и
  успешный native screenshot отдельно. Клик, hittest и lifecycle не приняты.
- **Следующий раз:** недоступный capture/input канал; ограничить заключение
  наблюдаемым отказом и выбрать независимый проверяемый результат.

## 8. VConsole: TCP и buffered log не равны живому ответу

- **Действие:** Tools однажды установил TCP без ответа; другой поток сначала
  показывал buffered startup messages и ToolsStallMonitor.
- **Причина:** ранняя готовность Tools не подтверждалась этими наблюдениями;
  поздний поток ответил, поэтому окончательный отказ не установлен.
- **Исправление:** новый уникальный echo после подключения; ждать ограниченно
  свежий marker, native load/game-state и нужное событие отдельно.
- **Проверка:** [foundation report](../reports/windows-foundation-2026-10-11.md)
  фиксирует поздний live ответ и panel_ready в Tools, 18:11:06 UTC.
- **Следующий раз:** новый процесс/порт/reload; API help, панель и ввод имеют
  разные доказательства. Справка о методах не подтверждает JS return values,
  адресность, полномочия или освобождение подписок.

## 9. Windows stat: сравнивать разные API с проверенной identity

- **Действие:** map audit выдавал ложный manifest_changed; 70 из 100 повторов.
- **Причина:** lstat/fstat совпадали по dev/ino/size/mtime, расходились по legacy
  ctime; st_birthtime_ns совпал в 50/50. Причина legacy ctime различия не установлена.
- **Исправление:** existing helper использует birthtime для cross-API identity
  на win32/Python 3.12; same-API snapshots сохраняют ctime mutation guards,
  POSIX/legacy fallback — прежние.
- **Проверка:** [identity report](../../../03-map-view/01-map-audit/reports/windows-identity-2026-10-11.md)
  — 100/100 stable associations; 34 tests: 28 passed/6 existing skipped;
  новые ctime-only mutation cases отвергаются. Bounded inventory не доказывает
  геометрию, патч или загрузку карты.
- **Следующий раз:** ложное «файл изменился» на Windows; сравнивать сырые поля
  до tolerance/retry/sleep и сохранять guards от настоящей мутации.

## 10. Timeout runner: сохранять настоящий ответ taskkill

- **Действие:** owned child fixture переживал sandbox timeout, stderr терялся.
- **Причина:** штатный taskkill вернул Access denied в sandbox; тот же owned
  fixture вне sandbox завершился с returncode 0. Отдельный mock ошибочно скрывал
  все shutil.which вместе с taskkill.
- **Исправление:** stdout/stderr taskkill направлять в suite log; Node absence
  mock скрывает только Node. Не менять privilege/kill scope/strict status.
- **Проверка:** [runner report](../../../11-integration/03-end-to-end/reports/windows-runner-2026-10-11.md)
  — три timeout tests прошли вне sandbox; synthetic refusal остаётся
  timeout_termination_failed и verified=false с диагностикой.
- **Следующий раз:** неизвестная причина timeout/termination error; сначала
  прочитать returncode/stderr и режим исполнения, fallback kill не считать
  доказательством завершения всего дерева.

## 11. Junction evidence дополняет, но не заменяет file symlink tests

- **Действие:** file symlink fixtures упали с WinError 1314; доступная Junction
  использована для отдельной проверки directory redirect guards.
- **Причина:** file symlink privilege отсутствовал; directory Junction — другое
  условие, её создание не устраняет этот отказ.
- **Исправление:** scoped Junction fixture, подтверждение ReparsePoint и запрета
  external open; удалить только redirect после проверки пути и target.
- **Проверка:** [reparse report](../../../11-integration/03-end-to-end/reports/windows-reparse-2026-10-11.md)
  — 3/3 actual redirect tests, без skips/errors; external target сохранён.
  File-symlink tests и отказ полного runner сохранены.
- **Следующий раз:** недоступный fixture без прав; добавить самостоятельный
  доказуемый сценарий, не подменять исходный и не ослаблять acceptance policy.

## 12. Полная регрессия: смотреть failed suites и verified

- **Действие:** первые Windows source runs дали encoding errors; UTF-8 убрал
  два отказа, но не все. Targeted GREEN и hundreds passed не закрыли full run.
- **Причина:** кроме encoding оставались WinError 1314, платформенные tests и
  строгий invalid_summary для suites со skipped; aggregate не включает все
  passed tests из неуспешных suites.
- **Исправление:** process-local `PYTHONUTF8=1`; сохранять полный summary,
  failures/skips/errors отдельно, не менять policy ради зелёного статуса.
- **Проверка:** [foundation report](../reports/windows-foundation-2026-10-11.md);
  [full-source log 12 октября](../../../../../build/dota_coach/native-hud-scene-final-full-source-20261012.log)
  и [JSON](../../../../../build/dota_coach/source-checks-20261012T064424Z-e9261c/source-checks.json)
  — 46 suites/752 passed_tests/6 failed suites, `verified=false`.
- **Следующий раз:** перед заявлением о готовности проверять свежую сводку всего
  требуемого объёма. Компиляция, screenshot, targeted source PASS, native input,
  C1/server/lease/возврат ИИ и проверка второго владельца закрываются отдельно.

## 13. Native фаза, getter и изображение — разные наблюдения

- **Действие:** hidden predicate PASS при visible=false; cached layout оставался140×30.
  Первый screenshot hidden попал между re-show setter и обновлением phase label.
- **Причина:** getter/сохранённый размер не гарантируют изображение; label обновляется
  отдельным scheduled callback и может ещё описывать предыдущую фазу.
- **Исправление:** получать engine кадр через две секунды после phase record,
  до следующего setter; проверять initial→shown→hidden→reshown по log и кадрам.
- **Проверка:** [native CSS cycle](../../../11-integration/02-addon-packaging/reports/native-hud-scene-2026-10-12.md)
  — четыре predicates PASS и четыре осмотренных кадра: отсутствует/виден/отсутствует/виден.
- **Следующий раз:** timed UI проверять в устойчивом интервале; промежуточный label
  и положительная ширина не заменяют actual frame. Setter fixture не закрывает полный bind.

## 14. WindowsApps alias не является рабочим Python

- **Действие:** проверка реестра175 через python --version дала ResourceUnavailable
  для WindowsApps/python.exe.
- **Причина:** обнаруженный alias недоступен в этой среде; это не отказ bundled runtime.
- **Исправление:** получить путь через load_workspace_dependencies и использовать
  проверенный C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe.
- **Проверка:** [реестр и проверочный код](agent-activation-2026-10-12.md)
  —175 matching IDs/names, JSON,75 local links, exit0 этим runtime.
- **Следующий раз:** выбирать launcher по фактической доступности; не повторять alias
  и не переустанавливать Python без необходимости.

## 15. Direct UI API calls не доказывают native ввод

- **Действие:** native fixture вызвала explicit bind/selectPlayer/remove/dispose/rebind
  и получила пять PASS predicates/actual кадров.
- **Причина:** это проверка существующих UI методов и layout. Mouse click/hittest,
  серверный источник/clock/identity и исполнение не были частью этого пути.
- **Исправление:** TEST/synthetic Labels и постоянный TEST banner; не передавать
  sender/gateway/resolver, сохранять disabled actions. TEST control AI маркировать
  как тестовый DTO, даже если существующий UI paint пишет «подтверждён».
- **Проверка:** [native binding report](../../../11-integration/01-ui-binding/reports/native-hud-binding-2026-10-12.md)
  — пять кадров и guards, no transport/gateway/identity; полноценный ввод остаётся открытым.
- **Следующий раз:** ограничивать вывод тем, что реально наблюдалось; отдельная
  test fixture не включается в fixed production kind и не заменяет C1 contract.

## 16. Quit и завершение процесса разделены во времени

- **Действие:** после fresh live quit PID21460 ещё существовал при первой
  немедленной проверке, следующая проверка показала его отсутствие.
- **Причина:** shutdown не завершился к первой проверке; механизм задержки отдельно
  не исследован. Live response команды не является доказательством PIDgone.
- **Исправление:** дать собственной сессии завершиться и повторно проверить owned PID;
  не отправлять повторный quit и не forcekill без нового основания.
- **Проверка:** [native binding report](../../../11-integration/01-ui-binding/reports/native-hud-binding-2026-10-12.md)
  и ignored native-hud-binding-quit-20261012.jsonl; финально Dota client отсутствовал.
- **Следующий раз:** перед новым launch проверять actual process state, сохранять Steam
  и чужие процессы; shutdown state проверяется отдельно от TCP/echo.

## 17. Source outputs и active compiled graph считать отдельно

- **Действие:** test-only fixture содержит15source outputs, а manifest compile
  дал14compiled UI files.
- **Причина:** неизменённый canonical coach_hud.xml сохранён как input/output,
  но test manifest загружает derived layout. Этот retained source не в active graph.
- **Исправление:** проверять реальный dependency graph и compiled file list, не требовать
  одинакового числа sources/compiled и не заявлять компиляцию неиспользованного файла.
- **Проверка:** [native binding report](../../../11-integration/01-ui-binding/reports/native-hud-binding-2026-10-12.md)
  —15matched payloads/14compiled hashes/95765UIbytes; fixed HUD13/12 неизменён.
- **Следующий раз:** при композиции fixture записывать copied/derived/retained inputs
  и active outputs явно; canonical source сохраняется единственным.

## 18. Root Panel XML должен быть анонимным

- **Действие:** скомпилировать native text preview fixture с id у внешнего Panel.
- **Причина:** Source2 compiler явно запретил root panel id; VM/XML parsing этого
  не проверяли. Canonical voice layout имел тот же дефект.
- **Исправление:** anonymous outer Panel, прежний VoiceTextRoot внутри; exact package
  policy принимает только новую topology, public bind получает inner scope.
- **Проверка:** [native voice report](../../../06-voice/03-voice-feedback/reports/native-voice-text-2026-10-12.md)
  — отдельные RED root regressions→GREEN; canonical XML и fixture compilation1/0.
- **Следующий раз:** до scene launch компилировать canonical layout отдельно от
  derived fixture; parsing и retained source не считать native compilation.

## 19. TextEntry требует явного оформления

- **Действие:** осмотреть пустое и заполненное поле в actual Dota screenshots.
- **Причина:** canonical CSS задавал только размеры/отступ; default native appearance
  не показывал границу пустого поля и рисовал красный текст. Причина default skin
  не установлена, ошибкой парсера этот цвет не является.
- **Исправление:** явные color/font-size/background/border/padding в canonical CSS.
- **Проверка:** [native voice report](../../../06-voice/03-voice-feedback/reports/native-voice-text-2026-10-12.md)
  — новый own launch, bound/ready кадры показывают рамку и светлый текст.
- **Следующий раз:** проверять native input одновременно пустым и заполненным;
  реальные dimensions и green assertions не доказывают читаемость поля.

## 20. Label100% внутри auto-width Button может скрыть подпись

- **Действие:** native preparation кадр показал пустые navigation controls и
  высокий узкий HeroRole control, хотя canonical XML содержал текст.
- **Причина:** width100% у Label при parent Button без fixed width; вывод по CSS
  и изменению кадров, внутренний native sizing алгоритм не исследован.
- **Исправление:** scoped Control Label width:fit-children в трёх canonical styles.
- **Проверка:** [native preparation report](../../../11-integration/01-ui-binding/reports/native-preparation-2026-10-12.md)
  — fresh launch, семь labels с text/native dimensions, подписи видны на кадрах.
- **Следующий раз:** отдельно смотреть статические control labels; непустая XML
  подпись и активность кнопки не доказывают, что native layout показывает её.

## 21. Прокручивать после расчёта нового content layout

- **Действие:** сразу после заполнения three-pane draft вызвать ScrollToBottom.
- **Причина:** scroll=-693 соответствовал предыдущему content1333/viewport640,
  а после layout content2083; actual complete кадр не показывал тактику.
- **Исправление:** test driver ждёт0.5s native layout перед API scroll.
- **Проверка:** [native preparation report](../../../11-integration/01-ui-binding/reports/native-preparation-2026-10-12.md)
  — final content1933/viewport640/scroll=-1293, выбранные plan/talk и summary видны.
- **Следующий раз:** сверять geometry и actual frame после content changes;
  nonzero scroll не доказывает нижний край, API scroll не означает physical input.

## 22. Проверять текущую игровую фазу непосредственно перед командой

- **Действие:** первый dota_pick_hero был отправлен после перехода в STRATEGY_TIME;
  VConsole marker принят, но hero HUD остался пустым.
- **Причина:** HERO_SELECTION окно закончилось; marker подтверждает соединение,
  а не выполнение phase-sensitive команды. Внутренний отказ отдельно не исследован.
- **Исправление:** fresh log state проверяется перед каждой командой; helper ждёт
  HERO_SELECTION и не делает поздний повторный запрос.
- **Проверка:** [native preparation report](../../../11-integration/01-ui-binding/reports/native-preparation-2026-10-12.md)
  — R1 phase-scoped commands и actual disposed кадр с Axe; own PID gone послеquit.
- **Следующий раз:** не ставить длинные проверки между state preflight и action;
  записывать фактический game result отдельно от command/connection success.

## 23. Ready missing slot отличается от недоступного источника

- **Действие:** first native observation cycle ожидал пустой OpponentName1 после
  fresh rebind с ready roster одного игрока; rebound assertion failed.
- **Причина:** TEST driver перепутал два existing presentation состояния. Canonical
  panel.paint очищает имена при source ready=false; missing slot ready=true
  показывает «Имя неизвестно». Production model не требовала изменения.
- **Исправление:** изменить только fixture expectation на canonical missing label;
  сохранить initial failed cycle и повторить fresh addon/launch.
- **Проверка:** [native observation report](../../../11-integration/01-ui-binding/reports/native-observation-2026-10-12.md)
  — final6phase cycle PASS, actual rebound TEST FRESH/четыре unknown names;
  first5phase PASS/rebound failure не переименованы в полный PASS.
- **Следующий раз:** при переносе source scenarios в native driver сверять ready
  и slot availability отдельно; inferred blank не подменяет public panel semantics.

## 24. Проверять standalone window внутри нового host на actual кадре

- **Действие:** native intervention API cycle PASS, но request pane не видна.
- **Причина:** standalone height100% в auto-height host и fixed720px centered window; CSS/after-frame inference, initial geometry и внутренний sizing алгоритм не измерены.
- **Исправление:** только composition scope: root height:fit-children, window width100%/top/left; TEST driver проверяет положительные dimensions.
- **Проверка:** [native intervention report](../../../11-integration/01-ui-binding/reports/native-intervention-2026-10-12.md): R1 восемь фаз, панель справа; unknown root/window374.4×281. Initial defect сохранён.
- **Следующий раз:** непустой DTO/API PASS не заменяет actual кадр и geometry после native layout; адаптацию ограничивать новым host.

## 25. Разделять scheduler parameter и wall-clock наблюдение

- **Действие:** production Schedule(5) переводит request в unknown; Date.now samples4958/4952ms в двух native cycles.
- **Причина:** clock domains не калиброваны; причина различия с5000ms не установлена.
- **Исправление:** записывать API parameter и наблюдаемые samples отдельно, не заявлять точность deadline, permission или lease.
- **Проверка:** [native intervention report](../../../11-integration/01-ui-binding/reports/native-intervention-2026-10-12.md): два timeout кадра и watcher без driver.expire, повтор блокируется.
- **Следующий раз:** для серверного deadline нужен настоящий clock/contract; local timer наблюдение не подтверждает полномочия или возврат ИИ.

## 26. Читать возвращённый путь свежего отчёта без реконструкции

- **Действие:** Get-Content guessed source-checks-20261012T125713Z-* не нашёл файл; actual125720Z-c40c6d существовал.
- **Причина:** свежий timestamp/random suffix не совпал с предположением.
- **Исправление:** использовать точный output report path и results[].log, возвращённые исполнителем.
- **Проверка:** initial125720Z-c40c6d и final130742Z-081143 прочитаны: packaging155tests/8WinError1314, full46/753/6failed.
- **Следующий раз:** сохранять возвращённый путь один раз; перед чтением подпункта использовать фактический href/rg --files вместо предположения имени. Ошибка чтения не является результатом проверок.

## 27. Fingerprints raw source и composed canonical output различаются

- **Действие:** новый mouse-targeting fixture test сравнил retained canonical XML с raw standalone source; first6PASS/1FAIL.
- **Причина:** существующая fixed targeting policy добавляет Targets/coordinator scripts и source comment. Canonical targeting output уже generated, хотя исходный XML не меняется.
- **Исправление:** metadata derived для retained canonical layout; отдельно сравнивать raw input hashes, exact prepare_assets outputs и preserved native subtree.
- **Проверка:** [native targeting report](../../../11-integration/01-ui-binding/reports/native-mouse-targeting-2026-10-12.md): final7builder PASS,7raw input hashes/7canonical output hashes,9installed files,8native API фаз.
- **Следующий раз:** source path в asset metadata не гарантирует byte-copy. Перед сравнением определить уровень преобразования; active graph проверять по уроку17 отдельно.

## 28. Capability skip не должен скрывать доступные проверки

- **Действие:** Windows symlink fixture creation далWinError1314 доguard; смешанный testcase также содержал tamper/preservation checks.
- **Причина:** ссылка недоступна в этом контексте. Skip всего mixed case потерял бы независимые проверки; OK(skipped=N) не означает полный PASS или process error.
- **Исправление:** общий real probe до mutation, skip толькоWindows1314; split cases/ограниченный subTest. Reporter отделяет incomplete отerrors, сохраняет strict verifiedfalse/exit1.
- **Проверка:** [Windows portability report](../../../11-integration/03-end-to-end/reports/windows-portability-2026-10-12.md): final1020PASS/28skip/0errors, actual tamper/preservation/junction/ownedtimeout PASS; первое неправильное root expectation исправлено и full повторён.
- **Следующий раз:** сначала установить, failed setup/guard/process или unsupported capability; сохранить независимые assertions и raw skip reasons. Не менять OS и не выдавать incomplete за приёмку.

## 29. Supported format не подтверждает открытие микрофона

- **Действие:** все4WinMM format queries вернули0/не открывалиhandle; actual FIFINEopen вsandbox вернул1.
- **Причина:** query и actualopen проверяют разные стадии. Та же команда outside approvedsandbox записалаPCM; низкоуровневая причина MMRESULT1 отдельно не установлена, privacy registry/CIM нельзя считать проверенными при отсутствии результата/access denied.
- **Исправление:** отдельно query/open/WHDR_DONE/bytes/reset/unprepare/close; bounded3s/owned output, без измененийOS/default device. Context comparison вместо отключения privacy; независимое чтениеWAV. ReviewP2: write/print error не должен отменять emergencyexit, finallyosexit и4failure injection tests проверены.
- **Проверка:** [microphone report](../../../06-voice/01-microphone-probe/reports/microphone.md): capture3.000s/48000frames/96044WAVbytes, все8APIresults0,cleanuptrue/hashmatch. RMS−51.715dBFS не доказательство речи; speech/ASR/bridgefalse.
- **Следующий раз:** не объявлять наличие устройства/format0/nonzeroPCM голосом. Не включать activating capture в обычный test catalog или импорт; отделять capture overhead отASR latency/resources.

## 30. Нижняя граница зависимости не гарантирует совместимость

- **Действие:** wheels-only faster-whisper1.2.1 с av>=11 получил PyAV19.0.1; модель загрузилась, но WAV decode упал на metadata_errors.
- **Причина:** PyAV19 удалил этот параметр, faster-whisper1.2.1 ещё передаёт его. Причина сверена по installed code/METADATA и официальному issue1589, не по догадке о микрофоне/сети.
- **Исправление:** отдельный pinned av18.0.0 overlay с явным import precedence; плохойenvironment/result сохранены. Не monkeypatch стороннийкод и не изменять audio радиPASS; хранить фактическиеversions/modelrevision/hashes.
- **Проверка:** [offline ASR report](../../../06-voice/01-microphone-probe/reports/offline-asr-2026-10-12.md): repeat exit0/model_loaded/generatorconsumed/VAD0/segments[]; officialmodelLFShash/size match. Positive speech decoder/quality не проверены, Python socket guard не OSnetwork trace.
- **Следующий раз:** проверять реальный native decode, не только import/model constructor. После compatibilitypin повторить тотже вход; пустойрезультатVAD не выдавать за точностьASR/речь/команду.

## 31. Native запрос фокуса не доказывает совпадение камеры с героем

- **Действие:** реальная активация native кнопки вызвала MoveCameraToEntity один раз и displayed requested; отдельно измерены lookAt и origin собственного проверенного живого героя.
- **Причина:** actual distanceXY4520.37 через1,5s, позднее исходная позиция. Причина возврата неизвестна; input/template bounds/API semantics пока предположения.
- **Исправление:** отделить pass семи API/render фаз от незакрытого критерия arrival; сохранить source gateway без origin/lock/orders, не подменять цель или API радиPASS.
- **Проверка:** [Native camera report](../../../03-map-view/02-camera-overlays/reports/native-camera-2026-10-12.md):7actual кадров1280×720 осмотрены, selected/refresh calls0 и immediatepositions equal, focus1/requested/distance, invalid−1reject/dispose/rebind.
- **Следующий раз:** измерять native motion/input/scene bounds раздельно. TEST id/API activation не real identity/hittest; origin читать только после guard собственного разрешённого героя.

## 32. ConvertFrom-Json может вернуть DateTime вместо строки

- **Действие:** строгая защита quit сравнила ToString('o') времени старта ownPID с JSON timestamp и отказала «identity changed».
- **Причина:** ConvertFrom-Json дал System.DateTime; сравнение stringvsobject не было сравнением UTC timestamps. Actual и saved ticks одинаковы639274225179114656.
- **Исправление:** сохранить строгую проверку PID/name и сравнивать точные UTCticks; не применять tolerance, отключениеguard или forcekill.
- **Проверка:** после исправления ownPID29544 закрыт черезquit/marker, процесс отсутствует, Steam12336 сохранён. [Отчёт](../../../03-map-view/02-camera-overlays/reports/native-camera-2026-10-12.md), initial safe refusal сохранён в журнале выполнения.
- **Следующий раз:** нормализовать типы дат перед identity comparison; отдельно проверить mismatch и owned completion. Guard failure не является auto-review rejection или причиной завершать чужойPID.

## 33. Имя native API не устанавливает форму возвращаемого массива

- **Действие:** motion diagnostic ожидал2элемента WorldToScreenXYClamped и остановился доsample0; первое сообщение не называло поле.
- **Причина:** runtime m3 вернул[0.5,0.45477646589279175,0], тогда как registeredAPI толькоjs_array безточной длины. Exact2 было догадкой поXY; третья компонента нерасшифрована.
- **Исправление:** named/rawerror вместо слепого изменения; actualtriple вVM сначалаRED, затемraw3 сохранён безvisibility interpretation. Postrequestguard отдельно закрывает newlyunavailable hero доorigin.
- **Проверка:** [Motion report](../../../03-map-view/02-camera-overlays/reports/native-camera-motion-2026-10-12.md): failedm2/m3 preserved, final100samples/raw3/5VMPASS, postguardRED→GREEN. OwnfailedPIDs quitgone.
- **Следующий раз:** в первичном диагностическом сообщении сохранять API/ожидаемую форму/actualshape/value и scope. Callback/registeredtype/JSarray name не позволяют угадатьlength/units/meaning.

## 34. Измерение с активным вводом не является управляемым сравнением

- **Действие:** вокругnativefocus получены20baseline/80post samples; near0 вpost сначала выглядел как подтверждениеприбытия.
- **Причина:** baselinealreadynear18/20, cursor68значений/buttontrue14samples/ownorigin8; одновременно менялись несколько условий. Index2 былtrue приrequest; семантика индекса отдельно не подтверждена.
- **Исправление:** не заявлятьcause/удержание/edgepan fix; сохранитьoriginalfailedarrival, rawinput/position/time. Preferences не менять радиGREEN; отделить samplednear отcausalarrival.
- **Проверка:** [100sample evidence](../../../03-map-view/02-camera-overlays/reports/native-camera-motion-samples-2026-10-12.jsonl), postnear2/80,min0,last312.7443/fouractualframes inspected; controlledcomparisonfalse.
- **Следующий раз:** до причинного опыта определить inputcontrol/baseline, фиксировать hero motion и provenance. Nearthreshold не global acceptance, mouse state не C2hittest/permission/ИИreturn; однапеременная иrollback отдельнымпланом.

## 35. Нормализация окончаний строк меняет хеш, сохраняя данные

- **Действие:** после публикации SHA-256 Windows JSONL отличался от хеша Git blob.
- **Причина:** исходные 100 записей имели CRLF, опубликованный blob — LF; побайтовая замена CRLF→LF дала точное совпадение. Это не изменение измерений.
- **Исправление:** исходный `samples_sha256` сохранён с явным scope `raw_windows_crlf`; добавлен `samples_sha256_lf`. Хеши фактических входов компилятора отдельно обозначены как Windows-входы.
- **Проверка:** [Отчёт и metadata](../../../03-map-view/02-camera-overlays/reports/native-camera-motion-2026-10-12.md): оба SHA-256 сверены, normalized bytes равны опубликованному Git blob, все 100 JSON-записей совпадают.
- **Следующий раз:** при проверке опубликованных текстовых артефактов фиксировать область хеша и окончания строк; различать исходные байты и Git-нормализацию, не менять исторический digest ради совпадения.

## 36. Проверка reset модели не подтверждает возврат viewport

- **Действие:** на native1600×900 existing preparation reset дал model predicate PASS после ScrollToTop, но actual scroll−695 и кадр середины состава. На1024×768 новый run дал scroll0 и начало4/5.
- **Причина:** причина расхождения не установлена; возможны input/layout/runtime differences. Build_id между опытами изменился25845666→25894101, контроль ввода не фиксировался, это не чистое сравнение разрешений.
- **Исправление:** отдельно оценить DTO reset, scroll geometry и actual frame; сохранить отрицательный visual result. После паузы сверить build_id, собрать новый отдельный addon вместо переноса старой compilation acceptance.
- **Проверка:** [Scaling report](../../../09-presentation/02-settings-layout/reports/preparation-scaling-2026-10-13.md):12actualPNG/6predicates на каждом размере, failed visual reset сохранён; interrupted run не выдан за completed, final ownPIDgone/Steam сохранён.
- **Следующий раз:** причинный опыт вести на одном build с before/after geometry и контролем ввода; ненулевой/нулевой sampled scroll и API success не заменяют physical wheel/hittest или поддержку resolution продуктом.

## 37. ScrollToTop и наблюдаемый scroll не изменяются атомарно

- **Действие:** resettrace записал geometry до/послеScrollToTop в одномcallback и последующиеsamples наодномbuild25894101.
- **Причина:** немедленное чтение сохранило−1674/−695; первоеsampled0 было позднее215/301/225/302ms. Внутренниймеханизмдвижка и причинаисторическогоотказа неустановлены; этонаблюдаемаяраздельностьcall/read/layout, не timing guarantee.
- **Исправление:** recordoperation boundaries/finalgeometry/actualframes отдельно; не менятьproductionкод по предположению. Context rechecked послеprepare/geometry доinputreads, postguardRED→GREEN.
- **Проверка:** [Resettrace](../../../09-presentation/02-settings-layout/reports/reset-trace-2026-10-13.md):131records/124samples/4ABAB/finaltop0/6frames; VM8PASS/builder10PASS. Sampledquiet неphysicalcontrol, oldfailure сохранён.
- **Следующий раз:** сверять результат послеnative layout, не толькоimmediategetter; wallclock/sampling неSLA. Не объявлятьневоспроизведённуюошибкуисправленной, guardпроверятьпослевнешнеговызова.

## 38. Synthetic decoder positive не подтверждает правильность приказа

- **Действие:**3фиксированныхрусскихreference синтезированыIrinaDesktop16kPCM16mono иполностьюдекодированыlocaltiny/PyAV18.
- **Причина:**путьdecoderработал, нодвефразыошибочны;9правок/11referencewords WER81.8% толькоэтихsamples. Installedvoice inventory также не подтверждалSelectVoice вsandbox; причинаконтекстногоразличиянеустановлена. Недоступныйoverload сверятьlocalreflection, анеугадывать.
- **Исправление:** раздельныеsynthetic_decoder_positive/real speech/accuracy/bridge flags, rawsegments/referencecomparison; false safety claims/команды0. Failedreceipts сохранены, WaveFileformat verified, thresholdsнеподгонялись.
- **Проверка:** [SyntheticASR](../../../06-voice/01-microphone-probe/reports/synthetic-asr-2026-10-13.md):thirdexact/twoincorrect,PCM/modelhashes/9puretests PASS, existingoutputrefusalpreservesbytes, full1059pass/28skip/0errors.
- **Следующий раз:** decoder/text/no_speech score не semanticconfidence; WERinsertions можетпревысить100% отдельнойфразы. Реальнаяречь/команднаяточность/authority требуютотдельнойвыборки, не трёхTTSпроб.

## 39. Source media inventory требует явного среза и не устанавливает права

- **Действие:** readonlyinventoryнашёл83C2source/98literalrefs/98HEADmedia; послеnativecommitпоявилисьещё6PNG, progressSVGизменилсяпослеcheckbox.
- **Причина:** HEAD/filesystem/generated-artifact scopesразличаются; literalfile refs неохватываютengine/transitive/dynamic assets. Git/SHA256/техническое происхождение не подтверждаютauthor/IPlicense.
- **Исправление:** current104media deltaявноучтена, generator/data/SVGworkingoverride хешированы; sourceкод, diagnosticPNG, concept иruntime selectionразделены. Всеправаnot_assessed, неизвестноеacquisitionневыдумано.
- **Проверка:** [Registry](../../../09-presentation/01-assets/reports/assets-register-2026-10-13.md):187filehashes/104media membership/10recipehashes/98internalrefs/31links,ниdeclaredmedia вrecipes. Толькоregistrycheckbox54/213, licenses/humanowneropen.
- **Следующий раз:** указыватьHEAD/дату/workingdelta иневыдаватьотсутствиеexplicitURLsзаallruntimeaudit. Concept/mapreference/screenshot неlicensedruntimeasset; будущийinventoryобновлятьпослеmedia/progresschanges.

## 40. Статический source PASS не доказывает исполнение Lua и совместимость модулей

- **Действие:** C2 рассмотрел 172 переданных файла C1; actual Lua 5.1 RED воспроизвёл семь разрывов, хотя существующие строковые проверки проходили. Voice producer source=voice не принимался арбитром; каталог не охватывал 35 новых наборов.
- **Причина:** проверки наличия строк и отдельные DTO shape assertions не исполняли переходы/межмодульную передачу. Верхняя граница 64 уже не вмещала 85 реальных наборов; sandbox timeout отказ отдельно совпал с ранее установленным ограничением.
- **Исправление:** bounded guards/public return/copy binding/source=coach+origin=voice; executable Lua5.1 harness, actual producer→arbiter; каталог85/max128 при сохранённых byte/path/schema guards. Реальную authority не выдумывать.
- **Проверка:** [Рассмотрение C1](../../../11-integration/03-end-to-end/reports/creator-1-review-2026-10-13.md): Lua8/voice13 PASS; all85/1242passed/28skip/6incomplete/0errors/strictfalse. C1 36/188PASS, progress112/181 равен генератору, 69 open actions; критик подтвердил устранение ограниченных замечаний.
- **Следующий раз:** дополнять static проверки исполнением настоящего source и actual producer/consumer; различать streaming epoch, server commit и engine effect. Перед интеграцией сверять полный каталог и Git HEAD, не доверять историческому handoff/progress.

## 41. Decoder и lexical parser требуют раздельной проверки на фиксированном корпусе

- **Действие:** baseline эталоны не принадлежали exact VoiceText grammar; заранее выбран новый parser_grammar корпус, TTS→tiny дал6wordedits/7words, все3 decoded hypotheses rejected.
- **Причина:** даже понятная человеку phrase не обязательно совпадает с фиксированной грамматикой; lexical ASR ошибка не даёт оснований добавить fuzzy mapping или заменить captured revision. Три TTS sample не оценивают реальные речь/accuracy.
- **Исправление:** exact sample_set сохраняет baseline/old receipts, refs фиксируются до наблюдения; модель/параметры/vocabulary unchanged. Root отдельно проверяет PCM/model/hash/метрику и actual parser refs/hyps/guards; commands0.
- **Проверка:** [Grammar pilot](../../../06-voice/02-recognition-parser/reports/synthetic-grammar-2026-10-13.md): 12purePASS, refs3ready/hyps0ready, duplicate/stale/ambiguous guards и disposedProxy0; baseline4hashes unchanged, full85/1242/28skip/0errors/false. Критик без существенных замечаний.
- **Следующий раз:** фиксировать test corpus до decoder outputs, сохранять errors/rawtexts и semantic outcomes отдельно. Случайная lexical удача, WER или no_speech score не server authority/semantic confidence. Пути сначала получать через rg --files; в apply_patch использовать только прочитанный exact context, иначе весь batch отклоняется без изменений.

## 42. Сходные имена полей двух библиотек не образуют общий контракт

- **Действие:** C2 сопоставил12actualC1/C2источников: C2recipientId/epoch/ticket противC1actorEntity/revision/orderId; hold/regroup противgather/attack, нет общегоsnapshot/outcomeproducer. Existing source панель tested на actual3synthetic decoded failures послеready.
- **Причина:** scope revision/identity/target/correlation различается; прямое переименование/подстановка полей создаст неподтверждённую authority. Визуально старое ready могло бы вводить в заблуждение после нового reject — это риск, а не найденная production ошибка.
- **Исправление:** [Gap review](../../03-interface-contract/notes/c1-gap-review-2026-10-13.md) фиксирует закрывающие решения и одного будущего автора общего envelope; runtime переходник не выдуман. Existing labels/action/address очищаются на failure, captured revision не заменяется, stale handle не читает DTO.
- **Проверка:** 12raw/LFhashes совпали с published108b6dd, fields/enums извлечены из actualsource; [feedback](../../../06-voice/03-voice-feedback/reports/synthetic-feedback-2026-10-13.md): actual3pairs/context/hash/oldtestprefix/production unchanged,24VMPASS/full85/1245/28skip/0errors/strictfalse.
- **Следующий раз:** сначала согласовать семантику и authoritative источник поля, затем один adapter; не превращать caller Confirm/revision/visible flag в server evidence. Проверять UI после последовательности ready→reject и ownership смены, не только одно состояние.

## 43. Native sender и исходный adapter нужно измерять отдельно от TEST glue

- **Действие:** C1/C2 native ping на build25894101: три fresh9source/7compiledUI addons,18фаз/18actualframes. Sourceindex1 разрешился в nativeentity(table)/player0 и совпал с PlayerResource handle; originalautoAdapter тоже дал2correlatedOK иdispose.
- **Причина:** прежние pure/static проверки не подтверждали callback source semantics, firstTESTglue не исполнял originaladapter, а отсутствие metadata trace не объясняло PlayerID spoof. Механизм engine internals не установлен; наблюдаемое значение изменилось между pre-send и callback.
- **Исправление:** sender выбирается только nativeentity/getPlayerID/equality; metadataenum и presendJSONcopy добавлены TEST-only. Snapshot RED18PASS/1fail→19GREEN, Lua metadata RED13PASS/1error→14GREEN; nativeActivateddispatch проверяетoriginalonactivate, неphysical mouse/hittest.
- **Проверка:** [Native ping](../../../01-foundation/02-panorama-capability/reports/native-ping-2026-10-13.md): fixedprobe5/sourcepolicy/production unchanged,18frames viewed,9builder/14Lua/19VM/full85/1271PASS/28skip/6incomplete/0errors/strictfalse; all3ownPIDsquitgone/Steam12964 retained. Одинкритикnofindings; толькоdiagnosticcheckbox→55/213.
- **Следующий раз:** не считать helper missingdependency ошибкойbuilder: дождаться stableauthor inputs; sourcequery сначала inventory, rg наWindowsс--glob, не literal*. Полные registry/logblob не печатать вместо scoped строк. Не отождествлять sourceconnection с actor/lease/authority, metadatachange с конкретным engine механизмом и Activated mouse argument с настоящей мышью.

## Как продолжать обучение

Каждый исполнитель перед подходящей задачей применяет соответствующий пункт.
После завершения задачи сохраняет фактический result/evidence; новый урок
добавляет только при новом знании по пяти полям выше. Неустановленную причину
так и помечает. Историческую проверку не переименовывает в свежий результат.
Длинные raw logs остаются локально; в библиотеке — краткая причина, действие,
критерий повторной проверки и ссылка. Поручение/файлы/непроведённые шаги остаются
в [журнале действий](../../../00-action-log/README.md).
