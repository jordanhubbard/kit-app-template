# Kit Dependency Validation

## Overview

This document explains how to validate Kit dependencies declared in `.kit` files and understand dependency resolution behavior.

## The Problem

**Build succeeds, but runtime fails**:
- `./repo.sh build` completes successfully
- But app hangs/crashes when launched
- Root cause: Extensions can't be resolved at runtime

**Why?**
- Build only validates **local** extensions (`source/extensions/`)
- Build does **NOT** validate **registry** extensions (150+ extensions from online registry)
- Dependency resolution happens at **runtime**, not build time

## Solution: Dependency Validation Tool

### Basic Validation

```bash
# Validate all .kit files
python tools/repoman/validate_kit_deps.py

# Validate specific app
python tools/repoman/validate_kit_deps.py --kit-file source/apps/my.app/my.app.kit

# Skip online registry checks (local only, fast)
python tools/repoman/validate_kit_deps.py --no-registry-check
```

**Output**:
```
======================================================================
Validating my.app.kit
======================================================================
Found 150 dependencies to validate

  ✓ omni.kit.livestream.app                      [kit/default]
  ✓ omni.kit.livestream.webrtc                   [kit/default]
  ✓ omni.activity.ui                             [local]
  ✗ omni.fake.extension                          [NOT FOUND]

======================================================================
Validation Summary:
  Total checked:     150
  Found locally:     10
  Found in registry: 139
  Missing:           1
======================================================================

✗ VALIDATION FAILED
```

### Pre-Fetching Extensions

**Problem**: First launch takes 5-10 minutes downloading extensions

**Solution**: Pre-fetch at build time

```bash
# Pre-download all extensions (for fast first launch)
python tools/repoman/validate_kit_deps.py --prefetch
```

**Benefits**:
- Fast first launch (~15 seconds instead of 5-10 minutes)
- Offline-capable
- Deterministic extension versions

**Trade-offs**:
- Longer build time (first build: +5-10 minutes)
- More disk space (~2-3 GB)

## Configuration

### repo.toml Settings

```toml
[kit_deps_validation]
# Enable automatic validation on build
enabled = false

# Check online registries during validation
check_registry = true

# Fail build on validation errors
fail_on_error = false

# Pre-fetch extensions during build
prefetch_on_build = false
```

### Enabling Build-Time Validation

**Option 1**: Enable globally in `repo.toml`
```toml
[kit_deps_validation]
enabled = true
fail_on_error = true
```

**Option 2**: Manual validation before launch
```bash
./repo.sh build
python tools/repoman/validate_kit_deps.py
./repo.sh launch --name my.app.kit
```

## Understanding Extension Resolution

### Build Time
```
┌──────────────────┐
│  ./repo.sh build │
└────────┬─────────┘
         │
         ├─> ✅ Fetch Kit SDK
         ├─> ✅ Build C++ extensions
         ├─> ✅ Copy local extensions
         └─> ❌ Does NOT validate registry extensions
```

### Runtime (First Launch)
```
┌───────────────────┐
│  ./repo.sh launch │
└─────────┬─────────┘
          │
          ├─> Parse .kit dependencies
          ├─> Check local cache
          ├─> Download from registry (150+ extensions)
          │   ⏱️  5-10 minutes
          └─> Start streaming server
```

### Runtime (Subsequent Launches)
```
┌───────────────────┐
│  ./repo.sh launch │
└─────────┬─────────┘
          │
          ├─> Parse .kit dependencies
          ├─> Load from local cache ✅
          │   ⏱️  15 seconds
          └─> Start streaming server
```

## Common Issues

### Issue 1: Slow First Launch

**Symptoms**:
- App takes 5-10 minutes to start
- Log shows "Pulling extension..."

**Solution**:
```bash
# This is NORMAL for first launch
# Monitor progress:
tail -f ~/.nvidia-omniverse/logs/Kit/*/kit_*.log | grep "installed"

# Or pre-fetch before launching:
python tools/repoman/validate_kit_deps.py --prefetch
```

### Issue 2: Build Succeeds, Launch Fails

**Symptoms**:
- `./repo.sh build` completes
- App crashes or hangs at launch
- "Cannot resolve extension" errors

