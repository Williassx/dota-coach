# План reset tracing

**Цель:** раздельно измерить модель, layout и ScrollToTop наодномbuild.
**Спецификация:** [reset-design.md](reset-design.md). Inline root; readonly helperAPI.

- [x] RED3builder cases: reset17outputs/defaultpreserved, exactvariant refusal
  beforewrites, missing resetdriver refusal. GREEN minimally allowlisted selector.
- [x] RED driver VM tests: fourABABtrials/delayedtop0.5s, raw malformedinput closes,
  sampledinputquiet neverphysicalcontrol, invalidcontext skips deferred reads.
  Add test-only native resetdriver; production modules remain unchanged.
- [x] Exact capture helper variant/receipt/addon guards and native phase list;
  source catalog adds only nonactivating VM suite. AST/Node/targeted checks.
- [x] Currentbuild preflight; freshbundle/freshaddon17outputs/compileUI1/canonical1/
  map13, own1600×900 launch and capture traces/6frames; guardedquit/gone.
- [x] Trace/statistics/frames/limitations report; complete source regression only
  after implementation stabilises,1finalcritic, lessons/usage/journal/resume.
- [x] Regular commit/push/remoteSHA. Continue other available C2 tasks until
  two-hour deadline, record actual time; no claim product completion.
