# План исполнения +30 пунктов процента двух создателей

> **For agentic workers:** Use superpowers:executing-plans for root tasks and
> scoped independent C1/C2 agents for parallel deliverables. Пользователь прямо
> поручил составить и сразу выполнять план; повторного approval gate нет.

**Goal:** проверенная автономная сцепка двух библиотек и минимум55/64 новых actions.
**Architecture:** server-owned one TEST hero, exact independent roster protocol,
Panorama consumer, separate fixed bundle kinds; source/native/review evidence ledger.
**Tech Stack:** Dota Workshop Windows build25894101; Lua5.1/Lupa, PanoramaJS/XML/CSS,
Node tests, Python3.12, guarded PowerShell/VCon native fixtures.
**Spec:** [Дизайн](autonomous-30pp-design-2026-10-13.md).

## Global Constraints

- C1 baseline113/182 (format-only correction excluded), target168/182; C2 baseline56/213,target120/213.
- Frozen [1180-file inventory/action baseline](autonomous-30pp-baseline-2026-10-13.json).
- No new checkbox denominator; existing IDs and single-source ownership preserved.
- Manual wire17/lease5, defaults fixed7/9; new normal15/TEST18 kinds separate.
- Real data/fidelity/legal distribution/full5×5/human physical input require actual proof.
- Separate AI technical peer review authorised by user; source review is not product/legal approval.
- Fresh bundle/addon/ownPID+UTC, no existing client overwrite; no build edits/send/public release.

## Review Focus

- Pause unknown/true plus disconnect must never stop replacement or resume closed AI.
- New generation/session/reload cannot revive old grant or stale callback.
- Native nested roster table numeric-string keys/bool wire must match exact client schema.
- Policy/arbiter/journal must execute actual source, not parallel test-only copies.
- Claimed progress must match original actions and evidence, including format correction.

## Task A — Аудит и работающий диспетчер

**Owner/files:** root/C2; this notes baseline/design/plan; tools/autonomous_progress.py,
tests/test_autonomous_progress.py in C2-01-01; shared policy/AGENTS/decisions onlyroot.
**Interfaces:** report_delta(repository,baseline,evidence)->JSON targets/new/reopened/errors;
CLI read-only --baseline/--evidence, --require-target exits1 if targetnotachieved.
Evidence record task path/action indices/author_creator/reviewer_creator/report/proofs/scope.

- [x] Inventory all tracked files and72taskREADME, freeze hashes/actionflags/HEAD.
- [x] Record user's AI technical peer review override with product/legal gates preserved.
- [x] RED tests: stale baseline, changed action count, oldx not new, reopened subtracts,
wrong creator review, missing evidence report, target55/64 not silently accepted.
- [x] Implement read-only delta/next-ready reporting; run GREEN and preserve log.
- [x] Correct embedded C1 checkbox as existing113/182; update generator (not a newaction).

## Task B — Actual C1 runtime source integration

**Owner:** C1 agent; root onlysharedcontract; files C1-03-01/tests/test_execution.py,
C1-03-02/src synthetic_policy.lua/tests; C1-02-03 event_log.lua/tests;
C1-04-01/manual_move_game_mode.lua + tests; C1-11-01/src/scripts/vscripts/coach_scene_game_mode.lua + tests.
**Interface:** manual native module returns resolve_sender(source)->player,id and
configure_server_hooks({decide_ai=function(observation)->XYZorNil,
on_snapshot=function(snapshot)}) beforeActivate once. Hooks cannot set client owner/mode.
New wrapper requires existing observation/synthetic_policy/order_arbiter/event_log
actual sources, uses projection of own allowed point only and no hidden data;
policy move from current own position, arbiter ai/manual priority admission, journal
Append(server_time,...),LinkOrder/TagMode of copied records.

- [x] Write/execute RED actual Lua51 invariance/filter/future and policy→arbiter scenarios.
- [x] Implement copy/guard fixes needed by actual execution, no fixture-only runtime.
- [x] Wire server hooks with fresh own observation; errors fail closed, pause noeffects.
- [x] Produce contract conformance examples repeat/foreign/stale exactmanualv1 bothdirections.
- [x] Targeted GREEN plus docs exact source/native scopes, publish technical evidence to C2.

## Task C — Confirmed TEST roster C1→C2

**Owner:** C1 agent roster module/bridge; root C2 consumer and shared protocol.
**Files:** C1-07-01/src/scripts/vscripts/roster_confirmation.lua + tests/test_roster_confirmation.py;
C1-11-01 coach_scene_game_mode.lua owns native event registration;
C2-11-01/src/panorama/scripts/custom_game/server_roster_panel.js/tests/server-roster.test.cjs;
shared/contracts/preparation-roster-v1.md (root); no copy of validators into tests.
**Interfaces:** roster.confirm(assignments,serverProfiles)->confirmation/reason;
fixed server-owned TEST compatibility/profile definitions; native read-only
`dota_coach_roster_request`→`dota_coach_roster_state` exactdesign8fields.
C2 create/bind/dispose strict8field snapshot +5slots entry5fields, capturedsession/highwater,
explicit unknown/reject, disabled arbitrary client confirmation.

- [x] RED actual production Lua validator for count/duplicates/hero-role/NaN/bool/malformed/synthetic coverage.
- [x] Native original sender resolver before DTO inspection; addressed owner only, copy metadata,
exact payload/query/response, no raw client profiles.
- [x] RED/GREEN C2 actualconsumer+panel with native-shaped stringslot0/1 data and stale/dispose guards.
- [x] Register server snapshot beside manual panel; current preparation private flow unchanged.

## Task D — Exact bundle + native lifecycle acceptance

