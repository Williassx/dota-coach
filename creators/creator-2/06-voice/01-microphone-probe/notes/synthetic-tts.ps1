<# Explicit synthetic WAV experiment. Never microphone, speakers or default voice settings. #>
[CmdletBinding()]
param(
    [string]$OutputDirectory,
    [ValidateSet('baseline', 'parser_grammar', IgnoreCase=$false)][string]$SampleSet = 'baseline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$taskRepository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..\..'))
$taskBoundary = Join-Path $taskRepository 'build\dota_coach'

function Assert-TaskPath([string]$Candidate) {
    $taskFull = [IO.Path]::GetFullPath($Candidate)
    $taskPrefix = $taskRepository.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $taskFull.StartsWith($taskPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Synthetic experiment path escapes the repository'
    }
    $taskCursor = $taskFull
    while ($true) {
        $taskItem = Get-Item -LiteralPath $taskCursor -Force -ErrorAction SilentlyContinue
        if ($null -ne $taskItem -and ($taskItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Synthetic experiment refuses reparse points'
        }
        if ($taskCursor.Equals($taskRepository, [StringComparison]::OrdinalIgnoreCase)) { break }
        $taskCursor = [IO.Path]::GetDirectoryName($taskCursor)
    }
    return $taskFull
}

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $taskBoundary ('asr-synthetic-20261013-' + [Guid]::NewGuid().ToString('N'))
} elseif (-not [IO.Path]::IsPathRooted($OutputDirectory)) {
    $OutputDirectory = Join-Path $taskRepository $OutputDirectory
}
$taskOutput = Assert-TaskPath $OutputDirectory
if (-not ([IO.Path]::GetDirectoryName($taskOutput)).Equals($taskBoundary, [StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetFileName($taskOutput) -cnotmatch '^asr-synthetic-20261013-[0-9a-f]{32}$') {
    throw 'Output must be a fresh direct asr-synthetic-20261013-<32hex> child of build/dota_coach'
}
if (Test-Path -LiteralPath $taskOutput) { throw 'Existing synthetic output is preserved' }
[void](New-Item -ItemType Directory -Path $taskOutput -ErrorAction Stop)
$taskReferences = if ($SampleSet -ceq 'parser_grammar') {
    @('керри отступай', 'мидер держи позицию', 'команда соберитесь')
} else {
    @('Игрок два, отойди назад.', 'Игрок один, атакуй цель.', 'Команда, соберитесь вместе.')
}
$taskReceipt = [ordered]@{
    schema_version = 1
    stage = 'synthetic_tts'
    source = 'synthetic_system_tts'
    sample_set = $SampleSet
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    voice_name = 'Microsoft Irina Desktop'
    voice_culture = 'ru-RU'
    voice_id = $null
    system_speech_assembly = $null
    audio_format = [ordered]@{sample_rate=16000;sample_width_bytes=2;channels=1;encoding='PCM'}
    references = $taskReferences
    samples = @()
    tts_completed = $false
    microphone_used = $false
    speakers_used = $false
    network_requested = $false
    error = $null
}
$taskSynth = $null
$taskWatch = [Diagnostics.Stopwatch]::StartNew()
try {
    Add-Type -AssemblyName System.Speech -ErrorAction Stop
    $taskReceipt.system_speech_assembly = [System.Speech.Synthesis.SpeechSynthesizer].Assembly.FullName
    $taskSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $taskVoice = @($taskSynth.GetInstalledVoices() | Where-Object {
        $_.Enabled -and $_.VoiceInfo.Name -ceq 'Microsoft Irina Desktop' -and $_.VoiceInfo.Culture.Name -ceq 'ru-RU'
    })
    if ($taskVoice.Count -ne 1) { throw 'Exact enabled Microsoft Irina Desktop ru-RU voice unavailable' }
    $taskSynth.SelectVoice('Microsoft Irina Desktop')
    if ($taskSynth.Voice.Name -cne 'Microsoft Irina Desktop' -or $taskSynth.Voice.Culture.Name -cne 'ru-RU') {
        throw 'Selected TTS voice differs from the requested synthetic voice'
    }
    $taskReceipt.voice_id = $taskSynth.Voice.Id
    $taskFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(
        16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,
        [System.Speech.AudioFormat.AudioChannel]::Mono)
    for ($taskIndex=0; $taskIndex -lt $taskReferences.Count; $taskIndex++) {
        $taskName = 'sample-{0:D2}.wav' -f ($taskIndex + 1)
        $taskWav = Assert-TaskPath (Join-Path $taskOutput $taskName)
        if (Test-Path -LiteralPath $taskWav) { throw 'Existing synthetic WAV is preserved' }
        try {
            $taskSynth.SetOutputToWaveFile($taskWav, $taskFormat)
            $taskSynth.Speak($taskReferences[$taskIndex])
        } finally {
            $taskSynth.SetOutputToNull()
        }
        $taskReceipt.samples += [ordered]@{
            name=$taskName
            reference=$taskReferences[$taskIndex]
            bytes=(Get-Item -LiteralPath $taskWav).Length
            sha256=(Get-FileHash -LiteralPath $taskWav -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $taskReceipt.tts_completed = $true
} catch {
    $taskReceipt.error = $_.Exception.GetType().Name + ': ' + $_.Exception.Message
} finally {
    if ($null -ne $taskSynth) {
        try { $taskSynth.SetOutputToNull() } catch {
            if ($null -eq $taskReceipt.error) { $taskReceipt.error = 'Cleanup: ' + $_.Exception.Message }
        } finally { $taskSynth.Dispose() }
    }
    $taskWatch.Stop()
    $taskReceipt.elapsed_seconds = $taskWatch.Elapsed.TotalSeconds
    $taskReceipt.completed_at_utc = [DateTime]::UtcNow.ToString('o')
    $taskReceiptPath = Join-Path $taskOutput 'tts-receipt.json'
    $taskJson = $taskReceipt | ConvertTo-Json -Depth 8
    $taskBytes = [Text.UTF8Encoding]::new($false).GetBytes($taskJson + [Environment]::NewLine)
    $taskReceiptStream = [IO.File]::Open($taskReceiptPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $taskReceiptStream.Write($taskBytes, 0, $taskBytes.Length) } finally { $taskReceiptStream.Dispose() }
}
[ordered]@{receipt=$taskReceiptPath;tts_completed=$taskReceipt.tts_completed;samples=$taskReceipt.samples.Count;
    source=$taskReceipt.source;sample_set=$taskReceipt.sample_set;speakers_used=$false;microphone_used=$false;error=$taskReceipt.error} | ConvertTo-Json
if ($null -ne $taskReceipt.error -or -not $taskReceipt.tts_completed) { exit 1 }
