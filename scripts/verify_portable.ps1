$ErrorActionPreference = "Stop"
$exe = Join-Path $PSScriptRoot "..\dist\AI Automatic Video Composer\AI Automatic Video Composer.exe"
if (-not (Test-Path $exe)) { throw "Portable EXE tidak ditemukan: $exe" }
$output = & $exe --foundation-smoke
if ($LASTEXITCODE -ne 0 -or ($output -join "`n") -notmatch "AAVC_FOUNDATION_SMOKE_OK") {
  throw "Foundation smoke gagal. Output: $output"
}
$forbidden = Get-ChildItem (Split-Path $exe) -Recurse -File | Where-Object {
  $_.Name -match '(^\.env|\.key$|\.pem$|autosave|recovery)' -or $_.FullName -match '\\cache\\|\\logs\\|\\user_data\\'
}
if ($forbidden) { throw "Forbidden runtime/user file ditemukan dalam artifact: $($forbidden.FullName -join ', ')" }
Write-Host "PORTABLE_SMOKE_OK"
