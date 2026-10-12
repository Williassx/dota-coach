# Read-only query; never instantiates a recognizer or opens audio.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$result = [ordered]@{
    schema_version = 1
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    process_bitness = [IntPtr]::Size * 8
    recognizers = @([System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() | ForEach-Object {
        [ordered]@{ id=$_.Id; name=$_.Name; culture=$_.Culture.Name }
    })
    grammar_languages = @()
    topic_languages = @()
    grammar_is_null = $null
    topic_is_null = $null
    winrt_query_error = $null
    audio_opened = $false
    recognition_run = $false
}
try {
    $speechType = [Windows.Media.SpeechRecognition.SpeechRecognizer,Windows.Media.SpeechRecognition,ContentType=WindowsRuntime]
    $grammar = $speechType::SupportedGrammarLanguages
    $topic = $speechType::SupportedTopicLanguages
    $result.grammar_is_null = ($null -eq $grammar)
    $result.topic_is_null = ($null -eq $topic)
    $result.grammar_languages = @($grammar | ForEach-Object LanguageTag)
    $result.topic_languages = @($topic | ForEach-Object LanguageTag)
} catch {
    $result.winrt_query_error = $_.Exception.Message
}
$result | ConvertTo-Json -Depth 6
