@echo off
cd /d "%~dp0"
python song-manager.py
if %ERRORLEVEL% NEQ 0 (
  pause
)
