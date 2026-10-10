# Отдельная панель предматчевого черновика

[Подпункт](../README.md) · [Дизайн панели](../panel-design.md) · [Модель](team-draft.md).

`DotaCoachTeamPickerPanels.bind(root)` получает root из team_picker.xml и явно
создаёт модель; загрузка двух scripts не запускает panel. Методы update(snapshot),
choose(id), remove(id), clear(), draft(), dispose(), isDisposed(). Схема snapshot
остаётся частной схемой модели. Без submit callback/network/storage/server confirmation.

Пять кандидатов на страницу, до 13 страниц/64 профилей; пять выбранных записей
показывают версии и предупреждения. Synthetic/unverified model/source/coverage видны
до выбора. Hint объясняет добавление, уже выбранную запись или лимит. Выбранный slot
явно говорит «Убрать из черновика». Clear снимает все. Page navigation не меняет draft.

Смена страницы/каталога делает старые handlers недействительными. Generation меняется
до чтения DTO getters, поэтому старый candidate handler внутри revision getter не
отменяет новый каталог. Old remove не действует на новую версию того же id.
При пустом каталоге ноль страниц, стрелки и clear отключены; 1/0 не появляется.

Один owner root, explicit cleanup и watcher 0.25s только lifecycle. Все required
panels проверяются до update/handlers/draft, даже скрытые/offpage. Destroy/error
делает draft null, очищает labels/buttons, отменяет timer до release root. После
rebind старые callbacks не меняют новый panel. Все внешние texts html=false.

XML имеет собственный root и two-script graph, без custom_ui_manifest, bootstrap,
assets/картинок или включения в match HUD. Контейнеры списков source CSS scrollable,
карточки fit-content. Граф/ids/style проверены как source; размер, перенос строк,
scroll/hittest, разрешения и совместимость CSS проверяются в native Tools позже.

```sh
node --test creators/creator-2/04-preparation-ui/01-team-picker/tests/team-picker-panel.test.cjs
python3 -m unittest discover -s creators/creator-2/04-preparation-ui/01-team-picker/tests -p 'test_*.py' -v
```

C1-07-01, реальные профили/identity, roles/heroes/server и второй владелец открыты.
Complete — только local count5; запуска матча нет.
