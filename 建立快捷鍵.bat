@echo off
rem Pure ASCII on purpose - cmd reads .bat in the system ANSI codepage.
chcp 65001 >nul
title local-dictate - shortcut setup
python "%~dp0setup_shortcuts.py" --startup %*
echo.
pause
