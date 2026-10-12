# C2-06-01: offline ASR runtime и VAD

[Карточка](../README.md) · [Дизайн](../asr-design.md) · [План](../asr-plan.md) · [Воспроизведение](../notes/asr-setup.md).
12 октября2026. Baseline4a9e9cc/main/clean, leading76, root76/107/108/173/174/175 — один автор. Новыеagents0/implementationhelpers0, reusedfinalcritic после готового bounded результата. Windows/Steam/Dota/C1/sharedcontracts не менялись; capture не повторялся.

## Windows inventory

[64bit strict](../../../../../build/dota_coach/system-speech-strict-64-20261012.json) и [32bit strict](../../../../../build/dota_coach/system-speech-strict-32-20261012.json), outside approved sandbox: System.Speech4.0 InstalledRecognizers=[], WinRT grammar/topic collections=[], is_null=false, query_error=null, audio_opened=false. Предыдущие queries sandbox64/outside64/32 согласуются. Это отсутствие результата данныхAPI в этихпроцессах, не доказательство отсутствия всехпакетов Windows или запретаASR. Строгий PS -File проверил, что collection неnull; ранний stdin compoundtry невывелрезультат и неиспользованкакevidence.

[Microsoft InstalledRecognizers](https://learn.microsoft.com/en-us/dotnet/api/system.speech.recognition.speechrecognitionengine.installedrecognizers?view=netframework-4.8.1) документирует installed engines этогоAPI. [Microsoft language selection](https://learn.microsoft.com/en-us/windows/apps/develop/input/specify-the-speech-recognizer-language) различает localgrammar/remote topic и указывает package identity дляWindows.Media.SpeechRecognition. Packaged companion/recognizer не создавался; Windows language packs не устанавливались.

## Пакеты и модель

Wheels-only dependencies установлены в fresh ignored project targets; log build/dota_coach/asr-pilot-install-20261012.log, exit0. Прямой CPU pilot выбран как небольшой experiment, не финальный speech backend. [Разработчик faster-whisper](https://github.com/SYSTRAN/faster-whisper) документирует CPU/int8/localmodel/VAD; этот отчёт не переносит benchmark автора накомпьютер пользователя.

| Фактически загруженный пакет | Версия |
|---|---|
|faster-whisper|1.2.1|
|ctranslate2|4.8.2|
|onnxruntime|1.31.0|
|PyAV|18.0.0 (отдельный deps-av18)|
|numpy|2.5.4|
|huggingface-hub|2.2.0|
|tokenizers|0.23.3|

Multilingualtiny, explicit language=ru; [source receipt](../../../../../build/dota_coach/asr-pilot-20261012/model-source.json), [download](../../../../../build/dota_coach/asr-pilot-20261012/model-download.json). Официальный repo Systran/faster-whisper-tiny, commitd90ca5fe260221311c53c58e660288d3deb8d356. Только4runtime files, localmodel/cache, download11.171s. model.bin75,538,270bytes/SHA256dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1 совпадает с [remoteLFS metadata](../../../../../build/dota_coach/asr-pilot-20261012/model-remote-verification.json) pinnedcommit. Download требовал сети; это неoffline setup. Пакеты/model/rawaudio не входят вGit.

## Ошибка и направленное исправление

Первый [run-ab6f8f](../../../../../build/dota_coach/asr-pilot-20261012/run-ab6f8f/asr-result.json), exit1: model_loaded=true, generator_consumed=false, PyAV19.0.1 TypeError `open() got an unexpected keyword argument 'metadata_errors'`. Установленный faster_whisper/audio.py line46 передаётmetadata_errors; его METADATA требуеттолько av>=11. PyAV19 удалил параметр. [Официальное issue1589](https://github.com/SYSTRAN/faster-whisper/issues/1589) и [PyAV releases](https://github.com/PyAV-Org/PyAV/releases) согласуются с локальной диагностикой.

Не применяли monkeypatch стороннего decoder и не меняли WAV. Отдельныйav18.0.0 wheel вdeps-av18, import precedence явный; исходныйav19environment и failedresult сохранены. Repeat [run-591fba](../../../../../build/dota_coach/asr-pilot-20261012/run-591fba/asr-result.json) exit0/model_loaded/generator_consumed=true.

## Фактический smoke и ресурсы

[Measured run-ebf535](../../../../../build/dota_coach/asr-pilot-20261012/run-ebf535/asr-result.json), собственный PID9416/exit0. Approved3secFIFINEfile SHA94ab5c110254af6692377fe983120b3b1cf6319e4526875f9c875d62d6bf9b0e, CPU/int8/threads2/beam1/language ru/vadtrue, condition_on_previous_textfalse. Full generator consumed. Input3.000s; afterVAD0.000s; segments[]; decoder_exercised=false; commands_sent0. Это runtime/model/decode-to-PCM/VAD path, не positive speech decoder/живые команды.

Model load0.558473s, VAD/transcribepath0.225459s, wholeprobe1.336628s/CPU1.375s. [Process measurement](../../../../../build/dota_coach/asr-pilot-20261012/process-measure-f748c5.json):17samples/100ms/max observed reportedpeak226,553,856bytes (~216.06MiB); unobserved finalpeak можетбытьвыше. Собственныйпроцесс завершился; timeout/forcekill неиспользован. Warmfilesystem/processpath отличаютсяотпервогоsuccesselapsed3.528752s, поэтомуневыводимASR real-time latency/benchmark изэтогопилота.

HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE/local_files_only иlocalfiles действуютприinference; Python socket connect/connect_ex/create_connection/getaddrinfo guard доthirdpartyimports. python_socket_attempts=[], errornull. Это config плюс наблюдениеPythonlayer, неOSfirewall/packet capture: native_network_monitoredfalse, абсолютныйnetworkproofнеобъявлен. Decode/inference получаютlocalpath, cloudASR неиспользован; audio невыдавалосьnetworkclient.

## Что остаётся открытым

Speech_verified/accuracy_verified/dota_bridge_verified=false. Ни одной разборчивойфразы/независимоготранскрипта/positive decode/WER/command latency не проверено. Quiet3sec/VAD0 не доказывают отсутствие hallucinations илиfalsepositives на другихданных. Tinyнепринятакакproductionmodel; thresholds/language/identity/context/addressing/ASR→parser/C1 authorization/ACK/outcome не реализованы. Транспортcompanion→кастомка иhumansecondowner открыты. Не генерировалиTTS, не подавалиcandidateTextвприказы, не повышалиcheckboxзаустановкуmodel. Progress52/213(24.4%) должен остаться неизменным.

## Проверки и ревью

Requiredfull [162410Z-443264](../../../../../build/dota_coach/source-checks-20261012T162410Z-443264/source-checks.json):47suites/1024passed/28skipped/6incomplete/error_suites[]/verifiedfalse/CLIexit1. Все47suiteprocess exits0. Catalog не активируетмикрофон/modelsmoke; actualASRpilot проверен отдельно. Один reusedfinalcritic без существенных замечаний; AI не humansecondowner.

Финальные проверки:11изменённых Markdown/150локальных ссылок безразрывов;30уроков с пятьюполями/42uniqueusage tasks. PythonAST/PowerShellsyntax,4modelhashes/finalresult/progress--check52/213(24.4%) иgitdiff--check проходят. Бинарныепакеты/model/аудио ignoredlocal, sourceдиагностики один вC2. Publication определяется Git history и отдельнойсверкой remote SHA.
