# Synthetic ASR: decoder работает, две фразы ошибочны

13октября2026. [Spec](../synthetic-design.md), [план](../synthetic-plan.md),
[metadata/hashes](synthetic-asr-2026-10-13.json).
Внутри порученных2часов root leading76/107/108/173/174/175;1reusedhelper author
notes/synthetic-tts.ps1+synthetic-asr.py, отдельныйreusedhelper author9puretests.
Общиефайлы/rootreview/report пишетroot. Original quiet ASR/capture/deps сохранены.

Локальная Microsoft Irina Desktop ru-RU произнесла три фиксированныхreference
вfreshWAV16kHz/PCM16/mono. OutputтолькоWaveFile, микрофон/speakers неоткрывались.
Existing3WAV/receipt refusal не изменил иххеши. Raw audio остаётсяignoredlocal;
этоgeneric system voice, не запись человека/игрока и не voice clone.

Faster-whisper1.2.1/PyAV18first/CPUint8/ru/beam1/VADtrue, exacttinyrevision
d90ca5fe260221311c53c58e660288d3deb8d356/4modelhashes проверены. All3generators
consumed, VADduration3.06/2.98/3.37s, synthetic_decoder_positive=true.
Root независимо сверил actualPCM/hashes/4modelhashes и rawsegments→editdistance.

| Reference | Hypothesis | Правки/слова |
|---|---|---:|
| Игрок два, отойди назад. | Игрог 2, а той день назад. |5/4|
| Игрок один, атакуй цель. | Игра Уходин, атакует сель. |4/4|
| Команда, соберитесь вместе. | Команда, соберитесь вместе. |0/3|

Метрика: lowercase/ё→е/пунктуация; digits не заменяютсясловами. Levenshtein word
edits9/referencewords11, aggregateWER81.8% **только этих трёх synthetic samples**.
Insertion допускает WER>100% отдельнойфразы. Не production accuracy/recognition
acceptance. Ненулевой decoder/text и низкийno_speech_prob не подтверждают верный
адресат/приказ: оба первых hypothesis существенноошибочны, команды не отправлялись.
Model thresholds не подгонялись посленаблюдений, tiny не принятакакproductionmodel.

Время decoder5.087655s/CPU около3.91s в данномпроцессе; не realmicrophone latency/SLA
или benchmark. Offlineflags/localfiles/Python socketguard attempts[] сохраняются,
native/systemnetwork trace не проведён. Speech_verified/accuracy_verified/
dota_bridge_verified=false, commands_sent0. Parser/transport/C1 не подключались.

## Сбои и проверки

Installedvoice inventory не доказал SelectVoice вsandbox: firstfreshreceipt
сохранилfailure, outside context позволил selection. Причинаcontextdifference
отдельнонеустановлена, OS/privacy/settings не менялись. Первыйoutsideprobe ожидал
несуществующий2arg SetOutputToWaveStream; localreflectionпоказала1argstream/
2argWaveFile. FinalиспользуетWaveFile(path,explicitformat) вguardedfreshowneddir;
обаfailedreceipts сохранены, wavsink установлендоSpeak, finallyoutputnull/dispose.
Rawlog/receipts вignored asr-synthetic-20261013-*.

9puretests REDmissinghelper→GREEN: normalization/editmetrics/inert import,
receipt/header/PCM/hash/reference/path/modelpreflight refusals. NoTTS/inference
вordinarycatalog. ActualTTS/ASR exit0, badreceipt доmodel/import/inference exit1
сfresherrorreport, existingoutputrefusal/hashpreservation подтверждены. PSparse0/
AST0. Full062607Z-57578a50suites/1059passed/28skip/6incomplete/0errors/strictfalse/
CLI1/50process0; общийrun также включаетresetVM соседнегонезависимогоподпроекта.

Real speech/independenthumantranscript/quality/resources calibration/companion→Dota/
identity/C1 authorization/outcome/humansecondowner открыты. Progress53/213unchanged;
положительныйsyntheticdecoder не закрывает nativevoice приёмку. Одинитоговыйcritic
не нашёлсущественныхзамечаний; егоAIreview не заменяетдругогосоздателя.
