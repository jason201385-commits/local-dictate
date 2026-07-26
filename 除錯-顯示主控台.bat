@echo off
rem Debug launcher: keeps the console visible so errors are readable.
rem Pure ASCII on purpose - see the note in the main launcher.
chcp 65001 >nul
title Dictation Engine - debug console
python "%~dp0dictate.py"
echo.
echo (stopped - press any key to close)
pause >nul
