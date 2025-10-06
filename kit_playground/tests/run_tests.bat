@echo off
REM Unified test runner for Kit Playground (Windows)
REM This script runs all tests and can be called from anywhere in the repo

setlocal enabledelayedexpansion

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Get parent directories
for %%I in ("%SCRIPT_DIR%\..") do set "PLAYGROUND_DIR=%%~fI"
for %%I in ("%PLAYGROUND_DIR%\..") do set "REPO_ROOT=%%~fI"
set "TEST_OUTPUT_DIR=%REPO_ROOT%\_build\test-output"

REM Create test output directory
if not exist "%TEST_OUTPUT_DIR%" mkdir "%TEST_OUTPUT_DIR%"

REM Change to playground directory
cd /d "%PLAYGROUND_DIR%"

echo ==========================================
echo Kit Playground Test Suite
echo ==========================================
echo.

REM Parse arguments
set "QUICK_MODE=false"
set "VERBOSE=false"
set "COVERAGE=false"
set "TEST_PATTERN="

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--quick" (
    set "QUICK_MODE=true"
    shift
    goto parse_args
)
if /i "%~1"=="-q" (
    set "QUICK_MODE=true"
    shift
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto parse_args
)
if /i "%~1"=="-v" (
    set "VERBOSE=true"
    shift
    goto parse_args
)
if /i "%~1"=="--coverage" (
    set "COVERAGE=true"
    shift
    goto parse_args
)
if /i "%~1"=="-c" (
    set "COVERAGE=true"
    shift
    goto parse_args
)
if /i "%~1"=="--pattern" (
    set "TEST_PATTERN=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="-p" (
    set "TEST_PATTERN=%~2"
    shift
    shift
    goto parse_args
)
echo Unknown option: %~1
echo Usage: %~nx0 [--quick^|-q] [--verbose^|-v] [--coverage^|-c] [--pattern^|-p TEST_PATTERN]
exit /b 1

:args_done

REM Build pytest command with JUnit XML output for CI/CD
set "PYTEST_CMD=python -m pytest tests/ --junit-xml=%TEST_OUTPUT_DIR%\junit-results.xml"

if "%QUICK_MODE%"=="true" (
    echo Running in QUICK mode (excluding slow tests)...
    set "PYTEST_CMD=!PYTEST_CMD! -m "not slow""
)

if "%VERBOSE%"=="true" (
    set "PYTEST_CMD=!PYTEST_CMD! -v"
) else (
    set "PYTEST_CMD=!PYTEST_CMD! -q"
)

if "%COVERAGE%"=="true" (
    echo Running with coverage analysis...
    set "PYTEST_CMD=!PYTEST_CMD! --cov=backend --cov=core --cov-report=term-missing --cov-report=html:%TEST_OUTPUT_DIR%\coverage"
)

if not "%TEST_PATTERN%"=="" (
    echo Running tests matching pattern: %TEST_PATTERN%
    set "PYTEST_CMD=!PYTEST_CMD! -k "%TEST_PATTERN%""
)

REM Run tests
echo.
echo Executing: !PYTEST_CMD!
echo.

call !PYTEST_CMD!

REM Capture exit code
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if %EXIT_CODE% equ 0 (
    echo ✓ All tests passed!
) else (
    echo ✗ Some tests failed (exit code: %EXIT_CODE%)
)

echo.
echo ==========================================

exit /b %EXIT_CODE%
