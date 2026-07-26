@echo off
rem Keep this file pure ASCII - cmd reads .bat in the system ANSI codepage
rem (cp950 here), so Chinese inside the file gets mis-decoded and breaks it.
rem The Chinese path is fine: %~dp0 is resolved at runtime.
rem pythonw = no console window, only the small floating panel.
start "" pythonw "%~dp0dictate.py"
