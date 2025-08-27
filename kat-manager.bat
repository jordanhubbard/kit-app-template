@echo off
REM Kat Manager - Windows Entrypoint
REM Cross-platform template system for Omniverse Kit applications and extensions

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Fast path commands - these try system Python first before setting up venv
set "FAST_PATH_COMMANDS=list schema"

REM Handle special commands
if "%1"=="clean" (
    echo 🧹 Cleaning Kat Manager environment...
    python "%SCRIPT_DIR%\kat_env_manager.py" clean
    exit /b %ERRORLEVEL%
)

if "%1"=="status" (
    REM Status is always fast since it doesn't need dependencies
    python "%SCRIPT_DIR%\kat_env_manager.py" status
    exit /b %ERRORLEVEL%
)

if "%1"=="deploy" (
    if "%2"=="" (
        echo ❌ Deploy command requires source name and target path
        echo Usage: kat-manager deploy ^<source_name^> ^<target_path^>
        echo.
        echo Available templates:
        python "%SCRIPT_DIR%\kat_env_manager.py" list
        exit /b 1
    )
    if "%3"=="" (
        echo ❌ Deploy command requires target path
        echo Usage: kat-manager deploy ^<source_name^> ^<target_path^>
        exit /b 1
    )
    python "%SCRIPT_DIR%\kat_env_manager.py" deploy --source "%2" --target "%3"
    exit /b %ERRORLEVEL%
)

if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="" goto :show_help

REM Try fast path first for eligible commands
call :try_fast_path %*
if !ERRORLEVEL!==0 exit /b 0

REM Fall back to full venv setup for all commands (fast path failed or not applicable)
python "%SCRIPT_DIR%\kat_env_manager.py" run %*
exit /b %ERRORLEVEL%

:try_fast_path
REM Check if this is a fast path command and try system Python first
set cmd=%1
echo !FAST_PATH_COMMANDS! | findstr /b /w "!cmd!" >nul
if !ERRORLEVEL!==0 (
    REM Try system Python first (suppress errors)
    python "%SCRIPT_DIR%\kat-manager" %* >nul 2>&1
    if !ERRORLEVEL!==0 (
        REM Success with system Python, run it again with output
        python "%SCRIPT_DIR%\kat-manager" %*
        exit /b 0
    )
)
REM Fast path not applicable or failed
exit /b 1

:show_help
echo Kat Manager - Modern Template System for Omniverse Kit
echo.
echo USAGE:
echo   kat-manager ^<command^> [options]
echo.
echo TEMPLATE COMMANDS:
echo   list                     List available templates
echo   generate ^<template^>      Generate from template
echo   schema ^<template^>        Show template schema
echo   validate ^<template^>      Validate configuration
echo.
echo ENVIRONMENT COMMANDS:
echo   status                   Show environment status
echo   clean                    Remove virtual environment and generated content
echo   deploy ^<name^> ^<path^>     Deploy generated template to external location
echo.
echo EXAMPLES:
echo   kat-manager list
echo   kat-manager generate kit_base_editor -c config.yaml
echo   kat-manager deploy my_app C:\Projects\
echo   kat-manager clean
echo.
echo For detailed help on template commands:
echo   kat-manager generate --help
echo   kat-manager schema --help
exit /b 0