# Source-проверка общего экрана вмешательства

[Подпункт](../README.md) · [План](../intervention-screen-plan.md).
Дата UTC2026-10-11. Основа3306834.

Canonical RosterPanels принимает optional owned projection; один stable rosterPort
использует existing private selection flow. Модель карточек/Requests не дублируется.
Standalone ID callback после reorder сохранён; integrated callback истекает при
repaint. Root reservation до discovery, all-node guard, busy/staging, guarded
plain writes, suspend/refresh и полная очистка добавлены в existing renderer.

Новый ScreenPanels явно связывает две distinct scopes с одним flow, suspend обеих
областей предшествует DTO getters; onSelection синхронизирует адресата без отправки.
Captured request actor не меняется при выборе другой карточки. Parent lifecycle
закрывает children/таймеры; partial bind не скрывает independently-owned child.
Общая сводка обновляется watcher0.25сек, не считается игровым clock/lease.

7 начальных RED→GREEN roster-port; 10 RED→GREEN group; 3 self-review RED→GREEN:
hidden required label, observer exception после repaint, summary после ACK timeout.
Причина observer gap: render менял generation, старый catch не закрывал текущего
владельца. Generation сохранён после успешного render; новый reentry всё ещё побеждает.
Новый suite20PASS; добавлены3 таймерных сценария к port suite.
Полная регрессия после исправления30suites/690PASS, skips/cancelled/todo0.
Логи сессии /tmp/intervention-screen-final-regression-0..29.log, сводка results.json.

Итоговый критик выявил потерю ACK expiry при suspend. В одной fix pass два RED→GREEN
и контроль уже принятого ответа: истечение сохраняется при suspended/busy, затем
применяется на refresh/конце mutation только к тому же pending ticket. Updating view
не теряет отложенное expiry. Accepted/new epoch не перезаписываются timeout.
Второй reviewer не запускался; после изменения кода повторена полная регрессия.
Actual fresh build/verify existing HUD13/12links и manual6/5links проходят:
probe-ui-20261011T075302Z-bf3d64 и probe-ui-20261011T075302Z-79c111;
compiled/runtime=false, установка не менялась.

Layout/recipe этой группы ещё следующий подпроект. Existing standalone/HUD/tests
сохранены. Native/gameplay/hittest/server authorization/manual input/lease/ИИ return,
общий server contract и другой человеческий владелец остаются открытыми.
