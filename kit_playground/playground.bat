@echo off
REM Kit Playground Launcher Script for Windows
REM This script builds the UI and launches the Kit Playground web interface

setlocal enabledelayedexpansion

echo Kit Playground Launcher
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "UI_DIR=%SCRIPT_DIR%ui"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "BUILD_DIR=%UI_DIR%\build"

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed
        echo Please install Python from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)
echo [OK] Python is installed

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js is installed

REM Check for npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed
    echo Please install npm (usually comes with Node.js)
    pause
    exit /b 1
)
echo [OK] npm is installed

REM Install Python dependencies
echo.
echo Installing Python dependencies...
%PYTHON_CMD% -m pip install -r "%BACKEND_DIR%\requirements.txt" --quiet

REM Check if build exists
if not exist "%BUILD_DIR%" (
    echo.
    echo [WARNING] UI build not found. Building...
    cd "%UI_DIR%"
    call npm install
    call npm run build
    cd "%SCRIPT_DIR%"
)

REM Launch the server
echo.
echo Launching Kit Playground...
echo The web interface will open in your default browser
echo Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% "%BACKEND_DIR%\web_server.py" --port 8081 --open-browser

pause
