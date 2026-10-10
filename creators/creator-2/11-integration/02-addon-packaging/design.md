# Пакет исходников общего HUD

**Связанная спецификация:** [общий шаблон](../../07-match-screen/01-own-cards/design.md).
Пользователь разрешил автономное продолжение. Выполняем раннюю упаковку UI source,
не полный addon build/runtime и не установку. Зависимости C2-11-01/C2-10-01 открыты.

## Один источник и политика

Новый bundle-manifest.json kind=panorama_source_hud содержит12 ресурсов: три новых
XML/CSS и девять JS из собственных библиотек C2-02-01/02/03,C2-03-02/03.
Source→content/panorama target — явное соответствие; никаких game/VPK/map/server files.
JS implementations не копируются в src другого подпункта. Только build output копирует bytes.

Повторное создание build/verify helper дублировало бы уже проверенные ограничения.
Расширяем существующие foundation helper точной второй политикой kind=panorama_source_hud
с точным фиксированным набором12 соответствий source→target: prefixes сами по себе
допустили бы demo или произвольное переназначение ресурса. Старый kind=panorama_source_probe сохраняет прежнюю
ограниченную policy/defaultmanifest. Произвольные prefixes/kind не разрешаются.
Manifest не может расширить policy или изменить mapping самостоятельно. Существующие команды --manifest
выбирают новый явно указанный manifest; новые CLI wrappers не требуются.

Build сохраняет bounded source/manifest/path checks, Windows casefold collision,
symlink/reparse rejection и exclusive новый child build/dota_coach. Source2_compiled/
runtime_verified=false. Report kind совпадает с manifest; verifier сравнивает полный
набор текущих bytes/hash/metadata и XML graph, rejects missing/unexpected/tampered files.
HUD graph дополнительно требует manifest→coach_hud и достижимость всех12 ресурсов,
девять scripts в dependency order, один стиль и отсутствие onload/run/bootstrap
в XML. Probe graph semantics не меняются. Нестроковый kind даёт ValueError/CLI2.
Установка и существующие output сохраняются. No dependencies/network/config secrets.

## Проверки

До code новые Python tests: current HUD graph/scopes/order/no demo, kind/sourcepolicy,
default probe unchanged, Windows collision, out-of-output/overwrite rejection,
tampering/source mutation/unexpected entries/report false runtime/XML missing resource.
Отдельный output создаётся и проверяется фактическими CLI после GREEN.
Это source integrity, не native Dota или серверный smoke test.

README/notes/reports и отдельный action log объясняют native limitations;
пять read-only критиков рассматривают дизайн и исправления. Равноправный второй
владелец, Tools/clock/identity/hittest и общий контракт остаются открытыми.
