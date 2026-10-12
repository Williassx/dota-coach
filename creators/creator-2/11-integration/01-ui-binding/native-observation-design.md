# Native observation smoke

[Родитель](README.md) · [Existing design](match-observation-design.md).
Поручение продолжать автономно применяется к существующей source-композиции.
Ведущая роль75; история134, читаемость80, проверки114 и диспетчер173 — root.
Read-only API helper консультирует; root единственный автор файлов этой задачи.

Цель — actual Dota render/public API evidence двух existing private bindings.
Выбран отдельный test-only addon вместо production bootstrap или расширения HUD.
Fixed kind10outputs/9links/2canonical XML inputs остаётся неизменным по inventory.
Применяется урок18: anonymous canvas с прежним CoachMatchObservation внутри.
Composer строго проверяет новую outer shape; child scopes не переименовываются.
Альтернатива обёртки только в fixture оставила бы canonical layout некомпилируемым.

Fixture содержит retained generated canonical layout, derivative с одним TEST
driver/banner, свой manifest;12sources/11active resources +retained layout отдельно.
Сохраняются10canonical output hashes и12raw input hashes, включая2XML inputs.
Public API сценарии: bound empty, пять TEST opponents +presentation order, invalid
opponents с сохранением history, строго новая roster revision +invalid history,
dispose и fresh rebind. Closed handle должен отвергать DTO Proxy без inspection.
Source authorization/nativeConfirmed flags остаются false; accepted history label
не является серверным ACK, синтетический heroName не entity identity.

Приёмка smoke: targeted source tests, compile manifest/canonical/map, проверенные
installed hashes, phase predicates и actual PNG каждого этапа, own quit/PID gone.
При visual defect исправить canonical CSS и проверить fresh addon/launch.
Границы: physical input, общий игровой HUD, C1/реальные источники/clock/identity,
серверная авторизация/эффекты и человеческая проверка не закрываются.
