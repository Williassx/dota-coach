# План локального экрана карточек и запроса

[Спецификация](intervention-screen-design.md). Inline, журнал00-action-log.

1. RED tests actual roster panel/flow port: один source, select/clear, stale handler,
   busy getter/required node/duplicate owner/dispose. Добавить rosterPort и optional
   adoption в canonical roster_cards.js, сохранить старый standalone suite.
2. RED tests actual two-panel bind: click→same recipient, captured actor after
   selection, staging before getters, source loss/partialbind/rebind/timers/ACK.
   Добавить intervention_screen_binding.js, required guard и public wrappers.
3. Targeted suites, затем full source regression, один final critic/fix pass.
   Отчёт/индексы/checkbox/генерация progress, whitespace/links, commit/push main.
   После публикации продолжить inert composition recipe отдельным подпроектом.

Commands: node --test creators/creator-2/11-integration/01-ui-binding/tests/intervention-screen.test.cjs;
node --test creators/creator-2/02-coach-interface/01-roster-cards/tests/roster-cards.test.cjs.
Expected: новый test сначала RED, после implementation GREEN; прежние suites GREEN.
