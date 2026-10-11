# План локального предложения действий

[Родитель](README.md) · [Спецификация](design.md).
Root выполняет inline `superpowers:executing-plans`, без дополнительных исполнителей.

1. Node VM tests до JS: frozen actor/reset/second click, move bounds/no coercion,
   ready target→attack/last_hit/deny, allied hero/hidden/dead/no identity leak,
   exact DTO/accessor/symbol/extra fields, copied projection, clear-before-traps,
   reentry/reset/dispose/closed guards. RED missing module.
2. Единственный pure JS в src/panorama/scripts/custom_game, GREEN. Ни native
   mouse hook, ни sender, ни server permission/lease/remaining-time не добавлять.
3. Новый Node suite в каталоге, полный runner; один reused final critic готового
   подпроекта, замечания воспроизводить и исправлять. Full повторять лишь при новом коде.
4. API/README/report/UTC journal/progress/usage/draft, обязательные документные
   проверки, guarded normal main publication и remote/clean verification.

Все материалы изначально в C2-05-02. C1 и shared contract не изменяются.

## Исполнение

Шаги 1–2: 16 RED missing module → 16 GREEN, затем meaningful real Targets.view/
expiry test → 17 PASS. Шаг 3: catalog добавлен, targeted 53 PASS, full 43 / 915 PASS,
один reused final critic без существенных замечаний. Шаг 4: документация/журнал/
graph 42/209 (20.1%)/usage/draft обновлены. Документные проверки и guarded normal
push выполняются перед публикацией; remote SHA и clean подтверждаются выводом
задачи и Git, без отдельного commit ради собственного хеша.
