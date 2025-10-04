@echo off
REM Kit Playground Development Mode for Windows
REM Runs backend and frontend with hot-reloading

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set UI_DIR=%SCRIPT_DIR%ui
set BACKEND_DIR=%SCRIPT_DIR%backend

echo ╔════════════════════════════════════════════════════════════╗
echo ║  Kit Playground Development Mode                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is required for development mode
    echo Install from: https://nodejs.org/
    exit /b 1
)

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 is required
    exit /b 1
)

REM Check if we have npm packages
if not exist "%UI_DIR%\node_modules" (
    echo Installing npm dependencies...
    cd "%UI_DIR%"
    call npm install
    cd "%SCRIPT_DIR%"
)

echo Starting services:
echo   • Backend API:  http://localhost:8081
echo   • Frontend UI:  http://localhost:3000 (with hot-reload)
echo.
echo Changes to React/TypeScript files will hot-reload automatically!
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in background
echo [1/2] Starting Backend API server...
cd "%BACKEND_DIR%"
start /B python web_server.py --port 8081 > %TEMP%\playground-backend.log 2>&1

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend dev server
echo [2/2] Starting React dev server with hot-reload...
cd "%UI_DIR%"
set BROWSER=none
call npm start

REM When npm start exits (user pressed Ctrl+C), we're done
echo.
echo Shutting down servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq web_server.py*" >nul 2>nul

endlocal
