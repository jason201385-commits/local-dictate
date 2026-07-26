@echo off
rem Pure ASCII on purpose - cmd reads .bat in the system ANSI codepage.
chcp 65001 >nul
title local-dictate - environment check
python "%~dp0doctor.py"
echo.
pause
