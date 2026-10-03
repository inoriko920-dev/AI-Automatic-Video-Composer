param(
  [Parameter(Mandatory = $true)][string]$Version,
  [Parameter(Mandatory = $true)][string]$SourceSha
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$dist = Join-Path $root "dist\AI Automatic Video Composer"
if (-not (Test-Path $dist)) { throw "PyInstaller onedir tidak ditemukan: $dist" }

$out = Join-Path $root "artifacts\rc"
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

$safeVersion = $Version -replace '[^0-9A-Za-z._-]', '-'
$artifactName = "AI-Automatic-Video-Composer_${safeVersion}_win64"
$stage = Join-Path $out $artifactName
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item (Join-Path $dist "*") $stage -Recurse -Force

$builtUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$pythonVersion = (& python --version 2>&1) -join " "
@(
  "product=AI Automatic Video Composer"
  "version=$Version"
  "source_sha=$SourceSha"
  "built_utc=$builtUtc"
  "python=$pythonVersion"
  "workflow_run_id=$env:GITHUB_RUN_ID"
  "workflow_run_number=$env:GITHUB_RUN_NUMBER"
) | Set-Content -Encoding UTF8 (Join-Path $stage "BUILD_INFO.txt")

$manifestPath = Join-Path $stage "MANIFEST.tsv"
$manifestRows = New-Object System.Collections.Generic.List[string]
$manifestRows.Add("sha256`tbytes`tpath")
$files = Get-ChildItem $stage -Recurse -File | Where-Object { $_.FullName -ne $manifestPath } | Sort-Object FullName
foreach ($file in $files) {
  $relative = $file.FullName.Substring($stage.Length + 1).Replace('\', '/')
  $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $manifestRows.Add("$hash`t$($file.Length)`t$relative")
}
$manifestRows | Set-Content -Encoding UTF8 $manifestPath

$provenance = [ordered]@{
  product = "AI Automatic Video Composer"
  version = $Version
  source_sha = $SourceSha
  built_utc = $builtUtc
  runner_os = $env:RUNNER_OS
  runner_arch = $env:RUNNER_ARCH
  workflow = $env:GITHUB_WORKFLOW
  workflow_run_id = $env:GITHUB_RUN_ID
  workflow_run_number = $env:GITHUB_RUN_NUMBER
  python = $pythonVersion
  packaged_file_count = (Get-ChildItem $stage -Recurse -File).Count
}
$provenance | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $out "PROVENANCE.json")

$zip = Join-Path $out "$artifactName.zip"
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -CompressionLevel Optimal
$zipHash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
"$zipHash  $artifactName.zip" | Set-Content -Encoding ASCII (Join-Path $out "CHECKSUMS.sha256")

Write-Host "RC_ARCHIVE=$zip"
Write-Host "RC_SHA256=$zipHash"
