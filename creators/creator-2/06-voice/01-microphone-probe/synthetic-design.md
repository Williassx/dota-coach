# Положительный decoder pilot на synthetic speech

13октября2026, C2-06-01, leading76/root107/108/173/174/175.
Внутри порученных2часов продолжить existing offline ASR path без capture/bridge.
Readonly inventory обнаружил enabled Microsoft Irina Desktop ru-RU; generic system
voice, не голос реального человека или игрока. Model/deps находятся локально,
PyAV18 overlay должен предшествовать несовместимому PyAV19.

Сгенерировать3фиксированные русские фразы через System.Speech в fresh ignored
directory, SetOutputToWaveFile/16kHz16bitmono. Не воспроизводить через speakers,
не открывать микрофон, не менять voice defaults/OS/network. WAV hashes иreference
text вreceipt. SpeechSynthesizer.Close/Dispose вfinally, oldoutputsнеперезаписывать.

Новый explicit inference command принимает только собственный synthetic receipt,
проверяет WAV/hash/PCM/точную modelrevision+4hashes. CPU/int8/ru/beam1/VADtrue,
generatorconsumed, raw segments и нормализованный edit-distance/reference comparison.
Не направлять transcript в game/parser/execution. WER только этих3synthetic samples,
не accuracy реального микрофона или production threshold. Speech_verified и
dota_bridge_verified остаютсяfalse; отдельно synthetic_decoder_positive.

Readonly/source helper и rawaudio остаютсяlocal/ignored; tracked диагностические
команды в этом подпункте, не ordinary capture/test catalog. Включить полезные
nonactivating tests только для receipt/refusal/metric logic если такая логика есть.
Existing quiet pilot и deps-av19 сохраняются.1finalcritic после результата.
