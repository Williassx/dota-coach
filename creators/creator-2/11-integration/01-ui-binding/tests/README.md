# tests — C2-11-01

[Родитель](../README.md).

- [native-hud-binding](native-hud-binding/README.md) — отдельная explicit native
  fixture; TEST данные, no sender/gateway/identity. Не fixed source kind.

- [hud-binding.test.cjs](hud-binding.test.cjs)
- [preparation-flow.test.cjs](preparation-flow.test.cjs)
- [panel-port.test.cjs](panel-port.test.cjs)
- [preparation-binding.test.cjs](preparation-binding.test.cjs)
- [intervention-selection.test.cjs](intervention-selection.test.cjs)
- [intervention-port-binding.test.cjs](intervention-port-binding.test.cjs)
- [intervention-screen.test.cjs](intervention-screen.test.cjs)

- [match-observation.test.cjs](match-observation.test.cjs) — 15 сценариев реальных
  child panels: separate sources, lifecycle/reentry/partial bind/old owner.

[mouse-targeting.test.cjs](mouse-targeting.test.cjs) — 20 VM интеграционных сценариев с real Targets/model/panel: expiry, clear-beforeDTO, immutable actor/move independence, clock/native reentry/dispose.

[Native preparation fixture](native-preparation/README.md) — отдельный API-driven
TEST driver и native scroll/geometry assertions, без production auto-bind/input.
