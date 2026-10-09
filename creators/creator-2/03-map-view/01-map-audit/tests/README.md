# Проверки файловых доказательств

[Подпункт](../README.md) · [Отчёт](../reports/cloud-map-audit.md)

[test_inspect_map_workspace.py](test_inspect_map_workspace.py) создаёт синтетические
файлы во временных каталогах, а не загружает оригинальные материалы Dota.
Проверяются map/addon/archive категории, сохранность байтов, SHA и лимиты,
Steam association/комментарии/дубликаты/размер manifest, links/reparse/special files,
изменение файла, частичный отчёт, CLI/output и кириллица при CP1252 stdout.

```sh
python3 -m unittest discover -s creators/creator-2/03-map-view/01-map-audit/tests -v
```

Python 3.10+. В Linux все сценарии выполнены без пропусков. На Windows FIFO
не создаётся; symlink без доступной привилегии и длинные пути при WinError 206
отмечаются пропусками с причиной. Такие пропуски не являются проверкой этих условий
на Windows; реальная установка/движок этой suite не запускаются.
