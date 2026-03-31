@echo off
setlocal

REM Start in the repository root regardless of where the script is called from.
cd /d "%~dp0"

set "BOOTSTRAP_PYTHON="
set "VENV_DIR=venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "ACTIVATE_CMD=%VENV_DIR%\Scripts\activate.bat"

if not exist "%VENV_PYTHON%" (
    echo No virtual environment found at %VENV_DIR%. Creating one now...

    where py >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "BOOTSTRAP_PYTHON=py -3"
    ) else (
        where python >nul 2>&1
        if %ERRORLEVEL%==0 (
            set "BOOTSTRAP_PYTHON=python"
        )
    )
)

if not exist "%VENV_PYTHON%" if "%BOOTSTRAP_PYTHON%"=="" (
    echo Python was not found, so the virtual environment could not be created.
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    %BOOTSTRAP_PYTHON% -m venv "%VENV_DIR%"
    if not %ERRORLEVEL%==0 (
        echo Failed to create the virtual environment.
        exit /b 1
    )
)

if not exist "%ACTIVATE_CMD%" (
    echo Virtual environment activation script was not found at %ACTIVATE_CMD%.
    exit /b 1
)

echo Activating virtual environment: %ACTIVATE_CMD%
call "%ACTIVATE_CMD%"
if not %ERRORLEVEL%==0 (
    echo Failed to activate the virtual environment.
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    echo Virtual environment Python was not found at %VENV_PYTHON%.
    exit /b 1
)

echo Using Python command: %VENV_PYTHON%
echo Starting Sudoku desktop app
"%VENV_PYTHON%" tkinter_gui.py
if not %ERRORLEVEL%==0 (
    echo Failed to start the desktop app.
    exit /b 1
)
