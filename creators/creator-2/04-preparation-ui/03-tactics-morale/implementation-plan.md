# Черновик тактики и поддержки — план

> Для агента: superpowers:executing-plans и TDD; основной агент пишет source,
> пять критиков read-only. Автономное продолжение разрешено пользователем.

**Цель:** сохранить явные локальные намерения тактики/разговора без ложного эффекта.
**Архитектура:** pure frame→model→copied view/draft, reuse полного C2-04-02 draft.
**Стек:** ES5, Node VM/node:test. **Spec:** [design.md](design.md).

## Ограничения и фокус

Exact5 assignments/team; до8options на группу; все strings plain bounded, no autochoice.
Неверный состав, исчезновение option, sameversion intent change, newer getter и
invalid reset/recovery не должны оживить старые выборы. Staging не выдаёт draft.

## 1. Модель

**Создать:** tests/preparation.test.cjs, src/panorama/scripts/custom_game/preparation_state.js.
**Consumes:** update({revision,lineup,plans,talks}); lineup — exact complete hero draft.
**Produces:** DotaCoachPreparation.create() API из design.md.

- [x] Написать explicitselection/copy/noop/counters/empty/sourcewarnings tests.
- [x] Написать lineup exactschema/conflict, update retention/reset/invalid/highwater,
  sameversion intent и getter newer/dispose/ownKeys/length/staging tests.
- [x] `node --test creators/creator-2/04-preparation-ui/03-tactics-morale/tests/preparation.test.cjs`: RED missing source.
- [x] Implement create/update/choosePlan/chooseTalk/removePlan/removeTalk/clear/view/draft/dispose/isDisposed → GREEN.
- [x] Пять критиков: concrete defects reproduce RED→GREEN; source boundaries review.

## 2. Проверка и фиксация

**Создать:** notes/preparation-copy.md, reports/cloud-preparation.md и README каталоги.
**Modify:** README подпункта/раздела/PLAN/AGENTS, action log отдельно; start_skill partial.

- [x] Повторить прежние403 и новые сценарии; syntax/links/README/diff.
- [x] Записать реальные результаты, limits, пять verdicts и config readback.
- [x] Commit/fast-forward main, remote SHA совпадает/clean: a882841.

Реальные C1 правила, эффекты, native/panel/server, второй владелец остаются открытыми.
