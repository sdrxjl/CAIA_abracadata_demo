@echo off
setlocal
cd /d "%~dp0"

set "APP_URL=http://127.0.0.1:8000"
set "LOG_FILE=%~dp0server.log"
set "PYTHON_CMD="
set "LOCAL_ANACONDA=C:\Users\hanyi\anaconda3\python.exe"

netstat -ano | findstr /r /c:":8000 .*LISTENING" >nul 2>nul
if not errorlevel 1 goto :open_browser

if exist "%LOCAL_ANACONDA%" (
  set "PYTHON_CMD=%LOCAL_ANACONDA%"
  goto :run
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  goto :run
)

for /f "delims=" %%i in ('where python 2^>nul') do (
  set "PYTHON_CMD=%%i"
  goto :run
)

for /f "delims=" %%i in ('where python3 2^>nul') do (
  set "PYTHON_CMD=%%i"
  goto :run
)

echo Could not find a usable Python executable.
echo.
echo Please install Python 3 and make sure one of these works:
echo   %LOCAL_ANACONDA%
echo   py -3
echo   python
echo   python3
echo.
echo Then run this launcher again.
pause
exit /b 1

:run
echo Starting CAIA Navigator with:
echo %PYTHON_CMD%
echo.
echo Do not close the server window while using the app.
echo Logs will be written to:
echo %LOG_FILE%
echo.
start "CAIA Navigator Server" cmd /k "%PYTHON_CMD% -u "%~dp0caia_navigator_server.py" 1>> "%LOG_FILE%" 2>&1"
timeout /t 3 >nul

:open_browser
start "" "%APP_URL%"
endlocal
