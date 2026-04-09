@echo off
cd /d "%~dp0"

where code >nul 2>&1
if %ERRORLEVEL%==0 (
  code songs.js
) else (
  notepad songs.js
)
