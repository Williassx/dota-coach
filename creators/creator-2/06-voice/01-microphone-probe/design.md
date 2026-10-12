# C2-06-01: ограниченное обследование Windows микрофона

[Карточка](README.md) · [План](implementation-plan.md).
Дата: 12 октября 2026. Ведущая роль76; root76/107/173/174/175 владеет документами и диагностической командой. Один reused read-only исследователь76/107 возвращает официальные источники, один final critic проверяет готовый результат. Контракт и сервер принадлежат C1.

## Цель и область

Продолжение DEC-06/21 и P08: установить, доступен ли настоящий аудиовход Windows, сохранить bounded local capture или точный отказ, отдельно исследовать документированную связь с кастомкой. Это обследование C2-06-01, не добавление голосовой механики и не приёмка речи/ASR.

Проверены текущие PLAN/PROGRESS, решения, замысел, roadmap/backlog, skills, правила библиотеки. Применяются brainstorming/writing-plans как уточнение области обследования; пользователь уже поручил самостоятельное продолжение. Первичная read-only query обнаружила четыре входа; FIFINE device0 выбран только для этого запуска, индекс не стабильная identity/default device. CAPS name имеет предел32WCHAR.

## Варианты

1. Полноценный WASAPI capture/ASR companion: современная рекомендуемая архитектура Windows, но выбор recognizer, runtime, ресурсов и bridge ещё не сделан.
2. Legacy WinMM для ограниченного диагностического захвата: штатный API, без установки библиотек и сетевых запросов. Выбран только как probe; не фиксирует production backend.
3. Panorama text preview: уже проверен, но не является microphone/ASR.

## Критерии обследования

- Query с WAVE_FORMAT_QUERY не открывает устройство; сохранить raw коды всех четырёх входов.
- Один bounded capture: explicit device0 FIFINE, PCM16000Hz/mono/16bit, один буфер на3секунды, CALLBACK_NULL, bounded wait5секунд; без loopback/stereo mixer, переключения default/privacy settings или записи в память игры.
- Сохранять stdout/result и PCM только в новом собственном build/dota_coach каталоге; raw audio не включать в Git и не отправлять в сеть. Команда в notes — единственный source этого probe, не в сборочном каталоге.
- Каждый вызов WinMM с кодом проверяется. Start/timeout/reset/unprepare/close различаются; нельзя освобождать queued buffer до подтверждённого reset/unprepare. При unsafe cleanup завершить собственный диагностический процесс и не заявлять освобождение по логике одного finally.
- Проверить записанные bytes/frame alignment/WAV metadata/hash и close/reset коды. Не считать nonzero PCM настоящей речью: шум, silence и ambient recording не доказывают распознавание или speaker identity.
- Не генерировать тестовую речь вместо живого входа. Speech/latency/accuracy/ASR resources и bridge отмечать непроведёнными. Права на распространение не выводить из API availability.
- Отсутствие документа Panorama mic/ASR или 403 не означает отсутствия API или запрета. C1 bridge/contract не изобретать и не реализовывать.

Полная приёмка README требует настоящей речи И проверенного пути. После bounded probe остаётся открытой. Product checkboxes повышаются только для точного выполненного действия.
