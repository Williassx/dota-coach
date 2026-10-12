# Ограниченная native проверка mouse targeting

[Родитель](README.md). Пользователь поручил продолжать самостоятельно по плану.
Ведущая роль76, root — единственный автор; helper сверяет API read-only.

Существующая группа Targets/MouseProposalPanel требует actual native bind evidence.
Проверка не подключает мышь или отправку действий: explicit API вызовы используют
TEST actor/targets и управляемый локальный clock, maxAgeMs1000. Это проверяет
переходы TTL при заданных значениях времени, не настоящий серверный deadline.

Отдельная fixture сохраняет fixed mouse-targeting7assets/6links. Canonical source
layout/четыре определения подготавливаются через существующую guarded policy; test-only
derived layout добавляет driver и literal status label вне MouseProposalRoot.
Девять outputs: семь canonical за вычетом manifest плюс own manifest, driver,
derived layout. Retained canonical layout также компилируется отдельно.

Восемь actual API фаз: bound, attack, captured-switch (last_hit затем deny), expiry,
move, recovery (invalid до valid), disposed, rebound. Смена цели не переиздаёт
действие; captured actor A нельзя заменить B без reset. Move сохраняется при
hidden/stale source, target action снимается при invalid/TTL. Старые API после
dispose не читают Proxy DTO и не меняют fresh bind. Literal HTML-like label остаётся
html=false. Все три authority flags false в группе/панели.

Альтернатива — сразу physical mouse/world mapping — зависит от native hook,
identity/permission/lease/C1; неподтверждённые зависимости не подменяются TEST DTO.
Приёмка этого этапа: bounded builder refusal tests, existing binding tests,
компиляция/хеши, fresh launch/восемь кадров, обзор фактического UI, required full
source regression, собственный quit, один final critic и документы/публикация.
Native product/input/AI-return/human second owner/common HUD/map остаются открытыми.
