@echo off
REM Kat Manager - Windows Entrypoint
REM Cross-platform template system for Omniverse Kit applications and extensions

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Handle special commands
if "%1"=="clean" (
    echo 🧹 Cleaning Kat Manager environment...
    python "%SCRIPT_DIR%\kat_env_manager.py" clean
    exit /b %ERRORLEVEL%
)

if "%1"=="status" (
    python "%SCRIPT_DIR%\kat_env_manager.py" status
    exit /b %ERRORLEVEL%
)

if "%1"=="list" (
    python "%SCRIPT_DIR%\kat_env_manager.py" list
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

REM All other commands go through the environment manager
python "%SCRIPT_DIR%\kat_env_manager.py" run %*
exit /b %ERRORLEVEL%

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
