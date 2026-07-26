@echo off
rem Keep this file pure ASCII. cmd reads .bat in the system ANSI codepage
rem (cp950 on Traditional Chinese Windows), so Chinese text inside a .bat
rem gets mis-decoded and breaks the commands. Chinese PATHS are fine.
chcp 65001 >nul
title local-dictate - installer

echo.
echo === local-dictate installer ===
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [X] Python not found in PATH.
  echo     Install Python 3.10+ from https://www.python.org/downloads/
  echo     and tick "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)

echo [1/2] Installing dependencies...
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
  echo [X] pip install failed. See the messages above.
  pause
  exit /b 1
)

echo.
echo [2/2] Preparing your vocabulary file...
if exist "%~dp0vocab.txt" (
  echo     vocab.txt already exists - leaving it alone.
) else (
  copy "%~dp0vocab.example.txt" "%~dp0vocab.txt" >nul
  echo     Created vocab.txt from the example. Edit it with your own terms.
)

echo.
echo === Done ===
echo Start it by double-clicking the launcher .bat next to this file.
echo The first run downloads the whisper model ^(~1.5GB^) and takes a while.
echo.
echo Optional - run at logon:
echo   Win+R  ^>  shell:startup  ^>  drop a shortcut to the launcher there.
echo.
pause
