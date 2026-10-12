# C2-06-01: изолированный offline ASR smoke

[Карточка](README.md) · [План](asr-plan.md).12октября2026, baseline4a9e9cc/main/clean. Ведущая76, root76/107/108/173/174/175 одинавтор. Один finalcriticпослеготовогорезультата, безimplementationhelpers. Scope микрофонныйподпункт; C1/server/sharedcontracts не изменяются.

## Выбор и границы

Read-only System.Speech4.0 (.NET Framework) query в64/32bitWindowsPowerShell5.1 не вернул recognizers; WinRT static language queries не далиlanguage tags и не выбросилиexception. Это результат этихAPI/контекстов, не доказательство отсутствия всех speechpacks/backendWindows. Полноценный Windows.Media.SpeechRecognition путь требует собственного package identity согласно currentMicrosoft guidance; его здесь не создаём. OS/lang/privacy не меняем.

Для независимого эксперимента выбран faster-whisper CPU/int8 с маленькой multilingual tiny model, явноlanguage=ru. Это пилот API/runtime/VAD, не production choice/качество русской речи. Альтернативы: packagedWindowsASR требуетотдельногоплана; облачныйASR требуетсеть дляaudio и выборасервиса. Пилот использует downloadпакетов/модели, ноinferencelocal/безaudio uploads.

## Критерии

- Pythondeps/model/cache только вновомownedignoredbuildchild; wheels-only install, no globalpackages/CUDA/OSsettings. Точныеversions/модельrevision/hash/inventory сохраняются.
- Modelзагрузка не смешивается сofflineinference: отдельный downloadstep, pinnedHFcommit, затем offline flags/local_files_only иlocaldirectory. Не утверждатьпакетыходиливсетьеслинепроверено: processofflineconfig иsocketguard/evidence отдельно.
- Один existingapprovedFIFINE WAV3s/SHA94ab5c110254af6692377fe983120b3b1cf6319e4526875f9c875d62d6bf9b0e; неактивироватьmicповторно, несоздаватьTTS/реальнуюфразуизшума.
- CPUthreads2, beam1, language ru, vad_filter=true, consumegenerator полностью. Зафиксироватьduration/VADretained/segments/timings/resourcepeakprocess; NO gamingcommand/transport/servercalls.
- Результатсегментов — недоверенныйтекст, неготовыйприказ. Empty/VAD0 наэтомclip — толькоboundednegativeobservation, недоказательствоfalsepositivefree/general silence/voiceaccuracy. ЕслиASRпридумаеттекст, сохранитькакнаблюдение, непосылатькоманду.
- Actual speech/словарь/WER/real-time latency/acceptance/bridge/C1/humanowner остаютсяоткрытыми. Fullproductactions не повышаемзаустановкуmodel.

Это продолжениеexistingauditdesign. Skillsbrainstorming/writing-plans примененыкобластипилота; пользовательпоручилсамостоятельноепродолжение, новыеuserchoices невыдуманы.
