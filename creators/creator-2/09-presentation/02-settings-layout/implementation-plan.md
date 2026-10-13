# План проверки preparation scaling

**Цель:** измерить существующую TEST-сцену при1600×900 и1024×768.
**Спецификация:** [design.md](design.md). Исполнение root в текущем checkout.
**Среда:** Windows/Source2, существующий VConsole helper, bundled Python/Pillow.

- [x] Сверить исходный HEAD/clean, build_id25845666, отсутствие dota2;
  проверить17sources/18raw inputs/17compiled/map исторического addon.
- [x] Создать explicit capture helper в tools: fresh run id, bounded420s,
  HERO_SELECTION перед каждой из двух TEST команд, шесть фаз/PNG/hash/dimensions.
  Не включать его в ordinary source catalog; запуск требует отдельной команды.
- [x] Собственный launch через Start-Process -WindowStyle Hidden, прежние flags
  и новый -w/-h. Fresh console/receipt с PID/start UTCticks; сохранить команды.
- [x] На каждом размере capture/осмотр6кадров, native phase predicates и scroll
  geometry; quit только exact owned PID/start, проверить gone/Steam preserved.
- [x] Проверить helper AST, required source checks и неизменность canonical hashes;
  написать отчёт с раздельными API/visual/physical/product результатами.
- [x] Один final critic, lessons при новом знании, usage/journal/resume, progress
  только по полным критериям; подготовить обычную публикацию.
  Commit/push и сверка remote HEAD выполняются последними командами;
  commit самой записи доступен из Git history, без вставки собственного хеша.

Review focus: фактический размер вместо flags; обрезанные колонки/текст;
API bottom вместо ненулевого scroll; неуправляемый ввод; чужой PID и старые receipts.
Не делать повтор compile без изменения источников или рассогласования hashes.

Возобновление13октября:1600×900 завершено12октября, второй запуск остановился
до первой preparation-фазы; old PID отсутствует, прежняя tool session недоступна.
Причина остановки native процесса не установлена. Сохранить старый log/receipt;
повторить1024×768 только с новым attempt/date и fresh outputs, не перезаписывать run.
Actual build25894101 потребовал нового isolated addon/compile, completed1024×768
не присвоен старому runtime. [Фактические результаты](reports/preparation-scaling-2026-10-13.md).
