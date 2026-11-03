$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python -m pip install --upgrade pip
python -m pip install -e ".[desktop,build]"
python -m PyInstaller --noconfirm --clean --onedir --name Roster main.py

$Executable = Join-Path $Root "dist\Roster\Roster.exe"
if (-not (Test-Path $Executable)) {
    throw "Expected portable executable was not created: $Executable"
}
& $Executable --list-providers
if ($LASTEXITCODE -ne 0) {
    throw "Packaged CLI smoke test failed"
}
Write-Host "Portable bundle created: $Executable"
