# Jellyfish World - Quick Setup for PowerShell
$ErrorActionPreference = "Stop"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "       Jellyfish World — Quick Setup" -ForegroundColor Cyan
Write-Host "===================================================`n" -ForegroundColor Cyan

# 1. Check Python
try {
    $pyVer = & python --version 2>&1
    Write-Host "[1/4] Found $pyVer" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in your PATH. Please install Python 3.11+."
}

# 2. Virtual Environment
$venvPath = Join-Path $PSScriptRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[2/4] Creating virtual environment (venv)..." -ForegroundColor Yellow
    & python -m venv $venvPath
} else {
    Write-Host "[2/4] Virtual environment already exists." -ForegroundColor Green
}

$pyExe = Join-Path $venvPath "Scripts\python.exe"

# 3. Dependencies
Write-Host "[3/4] Installing requirements..." -ForegroundColor Yellow
& $pyExe -m pip install --quiet --upgrade pip
& $pyExe -m pip install --quiet -r (Join-Path $PSScriptRoot "requirements.txt")

# 4. Verify with Tests
Write-Host "[4/4] Verifying with test suite..." -ForegroundColor Yellow
$env:PYTHONPATH = $PSScriptRoot
& $pyExe -m pytest (Join-Path $PSScriptRoot "tests") --quiet

Write-Host "`n===================================================" -ForegroundColor Green
Write-Host "      [SUCCESS] Jellyfish World is ready!" -ForegroundColor Green
Write-Host "===================================================`n" -ForegroundColor Green
Write-Host "To start:          .\jellyfish.ps1" -ForegroundColor Cyan
Write-Host "To connect agents: .\venv\Scripts\python.exe src/cli/jelly.py connect all" -ForegroundColor Cyan
