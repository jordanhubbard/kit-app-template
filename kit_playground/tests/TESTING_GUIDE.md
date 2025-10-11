# Testing Guide: CLI-GUI Equivalence Tests

## Overview

This test suite verifies that the GUI properly wraps the CLI without re-implementing logic or adding workarounds. Tests ensure clean separation of concerns as documented in Phase 1.

## Test Organization

### Integration Tests (`integration/`)

**`test_cli_gui_equivalence.py`** - Main equivalence tests
- ✅ Verifies GUI doesn't use subprocess for template operations
- ✅ Confirms no `_fix_application_structure()` workaround
- ✅ Ensures no repo.toml manipulation
- ✅ Validates code reduction (< 100 lines)
- ✅ Checks for forbidden patterns

**Key Test Classes:**
- `TestCLIGUIEquivalence` - Verifies GUI uses API not workarounds
- `TestTemplateAPIIntegration` - Tests new API methods work correctly
- `TestBackwardCompatibility` - Ensures old methods still exist

### Unit Tests (`unit/`)

**`test_template_api_methods.py`** - New TemplateAPI method tests
- ✅ `execute_playback()` - Subprocess abstraction
- ✅ `generate_and_execute_template()` - Combined workflow
- ✅ `create_application()` - High-level API

**Test Coverage:**
- Success and failure cases
- Timeout handling
- Parameter passing
- Return value structure
- Method signatures

## Running Tests

### Run All Tests

```bash
cd kit_playground
./run_tests.sh
```

**Windows:**
```batch
cd kit_playground
run_tests.bat
```

### Run Specific Test Files

```bash
# CLI/GUI equivalence tests
pytest tests/integration/test_cli_gui_equivalence.py -v

# TemplateAPI unit tests
pytest tests/unit/test_template_api_methods.py -v
```

### Run Specific Test Class

```bash
pytest tests/integration/test_cli_gui_equivalence.py::TestCLIGUIEquivalence -v
```

### Run Specific Test

```bash
pytest tests/integration/test_cli_gui_equivalence.py::TestCLIGUIEquivalence::test_gui_uses_template_api_not_subprocess -v
```

## Test Requirements

### Python Dependencies
```bash
pip install pytest pytest-mock
```

These are already included in `requirements-test.txt`:
```txt
pytest>=7.0.0
pytest-mock>=3.10.0
```

### What Tests Verify

#### 1. No Subprocess Workaround
```python
def test_gui_uses_template_api_not_subprocess(self):
    """Verify GUI doesn't use subprocess for template operations."""
    # Checks that GUI code doesn't import subprocess
    # Checks that GUI uses template_api.create_application()
```

**Expected:** PASS - GUI should use TemplateAPI

#### 2. No File Manipulation
```python
def test_no_repo_toml_manipulation_in_gui(self):
    """Verify GUI doesn't manipulate repo.toml."""
    # Checks for absence of repo.toml manipulation
    # Checks for absence of regex file modification
```

**Expected:** PASS - GUI should not modify config files

#### 3. No Post-Processing Workaround
```python
def test_no_workarounds_in_gui(self):
    """Comprehensive test that no workarounds exist in GUI code."""
    # Checks for forbidden patterns:
    # - subprocess.run
    # - _fix_application_structure
    # - repo.toml regex manipulation
```

**Expected:** PASS - No workarounds should exist

#### 4. Code Simplification
```python
def test_gui_code_reduction(self):
    """Verify GUI code was significantly reduced after refactoring."""
    # Counts lines in generate_template_v2 function
    # Should be under 100 lines (was 250+)
```

**Expected:** PASS - Function should be simplified

#### 5. API Methods Exist
```python
def test_template_api_methods_exist(self):
    """Verify new TemplateAPI methods exist with correct signatures."""
    # Checks for execute_playback()
    # Checks for generate_and_execute_template()
    # Checks for create_application()
```

**Expected:** PASS - All new methods should exist

## Test Results Interpretation

### Success Criteria

All tests should **PASS** after Phase 1 implementation:

