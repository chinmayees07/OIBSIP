@echo off
title Nova AI Setup
setlocal EnableExtensions
cd /d "%~dp0"
echo =====================================================
echo        NOVA VOICE ASSISTANT - AI SETUP
echo =====================================================
echo.
if not exist ".env" copy /Y ".env.example" ".env" >nul
set /p KEY=Paste your OpenAI API key (leave blank to edit .env yourself): 
if "%KEY%"=="" goto done
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='.env'; $s=Get-Content -Raw $p; $s=[regex]::Replace($s,'(?m)^OPENAI_API_KEY=.*$',[regex]::Escape('OPENAI_API_KEY=%KEY%')); $s=$s -replace '\\',''; Set-Content -Path $p -Value $s -Encoding UTF8"
echo API key saved.
:done
echo.
echo Start the assistant with run_web.bat
pause
