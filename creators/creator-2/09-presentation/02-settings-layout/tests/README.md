# TEST reset trace

[Spec](../reset-design.md) · [План](../reset-plan.md).
[reset_fixture.js](reset_fixture.js) — onlyexplicitnativefixturevariantreset,
неfixedkind. [reset-trace.test.cjs](reset-trace.test.cjs) проверяет8VMscenarios;
nativeautostart удерживаетсяfakeSchedule и неисполняется. Nohardware/realinput.

Private `DotaCoachPreparationResetTrace.start(ports)` orchestrates fourABABtrials,
returns idempotentdispose; ports geometry/input/schedule/now/UIoperations/record.
Snapshots have physicalInputControlled=false; sampledquiet не autorization.
Nativeadapter использует existingexplicit public preparation bindings,
неserver/start/storage и ниоднойoriginread/приказа. Contextguards до/послеports.
