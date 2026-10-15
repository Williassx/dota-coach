# Локальный DEM importer v1

[Подпункт](../README.md) · [согласованный план](../telemetry-import-implementation-plan.md).

Импортёр читает существующий plain `PBDEMS2` DEM на Windows. Он не скачивает файлы, не запускает Dota и не обучает игрока. Профиль схемы пока проверен для одного replay9042986015/Storm Spirit; другой actor/class/patch может получить отказ2. Доступность данных игроку/fog и семантика control bits не подтверждены.

## Подготовка runtime

Требуются Python3.12, локальный Temurin21.0.12.1+1 и восемь уже полученных JAR из [lock](dem-dependencies-v1.json). JDK `release`, `java.exe`, `javac.exe` и всеJAR проверяются поbytes/SHA. Никаких network/install действий в CLI. В текущем checkout они уже подготовлены в ignored `build/dota_coach/replay-9042986015/telemetry-spike/`.

Config — локальный JSON `dem-import-config-v1` с обязательными ключами `java_home`, `jar_directory`, `fields`, `episode_windows`, `limits` и `schema`. Пример значений:

```json
{
  "schema": "dem-import-config-v1",
  "java_home": "D:/AI/dota2coach/build/dota_coach/replay-9042986015/telemetry-spike/jdk/jdk-21.0.12.1+1",
  "jar_directory": "D:/AI/dota2coach/build/dota_coach/replay-9042986015/telemetry-spike/deps",
  "fields": ["raw_position", "raw_control"],
  "episode_windows": [{"id":"ordinary", "start_demo_tick":10000, "end_demo_tick":10060}],
  "limits": {}
}
```

`limits={}` использует точные defaults плана; любой override должен быть положительным целым. Полный dump чужих entities/chat не предоставляется. `fields=[]` сохраняет required actor/resources/clock; optional raw channels отключены. Окна inclusive поdemo tick, uniqueid; пересекающиеся интервалы получают общую запись с несколькимиwindowids. Пустой список оставляет только общий компактный индекс.

## Воспроизводимая локальная компиляция

Runtimeclasses/compile-receipt не хранятся вGit. Следующий Python fragment запускается из корня репозитория; `local_config`, `local_dem`, `new_output` передаются исполнителем как реальные локальные Path. В текущем checkout build уже имеется: проверка не перезаписывает его. Для изменения Java исходников сначала сохранить старый **собственный** build отдельно; чужой/неизвестный каталог не удалять.

```python
import hashlib, json, os, subprocess, sys
from pathlib import Path
base = Path('creators/creator-1/05-match-data/03-replay-normalization').resolve()
sys.path.insert(0, str(base/'src'))
from dem_inputs import BUILD, checked_path, validate_inputs, sha256
from dem_types import InputSpec
from dem_store import prepare_runtime
# Выполняется после проверки/создания своих BUILD parent directories.
ctx = validate_inputs(InputSpec(local_dem, 9042986015, 70388657,
    base/'notes/dem-dependencies-v1.json', local_config, new_output))
if (BUILD/'compile-receipt.json').exists():
    prepare_runtime(ctx)
else:
    checked_path(BUILD)
    classes = BUILD/'classes'
    classes.mkdir(exist_ok=False)
    env = {k:v for k,v in os.environ.items() if k.upper() not in
           {'JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'}}
    sources = sorted((base/'src').glob('*.java'))
    subprocess.run([str(Path(ctx.runtime['java_home'])/'bin/javac.exe'),
        '-proc:none', '--release', '21', '-cp', os.pathsep.join(ctx.runtime['jars']),
        '-d', str(classes), *map(str,sources)], check=True, timeout=60, env=env)
    receipt = {'schema':'dem-compile-v1', 'sources':{p.name:sha256(p) for p in sources},
        'classes':{p.name:sha256(p) for p in classes.glob('*.class')},
        'lock_sha256':ctx.hashes['lock'], 'options':['-proc:none','--release','21']}
    (BUILD/'compile-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    prepare_runtime(ctx)
```

Текущая реализация даёт восемь runtime classfiles; test compile может добавить девятый. Receipt фиксирует точный состав и hashes, CLI отвергает добавленные/заменённые classfiles. Ordinary Python tests не компилируют Java, не запускают DEM, Dota или сеть.

## Запуск и приёмка

CLI: `python creators/creator-1/05-match-data/03-replay-normalization/src/import_dem.py --input VERIFIED.dem --match-id 9042986015 --account-id 70388657 --lock creators/creator-1/05-match-data/03-replay-normalization/notes/dem-dependencies-v1.json --config LOCAL.json --output NEW_DIR`.

NEW_DIR не должен существовать, кроме полностью совпадающего проверяемого кэша. Родитель должен уже существовать; UNC/reparse paths отвергаются. В текущем checkout используется bundled Python, указанный в плане. Повтор на том же output сверяетreceipt digest, provenance, все output hashes и raw record counts; Java не запускается. Иной input/config/source/runtime требует другого NEW_DIR; существующие файлы сохраняются.

Результат: states/events/gaps JSONL, episodes.json, optional windows.jsonl иreceipt.json. Digest квитанции выявляет её несогласованное изменение, **не является подписью или доказательством прав**. Stage/diagnostic/failure каталоги — уникальные sibling; они сохраняются для проверки. Таймаут/лимит/повреждение не публикуют completed output. Receipt публикуется последним и переносится вместе сownedstaging через Windows no-replace rename.

Exit0 — завершённое scoped извлечение/cachehit;2input/lock/schema;3identity;4required clock/data;5integrity/IO;6limits/timeout. JSONstdout не утверждает модель/сходство/нативную игру. Control state/rawlife_state остаются числами/uint64string; именованные события остаются candidate_name_only, не подтверждёнными приказами игрока.

Обычная проверка: `python -m unittest discover -s creators/creator-1/05-match-data/03-replay-normalization/tests -p 'test_*.py' -v`. JavaCore main suite и real golden checker запускаются явно по плану. Для общего каталога дочерним Python нужны process-local `PYTHONUTF8=1` и существующий optionalLua `PYTHONPATH`; отсутствие этой зависимости/Windows privileges должно оставаться видимым пропуском.

Приёмка и ограничения: [отчёт04](../reports/04-local-dem-import/README.md). Три old exact HUDpoints проверяются только для соответствующих DEMhash/account; весь импорт и другие матчи остаются native_verified=false.
