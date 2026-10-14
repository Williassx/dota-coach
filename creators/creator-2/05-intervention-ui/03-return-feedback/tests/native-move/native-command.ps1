param(
 [Parameter(Mandatory=$true)][ValidateSet('Install','Launch','Check','Quit')][string]$Mode,
 [string]$Bundle='',
 [ValidateSet('dota_coach_c2_move_20261013','dota_coach_c2_move_r2_20261013','dota_coach_c2_move_r3_20261013','dota_coach_c2_move_r4_20261013','dota_coach_c2_move_r5_20261013','dota_coach_c2_move_r6_20261013','dota_coach_c2_move_r7_20261013','dota_coach_c2_move_final_20261013','dota_coach_c2_move_r8_20261013','dota_coach_c2_move_final2_20261013','dota_coach_scene_r1_20261014','dota_coach_scene_r2_20261014','dota_coach_scene_r3_20261014','dota_coach_scene_ui_20261014','dota_coach_scene_ui2_20261014')][string]$Addon='dota_coach_c2_move_final2_20261013',
 [ValidatePattern('^[a-z0-9_-]{1,32}$')][string]$Run='r1',
 [ValidatePattern('^202610(13|14)$')][string]$EvidenceDate='20261013'
)
$ErrorActionPreference='Stop'
$taskRepo=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../../')).Path
$taskDota='C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta'
$taskContent="$taskDota/content/dota_addons/$Addon"
$taskGame="$taskDota/game/dota_addons/$Addon"
$taskPrefix="$taskRepo/build/dota_coach/native-move-$Run-$EvidenceDate"
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
 $taskReport=Get-Content -LiteralPath "$taskBundle/bundle-report.json" -Raw | ConvertFrom-Json
 $taskAllowed=@('content/panorama/layout/custom_game/custom_ui_manifest.xml','content/panorama/layout/custom_game/manual_move.xml','content/panorama/styles/custom_game/manual_move.css','content/panorama/scripts/custom_game/manual_move_state.js','content/panorama/scripts/custom_game/manual_move_panel.js','game/scripts/vscripts/manual_move_controller.lua','game/scripts/vscripts/addon_game_mode.lua')
 $taskKinds=@{manual_move_source_bundle=@{Sources=7;Compiled=5};manual_move_native_test_fixture=@{Sources=9;Compiled=7};coach_scene_source_bundle=@{Sources=15;Compiled=7};coach_scene_native_test_fixture=@{Sources=18;Compiled=9}}
 $taskKind=$taskKinds[$taskReport.stage]
 if ($null -eq $taskKind -or $taskReport.assets.Count -ne $taskKind.Sources -or $taskReport.source2_compiled -ne $false -or $taskReport.runtime_verified -ne $false) {throw 'Wrong source bundle'}
 if ($taskReport.stage.StartsWith('coach_scene_')) {
  & 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $taskRepo 'creators/creator-2/11-integration/02-addon-packaging/tools/build_coach_scene.py') --verify $taskBundle
  if ($LASTEXITCODE -ne 0) {throw 'Coach source verifier refused'}
  $taskAllowed += @('game/scripts/vscripts/manual_move_game_mode.lua','game/scripts/vscripts/roster_confirmation.lua','game/scripts/vscripts/observation.lua','game/scripts/vscripts/synthetic_policy.lua','game/scripts/vscripts/order_arbiter.lua','game/scripts/vscripts/event_log.lua','content/panorama/scripts/custom_game/server_roster_panel.js','content/panorama/layout/custom_game/coach_scene.xml')
  if ($taskReport.stage -eq 'coach_scene_native_test_fixture') {$taskAllowed += @('game/scripts/vscripts/coach_scene_game_mode.lua','content/panorama/scripts/custom_game/coach_scene_fixture.js','content/panorama/layout/custom_game/coach_scene_fixture.xml')}
 }
 if ($taskReport.stage -eq 'manual_move_source_bundle') {
  & 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $taskRepo 'creators/creator-2/05-intervention-ui/03-return-feedback/tools/build_manual_move_bundle.py') --verify $taskBundle
  if ($LASTEXITCODE -ne 0) {throw 'Source verifier refused'}
 } elseif ($taskReport.stage -eq 'manual_move_native_test_fixture') {
  & 'C:/Users/Dagda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' (Join-Path $taskRepo 'creators/creator-2/05-intervention-ui/03-return-feedback/tools/build_native_move_fixture.py') --verify $taskBundle
  if ($LASTEXITCODE -ne 0) {throw 'TEST verifier refused'}
 }
 if ($taskReport.stage -eq 'manual_move_native_test_fixture') {
  $taskAllowed += @('content/panorama/layout/custom_game/manual_move_fixture.xml','content/panorama/scripts/custom_game/manual_move_fixture.js')
 }
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
 $taskJobs=@(@{Name='ui';Input='panorama/layout/custom_game/custom_ui_manifest.xml'},@{Name='map';Input='maps/template_map.vmap'})
 if ($taskReport.stage -eq 'manual_move_native_test_fixture' -or $taskReport.stage.StartsWith('coach_scene_')) {$taskJobs+=@{Name='canonical';Input='panorama/layout/custom_game/manual_move.xml'}}
 if ($taskReport.stage -eq 'coach_scene_native_test_fixture') {$taskJobs+=@{Name='coach-canonical';Input='panorama/layout/custom_game/coach_scene.xml'}}
 foreach ($taskJob in $taskJobs) {
  & "$taskDota/game/bin/win64/resourcecompiler.exe" -v -nop4 -game "$taskDota/game/dota" -i "$taskContent/$($taskJob.Input)" > "$taskPrefix-$($taskJob.Name)-compile.log" 2>&1
  if ($LASTEXITCODE -ne 0) {throw "Compile failed: $($taskJob.Name)"}
  Write-Output "compiled=$($taskJob.Name) exit=0"
 }
 $taskCompiled=@(Get-ChildItem -LiteralPath "$taskGame/panorama" -Recurse -File | ForEach-Object {@{path=$_.FullName.Substring($taskGame.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
 if ($taskCompiled.Count -ne $taskKind.Compiled) {throw "Expected $($taskKind.Compiled) compiled UI outputs, got $($taskCompiled.Count)"}
 $taskVpk=Get-Item -LiteralPath "$taskGame/maps/template_map.vpk"
 @{source_inputs=$taskReport.source_inputs;assets=$taskReport.assets;compiled=$taskCompiled;map_bytes=$taskVpk.Length;map_sha256=(Get-FileHash -LiteralPath $taskVpk.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath "$taskPrefix-hashes.json" -Encoding utf8
 Write-Output "installed_sources=$($taskReport.assets.Count) compiled_ui=$($taskCompiled.Count) map_bytes=$($taskVpk.Length)"
 return
}
if ((Test-Path -LiteralPath $taskReceipt) -or (Test-Path -LiteralPath "$taskPrefix-console.log")) {throw 'Fresh launch evidence required'}
if (-not (Test-Path -LiteralPath "$taskGame/maps/template_map.vpk")) {throw 'Compile first'}
$taskArgs="-game `"$taskDota/game/dota`" -steam -addon $Addon -novid -windowed -w 1280 -h 720 -console -dev -insecure -vconsole -vconport 29000 -con_logfile `"$taskPrefix-console.log`" +dota_launch_custom_game $Addon template_map"
$taskProcess=Start-Process -FilePath "$taskDota/game/bin/win64/dota2.exe" -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
@{pid=$taskProcess.Id;start_time_utc=$taskProcess.StartTime.ToUniversalTime().ToString('o');addon=$Addon;arguments=$taskArgs;log="$taskPrefix-console.log"} | ConvertTo-Json | Set-Content -LiteralPath $taskReceipt -Encoding utf8
Write-Output "owned_pid=$($taskProcess.Id)"
