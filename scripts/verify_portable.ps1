$ErrorActionPreference = "Stop"
$dist = Join-Path $PSScriptRoot "..\dist\AI Automatic Video Composer"
$exe = Join-Path $dist "AI Automatic Video Composer.exe"
if (-not (Test-Path $exe)) { throw "Portable EXE tidak ditemukan: $exe" }

$marker = Join-Path $PSScriptRoot "..\artifacts\portable-smoke.txt"
New-Item -ItemType Directory -Force (Split-Path $marker) | Out-Null
if (Test-Path $marker) { Remove-Item $marker -Force }
$arguments = @("--foundation-smoke", "--foundation-smoke-file", $marker)
$process = Start-Process -FilePath $exe -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "Foundation smoke gagal dengan exit code $($process.ExitCode)" }
if (-not (Test-Path $marker)) { throw "Foundation smoke marker tidak dibuat" }
$smoke = Get-Content $marker -Raw
if ($smoke -notmatch "AAVC_FOUNDATION_SMOKE_OK") { throw "Foundation smoke token tidak valid: $smoke" }

$requiredNames = @(
  "project.schema.json",
  "RELEASE_NOTES_0.1.0.md",
  "MAINTENANCE.md",
  "BACKUP_AND_RECOVERY.md"
)
foreach ($requiredName in $requiredNames) {
  $found = Get-ChildItem $dist -Recurse -File -Filter $requiredName | Select-Object -First 1
  if (-not $found) { throw "$requiredName tidak ditemukan dalam portable artifact" }
}

$ffmpegReadme = Get-ChildItem $dist -Recurse -File -Filter "README.md" | Where-Object {
  $_.FullName -match 'tools\\ffmpeg'
} | Select-Object -First 1
if (-not $ffmpegReadme) { throw "FFmpeg runtime policy README tidak ditemukan" }

# Block secret/runtime artifacts, but allow documentation files whose names contain
# words such as BACKUP or RECOVERY.
$forbidden = Get-ChildItem $dist -Recurse -File | Where-Object {
  $_.Name -match '(^\.env($|\.)|\.key$|\.pem$|\.autosave($|\.)|\.recovery($|\.))' -or
  $_.FullName -match '\\cache\\|\\logs\\|\\user_data\\|\\runtime_data\\'
}
if ($forbidden) { throw "Forbidden runtime/user file ditemukan dalam artifact: $($forbidden.FullName -join ', ')" }

Write-Host "PORTABLE_SMOKE_OK"
Write-Host "EXE=$exe"
Write-Host "FINAL_RELEASE_DOCS_OK"
