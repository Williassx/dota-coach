# Internal technical review packet — ранний ограниченный прототип

14 октября 2026. [Manifest](technical-packet-2026-10-14.json) описывает exact members,
bytes/SHA256, source/proof purpose и архив. [Упаковщик](../tools/build_review_packet.py)
читает исходники из библиотеки создателей и создаёт новый child build/dota_coach.
Не отправлено и не опубликовано. Архив не является устанавливаемой игрой.

Включены actual normal15/TEST18 source inputs, builder/path policy, проверки,
локальный guide, несент вопросы, десять actual R2 PNG и final normal UI3 PNG с native JSON/report.
Valve map/template/engine/VPK/compiled assets отсутствуют; сырые account logs,
модели/аудио, ключи и пользовательская .freebuff исключены. Screenshots являются
документальными proofs со штатным Dota содержимым, права на внешнее использование
не оценены. Принадлежность исходников проекту не заменяет договоры авторства/лицензию.

Recipe source outputs 15/18 повторно проверяются existing source verifier; flags false.
Архив проверяется чтением каждого member и его SHA256, exact membership и отсутствием
запрещённых путей/типов; этот процесс не компилирует/не устанавливает/не запускает Dota.
Фактическая native база отдельно: build25894101, R2 12 API phases PASS/10PNG; normal
compiled7 и TEST compiled9 описаны в исходном native evidence. Новая установка этим
review packet не выполнена. Пользовательский install и полный release pipeline открыты.

Буквальный критерий C1-12-03: «Выпуск имеет техническую проверку и применимые права;
перенос вне Dota отдельно разрешён». Exact internal source/archive integrity проверяется,
но основание распространения не установлено. Критерий выпуска **не выполнен**;
standalone права, оператор/территории, внешний installer, пользовательская приёмка и
решение о публикации открыты. Не обозначать technical archive готовым релизом.

[C2 guide](../../../../creator-2/12-release/03-release-guide/notes/prototype-local-guide-2026-10-14.md) ·
[Пакет демонстрации](../../../../creator-2/12-release/02-valve-presentation/notes/prototype-packet-2026-10-14.md).
