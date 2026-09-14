@echo off
title Nova Voice Assistant Launcher
echo =======================================================
echo           Nova Voice Assistant Setup & Launcher
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
    echo [ERROR] Python is not found in your system PATH or standard folders.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Activate Virtual Environment if exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo =======================================================
echo           Starting Nova Voice Assistant...
echo =======================================================
echo.
"%PYTHON_EXE%" main.py

pause
