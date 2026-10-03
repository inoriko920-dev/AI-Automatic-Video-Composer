param(
  [Parameter(Mandatory = $true)][string]$ZipPath
)

$ErrorActionPreference = "Stop"
$zip = Resolve-Path $ZipPath
$verifyRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("aavc-rc-verify-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $verifyRoot | Out-Null
try {
  Expand-Archive -Path $zip -DestinationPath $verifyRoot -Force
  $exe = Get-ChildItem $verifyRoot -Recurse -File -Filter "AI Automatic Video Composer.exe" | Select-Object -First 1
  if (-not $exe) { throw "RC EXE tidak ditemukan setelah ekstraksi" }

  $smokeFile = Join-Path $verifyRoot "foundation-smoke.txt"
  $process = Start-Process -FilePath $exe.FullName -ArgumentList @("--foundation-smoke-file", $smokeFile) -Wait -PassThru
  if ($process.ExitCode -ne 0) { throw "Packaged RC smoke process gagal: exit $($process.ExitCode)" }
  if (-not (Test-Path $smokeFile)) { throw "Packaged RC smoke token file tidak dibuat" }
  $output = Get-Content $smokeFile -Raw
  if ($output -notmatch "AAVC_FOUNDATION_SMOKE_OK") {
    throw "Packaged RC smoke token tidak valid: $output"
  }
  Remove-Item $smokeFile -Force

  $stage = $exe.Directory.FullName
  $buildInfo = Join-Path $stage "BUILD_INFO.txt"
  $manifest = Join-Path $stage "MANIFEST.tsv"
  if (-not (Test-Path $buildInfo)) { throw "BUILD_INFO.txt tidak ada di RC" }
  if (-not (Test-Path $manifest)) { throw "MANIFEST.tsv tidak ada di RC" }

  $forbidden = Get-ChildItem $stage -Recurse -Force | Where-Object {
    $_.Name -match '(^\.env|\.pem$|\.key$|\.pfx$|\.p12$|autosave|recovery|\.log$)' -or
    $_.FullName -match '\\.git(\\|$)|\\__pycache__(\\|$)|\\\.pytest_cache(\\|$)|\\user_data(\\|$)|\\cache(\\|$)|\\logs(\\|$)'
  }
  if ($forbidden) {
    throw "Forbidden/debug/user file ditemukan dalam RC: $($forbidden.FullName -join ', ')"
  }

  $textExtensions = @('.txt', '.json', '.md', '.ini', '.toml', '.yaml', '.yml', '.cfg')
  foreach ($file in Get-ChildItem $stage -Recurse -File) {
    if ($textExtensions -contains $file.Extension.ToLowerInvariant()) {
      $text = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
      if ($null -ne $text) {
        if ($text -match 'AIza[0-9A-Za-z_-]{30,}' -or $text -match '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----') {
          throw "Possible credential/private key ditemukan dalam RC text: $($file.FullName)"
        }
      }
    }
  }

  $rows = Import-Csv $manifest -Delimiter "`t"
  if (-not $rows) { throw "MANIFEST.tsv kosong" }
  foreach ($row in $rows) {
    $path = Join-Path $stage ($row.path -replace '/', '\')
    if (-not (Test-Path $path)) { throw "Manifest file hilang: $($row.path)" }
    $actual = (Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $row.sha256) { throw "Manifest hash mismatch: $($row.path)" }
    $size = (Get-Item $path).Length
    if ([int64]$row.bytes -ne $size) { throw "Manifest size mismatch: $($row.path)" }
  }

  Write-Host "RC_EXTRACTED_SMOKE_OK"
  Write-Host "RC_HYGIENE_OK"
  Write-Host "RC_MANIFEST_OK"
}
finally {
  if (Test-Path $verifyRoot) { Remove-Item $verifyRoot -Recurse -Force }
}
