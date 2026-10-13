# Проверки поведения диагностической панели

[Подпункт](../README.md). Node.js 18+ и встроенные node:test/vm, без npm-пакетов.
Исполняются настоящие игровые JS; только GameEvents, Panel и Schedule заменены
моделью недоступного движка. Это не рендеринг, компиляция Source 2 или сервер Lua.

```sh
node --test creators/creator-2/01-foundation/02-panorama-capability/tests/*.test.cjs
```

Проверки упаковки используют Python 3.9+ и реальные временные файлы:

```sh
python3 -m unittest discover -s creators/creator-2/01-foundation/02-panorama-capability/tests -p 'test_*.py' -v
```

Для проверки готового пакета агент задаёт DOTA_COACH_PROBE_ASSET_ROOT равным
его абсолютному content/panorama и выполняет ту же команду Node. По умолчанию
проверяются единственные исходники из библиотеки.

Python-набор включает проверки сборщика и read-only CLI готового пакета.
Последние исполняются в реальном временном checkout с копиями инструментов;
они проверяют и отсутствие новых/изменённых файлов после успеха и отказа.

[Native ping fixture](native-ping/README.md) · [Builder tests](test_native_ping_fixture.py); source/VM/pureLua не native acceptance.
