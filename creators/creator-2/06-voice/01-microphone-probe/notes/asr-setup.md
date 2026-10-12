# Воспроизведение ASR-пилота

[Заметки](README.md) · [Спецификация](../asr-design.md) · [Результат](../reports/offline-asr-2026-10-12.md).

Python3.12.14; все зависимости, модель и cache локальны в ignored `build/dota_coach/asr-pilot-20261012`. На новом checkout эти файлы отсутствуют. Команды ниже загружают программные пакеты/модель из сети. Исходное аудио не является частью загрузки. Existing directories не переиспользовать для иных проектов.

## Установка и совместимость

```powershell
$env:PIP_DISABLE_PIP_VERSION_CHECK='1'
python -m pip install --only-binary=:all: --no-cache-dir --target build/dota_coach/asr-pilot-20261012/deps faster-whisper==1.2.1
python -m pip install --only-binary=:all: --no-cache-dir --no-deps --target build/dota_coach/asr-pilot-20261012/deps-av18 av==18.0.0
```

Оригинальный deps с PyAV19 сохранён как evidence ошибки. Probe добавляет deps-av18 раньше deps в sys.path: фактические av module/metadata18.0.0. Future install resolver может дать другие transitive versions; точный проверенный список — отчёт. Два targets — diagnostic layout, не production packaging. Без CUDA/OS/global Python changes.

## Модель

Официальный [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny/tree/d90ca5fe260221311c53c58e660288d3deb8d356), commit d90ca5fe260221311c53c58e660288d3deb8d356. Загружены config.json/model.bin/tokenizer.json/vocabulary.txt, модель75,538,270bytes. Не менять revision наmain молча.

Download command использовала huggingface_hub.snapshot_download сrepo_id Systran/faster-whisper-tiny, revision указанного commit, allow_patterns этих4файлов, local_dir build/dota_coach/asr-pilot-20261012/model, cache_dir .../hf-cache, token=False/HF_HUB_DISABLE_TELEMETRY=1. Model-download.json содержит sizes/SHA256/versions; model-source.json содержит revision и filenames. Metadata model-remote-verification.json сверена через официальный HF API `/api/models/Systran/faster-whisper-tiny/revision/COMMIT?blobs=true`. model.bin совпал поLFS size/SHA256. Для нового эксперимента эти receipts создать по загруженным байтам, не выдумывать их из stdout.

## Проверки без записи

[Inventory](system-speech-inventory.ps1) запускался WindowsPowerShell5.1 -NoProfile -NonInteractive -File в64/32bitпроцессах. Он читает InstalledRecognizers/WinRT языки, ничего не распознаёт и не открывает микрофон. Результат зависит отконтекста, null/ошибка сохраняются отдельно от пустойcollection.

```powershell
$env:PYTHONUTF8='1'
python creators/creator-2/06-voice/01-microphone-probe/notes/asr-smoke.py
```

[ASR smoke](asr-smoke.py) использует только ранее approved capture SHA94ab5c110254af6692377fe983120b3b1cf6319e4526875f9c875d62d6bf9b0e иfixedlocalmodel. Для других WAV пока нет CLI/приёмки. Микрофон не открывается. HFoffline/local_files_only иPythonsocketguard применяются доthird-partyimports; native sockets/системный network trace не контролировались. Новый UUID result сохраняет старые результаты. Smoke не запускается обычным source catalog/приimport.
