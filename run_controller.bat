@echo off
title Flappy Bird Hand Gesture Controller
echo ===================================================
echo Starting Flappy Bird Hand Gesture Controller...
echo ===================================================

REM Check for virtual environment in .venv
if exist ".venv\Scripts\activate.bat" (
    echo Activating Python virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo Activating Python virtual environment (venv)...
    call venv\Scripts\activate.bat
)

REM Run Python script
python MP.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Notice] Python exited with code %ERRORLEVEL%.
    echo If packages are missing, run: pip install -r requirements.txt
    pause
)
