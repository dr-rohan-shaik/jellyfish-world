@echo off
cd /d "%~dp0"
.\venv\Scripts\python.exe src\ui\preview.py --cycles 1
pause
