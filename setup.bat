@echo off
setlocal enabledelayedexpansion
title Jellyfish World - Quick Setup
cd /d "%~dp0"

echo ===================================================
echo        Jellyfish World - Quick Setup
echo ===================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not on your PATH.
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [1/4] Found Python %PY_VER%

:: 2. Create virtual environment
if not exist "venv" (
    echo [2/4] Creating virtual environment (venv)...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment (venv) already exists.
)

:: 3. Install dependencies
echo [3/4] Installing dependencies from requirements.txt...
.\venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.\venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Verify installation with tests
echo [4/4] Verifying setup with unit tests...
.\venv\Scripts\python.exe -m pytest tests --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some tests did not pass. Check test logs.
) else (
    echo.
    echo ===================================================
    echo      [SUCCESS] Jellyfish World is ready!
    echo ===================================================
    echo.
    echo To start your floating companion:
    echo   - Run: .\jellyfish.cmd
    echo   - Or double-click: start.bat
    echo.
    echo To connect with AI agents (Claude Code, Cursor, OpenCode):
    echo   - Run: .\venv\Scripts\python.exe src/cli/jelly.py connect all
    echo.
)

pause