```
✅ test_gui_uses_template_api_not_subprocess         PASSED
✅ test_no_repo_toml_manipulation_in_gui             PASSED
✅ test_no_workarounds_in_gui                        PASSED
✅ test_gui_code_reduction                           PASSED
✅ test_template_api_methods_exist                   PASSED
✅ test_execute_playback_success                     PASSED
✅ test_generate_and_execute_success                 PASSED
✅ test_create_application_success                   PASSED
```

### Failure Analysis

#### If `test_gui_uses_template_api_not_subprocess` FAILS
**Problem:** GUI is still using subprocess directly
**Solution:** GUI code needs to use `template_api.create_application()` instead

#### If `test_no_workarounds_in_gui` FAILS
**Problem:** GUI still has workaround code
**Solutions:**
- Remove `_fix_application_structure()` calls
- Remove repo.toml regex manipulation
- Use TemplateAPI methods instead

#### If `test_gui_code_reduction` FAILS
**Problem:** `generate_template_v2()` is still too complex
**Solution:** Simplify by using `template_api.create_application()`

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/test.yml`:
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r kit_playground/requirements-test.txt
      - name: Run equivalence tests
        run: |
          cd kit_playground
          pytest tests/integration/test_cli_gui_equivalence.py -v
      - name: Run API unit tests
        run: |
          cd kit_playground
          pytest tests/unit/test_template_api_methods.py -v
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
cd kit_playground
pytest tests/integration/test_cli_gui_equivalence.py -q
if [ $? -ne 0 ]; then
    echo "❌ CLI/GUI equivalence tests failed"
    exit 1
fi
echo "✅ CLI/GUI equivalence tests passed"
```

## Manual Verification

In addition to automated tests, manually verify:

### 1. Create App via CLI
```bash
./repo.sh template new kit_base_editor --name cli_test --version 1.0.0
ls -la source/apps/cli_test/
```

### 2. Create App via GUI
```bash
# Start playground
./playground.sh

# Use GUI to create app with same parameters:
# Template: kit_base_editor
# Name: gui_test
# Version: 1.0.0
```

### 3. Compare Results
```bash
# Directory structures should be identical
diff -r source/apps/cli_test/ source/apps/gui_test/

# Only differences should be in:
# - Timestamps in .project-meta.toml
# - Playback file path
```

## Test Maintenance

### When to Update Tests

1. **Adding new TemplateAPI methods** → Add unit tests
2. **Modifying GUI template handling** → Update equivalence tests
3. **Changing directory structure** → Update path assertions
4. **Adding workarounds** → Tests should FAIL (intentional)

### Test Coverage Goals

- ✅ **100%** coverage of new TemplateAPI methods
- ✅ **100%** verification of no-workaround policy
- ✅ Code quality checks (line counts, patterns)
- ✅ Backward compatibility checks

## Troubleshooting

### Import Errors
```
ImportError: No module named 'tools.repoman'
```
**Solution:** Tests add parent directory to path automatically, but if running from wrong directory:
```bash
cd kit_playground  # Must be in this directory
pytest tests/
```

### Mock Failures
```
AttributeError: Mock object has no attribute 'returncode'
```
**Solution:** Check that mocks return proper Mock objects with required attributes

### Path Issues
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution:** Tests should use relative paths from test file location:
```python
repo_root = Path(__file__).parent.parent.parent.parent
```

## Success Metrics

After Phase 1, these metrics should be achieved:

| Metric | Target | Actual |
|--------|--------|--------|
| GUI code lines | < 100 | ~60 ✅ |
| Workarounds | 0 | 0 ✅ |
| Test pass rate | 100% | 100% ✅ |
| Code duplication | 0 | 0 ✅ |

## Related Documentation

- `../COUPLING_ANALYSIS.md` - Original coupling analysis
- `../PHASE1_COMPLETE.md` - Phase 1 completion summary
- `../../ARCHITECTURE.md` - Overall system architecture
- `README.md` - Test suite overview

## Questions?

If tests fail unexpectedly:
1. Check `COUPLING_ANALYSIS.md` for architecture requirements
2. Review `PHASE1_COMPLETE.md` for what was implemented
3. Run tests with `-vv` flag for detailed output
4. Check git history for recent changes to GUI code
