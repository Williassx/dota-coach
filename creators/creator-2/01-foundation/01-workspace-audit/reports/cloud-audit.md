# Облачная проверка C2-01-01

Дата: 9 октября 2026 года. Исполняющая среда: Linux, `/workspace/dota-coach`,
Python 3.12.14, Git 2.52.0. Проверен исходный HEAD
`f1494d705312ae9bd380452404d7befad5161a88` плюс изменения данного подпункта.

| Проверка | Фактический результат |
|---|---|
| C2 unittest до реализации | 8 сценариев RED: помощник отсутствовал |
| C2 unittest после реализации и расширения | 13 сценариев GREEN; пропущенных нет |
| Глубокое дерево | Сбой рекурсивного обхода воспроизведён тестом, итеративное исправление прошло тот же тест |
| Существующий обследователь C1 | 8 сценариев GREEN; чужие исходники не изменены |
| CLI C2 на облачном клоне | Код 0, корректный JSON, origin соответствует проекту |
| Инвентаризация Steam/Panorama в облаке | Steam roots и установки не найдены; runtime_verified=false |
| Windows-клон | Наличие подтверждено пользователем; отсюда не обследован |
| NTFS reparse points | Флаг проверен имитацией lstat; реальный junction на Windows не проверен |
| Нативная панель, Lua ping, компиляция | Не выполнялись |
| Документация и примеры | 726 локальных ссылок без ошибок; три JSON разобраны, корреляция успешного ответа проверена |
| Границы отдела и отчёты | Файлы создателя 1 не изменены; Windows-local.json исключён из Git |

Команды из корня:

```sh
python3 -m unittest discover -s creators/creator-2/01-foundation/01-workspace-audit/tests -v
python3 -m unittest discover -s creators/creator-1/01-foundation/01-environment-audit/tests -v
python3 creators/creator-2/01-foundation/01-workspace-audit/tools/inspect_ui_workspace.py
```

Каталоги и ресурсы Dota не изменялись; диагностика не вызывает сеть/игру.
Cloud CLI не является проверкой Windows и не закрывает C2-01-01.
Локальный шаг: [windows-start.md](../notes/windows-start.md).
