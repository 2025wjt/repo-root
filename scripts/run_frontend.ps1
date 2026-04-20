Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $RepoRoot "frontend"
$NodeModulesDir = Join-Path $FrontendDir "node_modules"

Push-Location $FrontendDir
try {
    if (-not (Test-Path $NodeModulesDir)) {
        Write-Host "Installing frontend dependencies..."
        npm install
    }

    npm run dev
}
finally {
    Pop-Location
}

