$ErrorActionPreference = "Stop"
$exe = Join-Path $PSScriptRoot "..\dist\AI Automatic Video Composer\AI Automatic Video Composer.exe"
if (-not (Test-Path $exe)) { throw "Portable EXE tidak ditemukan: $exe" }

$smokeFile = Join-Path ([System.IO.Path]::GetTempPath()) ("aavc-foundation-smoke-" + [guid]::NewGuid().ToString("N") + ".txt")
try {
  $process = Start-Process -FilePath $exe -ArgumentList @("--foundation-smoke-file", $smokeFile) -Wait -PassThru
  if ($process.ExitCode -ne 0) { throw "Foundation smoke process gagal: exit $($process.ExitCode)" }
  if (-not (Test-Path $smokeFile)) { throw "Foundation smoke token file tidak dibuat" }
  $output = Get-Content $smokeFile -Raw
  if ($output -notmatch "AAVC_FOUNDATION_SMOKE_OK") {
    throw "Foundation smoke token tidak valid: $output"
  }
}
finally {
  if (Test-Path $smokeFile) { Remove-Item $smokeFile -Force }
}

$forbidden = Get-ChildItem (Split-Path $exe) -Recurse -File | Where-Object {
  $_.Name -match '(^\.env|\.key$|\.pem$|autosave|recovery)' -or $_.FullName -match '\\cache\\|\\logs\\|\\user_data\\'
}
if ($forbidden) { throw "Forbidden runtime/user file ditemukan dalam artifact: $($forbidden.FullName -join ', ')" }
Write-Host "PORTABLE_SMOKE_OK"
