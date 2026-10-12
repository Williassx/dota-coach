param(
 [Parameter(Mandatory=$true)][ValidateSet('Install','Launch','Quit')][string]$Mode,
 [string]$Bundle='',
 [ValidatePattern('^dota_coach_c2_camera_[a-z0-9_]+$')][string]$Addon='dota_coach_c2_camera_20261012',
 [ValidatePattern('^[a-z0-9_-]+$')][string]$Run='r1'
)
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../../')).Path
$dotaRoot='C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$contentRoot="$dotaRoot/content/dota_addons/$Addon"
$gameRoot="$dotaRoot/game/dota_addons/$Addon"
$prefix="$repoRoot/build/dota_coach/native-camera-$Run-20261012"
$receipt="$prefix-owned.json"
if ($Mode -eq 'Quit') {
 $owned=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
 $process=Get-Process -Id $owned.pid -ErrorAction SilentlyContinue
 if ($process -and ($process.ProcessName -ne 'dota2' -or $process.StartTime.ToUniversalTime().Ticks -ne ([datetime]$owned.start_time_utc).ToUniversalTime().Ticks)) {throw 'Owned PID identity changed'}
 if ($process) { & node "$PSScriptRoot/vcon-query.cjs" 'quit' "$prefix-quit.jsonl" 1500; if ($LASTEXITCODE -ne 0) {throw 'Quit command failed'} }
 return
}
if (Get-Process dota2 -ErrorAction SilentlyContinue) {throw 'Existing Dota client preserved'}
if ($Mode -eq 'Install') {
 if ((Test-Path -LiteralPath "$prefix-hashes.json") -or
     (Test-Path -LiteralPath "$prefix-ui-compile.log") -or
     (Test-Path -LiteralPath "$prefix-canonical-compile.log") -or
     (Test-Path -LiteralPath "$prefix-map-compile.log")) {throw 'Fresh install receipt/log required'}
 if ((Test-Path -LiteralPath $contentRoot) -or (Test-Path -LiteralPath $gameRoot)) {throw 'Fresh addon directories required'}
 $sourceBundle=(Resolve-Path -LiteralPath $Bundle).Path
 $report=Get-Content -LiteralPath "$sourceBundle/native-fixture-report.json" -Raw | ConvertFrom-Json
 if ($report.fixture_type -ne 'native_camera_test_only' -or $report.assets.Count -ne 15) {throw 'Wrong fixture'}
 foreach ($asset in $report.assets) {
  if (-not $asset.target.StartsWith('content/panorama/') -or $asset.target.Contains('..') -or $asset.target.Contains('\')) {throw 'Unsafe target'}
  if ((Get-FileHash -LiteralPath (Join-Path $sourceBundle $asset.target) -Algorithm SHA256).Hash.ToLower() -ne $asset.sha256) {throw 'Bundle hash mismatch'}
 }
 New-Item -ItemType Directory -Path $contentRoot | Out-Null
 New-Item -ItemType Directory -Path $gameRoot | Out-Null
 foreach ($asset in $report.assets) {
  $destFile=Join-Path $contentRoot $asset.target.Substring(8)
  New-Item -ItemType Directory -Path (Split-Path $destFile) -Force | Out-Null
  Copy-Item -LiteralPath (Join-Path $sourceBundle $asset.target) -Destination $destFile
  if ((Get-FileHash -LiteralPath $destFile -Algorithm SHA256).Hash.ToLower() -ne $asset.sha256) {throw 'Installed hash mismatch'}
 }
 New-Item -ItemType Directory -Path "$contentRoot/maps" | Out-Null
 Copy-Item -LiteralPath "$dotaRoot/content/dota_addons/addon_template/maps/template_map.vmap" -Destination "$contentRoot/maps/template_map.vmap"
 Copy-Item -LiteralPath "$dotaRoot/game/dota_addons/workshop_testbed/addoninfo.txt" -Destination "$gameRoot/addoninfo.txt"
 foreach ($job in @(@{Name='ui';Input='panorama/layout/custom_game/custom_ui_manifest.xml'},@{Name='canonical';Input='panorama/layout/custom_game/coach_hud.xml'},@{Name='map';Input='maps/template_map.vmap'})) {
  & "$dotaRoot/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$dotaRoot/game/dota" -i "$contentRoot/$($job.Input)" > "$prefix-$($job.Name)-compile.log" 2>&1
  if ($LASTEXITCODE -ne 0) {throw "Compile failed: $($job.Name)"}
  Write-Output "compiled=$($job.Name) exit=0"
 }
 $compiled=@(Get-ChildItem -LiteralPath "$gameRoot/panorama" -Recurse -File | ForEach-Object {@{path=$_.FullName.Substring($gameRoot.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()}})
 if ($compiled.Count -ne 15) {throw "Expected15 compiled UI outputs, got$($compiled.Count)"}
 $vpk=Get-Item -LiteralPath "$gameRoot/maps/template_map.vpk"
 @{canonical_input_hashes=$report.canonical_input_hashes;compiled=$compiled;map_bytes=$vpk.Length;map_sha256=(Get-FileHash -LiteralPath $vpk.FullName -Algorithm SHA256).Hash.ToLower()} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath "$prefix-hashes.json" -Encoding utf8
 Write-Output "installed_sources=15 compiled_ui=15 map_bytes=$($vpk.Length)"
 return
}
if ((Test-Path -LiteralPath $receipt) -or (Test-Path -LiteralPath "$prefix-console.log")) {throw 'Fresh launch receipt/log required'}
if (-not (Test-Path -LiteralPath "$gameRoot/maps/template_map.vpk")) {throw 'Compiled map missing'}
$arguments="-game `"$dotaRoot/game/dota`" -steam -addon $Addon -novid -windowed -w 1280 -h 720 -console -dev -insecure -vconsole -vconport 29000 -con_logfile `"$prefix-console.log`" +dota_launch_custom_game $Addon template_map"
$process=Start-Process -FilePath "$dotaRoot/game/bin/win64/dota2.exe" -ArgumentList $arguments -WindowStyle Hidden -PassThru
@{pid=$process.Id;start_time_utc=$process.StartTime.ToUniversalTime().ToString('o');addon=$Addon;arguments=$arguments;log="$prefix-console.log"} | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
Write-Output "owned_pid=$($process.Id) receipt=$receipt"