**Owner:** root/C2 packaging/native PID; C1 creates test-only server probe.
**Files:** C2-11-02/tools/build_coach_scene.py +tests; C1-02-03/tests/01-native-lifecycle/
coach_scene_fixture.lua; C2-11-03/tests/01-native-coach-scene/fixture.js, native-command.ps1,
capture-command.py. New dirs README+parentlinks. Rootwrites fixedsource recipe only.
Normal15 targets: controller, original manual game module, wrapperaddon, roster,
observation, syntheticpolicy, arbiter, eventlog (8Lua); manual2JS+rosterJS(3);
canonicalmanualXML+derivedcoachXML(2), CSS(1),manifest(1).
TEST18: map normalwrapper to coach_scene_game_mode.lua, TESTLua as addon_game_mode.lua
(+1), fixtureJS(+1), derivedfixtureXML(+1); retain normal/canonical XML, exact hashes.

- [x] RED exactrecipe tests extra/missing/source hash/DTD/duplicate/path/reparse/freshguards.
- [x] Build fresh separatekind; verify15/18; nativecompile includes actualLua runtime and UI graph.
- [x] Probe native pause/kill/respawn capabilities before tests; log unsupported explicitly.
- [x] Actual snapshot+game clock before/during/after pause, no nativeeffects whilepaused,
expiry order andserver eventsequence, death/newgen rejects oldepoch; dispose/rebind staleDTO0reads.
- [x] Native receipt of five confirmedTEST assignments, weakcoverage shown; no5×5/startclaim.
- [x] Capture actualPNG/time/hash, quit ownPID; secondfreshlaunch normalclient noTESTdriver.

## Task E — Prototype packet and current material register

**Owner:** root C2 packet/media; C1 agent serverproof review/rightsregistry/docs.
**Files:** C1-12-01 reports currentregistry; C1-12-02 reports/notes earlypacket;
C1-12-03 reports technicalpackage; C2-12-02 prototype storyboard/packet reports;
C2-12-03 repeatable local run guide; no external sends/publicrelease.

- [x] Inventory current trackedmedia/newproofs with hashes/sourcepurpose/licenseunknowns;
read legalplan/review; source failure !=rightsholder refusal; no licence conclusion fabricated.
- [x] Assemble realframe annotated demonstration limitedtoTESTscene and verifiedresults;
clearly separateimplemented vsfuturefullgame/voice/profiles/map.
- [x] Write two unsent requests (customgame terms / possible independentproduct rights),
operator/jurisdiction unknown; concrete prototype packet, no claim approval/send.
- [x] Verify exactpackage/version/install with fresh normalkind; distributiongrounds remainopen.

## Task F — Acceptance and technical cross-review all72parts

**Owner:** root+scoped C1/C2 authors; independent othercreator reviewer perpart.
**Files:** each chosen task reports/autonomous-acceptance-2026-10-13.md,
36C1 technical review decisions byC2, 36C2 decisions byC1, summary inC2-01-01notes.
Agentcritic onlyafterfinishedsubproject, onefinalcritic overall, notpercheckbox.

- [x] C2 compare31unwrittencriteria against actual source/native/report, explicitly unperformed
cases; do not turn TEST/local ready/sourcehash/ASRsilence into product/native proofs.
- [x] Independent peer reads actual code/tests/docs, records foundissues andblockedscopes.
Fix material source findings before mark reviewed; documents-only/emptyruntime remainopenfunctional.
- [x] Root closes only evidenced existingactions with links; all36handoffsC1 (if reviewed),
C2 at least64new across functional/criterion/review, not a new arbitrary mini-plan.
- [x] Evidence ledger stores author/reviewer/commands/artifacts per action; delta tool
rejects unsupported or old/computed-format closures. Reopen incorrect existingclaims if found.

## Task G — Final verification/publication/report

- [x] Targeted checks aftercode; required full canonicalcatalog outsidechildcleanup sandbox,
source flags strictfalse for known28skips, no fabricated native claim.
- [x] Progress generators/check, linkedREADME hierarchy, JSON/hash/actualPNG, ownPIDs gone,
oldusageprefix/.freebuff/userchanges preserved; onefinalcritic/regrade; appendlesson/usage.
- [x] Evaluate --require-target: C1new>=55, C2new>=64 plus evidence/peer receipts.
If blocker prevents a criterion, retain unchecked and report exactshortfall, no falsecomplete.
- [ ] Commit/push authorisedmain withoutforce; remoteSHA==HEAD; finalreport actualcounts
newdeliverables/remainingblocks, no percent-as-game-readiness statement.

## Task H — Очередь после текущей цели

Real player data provenance→heldout models; native visibility/map/patch;
physical mouse+ASRpositive real speech; generalcommand/arbitration/5×5 andresult;
performance onlyafterreal scenario/bottleneck; rights/Valve/release onlyownproofs.
Root selects next unblocked dependency and reuses free agent slots; durable plan,
actiondelta and windows-resume make later continuation independent of chat history.

Ruling: server roster source uses existing panorama/scripts/custom_game hierarchy rather than flat src path; keeps a single implementation and existing index structure.


14октября TaskH уточнён ответами пользователя: следующий продуктовый вертикальный сценарий5×5 — выбортренера/пул20/состав/подготовка/матч/короткийMANUAL→AI/итог. Nativegeometry/visibility иgeneralcommands/itembuild требуют следующей localdesign/spec; physicalinput иреальнаяречь не считаются подтверждёнными. Около10POVвидеонаигрока предложены дляисследования; начать с одного и провестиheldout проверку, не обещатьточнуюкопию. Видео ещё непереданы. [Подробное видение](game-vision-proposal-2026-10-14.md).
