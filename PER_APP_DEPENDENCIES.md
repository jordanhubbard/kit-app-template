# Per-Application Dependencies Guide

**Status**: ✅ Implemented  
**Version**: 1.0  
**Date**: October 24, 2025

---

## Overview

Per-application dependencies allow each Kit application to maintain its own isolated Kit SDK and dependencies. This eliminates conflicts between applications and enables different apps to use different Kit versions.

### Benefits

✅ **Dependency Isolation** - Each app has its own Kit SDK  
✅ **Version Freedom** - Different Kit versions per app  
✅ **No Conflicts** - Custom configs don't affect other apps  
✅ **Custom Branches** - Track experimental Kit builds  
✅ **Proper Caching** - App-specific packman cache  
✅ **Backward Compatible** - Existing apps work unchanged

---

## Quick Start

### Create App with Per-App Dependencies

```bash
# Create new app with isolated dependencies
./repo.sh template new kit_base_editor my_app --per-app-deps

# The app will have this structure:
# source/apps/my_app/
# ├── my_app.kit
# ├── dependencies/
# │   └── kit-deps.toml    # Dependency configuration
# └── _kit/                 # Per-app Kit SDK (after build)
```

### Launch App

```bash
# Launch automatically detects and uses per-app Kit
./repo.sh launch my_app
```

The launch system automatically detects if an app uses per-app dependencies and sets the correct environment variables.

---

## Configuration

### Kit Dependency Configuration

**File**: `source/apps/my_app/dependencies/kit-deps.toml`

```toml
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"  # or "shared" for global cache

[dependencies]
# Add custom dependencies here
```

### Configuration Options

**`[kit_sdk]`** - Kit SDK settings
- `version` (required) - Kit SDK version (e.g., "106.0", "105.5")
- `branch` (optional) - Custom Kit branch name

**`[cache]`** - Cache strategy
- `strategy` - `"isolated"` (per-app cache) or `"shared"` (global cache)

**`[dependencies]`** - Custom dependency overrides
- Add app-specific dependency configurations

---

## Directory Structure

### Per-App Dependencies Structure

```
source/apps/my_app/
├── my_app.kit                  # Kit application file
├── .project-meta.toml          # Project metadata
├── dependencies/               # Per-app config (NEW)
│   └── kit-deps.toml          # Dependency configuration
└── _kit/                       # App-specific SDK (NEW)
    ├── kit/                    # Kit SDK installation
    │   ├── kit                 # Kit executable
    │   └── kernel/
    ├── exts/                   # App-specific extensions
    └── cache/                  # Packman cache
```

### Global Dependencies Structure (Default)

Without per-app dependencies, apps share the global Kit SDK:

```
_build/linux-x86_64/release/
├── kit/                        # SHARED Kit SDK
├── exts/                       # SHARED extensions
└── apps/                       # App directories
```

---

## Usage Examples

### Example 1: Create App with Specific Kit Version

```bash
# Create app with per-app deps
./repo.sh template new kit_base_editor my_app --per-app-deps

# Edit dependencies/kit-deps.toml to set Kit version
cd source/apps/my_app/dependencies
echo '[kit_sdk]
version = "105.5"

[cache]
strategy = "isolated"' > kit-deps.toml

# Build and launch
cd ../../../..
./repo.sh build --app my_app
./repo.sh launch my_app
```

### Example 2: Multiple Apps with Different Kit Versions

```bash
# App A with Kit 106.0
./repo.sh template new kit_base_editor app_a --per-app-deps
# (Kit 106.0 is default)

# App B with Kit 105.5
./repo.sh template new kit_base_editor app_b --per-app-deps
# Edit source/apps/app_b/dependencies/kit-deps.toml
# Set version = "105.5"

# Both apps work independently
./repo.sh launch app_a  # Uses Kit 106.0
./repo.sh launch app_b  # Uses Kit 105.5
```

### Example 3: Convert Existing App to Per-App Dependencies

```bash
# Add dependencies configuration to existing app
mkdir -p source/apps/existing_app/dependencies
echo '[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"' > source/apps/existing_app/dependencies/kit-deps.toml

# Rebuild to fetch per-app Kit SDK
./repo.sh build --app existing_app
```

---

## CLI Reference

### Template Creation Flags

**`--per-app-deps`** - Create app with per-app dependencies

```bash
./repo.sh template new <template> <name> --per-app-deps [options]
```

**Options**:
- `--accept-license` - Accept license automatically
- `--json` - Output JSON format
- `--verbose` - Verbose output
- `--standalone` - Create standalone project (can combine with --per-app-deps)

### Examples

