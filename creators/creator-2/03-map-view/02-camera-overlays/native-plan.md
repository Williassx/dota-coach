# План выполнения native camera smoke

1. Подготовить exact TEST manifest/driver; помощник проверяет fresh-output boundaries,
   canonical hashes/subtree, deterministic15outputs, executable manifest refusal.
   Его RED missing-builder сохранён; выполнить GREEN после появления входов.
2. Собрать TEST-only bundle в fresh ignored build. Проверить JS, existing27 VM и
   новый Python suite; добавить suite в общий каталог.
3. В свежем addon установленной Dota компилировать manifest, retained canonical HUD
   и template_map. Записать compiler results, build_id, source/compiled hashes.
4. Запустить собственный клиент; только в наблюдаемом HERO_SELECTION выбрать Axe.
   Driver ожидает живого realhero своей команды. Проверить семь API фаз, получить
   engine screenshots и осмотреть все кадры. Ошибки сохранять и исправлять по причине.
5. Закрыть собственный PID через quit; сохранить отчёт с фактическими ограничениями.
   Выполнить required source regression и docs checks. Один итоговый critic при
   доступном агенте; его лимит/недоступность честно записать, не считать human review.
6. Обновить PROGRESS/resume/action lessons/usage с null неизвестными расходами;
   после проверок опубликовать обычный commit без перезаписи чужих изменений.
