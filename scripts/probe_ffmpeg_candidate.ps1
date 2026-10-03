$ErrorActionPreference = "Stop"

$tag = "autobuild-2026-09-24-14-14"
$file = "ffmpeg-n9.0.2-3-ga5923073bf-win64-lgpl-shared-9.0.zip"
$expected = "735bae484ba2c3342bfb34df477b9c6b0f43f9819f4d2fde011be293ee1b6517"
$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/$tag/$file"

$work = Join-Path $env:RUNNER_TEMP "aavc-ffmpeg-probe"
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null
$zip = Join-Path $work $file
Invoke-WebRequest -Uri $url -OutFile $zip
$actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "FFmpeg candidate SHA256 mismatch: $actual" }

$expanded = Join-Path $work "expanded"
Expand-Archive -Path $zip -DestinationPath $expanded -Force
$ffmpeg = Get-ChildItem $expanded -Recurse -File -Filter ffmpeg.exe | Select-Object -First 1
$ffprobe = Get-ChildItem $expanded -Recurse -File -Filter ffprobe.exe | Select-Object -First 1
if (-not $ffmpeg -or -not $ffprobe) { throw "ffmpeg.exe/ffprobe.exe not found" }

$out = Join-Path $work "evidence"
New-Item -ItemType Directory -Path $out | Out-Null
& $ffmpeg.FullName -hide_banner -version 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "ffmpeg-version.txt")
& $ffmpeg.FullName -hide_banner -buildconf 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "ffmpeg-buildconf.txt")
& $ffmpeg.FullName -hide_banner -encoders 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "ffmpeg-encoders.txt")
& $ffmpeg.FullName -hide_banner -filters 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "ffmpeg-filters.txt")
& $ffmpeg.FullName -hide_banner -h encoder=h264_mf 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "h264-mf-help.txt")
& $ffmpeg.FullName -hide_banner -h encoder=libopenh264 2>&1 | Set-Content -Encoding UTF8 (Join-Path $out "libopenh264-help.txt")

$encoders = Get-Content (Join-Path $out "ffmpeg-encoders.txt") -Raw
$filters = Get-Content (Join-Path $out "ffmpeg-filters.txt") -Raw
$summary = [ordered]@{
  source_url = $url
  sha256 = $actual
  h264_mf = ($encoders -match '\bh264_mf\b')
  libopenh264 = ($encoders -match '\blibopenh264\b')
  libx264 = ($encoders -match '\blibx264\b')
  ass_filter = ($filters -match '(?m)^\s*[TSC\.]{3}\s+ass\s') -or ($filters -match '\bass\s+V->V')
  subtitles_filter = ($filters -match '\bsubtitles\s+V->V')
}
$summary | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $out "summary.json")
Get-Content (Join-Path $out "summary.json")
"EVIDENCE_DIR=$out" | Out-File -FilePath $env:GITHUB_ENV -Encoding utf8 -Append