```bash
# Basic per-app deps
./repo.sh template new kit_base_editor my_app --per-app-deps

# With JSON output
./repo.sh template new kit_base_editor my_app --per-app-deps --json

# Standalone project with per-app deps
./repo.sh template new kit_base_editor my_app --per-app-deps --standalone

# Verbose output
./repo.sh template new kit_base_editor my_app --per-app-deps --verbose
```

---

## Backward Compatibility

### Existing Apps Continue to Work

Apps without `dependencies/kit-deps.toml` automatically use global Kit SDK:

```bash
# Old apps work unchanged
./repo.sh template new kit_base_editor old_app
./repo.sh build --app old_app
./repo.sh launch old_app
```

### Migration is Optional

You can mix apps with and without per-app dependencies:

- Apps with `dependencies/` use per-app Kit SDK
- Apps without `dependencies/` use global Kit SDK
- Both types coexist peacefully

---

## Advanced Topics

### Cache Strategy

**Isolated Cache** (recommended):
```toml
[cache]
strategy = "isolated"
```
- Each app has its own packman cache
- No dependency pollution between apps
- Larger disk usage (each app downloads dependencies)

**Shared Cache** (compatibility mode):
```toml
[cache]
strategy = "shared"
```
- Uses global packman cache
- Saves disk space
- Potential for dependency conflicts

### Custom Kit Branches

For development/testing with experimental Kit builds:

```toml
[kit_sdk]
version = "106.0"
branch = "experimental-feature-x"
```

*Note: Custom branch support requires packman configuration.*

---

## Troubleshooting

### App Not Using Per-App Kit

**Symptom**: App launches with global Kit instead of per-app Kit

**Solutions**:
1. Verify `dependencies/kit-deps.toml` exists
2. Check file has valid TOML syntax
3. Rebuild app: `./repo.sh build --app my_app`
4. Verify `_kit/` directory exists in app

### Build Fails to Find Dependencies

**Symptom**: Build errors about missing dependencies

**Solutions**:
1. Check Kit version in `kit-deps.toml` is valid
2. Verify internet connection (for dependency download)
3. Try rebuilding: `./repo.sh build --app my_app --clean`

### Launch Shows "Using per-app Kit SDK" but Fails

**Symptom**: Message appears but app doesn't start

**Solutions**:
1. Check `_kit/kit/kit` executable exists
2. Verify permissions: `ls -la source/apps/my_app/_kit/kit/`
3. Try clean rebuild

---

## API Reference

Python API for per-app dependency management is available in `tools/repoman/app_dependencies.py`.

### Key Functions

```python
from app_dependencies import (
    should_use_per_app_deps,
    get_app_deps_config,
    get_app_kit_path,
    initialize_per_app_deps
)

# Check if app uses per-app deps
if should_use_per_app_deps(app_path):
    print("App uses per-app dependencies")

# Get configuration
config = get_app_deps_config(app_path)
kit_version = config['kit_sdk']['version']

# Get Kit SDK path
kit_path = get_app_kit_path(app_path)

# Initialize per-app deps programmatically
initialize_per_app_deps(app_path, kit_version="106.0")
```

---

## Best Practices

### When to Use Per-App Dependencies

✅ **Use per-app deps when**:
- App needs specific Kit version
- Testing with experimental Kit builds
- App has custom dependency requirements
- Working in multi-app repository
- Need dependency isolation

❌ **Don't use per-app deps when**:
- Single app in repository
- Disk space is critical
- All apps use same Kit version
- Simple prototyping

### Recommended Workflow

1. **Start without per-app deps** for prototyping
2. **Add per-app deps** when ready for production
3. **Use isolated cache** for production apps
4. **Document Kit version** requirements in README

---

## FAQ

**Q: Will this increase disk usage?**  
A: Yes, each app with per-app deps downloads its own Kit SDK (~1-2 GB per app). Use shared cache to reduce usage.

**Q: Can I switch between per-app and global deps?**  
A: Yes, add/remove `dependencies/kit-deps.toml` and rebuild.

**Q: Do I need to modify existing apps?**  
A: No, existing apps work unchanged. Per-app deps is opt-in.

**Q: What happens if build fails?**  
A: App falls back to checking global Kit SDK if per-app SDK is missing.

**Q: Can I use this with standalone projects?**  
A: Yes! Use `--per-app-deps --standalone` together.

---

## See Also

- [STANDALONE_PROJECTS.md](./STANDALONE_PROJECTS.md) - Standalone project guide
- [CLI_FEATURES.md](./CLI_FEATURES.md) - Complete CLI reference
- [Phase 6 Design](./PHASE_6_DESIGN.md) - Technical architecture

---

**Questions or Issues?** Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or file an issue.

