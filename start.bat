@echo off
title Jellyfish World Companion
cd /d "%~dp0"
.\venv\Scripts\python.exe src\companion\session.py %*
