$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Installing the Windows packaging dependencies..."
python -m pip install --upgrade pip
python -m pip install -e ".[desktop,build]"

Write-Host "Building the ROSTER portable folder..."
python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name ROSTER `
  --distpath dist `
  --workpath build/pyinstaller/work `
  --specpath build/pyinstaller/spec `
  --collect-submodules roster `
  --collect-all sounddevice `
  --collect-all pyttsx3 `
  --collect-all PySide6 `
  --hidden-import pyttsx3.drivers.sapi5 `
  --hidden-import pythoncom `
  --hidden-import pywintypes `
  --hidden-import win32com.client `
  main.py

if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller failed with exit code $LASTEXITCODE."
}

$exe = Join-Path $repoRoot "dist\ROSTER\ROSTER.exe"
if (-not (Test-Path $exe)) {
  throw "Expected packaged executable was not created: $exe"
}

Write-Host "Portable bundle created at: $exe"
Write-Host "This build does not contain API keys. Configure secrets on the target PC."
