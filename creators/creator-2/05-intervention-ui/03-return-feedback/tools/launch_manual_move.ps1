# Launch only the approved isolated addon; preserve an existing Dota client.
$ErrorActionPreference='Stop'
$taskPart=Split-Path $PSScriptRoot
$taskCommand=Join-Path $taskPart 'tests/native-move/native-command.ps1'
$taskRun='ui-'+[datetime]::UtcNow.ToString('yyyyMMddTHHmmssfff').ToLowerInvariant()
Write-Output "run=$taskRun addon=dota_coach_c2_move_final2_20261013"
& $taskCommand -Mode Launch -Addon dota_coach_c2_move_final2_20261013 -Run $taskRun
