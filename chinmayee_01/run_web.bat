@echo off
title Nova Voice Assistant — Web Application Launcher
echo =======================================================
echo        Nova Voice Assistant — Web App Setup & Launcher
echo =======================================================
echo.

:: Detect Python executable
set "PYTHON_EXE="
if exist "venv\Scripts\python.exe" set "PYTHON_EXE=venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%USERPROFILE%\.gemini\antigravity\tools\python\python.exe" set "PYTHON_EXE=%USERPROFILE%\.gemini\antigravity\tools\python\python.exe"
if not defined PYTHON_EXE (
    where py >nul 2>nul && set "PYTHON_EXE=py"
)
if not defined PYTHON_EXE (
    where python >nul 2>nul && set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo [ERROR] Python was not found in your system PATH or standard folders.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [INFO] Using Python: %PYTHON_EXE%
echo [INFO] Starting Nova Web Application at http://localhost:5000...
echo [INFO] Your browser will open automatically.
echo.

"%PYTHON_EXE%" web_app.py

pause
