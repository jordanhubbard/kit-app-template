# Kit Playground Test Suite

Comprehensive test suite for Kit Playground covering security, functionality, and integration testing.

## Test Organization

```
tests/
├── unit/                           # Fast unit tests
│   ├── test_security_validators.py # Security validation (13 tests)
│   └── test_xpra_manager.py        # Xpra manager (6 tests)
├── integration/                    # Integration tests
│   ├── test_template_icons.py      # Icon validation (5 tests)
│   ├── test_template_builds.py     # Full build tests (slow)
│   └── test_template_api.py        # Template API tests
├── conftest.py                     # Shared fixtures
└── README.md                       # This file
```

## Running Tests

### Quick Test Suite (Recommended for Development)
```bash
cd /home/jkh/Src/kit-app-template/kit_playground

# Run all fast tests (excludes slow build tests)
pytest tests/ -m "not slow" -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests (fast)
pytest tests/integration/ -m "not slow" -v
```

### Full Test Suite (CI/Production)
```bash
# Run ALL tests including slow builds (~10+ minutes)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Specific Test Categories
```bash
# Security tests only
pytest tests/ -m security -v

# Icon validation tests
pytest tests/integration/test_template_icons.py -v

# Quick template creation (no build)
pytest tests/integration/test_template_builds.py::TestQuickValidation -v

# Full build tests (SLOW - ~10 minutes)
pytest tests/integration/test_template_builds.py -m slow -v
```

## Test Coverage

### Unit Tests (19 tests - Fast)

**Security Validators** (`test_security_validators.py`)
- ✅ Project name validation (4 tests)
  - Valid names accepted
  - Shell metacharacters blocked
  - Length limits enforced
  - Empty names rejected

- ✅ Project path validation (4 tests)
  - Relative paths within repo accepted
  - Path traversal blocked
  - Absolute path escapes blocked
  - Non-existent paths rejected

- ✅ Filesystem path validation (3 tests)
  - Paths in allowed directories accepted
  - Paths outside allowed directories blocked
  - Creation flag handling

- ✅ Resource limits (2 tests)
  - Process limit check exists
  - Process storage validated

**Xpra Manager** (`test_xpra_manager.py`)
- ✅ Session initialization (2 tests)
- ✅ Session management (2 tests)
- ✅ Security validation (2 tests)
  - No shell injection
  - Safe URL generation

### Integration Tests

**Icon Validation** (`test_template_icons.py` - 5 tests)
- ✅ Application templates have icons
- ✅ All icons are valid image files (PNG/JPEG/SVG/ICO)
- ✅ Specific template icons validated
- ✅ Icon file sizes reasonable
- ✅ PNG icons readable by PIL

**Template API** (`test_template_api.py` - 13 tests)
- ✅ Template listing
- ✅ Template retrieval
- ✅ Template integrity
- ✅ Expected templates exist

**Build Tests** (`test_template_builds.py` - 6 tests)
- ✅ Quick template creation (fast)
- ⏱️ Kit Base Editor build (slow - 5-10 min)
- ⏱️ Kit Service build (slow - 5-10 min)
- ⏱️ Python extension creation (slow)
- ⏱️ C++ extension creation (slow)
- ✅ Template metadata validation

## Test Results Summary

### Current Status
```
Unit Tests:        19 passed ✅
Integration (Fast): 19 passed ✅
Integration (Icons): 5 passed ✅
Total Fast Tests:   43 passed ✅
```

### What's Tested

**Security** ✅
- Command injection prevention
- Path traversal prevention
- Path escape prevention
- Resource limit enforcement
- Shell injection prevention

**Functionality** ✅
- Template listing and retrieval
- Template icon validation
- Project creation from templates
- Wrapper script generation
- Project structure validation

**Build System** ⏱️ (Slow tests)
- Full application builds
- Microservice builds
- Extension builds
- Build artifact verification

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.slow` - Slow tests (> 60 seconds)
- `@pytest.mark.quick` - Quick tests (< 10 seconds)

## CI/CD Recommendations

### Pre-commit Hook
```bash
# Run fast tests before commit
pytest tests/ -m "not slow" -q
```

### Pull Request Checks
```bash
# Run unit + fast integration tests
pytest tests/unit/ tests/integration/ -m "not slow" --cov=backend
```

### Nightly Build
```bash
# Run full test suite including slow builds
pytest tests/ -v --cov=backend --cov-report=html
```

## Adding New Tests

### Unit Test Template
```python
# tests/unit/test_new_feature.py
import pytest
from kit_playground.backend.new_module import NewClass

@pytest.fixture
def new_instance():
    return NewClass()

class TestNewFeature:
    def test_basic_functionality(self, new_instance):
        result = new_instance.do_something()
        assert result == expected_value
```

### Integration Test Template
```python
# tests/integration/test_new_integration.py
import pytest

@pytest.mark.integration
def test_end_to_end_workflow():
    # Test complete workflow
    pass

@pytest.mark.slow
def test_expensive_operation():
    # Test that takes > 60 seconds
    pass
```

## Troubleshooting

### Import Errors
If tests fail with import errors:
```bash
# Ensure PYTHONPATH includes repo root
cd /home/jkh/Src/kit-app-template
export PYTHONPATH=$PWD:$PWD/kit_playground:$PYTHONPATH
pytest tests/
```

### Slow Test Failures
If build tests fail:
1. Check disk space: `df -h`
2. Check build logs: `tail -f /tmp/playground-backend.log`
3. Run single test: `pytest tests/integration/test_template_builds.py::TestApplicationTemplates::test_build_kit_base_editor -v -s`

### Missing Dependencies
```bash
# Install test dependencies
pip install -r kit_playground/requirements-test.txt
```

## Performance

- **Unit tests**: ~7 seconds total
- **Fast integration**: ~10 seconds total
- **Icon validation**: ~0.1 seconds
- **Template creation**: ~4 seconds per template
- **Full builds**: ~5-10 minutes per template

**Total fast test time**: < 20 seconds
**Total full test time**: ~30-60 minutes (with all builds)

## Test Data

Tests use:
- Real templates from `templates/` directory
- Test projects in `_build/test_projects/`
- Temporary directories via pytest `tmp_path` fixture

Test artifacts are cleaned up automatically (except `_build/test_projects/` for debugging).

## Future Improvements

- [ ] Add frontend React component tests
- [ ] Add API endpoint tests (with Flask test client)
- [ ] Add WebSocket communication tests
- [ ] Add Xpra session lifecycle tests
- [ ] Add performance benchmarks
- [ ] Add cross-platform tests (Windows/Mac)
- [ ] Add load testing for concurrent builds
- [ ] Add mutation testing for security validators

---

**Last Updated**: October 6, 2025
**Test Framework**: pytest 8.3.5
**Python Version**: 3.10.12
