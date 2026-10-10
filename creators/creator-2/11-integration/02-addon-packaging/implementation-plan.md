# План раннего пакета HUD

> Использовать superpowers:executing-plans, TDD и пять read-only критиков;
> пользователь разрешил автономное продолжение до остановки.

**Спецификация:** [design.md](design.md) и [HUD](../../07-match-screen/01-own-cards/design.md).
**Стек:** Python3 stdlib, ES5 scripts без изменения, XML/CSS Panorama.

## 1. RED

**Создать:** tests/test_hud_bundle.py; после фиксации требований выполнить до реализации.

- [x] Проверить реальный полный graph/IDs/order/no demo и пустые состояния.
- [x] Проверить exact kind/source allowlist и сохранение probe policy.
- [x] Проверить output preservation/case collisions/tamper/current sources/report limits.

## 2. Минимальная подготовка

- [x] HUD src XML/manifest/CSS у C2-07-01 и bundle-manifest здесь, без auto-bind/data.
- [x] Foundation build/verify: второй fixed kind/policy, reportkind=manifestkind.
- [x] GREEN новых/прежних suites; actual build+verify новый child build/dota_coach.

## 3. Проверка и публикация

- [x] Пять направлений read-only; confirmed defects RED→GREEN.
- [x] Повторить baseline247, node syntax/XML/links/README, CLI/report hashes.
- [x] Docs/status/index/action log, start_skill только проверенные команды.
- [ ] Обычный fast-forward main, подтвердить remote SHA/clean tree.

Не объявлять этот пакет полной игрой, установленным аддоном или запущенным HUD.
