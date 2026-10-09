# C2-01-02: план упаковки исходников

**Спецификация:** [packaging-design.md](packaging-design.md).
Архитектурный критик рассмотрел границы; требования осуществимости по переносимым
путям и выходным предкам внесены до кода. Поручение пользователя — автономная работа.

## Файлы и интерфейсы

- `bundle-manifest.json`: schema_version=1, kind=panorama_source_probe, assets с source/target.
- `tools/build_probe_bundle.py`: Python 3.9+; `build_bundle(repository: Path, manifest: dict, output: Path) -> dict`.
- CLI: `--repository`, `--manifest`, `--output`; выход только новый child build/dota_coach.
- `tests/test_build_probe_bundle.py`: реальные временные деревья и ошибки записи.
- `tests/probe.test.cjs`: необязательный DOTA_COACH_PROBE_ASSET_ROOT для проверки пакетных JS;
  исходная проверка остаётся по умолчанию.
- `reports/source-bundle.md`: фактические результаты, хеши и открытая нативная приёмка.

## Порядок

1. Создать тесты RED без сборщика: идентичность байтов, существующий выход,
   отсутствующий файл, выходящие/непереносимые пути, коллизии иерархии/регистра,
   source/output ссылки, reparse flag, превышение бюджета, неполная запись.
2. Реализовать проверки всего manifest и ограниченное чтение до создания выхода.
   Проверить lstat на существующих исходных/выходных предках; данные не перезаписывать.
3. Создать manifest пяти текущих UI-ресурсов и сборщик; отчёт записать последним.
4. Подтвердить GREEN командой из корня:

```sh
python3 -m unittest discover -s creators/creator-2/01-foundation/02-panorama-capability/tests -p 'test_*.py' -v
```

5. Собрать настоящий пакет командой:

```sh
python3 creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py
```

6. По JSON результата получить output. Проверить все SHA-256 и ссылки XML внутри
   output/content/panorama; выполнить существующие 16 JS сценариев из этих ресурсов:
   передать абсолютный output/content/panorama в DOTA_COACH_PROBE_ASSET_ROOT и
   вызвать `node --test creators/creator-2/01-foundation/02-panorama-capability/tests/probe.test.cjs`.
7. Рассмотреть код пятью критиками, исправить подтверждённые проблемы и сохранить в main.

Windows/Tools/Lua не запускаются; bundle не является полноценным аддоном. C2-01-02
остаётся открыт до нативной приёмки и другого владельца. Сборочный каталог игнорируется;
в Git сохраняются manifest, сборщик и резюме, а не редактируемая копия пакета.
