@echo off

:: Set OMNI_REPO_ROOT early so `repo` bootstrapping can target the repository
:: root when writing out Python dependencies.
:: Use SETLOCAL and ENDLOCAL to constrain these variables to this batch file.
:: Use ENABLEDELAYEDEXPANSION to evaluate the value of PM_PACKAGES_ROOT
:: at execution time.
SETLOCAL ENABLEDELAYEDEXPANSION
set OMNI_REPO_ROOT="%~dp0"

:: Set Packman cache directory early if repo-cache.json is configured
:: so that the Packman Python version is not fetched from the web.
IF NOT EXIST "%~dp0repo-cache.json" goto :RepoCacheEnd

:: Read PM_PACKAGES_ROOT from repo-cache.json and make sure it is an absolute path (assume relative to the script directory).
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "$PM_PACKAGES_ROOT = (Get-Content '%~dp0repo-cache.json' | ConvertFrom-Json).PM_PACKAGES_ROOT; if ([System.IO.Path]::IsPathRooted($PM_PACKAGES_ROOT)) { Write-Output ('absolute;' + $PM_PACKAGES_ROOT) } else { Write-Output ('relative;' + $PM_PACKAGES_ROOT) }"`) do (
    for /f "tokens=1,2 delims=;" %%A in ("%%i") do (
        if /i "%%A" == "relative" (
            set PM_PACKAGES_ROOT=%~dp0%%B
        ) else (
            set PM_PACKAGES_ROOT=%%B
        )
    )
)

:RepoCacheEnd

:: Check for special playground commands
if "%1"=="playground" (
    if "%2"=="install" goto PlaygroundInstall
    if "%2"=="dev" goto PlaygroundDev
    if "%2"=="build" goto PlaygroundBuild
    if "%2"=="" goto PlaygroundRun
)

if "%1"=="playground-install" goto PlaygroundInstall
if "%1"=="playground-dev" goto PlaygroundDev
if "%1"=="playground-build" goto PlaygroundBuild

:: Default: Use the Python dispatcher for enhanced template functionality and fallback to repoman
call "%~dp0tools\packman\python.bat" "%~dp0tools\repoman\repo_dispatcher.py" %*
if %errorlevel% neq 0 ( goto Error )
goto Success

:PlaygroundInstall
echo Installing Kit Playground dependencies...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed. Please install Node.js first.
    echo.
    echo Download from: https://nodejs.org/en/download/
    echo Or use: winget install OpenJS.NodeJS
    goto Error
)
cd /d "%~dp0kit_playground"
call npm install
if %errorlevel% neq 0 ( goto Error )
echo Kit Playground is ready! Run 'repo.bat playground' to launch.
goto Success

:PlaygroundRun
echo Launching Kit Playground...
if not exist "%~dp0kit_playground\node_modules" (
    echo Kit Playground dependencies not installed. Installing first...
    goto PlaygroundInstall
)
cd /d "%~dp0kit_playground"
call npm start
if %errorlevel% neq 0 ( goto Error )
goto Success

:PlaygroundDev
echo Starting Kit Playground in development mode...
cd /d "%~dp0kit_playground"
call npm run dev
if %errorlevel% neq 0 ( goto Error )
goto Success

:PlaygroundBuild
echo Building Kit Playground for production...
cd /d "%~dp0kit_playground"
call npm run build
if %errorlevel% neq 0 ( goto Error )

:Success
ENDLOCAL
exit /b 0

:Error
ENDLOCAL
exit /b %errorlevel%