# Ограниченная проверка синтетической грамматики

[Результат 13 октября](../reports/synthetic-grammar-2026-10-13.md).
Это уже выполненный диагностический опыт; команды сохраняются для воспроизведения
в проверенной Windows-среде, а не перекладывают работу на пользователя.

Единственные TTS/ASR команды находятся у C2-06-01; код сюда не копируется.
TTS вызывается явно через PowerShell7, создаёт только WAV в новом own UUID каталоге:

```powershell
pwsh -NoProfile -File creators/creator-2/06-voice/01-microphone-probe/notes/synthetic-tts.ps1 -SampleSet parser_grammar
```

`baseline` — default; допустимы только exact `baseline`/`parser_grammar`. Три
эталона grammar фиксированы в исходниках; произвольный текст не принимается.
Voice/PCM/hash/owned path проверяются; существующий output сохраняется.
Микрофон, speaker sink, system voice settings и ordinary tests не используются.

ASR запускается явно с receipt, возвращённым этой конкретной TTS командой:

```powershell
$env:PYTHONUTF8='1'
& 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' creators/creator-2/06-voice/01-microphone-probe/notes/synthetic-asr.py --receipt '<actual owned tts-receipt.json>'
```

Перед запуском требуются уже проверенные local pinned model/deps (в ignored build);
команда не скачивает их. Old receipt без sample_set означает baseline. Model/decoder
параметры этого опыта не меняются ради WER; metrics нельзя выдавать за качество
человеческой речи. Python socket guard не является OS network tracing.

Actual segments далее проверяются существующим local Roster/VoiceText с явно
синтетическим snapshot и captured revision. Proposal не преобразуется в C1 order
без общей версии контракта/identity/authority. Не исправлять гипотезы незаметно,
не подменять revision текущей и не трактовать ready как исполнение команды.
