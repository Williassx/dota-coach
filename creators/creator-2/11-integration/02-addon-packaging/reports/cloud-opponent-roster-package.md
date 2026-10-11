# C2-11-02 — source-пакет публичного состава

[Родитель](README.md) · [Команды](../notes/opponent-roster-package.md).

Дата UTC: 2026-10-11. База: 3885746. Исполнитель: root/создатель 2.
Восьмой fixed kind `panorama_source_opponent_roster`: пять ресурсов, четыре
resource links. Канонические исходники C2-07-02 не копируются в другую библиотеку.
Добавлены только inert loader, recipe, отдельный validator и trusted dispatch;
общий XML parser/portable paths/builder/verifier/handoff переиспользованы.
Panel.visible разрешён локально, прежние defaults и виды пакетов сохранены.

Проверки до реализации: 8 сценариев, 4 ERROR unsupported kind и 4 guard PASS.
После: все 8 GREEN. Целевые три набора: 132 PASS; packaging 90, foundation 28,
handoff 14. Full canonical runner: 41 suites / 875 PASS, fail/skip/cancel/todo = 0.
Логи: `build/dota_coach/source-checks-20261011T124152Z-e3a040/source-checks.json`.

Actual CLI создал `build/dota_coach/probe-ui-20261011T124143Z-795841` и companion
снаружи пакета. Проверено 5 assets / 4 links, Git 3885746, dirty=true на момент
подготовки. installation_performed=false, native_destination=null, все native
checks=not_run. Source2/runtime flags false. Отчёт не редактируется вручную.

Actual packaged XML и два JS загружены в один NodeVM: explicit bind, plain имя
с символами разметки, unknown hero/slot, extra health getter не прочитан, invalid
очищает данные, stale не восстанавливает их, более новый empty roster готов,
dispose скрывает root и очищает подписи. Запрещён доступ к game API.
Сверены все 8 экранов handoff registry, старые сценарии также прошли.

Самостоятельный просмотр проверил точный порядок и принадлежность полей каждого
слота, строгие атрибуты/пустые тексты, source hashes, output preservation и отсутствие
нового installer/bootstrap/transport. Один повторно используемый финальный критик
завершил проверку: существенных замечаний нет. Новых агентов или повторного ревью нет.

График создателя 2: 39/206 действий (18.9%); это выполнение чеклиста, не готовность
игры. Cloud draft revision 42 сохранён и проверен чтением: 41/875 и восемь вариантов
пакетов, прочие поля сохранены. Draft не активирован; callable publish отсутствует.

Открыты: настоящий C1 публичный источник и его авторизация, общий HUD/bootstrap,
Windows compile, внешний вид/читаемость/hittest в Dota, server/runtime и проверка
второго человеческого владельца. sourceAuthorizationConfirmed=false.
