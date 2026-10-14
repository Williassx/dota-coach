# Проверка internal packet и проектный урок

Автор: технический исполнитель C2. Независимый reviewer ещё не назначен;
самопроверка не является peer approval или готовностью выпуска.

[Сохранённый результат](packet-validation-2026-10-14.json) содержит проверенные
локальные Markdown ссылки без отсутствующих targets, exact 38 archive members и
SHA256. Existing output сохранён; append corruption и extra file отклонены на
отдельной owned test copy, исходный архив не менялся.

Команда fresh verification: bundled Python `-X utf8`
`creators/creator-1/12-release/03-release-package/tools/build_review_packet.py --verify build/dota_coach/coach-review-packet-final3-20261014`.
ZIP перечитан по каждому member, CRC и canonical bytes. Сырой build output локален,
никакой upload/publication не выполнен. [Manifest](technical-packet-2026-10-14.json).

Повторение source guide: actual tests 8 PASS, fresh outputs
`build/dota_coach/coach-guide-normal-20261014` (15),
`build/dota_coach/coach-guide-test-20261014` (18), оба builder вызывают verifier.
Это source-only, не новая native установка. Native доказательства взяты из
existing R2/UI3 отчёта, не заменены этими checks.

Урок: initial archive prepare отказал `UI resource exceeds 1 MiB` до создания
выхода, поскольку actual paused/ready proof PNG больше UI limit. Причина —
ошибочное применение UI resource limit к документальным кадрам. Решение:
отдельный bounded PNG reader 8 MiB только для exact allowlisted proofs, с теми
же portable path/ancestor checks и PNG signature; существующий probe/UI policy
не изменён. Повторный build/CRC/byte verification подтвердил38 members окончательного scope.

Перед повторением учитывайте: source changes меняют canonical hashes, поэтому
старый архив не будет проверяться как current snapshot; сохраните его и создайте
новый output/manifest. Не добавляйте в allowlist engine/template или raw account logs.

Проверено на деле: после первого snapshot native JSON/MD дополнились основным
исполнителем; verifier отклонил current comparison. Initial архив сохранён,
последующий legal plan/review тоже изменились; оба прежних архива сохранены,
Создан final3 без evolving registry MD (отдельный реестр продолжает обновляться),
manifest содержит только fixed source/docs/proof snapshot текущей версии.
