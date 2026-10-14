param([Parameter(Mandatory=$true)][ValidateSet('Install','Launch','Check','Quit')][string]$Mode,[string]$Bundle='',[ValidateSet('dota_coach_scene_r1_20261014','dota_coach_scene_r2_20261014','dota_coach_scene_r3_20261014','dota_coach_scene_ui_20261014','dota_coach_scene_ui2_20261014')][string]$Addon='dota_coach_scene_r1_20261014',[ValidatePattern('^[a-z0-9_-]{1,32}$')][string]$Run='r1')
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../../')).Path
$taskCommand=Join-Path $taskRepo 'creators/creator-2/05-intervention-ui/03-return-feedback/tests/native-move/native-command.ps1'
& $taskCommand -Mode $Mode -Bundle $Bundle -Addon $Addon -Run $Run -EvidenceDate 20261014
