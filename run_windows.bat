@echo off
setlocal

REM Start in the repository root regardless of where the script is called from.
cd /d "%~dp0"

set "PYTHON_CMD="

if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PYTHON_CMD=py -3"
    ) else (
        where python >nul 2>&1
        if %ERRORLEVEL%==0 (
            set "PYTHON_CMD=python"
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo Python was not found. Install Python 3 and try again.
    exit /b 1
)

echo Using Python command: %PYTHON_CMD%

echo Starting Sudoku desktop app
%PYTHON_CMD% tkinter_gui.py
if not %ERRORLEVEL%==0 (
    echo Failed to start the desktop app.
    exit /b 1
)
