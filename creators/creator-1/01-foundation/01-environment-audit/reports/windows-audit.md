# C1-01-01: Windows-аудит

Фактический запуск локального обследования 13 октября 2026 года. Сырой JSON:
локальный файл `reports/windows-local.json` (исключён из Git; перегенерируется
командой ниже). Обследование — только чтение: Steam/Dota и пользовательские файлы
не изменялись.

## Выполненная команда

```bash
python creators/creator-1/01-foundation/01-environment-audit/tools/inspect_environment.py \
  --repository . \
  --output creators/creator-1/01-foundation/01-environment-audit/reports/windows-local.json
```

## Подтверждённые факты

- ОС: Windows; Python 3.14.7 (>= 3.9), Git 2.55.0.windows.5.
- Клон: `D:\AI\dota2coach`, ветка `main`, HEAD `99555eb...`, origin соответствует
  Williassx/dota-coach; 6 несохранённых записей рабочего каталога сохранены без изменений.
- Steam-корень (реестр): `C:\Program Files (x86)\Steam`; вторая библиотека
  `D:\SteamLibrary` подключена, но манифест Dota там отсутствует.
- Dota 2 (appmanifest 570) в первой библиотеке: build_id **25894101** (это тот же
  билд, который создатель 2 фиксировал 12 октября как «new build»), путь
  `C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta`.
- Каталоги существуют: `game\dota_addons\` и `content\dota_addons\`.
- Шаблон Tools на месте: `game\dota_addons\addon_template\` содержит `addoninfo.txt`,
  `scripts\`, `resource\`, `materials\`, `particles\`.
- Исполнитель игры: `game\bin\win64\dota2.exe` присутствует. Отдельный `dota_ugc`
  каталог не найден; `game\bin\` содержит только декларации (`sdkenginetools.txt`),
  отдельного исполнителя Tools в нём нет.
- В обеих папках `game/content\dota_addons\` установлено по 25 аддонов
  `dota_coach_c2_*` — следы проверок создателя 2, к обследованию не относятся.

## Непроведённые проверки (не заявлять выполненными)

- Запуск Workshop Tools (`dota2.exe -tools` или через Steam) не выполнялся:
  `workshop_tools_runtime: not_verified` в JSON. Примеры `*.mdmp` в `game\bin\win64\`
  датированы 2024 годом — это следы прошлых падений клиента, а не проверка Tools.
- Загрузка шаблона в редакторе, серверный лог Lua, события Panorama и управление
  героем — предмет следующих подпунктов (C1-01-02 и далее).
- Отсутствие `dota_ugc` записано как факт каталога; его причину не устанавливали.

## Что это открывает

Техническая база для C1-01-02 (проверка аддона на одном герое) подтверждена на
уровне установки: build_id 25894101 одинакова с фиксацией создателя 2, шаблон и
обе папки аддонов существуют. Следующий шаг подпункта — передача резюме второму
создателю для рассмотрения; запуск Tools не входит в C1-01-01.
