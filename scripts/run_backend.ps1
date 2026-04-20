Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $RepoRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\\python.exe"
$Requirements = Join-Path $RepoRoot "backend\\requirements.txt"
$BackendDir = Join-Path $RepoRoot "backend"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
}

Write-Host "Installing backend dependencies..."
& $PythonExe -m pip install --upgrade pip | Out-Null
& $PythonExe -m pip install -r $Requirements

Push-Location $BackendDir
try {
    & $PythonExe -m uvicorn app.main:app --reload
}
finally {
    Pop-Location
}