**Solution**:
```bash
# Validate dependencies
python tools/repoman/validate_kit_deps.py --kit-file my.app.kit

# Fix any missing dependencies in .kit file
# Then rebuild and launch
```

### Issue 3: Extension Download Fails

**Symptoms**:
- "Failed to pull extension" in logs
- App hangs during startup

**Solution**:
```bash
# Check network connectivity
ping ovextensionsprod.blob.core.windows.net

# Clear cache and retry
rm -rf ~/.local/share/ov/data/exts/
./repo.sh launch --name my.app.kit
```

## Best Practices

### Development Workflow

```bash
# 1. Build
./repo.sh build --config release

# 2. Validate (optional but recommended)
python tools/repoman/validate_kit_deps.py

# 3. Pre-fetch (optional, for fast first launch)
python tools/repoman/validate_kit_deps.py --prefetch

# 4. Launch
./repo.sh launch --name my.app.kit --streaming
```

### Production Workflow

```bash
# Enable validation in repo.toml
[kit_deps_validation]
enabled = true
fail_on_error = true
prefetch_on_build = true

# Then normal build
./repo.sh build --config release

# Build will fail fast if dependencies are missing
# Extensions are pre-downloaded for fast deployment
```

### CI/CD Integration

```yaml
# .gitlab-ci.yml
build:
  script:
    - ./repo.sh build --config release
    - python tools/repoman/validate_kit_deps.py  # Validate
    - python tools/repoman/validate_kit_deps.py --prefetch  # Pre-download
  cache:
    paths:
      - ~/.local/share/ov/data/exts/  # Cache extensions
```

## Performance Comparison

| Scenario | Build Time | First Launch | Subsequent Launch |
|----------|-----------|--------------|-------------------|
| **Default** (no validation) | ~30s | 5-10 min | ~15s |
| **With validation** | ~35s | 5-10 min | ~15s |
| **With pre-fetch** | ~5 min | ~15s ✅ | ~15s |

## Related Documentation

- [Build-Time Dependency Validation Gap Analysis](../ai-docs/BUILD_TIME_DEPENDENCY_VALIDATION_GAP.md) - Detailed analysis
- [Kit App Streaming](.cursor/context/streaming.md) - Streaming configuration
- [Per-App Dependencies](../ai-docs/PER_APP_DEPENDENCIES.md) - App-specific dependency management

## Command Reference

### Validation
```bash
# Validate all .kit files
python tools/repoman/validate_kit_deps.py

# Validate specific app
python tools/repoman/validate_kit_deps.py --kit-file SOURCE/apps/my.app/my.app.kit

# Local only (no registry check)
python tools/repoman/validate_kit_deps.py --no-registry-check

# Stop on first error
python tools/repoman/validate_kit_deps.py --fail-fast

# Verbose output
python tools/repoman/validate_kit_deps.py -v
```

### Pre-Fetching
```bash
# Pre-fetch all extensions
python tools/repoman/validate_kit_deps.py --prefetch

# Pre-fetch for specific app
python tools/repoman/validate_kit_deps.py --prefetch --kit-file my.app.kit
```

## Troubleshooting

### Validation Script Not Found

```bash
# Ensure you're in repo root
cd /path/to/kit-app-template

# Check file exists
ls tools/repoman/validate_kit_deps.py

# Make it executable
chmod +x tools/repoman/validate_kit_deps.py
```

### Import Errors

```bash
# Ensure tomli is installed
pip install tomli

# Or use repo's Python
./repo.sh packman python -m pip install tomli
```

### Registry Timeout

```bash
# Use local-only validation (fast)
python tools/repoman/validate_kit_deps.py --no-registry-check

# Or increase timeout (modify script if needed)
```

## Future Enhancements

See [BUILD_TIME_DEPENDENCY_VALIDATION_GAP.md](../ai-docs/BUILD_TIME_DEPENDENCY_VALIDATION_GAP.md) for planned improvements:

1. ✅ Build-time validation (implemented)
2. ✅ Pre-fetching option (implemented)
3. ⏳ Integration with `./repo.sh build` command
4. ⏳ Automatic validation on CI/CD
5. ⏳ Phase 6: Per-app dependency isolation
