# Explicit launch of the installed normal TEST-profile scene, no fixture driver.
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../')).Path
$taskCommand=Join-Path $taskRepo 'creators/creator-2/11-integration/03-end-to-end/tests/01-native-coach-scene/native-command.ps1'
$taskRun='ui-'+[datetime]::UtcNow.ToString('yyyyMMddTHHmmssfff').ToLowerInvariant()
Write-Output "run=$taskRun addon=dota_coach_scene_ui2_20261014"
& $taskCommand -Mode Launch -Addon dota_coach_scene_ui2_20261014 -Run $taskRun
