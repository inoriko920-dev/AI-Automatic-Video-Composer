$ErrorActionPreference = "Stop"
$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
& $python -m PyInstaller --clean --noconfirm aavc.spec
