# Возможности голоса: проверка12октября2026

[Заметки](README.md) · [Отчёт](../reports/microphone.md).
Консультация reused agent76/107, root сверил локальный API dump. Сведения ниже не являются выбранной архитектурой ASR или юридическим разрешением.

## Проверенные источники

- [Microsoft waveInOpen](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveinopen): WAVE_FORMAT_QUERY проверяет формат без открытия; actual open — отдельный шаг. Native probe использует WinMM только для ограниченного обследования.
- [Microsoft waveInGetDevCapsW](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveingetdevcapsw) и [WAVEHDR](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/ns-mmeapi-wavehdr): capabilities и buffer layout/WHDR_DONE. Names ограничены32WCHAR, это не постоянные endpoint identifiers.
- [Reset](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveinreset), [Unprepare](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveinunprepareheader), [Close](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveinclose): освобождение queued buffer/handle проверяется по отдельным return codes. Прочитаны страницы, не только search snippets.
- [Microsoft devices/data types](https://learn.microsoft.com/en-us/windows/win32/multimedia/devices-and-data-types): Microsoft рекомендует новые WASAPI/Audio Graphs вместо legacy Waveform Audio, где возможно. [WASAPI capture](https://learn.microsoft.com/en-us/windows/win32/coreaudio/capturing-a-stream) документирует IAudioCaptureClient для отдельного Windows-процесса.
- [Microsoft Speech Recognition](https://learn.microsoft.com/en-us/windows/apps/develop/input/speech-recognition): в текущем Windows App SDK guidance указан package identity/MSIX; list/SRGS grammar local, dictation/web-search remote. Это относится к описанному Windows.Media.SpeechRecognition пути; не утверждение о всех ASR. Русский язык/runtime здесь не проверены, packages/models не устанавливались.
- [Valve Reborn updates](https://www.dota2.com/reborn/updates): исторические2015updates подтверждают custom game event API, не companion bridge и не текущую работоспособность целой цепочки.

## Недоступные источники и локальные факты

[VDC Panorama JS API](https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/Panorama/Javascript/API) и [Custom Game Events](https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/Custom_Game_Events) не прочитаны:403/Internal Error. Это отказ доступа источника, не запрет или доказательство отсутствия микрофонного API.

Локальный dump от11октября2026 [native-api-details](../../../../../build/dota_coach/native-api-details-20261011.txt), line1018: GameEvents.SendCustomGameEventToServer; line1080: AsyncWebRequest Make a web request (disabled). В этом dump поиск GetVoice/Microphone/SpeechRecognition/getUserMedia не дал matches. Вывод ограничен сохранённым перечнем: прямой mic/ASR и HTTP companion→Panorama bridge не подтверждены. Steam voice chat, CPlayerVoiceListener и DOTASpeechType не равны доступу к PCM или ASR.

## Следующая зависимость

Кандидат: отдельный Windows capture/ASR → подтверждённый текст → согласованный транспорт → кастомка → server validation/ACK. Проверен только ограниченный capture. Backend ASR, язык, latency/accuracy, модель/ресурсы/сеть и транспорт ещё не выбраны. C1 должен согласовать trusted sender/адресата/target/priority/duplicate handling/ACK/outcome; событие Panorama→server само по себе не решает доставку из внешнего процесса. Injected DLL/память игры и изменение системных privacy settings не входят в этот путь.
