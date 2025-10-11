@echo off
REM Wrapper script to call repository root repo.bat from any app directory
REM Automatically finds the repository root by walking up the directory tree

setlocal enabledelayedexpansion

:find_repo_root
set "current_dir=%CD%"

:loop
if exist "%current_dir%\repo.bat" (
    if exist "%current_dir%\repo.toml" (
        set "REPO_ROOT=%current_dir%"
        goto found
    )
)

REM Go up one directory
for %%I in ("%current_dir%\..") do set "current_dir=%%~fI"

REM Check if we reached the root
if "%current_dir%"=="%current_dir:~0,3%" (
    echo Error: Could not find repository root (looking for repo.bat and repo.toml) 1>&2
    exit /b 1
)

goto loop

:found
REM Call the main repo.bat with all arguments
call "%REPO_ROOT%\repo.bat" %*
exit /b %ERRORLEVEL%
