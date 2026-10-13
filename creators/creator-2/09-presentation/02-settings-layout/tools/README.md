# Explicit preparation capture

[Подпункт](../README.md) · [План](../implementation-plan.md).

[capture_preparation.py](capture_preparation.py) наблюдает заранее запущенный own
TEST-клиент по свежему receipt в `build/dota_coach/preparation-scale-SIZE-20261012-owned.json`.
Receipt содержит addon/log/pid/start_utc_ticks; exact PID/name/UTCticks проверяются
перед каждой VConsole командой. Script не запускает Dota, не закрывает клиент и
не меняет постоянные настройки. Это explicit diagnostic, не ordinary suite.

Допустимые SIZE:1600x900/1024x768. В HERO_SELECTION два TEST-запроса создают Axe;
затем шесть фаз существующего драйвера сохраняются в actual PNG/UTC/hash metadata.
Несовпадение actual dimensions сохраняет failed capture и прекращает проверку.
При ошибке root отдельно выполняет guarded quit собственного PID и проверяет gone.

```powershell
& 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' creators/creator-2/09-presentation/02-settings-layout/tools/capture_preparation.py --run 1600x900
```

Launch использует сохранённый проверенный addon `dota_coach_c2_preparation_r1_20261012`:
`-game "…/game/dota" -steam -addon ADDON -novid -windowed -w WIDTH -h HEIGHT
-console -dev -insecure -vconsole -vconport 29000 -con_logfile "FRESH_LOG"
+dota_launch_custom_game ADDON template_map` через Start-Process -WindowStyle Hidden.
Перед launch: отсутствие любого dota2, fresh receipt/log, source/compiled/map hashes.
Actual launch arguments и exact owned PID/time сохраняются в receipt.

Для отдельного возобновления: `--run 1024x768 --date 20261013 --attempt r2`.
Prefix получает `1024x768-r2-20261013`; PNG имеют настоящую дату нового capture.
Старые outputs сохраняются. Date/attempt валидируются до чтения receipts/writes;
дефолтная дата20261012 сохраняет исходный run format. После обновления build добавить
`--addon dota_coach_c2_preparation_scale_r2_20261013` для новой скомпилированной fixture.
Exact allowlist не принимает произвольный addon. Query/identity subprocess
ограничены10s, phase polling420s; импорт не активирует Dota или capture.
