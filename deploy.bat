@echo off
cd /d "%~dp0"

echo ================================
echo   Fumiha BGM SHOP Deploy
echo ================================
echo(

git status --short > tmp_status.txt 2>&1
for %%i in (tmp_status.txt) do set FILESIZE=%%~zi
del tmp_status.txt

if "%FILESIZE%"=="0" (
  echo No changes. Nothing to push.
  echo(
  pause
  exit /b
)

echo Changed files:
git status --short
echo(

set /p MSG=Commit message (e.g. add new song):

if "%MSG%"=="" set MSG=update

echo(
git add .
git commit -m "%MSG%"
git push

echo(
echo ================================
if %ERRORLEVEL%==0 (
  echo   Done! Site has been updated.
) else (
  echo   Error occurred.
)
echo ================================
echo(
pause
