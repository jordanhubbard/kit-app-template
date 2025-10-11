@echo off
REM Kit Playground Development Mode for Windows
REM Runs backend and frontend with hot-reloading
REM
REM Usage: dev.bat                    - Local mode (localhost)
REM        set REMOTE=1 & dev.bat     - Remote mode (0.0.0.0)

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set UI_DIR=%SCRIPT_DIR%ui
set BACKEND_DIR=%SCRIPT_DIR%backend

REM Determine host based on REMOTE environment variable
if "%REMOTE%"=="1" (
    set BACKEND_HOST=0.0.0.0
    set FRONTEND_HOST=0.0.0.0
    set DISPLAY_HOST=0.0.0.0
) else (
    set BACKEND_HOST=localhost
    set FRONTEND_HOST=localhost
    set DISPLAY_HOST=localhost
)

REM Find available ports using Python
echo Finding available ports...
for /f "tokens=1,2" %%a in ('python "%SCRIPT_DIR%\find_free_port.py" 2 8000') do (
    set BACKEND_PORT=%%a
    set FRONTEND_PORT=%%b
)

if "%BACKEND_PORT%"=="" (
    echo [ERROR] Failed to find available ports
    exit /b 1
)

echo ╔════════════════════════════════════════════════════════════╗
echo ║  Kit Playground - Development Mode                        ║
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

echo Services:
echo   • Backend API:  http://%DISPLAY_HOST%:%BACKEND_PORT%
echo   • Frontend UI:  http://%DISPLAY_HOST%:%FRONTEND_PORT%
if "%REMOTE%"=="1" (
    echo   ⚠ Remote mode: Listening on 0.0.0.0 ^(all interfaces^)
)
echo.
echo Press Ctrl+C to stop servers
echo.

REM Create temporary setupProxy.js with dynamic backend port
REM Important: The proxy (Node.js server) always connects to localhost because
REM it runs on the same machine as the backend. The router function handles
REM remote browser connections by extracting the hostname from the request.
(
echo const { createProxyMiddleware } = require('http-proxy-middleware'^);
echo.
echo module.exports = function(app^) {
echo   app.use(
echo     '/api',
echo     createProxyMiddleware({
echo       target: 'http://localhost:%BACKEND_PORT%',
echo       changeOrigin: true,
echo       logLevel: 'warn',
echo       router: function(req^) {
echo         const requestHost = req.headers.host;
echo         if (requestHost ^&^& !requestHost.includes('localhost'^) ^&^& !requestHost.includes('127.0.0.1'^)^) {
echo           const backendUrl = 'http://' + requestHost.split(':'^)[0] + ':%BACKEND_PORT%';
echo           console.log('[Proxy] Routing to:', backendUrl^);
echo           return backendUrl;
echo         }
echo         return 'http://localhost:%BACKEND_PORT%';
echo       },
echo     }^)
echo   ^);
echo };
) > "%UI_DIR%\src\setupProxy.js"

REM Start backend in background
echo [1/2] Starting Backend API server...
cd "%BACKEND_DIR%"
start /B python web_server.py --host %BACKEND_HOST% --port %BACKEND_PORT% --debug > %TEMP%\playground-backend.log 2>&1

REM Wait for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend dev server
echo [2/2] Starting React dev server...
cd "%UI_DIR%"
set BROWSER=none
set PORT=%FRONTEND_PORT%
if "%REMOTE%"=="1" (
    set HOST=%FRONTEND_HOST%
    set DANGEROUSLY_DISABLE_HOST_CHECK=true
)
call npm start

REM When npm start exits (user pressed Ctrl+C), cleanup
echo.
echo Shutting down servers...
del /F /Q "%UI_DIR%\src\setupProxy.js" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq web_server.py*" >nul 2>nul

endlocal
