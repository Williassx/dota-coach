# План панели ручного запроса

> Для исполнителя: superpowers:executing-plans/TDD, один редактор, пять read-only критиков.

**Goal:** requestpanel отражает pending/ACK/observedmode, без выдачи прав mouseinput.
**Architecture:** existingpuremodel + ownedpanel +optional callbacktransport; ACKwait5s отдельноlifecycle.
**Stack:** ES5/NodeVM/PythonXML. **Spec:** [panel-design.md](panel-design.md).

## Constraints/review focus

No copy model rules/HUD/defaultpolicy/sharedcontract; sourceonly3definitions, noautobind.
Timer failure before send ≠ sendthrow; lateACK capturedinstance; selected≠requestactor.
Every required child node validity/visibility guard; root staging visibility exempt; stagedDTO clearsfields; nativeclock notproven.

## 1. Adapter и source graph

**Create:** src/panorama/scripts/custom_game/intervention_request_panel.js,
src/panorama/layout/custom_game/intervention_request.xml,
src/panorama/styles/custom_game/intervention_request.css,
tests/intervention-panel.test.cjs, tests/test_intervention_layout.py; README newdirectories.
**Interface:** bind(root,send?) → update/select/request/dispose/isDisposed as design.

- [x] VM actualclick/requestACK/errors/timers/lifecycle/reentry tests RED.
- [x] Minimal adapter GREEN with actualpuremodel; no game/input/API additions.
- [x] XML/CSS IDs/exactrefs/order/inert/plain/disabled tests RED→GREEN.

## 2. Review и публикация

- [x] Пять read-only verdicts, concretefindings RED→GREEN; previous577+new PASS.
- [x] Syntax/sourcegraph/README/links/diff, notes/report/планы/журнал.
- [x] Onlystart_skill saved/readback preservedfields; fast-forwardmain/remoteSHA/clean.
