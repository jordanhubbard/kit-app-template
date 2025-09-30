@echo off
REM Build Kit Playground for Windows

echo ======================================
echo Kit Playground Build Script
echo ======================================
echo.

REM Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 16+ first.
    echo   Download from: https://nodejs.org/en/download/
    exit /b 1
)

echo Node.js version:
node --version

REM Check npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: npm not found. Please install npm first.
    exit /b 1
)

echo npm version:
npm --version

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    echo   Download from: https://www.python.org/downloads/
    exit /b 1
)

echo Python version:
python --version
echo.

REM Install npm dependencies
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
) else (
    echo npm dependencies already installed
)

REM Install Python dependencies
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r backend\requirements.txt
) else (
    echo Python dependencies already installed
)

echo.
echo ======================================
echo Building Production Distributable
echo ======================================
echo.

REM Build React app
echo Building React app...
call npm run build

REM Build Electron app
echo Building Electron installer...
call npm run dist

echo.
echo ======================================
echo Build Complete!
echo ======================================
echo.

if exist "dist\Kit Playground Setup 1.0.0.exe" (
    echo Installer created:
    dir "dist\Kit Playground Setup 1.0.0.exe"
    echo.
    echo To install:
    echo   "dist\Kit Playground Setup 1.0.0.exe"
) else (
    echo WARNING: Installer not found in dist\
    echo Check for errors above.
)

pause