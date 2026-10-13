param(
 [Parameter(Mandatory=$true)][ValidateSet('Install','Launch','Quit')][string]$Mode,
 [ValidatePattern('^dota_coach_c1_probe_[a-z0-9_]+$')]
 [string]$Addon='dota_coach_c1_probe_20261013',
 [ValidatePattern('^[a-z0-9_-]+$')][string]$Run='r1'
)
# C1-01-02 install/launch/quit. Recipe follows the verified procedure of
# creator 2 (creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/native-command.ps1):
# map from content template, addoninfo from workshop_testbed, compile to game addon.
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../..')).Path
$dotaRoot='C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot="$dotaRoot/content/dota_addons/$Addon"
$gameRoot="$dotaRoot/game/dota_addons/$Addon"
$src=(Resolve-Path (Join-Path $PSScriptRoot '../src')).Path
$prefix="$repoRoot/build/dota_coach/np-c1-probe-$Run-20261013"
$receipt="$prefix-owned.json"

if ($Mode -eq 'Quit') {
 $owned=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
 $process=Get-Process -Id $owned.pid -ErrorAction SilentlyContinue
 if ($process -and ($process.ProcessName -ne 'dota2' -or $process.StartTime.ToUniversalTime().Ticks -ne ([datetime]$owned.start_time_utc).ToUniversalTime().Ticks)) {throw 'Owned PID identity changed'}
 if ($process) { taskkill /PID $owned.pid /F | Out-Null; Write-Output "quit pid=$($owned.pid)" }
 return
}
if (Get-Process dota2 -ErrorAction SilentlyContinue) {throw 'Existing Dota client preserved'}
if ($Mode -eq 'Install') {
 if (Test-Path -LiteralPath $contentRoot) {throw "Fresh content addon required: $contentRoot"}
 if (Test-Path -LiteralPath $gameRoot) {throw "Fresh game addon required: $gameRoot"}
 New-Item -ItemType Directory -Path (Join-Path $gameRoot 'scripts\vscripts') | Out-Null
 New-Item -ItemType Directory -Path (Join-Path $contentRoot 'maps') | Out-Null
 Copy-Item -LiteralPath (Join-Path $src 'addoninfo.txt') -Destination "$gameRoot/addoninfo.txt"
 Copy-Item -LiteralPath (Join-Path $src 'scripts\vscripts\addon_game_mode.lua') -Destination "$gameRoot/scripts/vscripts/addon_game_mode.lua"
 Copy-Item -LiteralPath "$dotaRoot/content/dota_addons/addon_template/maps/template_map.vmap" -Destination "$contentRoot/maps/template_map.vmap"
 & "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/maps/template_map.vmap" > "$prefix-map-compile.log" 2>&1
 if ($LASTEXITCODE -ne 0) {throw "Map compile failed exit=$LASTEXITCODE"}
 if (-not (Test-Path -LiteralPath "$gameRoot/maps/template_map.vpk")) {throw 'Compiled map missing'}
 Write-Output "installed addon=$Addon map_compiled exit=0"
 return
}

if ($Mode -eq 'Launch') {
 if (-not (Test-Path -LiteralPath "$gameRoot/maps/template_map.vpk")) {throw 'Install first'}
 if (Test-Path -LiteralPath $receipt) {throw 'Fresh launch receipt required'}
 $arguments="-game `"$dotaRoot/game/dota`" -steam -addon $Addon -novid -windowed -w 1280 -h 720 -console -dev -insecure -vconsole -vconport 29001 -con_logfile `"$prefix-console.log`" +dota_launch_custom_game $Addon template_map"
 $process=Start-Process -FilePath "$dotaRoot/game/bin/win64/dota2.exe" -ArgumentList $arguments -WindowStyle Hidden -PassThru
 @{pid=$process.Id;start_time_utc=$process.StartTime.ToUniversalTime().ToString('o');addon=$Addon;arguments=$arguments;log="$prefix-console.log"} | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
 Write-Output "owned_pid=$($process.Id) receipt=$receipt"
 return
}
