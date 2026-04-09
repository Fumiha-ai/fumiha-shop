@echo off
cd /d "%~dp0"
echo 起動中...
python song-manager.py
echo.
echo 終了コード: %ERRORLEVEL%
pause
