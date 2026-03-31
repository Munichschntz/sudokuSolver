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

REM Install runtime dependencies if they are missing.
%PYTHON_CMD% -c "import fastapi, uvicorn, sqlalchemy, bcrypt" >nul 2>&1
if not %ERRORLEVEL%==0 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install fastapi uvicorn sqlalchemy bcrypt python-multipart jinja2
    if not %ERRORLEVEL%==0 (
        echo Failed to install dependencies.
        exit /b 1
    )
)

echo Starting Sudoku web app on http://127.0.0.1:8000
%PYTHON_CMD% -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
