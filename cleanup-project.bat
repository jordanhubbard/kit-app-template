@echo off
REM Cleanup script for removing partial/failed Kit project attempts (Windows)
REM Usage: cleanup-project.bat <project_name>

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Error: Project name required
    echo.
    echo Usage: %0 ^<project_name^>
    echo.
    echo Examples:
    echo   %0 my_company.explorer
    echo   %0 my_app
    echo.
    echo This will remove:
    echo   - source\apps\^<project_name^>\
    echo   - source\extensions\^<project_name^>*\
    echo   - _build\apps\^<project_name^>\
    echo   - All built artifacts in _build\
    exit /b 1
)

set PROJECT_NAME=%1
set REPO_ROOT=%~dp0

echo ================================================================
echo   Kit Project Cleanup Tool
echo ================================================================
echo.
echo Project to clean: %PROJECT_NAME%
echo.

set /p CONFIRM="Are you sure you want to remove all files for this project? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo Cleanup cancelled
    exit /b 0
)

echo.
echo Starting cleanup...
echo.

REM Remove from source\apps\
if exist "%REPO_ROOT%source\apps\%PROJECT_NAME%" (
    echo Removing: source\apps\%PROJECT_NAME%
    rmdir /s /q "%REPO_ROOT%source\apps\%PROJECT_NAME%"
    echo   [OK] Removed
) else (
    echo Skipping: source\apps\%PROJECT_NAME% ^(not found^)
)

REM Remove setup extension
set SETUP_EXT=%PROJECT_NAME%_setup
if exist "%REPO_ROOT%source\extensions\%SETUP_EXT%" (
    echo Removing: source\extensions\%SETUP_EXT%
    rmdir /s /q "%REPO_ROOT%source\extensions\%SETUP_EXT%"
    echo   [OK] Removed
) else (
    echo Skipping: Setup extension ^(not found^)
)

REM Remove from _build\apps\
if exist "%REPO_ROOT%_build\apps\%PROJECT_NAME%" (
    echo Removing: _build\apps\%PROJECT_NAME%
    rmdir /s /q "%REPO_ROOT%_build\apps\%PROJECT_NAME%"
    echo   [OK] Removed
)

REM Remove .kit symlink
if exist "%REPO_ROOT%_build\apps\%PROJECT_NAME%.kit" (
    echo Removing: _build\apps\%PROJECT_NAME%.kit
    del /q "%REPO_ROOT%_build\apps\%PROJECT_NAME%.kit"
    echo   [OK] Removed
)

REM Remove from build directories
for /d %%p in ("%REPO_ROOT%_build\*") do (
    for /d %%c in ("%%p\*") do (
        if exist "%%c\%PROJECT_NAME%.kit" (
            echo Removing: %%c\%PROJECT_NAME%.kit
            del /q "%%c\%PROJECT_NAME%.kit"
        )
        if exist "%%c\%PROJECT_NAME%.kit.bat" (
            del /q "%%c\%PROJECT_NAME%.kit.bat"
        )
        if exist "%%c\%PROJECT_NAME%.kit.sh" (
            del /q "%%c\%PROJECT_NAME%.kit.sh"
        )
        if exist "%%c\exts\%PROJECT_NAME%" (
            echo Removing: %%c\exts\%PROJECT_NAME%
            rmdir /s /q "%%c\exts\%PROJECT_NAME%"
        )
        if exist "%%c\exts\%SETUP_EXT%" (
            echo Removing: %%c\exts\%SETUP_EXT%
            rmdir /s /q "%%c\exts\%SETUP_EXT%"
        )
    )
)

echo.
echo ================================================================
echo   Cleanup Complete!
echo ================================================================
echo.
echo Project '%PROJECT_NAME%' has been completely removed.
echo You can now create a new project with the same name.
echo.

endlocal
