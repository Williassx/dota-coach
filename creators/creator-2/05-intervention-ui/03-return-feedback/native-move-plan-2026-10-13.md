# Native manual move implementation plan

> **For agentic workers:** Use superpowers:executing-plans for root tasks;
> independent C1 server and C2 packaging tasks delegated to existing helpers.
> User explicitly requested autonomous implementation of agreed design.

Spec: [native-move-design](native-move-design-2026-10-13.md).
Contract: [v1](../../../shared/contracts/manual-move-v1.md). Root single shared author.

1. C1 helper: new `04-intervention/01-manual-actions/src/scripts/vscripts/manual_move_controller.lua`
   pure module.new(ports) API handle(sender,request),tick(),snapshot(sender,id,status,reason,transition),close().
   New `manual_move_game_mode.lua` native bootstrap requires controller; files/tests
   in C1-04-01 only, old modules unchanged. Python LupaLua51 tests observe RED,
   then GREEN actual controller. ports owner/clock/paused/observe/move/stop/ai.
2. Root C2: `src/panorama/scripts/custom_game/manual_move_state.js` pure UMD
   create(ports),select/acquire/move/cancel/sync/receive/dispose/read methods;
   `manual_move_panel.js` explicit native auto-bootstrap for this new scene;
   layout/custom_game/manual_move.xml/styles/custom_game/manual_move.css.
   Node tests RED/GREEN real module; nativeUI script ordinary selection/request/
   cancel buttons and mouse world callback. TEST automator separate tests/native-move.
3. Packaging helper: `tools/build_manual_move_bundle.py` exact6outputs (2Lua,
   2JS,XML,CSS) + generatedmanifest =>7. Freshchild build/dota_coach;
   use existing probe read_source/output_path helpers, no policy expansion.
   receipt assets hashes/schema stage sourceonly; tests RED/GREEN. Native install
   separate `tests/native-move/native-command.ps1`, ownPID/startUTC/freshaddon;
   resourcecompiler manifest +template_map, no useraddon replacement.
4. Root add suites to existing fullcatalog, run targeted+full via bundledPython
   optional localLupa, save logs ignoredbuild. Native compile/install/launch
   requires exact ownedpath; native capture/fixtures use only scene and verifiedPID.
   Read native APIs locally first; verify positive game effects and lifecycle,
   keep failed receipts; physical input only if supported actual channel.
5. One final critic after completed code/native subproject; fix factual findings.
   Update README/lessons/journal/usage/progress by actual scope, unresolved human/
   input/native conditions explicit. Commit exactownedfiles, push authorisedmain,
   check remoteSHA==HEAD and preserve `.freebuff`.

Commands: bundledPython unittest discoverC1manual/tests andC2return/tests;
node --test C2return/tests/manual-move.test.cjs;
bundledPython run_source_checks.py --jobs3 --timeout180;
progress update_progress.py then --check. Native commands separate from catalog.
