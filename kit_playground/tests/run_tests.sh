#!/bin/bash
# Unified test runner for Kit Playground
# This script runs all tests and can be called from anywhere in the repo

set -e  # Exit on error

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLAYGROUND_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$PLAYGROUND_DIR")"
TEST_OUTPUT_DIR="$REPO_ROOT/_build/test-output"

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"

# Change to playground directory
cd "$PLAYGROUND_DIR"

echo "=========================================="
echo "Kit Playground Test Suite"
echo "=========================================="
echo ""

# Parse arguments
QUICK_MODE=false
VERBOSE=false
COVERAGE=false
TEST_PATTERN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --pattern|-p)
            TEST_PATTERN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick|-q] [--verbose|-v] [--coverage|-c] [--pattern|-p TEST_PATTERN]"
            exit 1
            ;;
    esac
done

# Build pytest command with JUnit XML output for CI/CD
PYTEST_CMD="python3 -m pytest tests/ --junit-xml=$TEST_OUTPUT_DIR/junit-results.xml"

if [ "$QUICK_MODE" = true ]; then
    echo "Running in QUICK mode (excluding slow tests)..."
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
fi

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

if [ "$COVERAGE" = true ]; then
    echo "Running with coverage analysis..."
    PYTEST_CMD="$PYTEST_CMD --cov=backend --cov=core --cov-report=term-missing --cov-report=html:$TEST_OUTPUT_DIR/coverage"
fi

if [ -n "$TEST_PATTERN" ]; then
    echo "Running tests matching pattern: $TEST_PATTERN"
    PYTEST_CMD="$PYTEST_CMD -k '$TEST_PATTERN'"
fi

# Run tests
echo ""
echo "Executing: $PYTEST_CMD"
echo ""

eval $PYTEST_CMD

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed (exit code: $EXIT_CODE)"
fi

echo ""
echo "=========================================="

exit $EXIT_CODE

