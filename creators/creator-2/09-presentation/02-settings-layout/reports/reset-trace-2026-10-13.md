# Reset trace: отказ не воспроизведён, немедленное чтение не финальный layout

13октября2026. [Spec](../reset-design.md), [план](../reset-plan.md),
[metadata](reset-trace-2026-10-13.json), [131 parsed native records](reset-native-records-2026-10-13.jsonl).
Первый bounded результат внутри2часов работы06:01:04–08:01:04UTC.
Leading157/root107/114/173/174/175;1reused helper дляAPI/VMtests, root авторdriver/
builder/capture/shared files. Production/C1/fixed preparation15/14/HUD13/probe unchanged.

На одном build25894101/1600×900 выполнены четыре independent bind cycles ABAB:
complete5synthetic records→removeTEST-p4→immediate или0.5s delayed ScrollToTop.
Geometry/input записывались вокругопераций и Schedule0.1s;124samples/131records,
6actualengineframes1600×900 осмотрены. В конце всехчетырёхtrial scroll0/content1496/
viewport801 и начало4/5 visible. Старый reset1600scroll−695 **не воспроизведён**.
Его исторический отчёт сохранён, причина не установлена.

| Trial | Samples | AfterTop непосредственный scroll | Первое sampled0 после call |
|---|---:|---:|---:|
| immediate-a |31|−1674 (старыйcontent2475)|215ms|
| delayed-a |31|−695 (новыйcontent1496)|301ms|
| immediate-b |32|−1674 (старыйcontent2475)|225ms|
| delayed-b |30|−695 (новыйcontent1496)|302ms|

В одномJScallback до/послеScrollToTop свойство сохранило прежнее значение; позднее
sample показал0. Поэтому чтение сразу после вызова не подтверждает конечное
состояние. Эти wall-clock observations зависятотsampling/layout/workload, неSLA,
не engine timing guarantee и не доказательство превосходстваdelay. Во всехsamples
cursor[810,234], buttons/modifiersfalse; sampledInputQuiet=true/taintedfalse.
**PhysicalInputControlled=false:** wheel/полныйkeyboard/события междуsamples не
наблюдались. Globalmousecallback не устанавливался, восстановлениеownership
не подтверждено API dump; Valve wiki403 не свидетельство отсутствиявозможностей.
Нет оснований менять production scroll/ввод или объявлять causalfix.

## Native evidence

- [bound](preparation-1600x900-trace1-bound-2026-10-13.png)
- [immediate-a](preparation-1600x900-trace1-immediate-a-2026-10-13.png)
- [delayed-a](preparation-1600x900-trace1-delayed-a-2026-10-13.png)
- [immediate-b](preparation-1600x900-trace1-immediate-b-2026-10-13.png)
- [delayed-b](preparation-1600x900-trace1-delayed-b-2026-10-13.png)
- [disposed](preparation-1600x900-trace1-disposed-2026-10-13.png)

TESTbanner/rootstate/localonlywarnings видны; ownAxe/template world неidentity/
realmap. HUD просвечивает, disposedminimap whitepolygon имеетнеизвестнуюпричину.
Freshbundle061918Z-593520/newaddon preparation_reset_trace_20261013:17outputs,
nativeUI1/canonical1/map13/0failed/0skipped/exits0,17compiledfiles/map3033508bytes.
OwnPID2128 exactticks quit→gone, finalDota0/Steam12964kept. Sourcebuilder flagsfalse;
native evidence отдельно. ParsedJSONL UTF8LF intentionally derived; rawconsole ignored,
SHA256scope указан вJSON. Preferences/OS/server/gameorders не изменялиськомандами.

## Source проверки

Builder3новыхcases сначалаREDunexpectedvariant, затем10PASS; defaultnative driver
preserved, exactbaseline/resetallowlist и17uniqueoutputs. VM6REDmissingdriver,
первыйGREEN5/6 выявиллишнийsample передbound; порядокисправлен. Дваpostguard RED
выявилиread послеsynchronousprepare/geometry contextloss; повторныеguards GREEN8.
Malformedinput/geometry closes once; dispose/stalequeued callbacks не делаютreads.
Actualcapturehelper variant/receipt/addonallowlists сохранены; ordinarycatalog не
активируетDota/mic/TTS/inference. Full062607Z-57578a:50suites/1059passed/28skip/
6incomplete/0errors/strictfalse/CLI1,50process exits0. Count включает9pure ASRtests
соседнего независимогоpilot; этиchecks не являются native trace.

Production/hittest/server/lease/realinput/causaloldfailure/humansecondowner открыты.
Progress53/213unchanged. Одинитоговыйtechnicalcritic не нашёлсущественныхзамечаний;
это не humansecondowner. Следующий шаг: сохранитьtraceкакbaseline и продолжить
независимыеC2задачи; повторбезновойгипотезы не требуется.
