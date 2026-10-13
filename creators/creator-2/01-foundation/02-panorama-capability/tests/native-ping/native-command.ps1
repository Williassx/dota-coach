param(
 [Parameter(Mandatory=$true)][ValidateSet('Install','Launch','Check','Quit')][string]$Mode,
 [string]$Bundle='',
 [ValidateSet('dota_coach_c2_ping_20261013','dota_coach_c2_ping_r2_20261013','dota_coach_c2_ping_r3_20261013')][string]$Addon='dota_coach_c2_ping_20261013',
 [ValidatePattern('^[a-z0-9_-]{1,32}$')][string]$Run='r1'
)
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../../')).Path
$taskDota='C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$taskContent="$taskDota/content/dota_addons/$Addon"
$taskGame="$taskDota/game/dota_addons/$Addon"
$taskPrefix="$taskRepo/build/dota_coach/native-ping-$Run-20261013"
$taskReceipt="$taskPrefix-owned.json"
$taskQuery=Join-Path $taskRepo 'creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/vcon-query.cjs'
function Assert-Owned {
 $taskOwned=Get-Content -LiteralPath $taskReceipt -Raw | ConvertFrom-Json
 if ($taskOwned.addon -ne $Addon) {throw 'Receipt addon mismatch'}
 $taskProcess=Get-Process -Id $taskOwned.pid -ErrorAction Stop
 if ($taskProcess.ProcessName -ne 'dota2' -or $taskProcess.StartTime.ToUniversalTime().Ticks -ne ([datetime]$taskOwned.start_time_utc).ToUniversalTime().Ticks) {throw 'Owned PID identity changed'}
 return $taskProcess
}
if ($Mode -eq 'Check') { $taskOwnedProcess=Assert-Owned; Write-Output "owned_pid=$($taskOwnedProcess.Id) identity=valid"; return }
if ($Mode -eq 'Quit') {
 $taskOwnedProcess=Assert-Owned
 if (Test-Path -LiteralPath "$taskPrefix-quit.jsonl") {throw 'Fresh quit output required'}
 & node $taskQuery 'quit' "$taskPrefix-quit.jsonl" 1500
 if ($LASTEXITCODE -ne 0) {throw 'Owned VCon quit failed'}
 return
}
if (Get-Process dota2 -ErrorAction SilentlyContinue) {throw 'Existing Dota client preserved'}
if ($Mode -eq 'Install') {
 if ((Test-Path -LiteralPath $taskContent) -or (Test-Path -LiteralPath $taskGame)) {throw 'Fresh addon directories required'}
 foreach ($taskSuffix in @('hashes.json','ui-compile.log','canonical-compile.log','map-compile.log')) {
  if (Test-Path -LiteralPath "$taskPrefix-$taskSuffix") {throw 'Fresh install evidence required'}
 }
 $taskBundle=(Resolve-Path -LiteralPath $Bundle).Path
 $taskBoundary=Join-Path $taskRepo 'build/dota_coach'
 if (-not $taskBundle.StartsWith($taskBoundary+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {throw 'Bundle must be a child of project build/dota_coach'}
 $taskReport=Get-Content -LiteralPath "$taskBundle/native-fixture-report.json" -Raw | ConvertFrom-Json
 $taskAllowed=@('content/panorama/layout/custom_game/custom_ui_manifest.xml','content/panorama/layout/custom_game/coach_probe.xml','content/panorama/layout/custom_game/ping_fixture.xml','content/panorama/styles/custom_game/coach_probe.css','content/panorama/scripts/custom_game/coach_probe_state.js','content/panorama/scripts/custom_game/coach_probe.js','content/panorama/scripts/custom_game/ping_fixture.js','game/scripts/vscripts/diagnostic_ping.lua','game/scripts/vscripts/addon_game_mode.lua')
 if ($taskReport.fixture_type -ne 'native_diagnostic_ping_test_only' -or $taskReport.assets.Count -ne 9 -or $taskReport.canonical_inputs -ne 5) {throw 'Wrong TEST fixture'}
 $taskSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 foreach ($taskAsset in $taskReport.assets) {
  if ($taskAllowed -cnotcontains $taskAsset.target -or -not $taskSeen.Add($taskAsset.target)) {throw 'Unexpected/duplicate output target'}
  $taskSource=Join-Path $taskBundle $taskAsset.target
  if ((Get-Item -LiteralPath $taskSource).Attributes -band [IO.FileAttributes]::ReparsePoint) {throw 'Linked bundle asset refused'}
  if ((Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskAsset.sha256) {throw 'Bundle hash mismatch'}
 }
 [void](New-Item -ItemType Directory -Path $taskContent)
 [void](New-Item -ItemType Directory -Path $taskGame)
 foreach ($taskAsset in $taskReport.assets) {
  $taskDest=if($taskAsset.target.StartsWith('content/')) {Join-Path $taskContent $taskAsset.target.Substring(8)} else {Join-Path $taskGame $taskAsset.target.Substring(5)}
  [void](New-Item -ItemType Directory -Path (Split-Path $taskDest) -Force)
  Copy-Item -LiteralPath (Join-Path $taskBundle $taskAsset.target) -Destination $taskDest
  if ((Get-FileHash -LiteralPath $taskDest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskAsset.sha256) {throw 'Installed hash mismatch'}
 }
 [void](New-Item -ItemType Directory -Path "$taskContent/maps")
 Copy-Item -LiteralPath "$taskDota/content/dota_addons/addon_template/maps/template_map.vmap" -Destination "$taskContent/maps/template_map.vmap"
 Copy-Item -LiteralPath "$taskDota/game/dota_addons/workshop_testbed/addoninfo.txt" -Destination "$taskGame/addoninfo.txt"
 foreach ($taskJob in @(@{Name='ui';Input='panorama/layout/custom_game/custom_ui_manifest.xml'},@{Name='canonical';Input='panorama/layout/custom_game/coach_probe.xml'},@{Name='map';Input='maps/template_map.vmap'})) {
  & "$taskDota/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$taskDota/game/dota" -i "$taskContent/$($taskJob.Input)" > "$taskPrefix-$($taskJob.Name)-compile.log" 2>&1
  if ($LASTEXITCODE -ne 0) {throw "Compile failed: $($taskJob.Name)"}
  Write-Output "compiled=$($taskJob.Name) exit=0"
 }
 $taskCompiled=@(Get-ChildItem -LiteralPath "$taskGame/panorama" -Recurse -File | ForEach-Object {@{path=$_.FullName.Substring($taskGame.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
 if ($taskCompiled.Count -ne 7) {throw "Expected7 compiled UI outputs, got$($taskCompiled.Count)"}
 $taskVpk=Get-Item -LiteralPath "$taskGame/maps/template_map.vpk"
 @{canonical_input_hashes=$taskReport.canonical_input_hashes;assets=$taskReport.assets;compiled=$taskCompiled;map_bytes=$taskVpk.Length;map_sha256=(Get-FileHash -LiteralPath $taskVpk.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath "$taskPrefix-hashes.json" -Encoding utf8
 Write-Output "installed_sources=9 compiled_ui=7 map_bytes=$($taskVpk.Length)"
 return
}
if ((Test-Path -LiteralPath $taskReceipt) -or (Test-Path -LiteralPath "$taskPrefix-console.log")) {throw 'Fresh launch evidence required'}
if (-not (Test-Path -LiteralPath "$taskGame/maps/template_map.vpk")) {throw 'Compile first'}
$taskArgs="-game `"$taskDota/game/dota`" -steam -addon $Addon -novid -windowed -w 1280 -h 720 -console -dev -insecure -vconsole -vconport 29000 -con_logfile `"$taskPrefix-console.log`" +dota_launch_custom_game $Addon template_map"
$taskProcess=Start-Process -FilePath "$taskDota/game/bin/win64/dota2.exe" -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;start_time_utc=$taskProcess.StartTime.ToUniversalTime().ToString('o');addon=$Addon;arguments=$taskArgs;log="$taskPrefix-console.log"} | ConvertTo-Json | Set-Content -LiteralPath $taskReceipt -Encoding utf8
Write-Output "owned_pid=$($taskProcess.Id)"
