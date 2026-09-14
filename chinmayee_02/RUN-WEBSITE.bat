@echo off
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
 echo Node.js is not installed. You can still open public\index.html directly.
 start "" "%~dp0public\index.html"
 pause
 exit /b
)
if not exist node_modules\express call npm install
start "" "http://localhost:5000"
node server.js
pause
