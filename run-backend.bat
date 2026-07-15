@echo off
setlocal

cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
)

echo Installing backend dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting QA Copilot backend on http://127.0.0.1:8000 ...
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
goto :eof

:error
echo.
echo Backend startup failed.
echo Make sure Python is installed and available on PATH.
exit /b 1