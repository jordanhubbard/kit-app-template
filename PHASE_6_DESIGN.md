# Phase 6: Per-App Dependencies - Design Document

**Date**: October 24, 2025  
**Status**: 🎯 **DESIGN PHASE**  
**Complexity**: High (build system architecture)  
**Estimated Time**: 4-5 hours

---

## Executive Summary

**Objective**: Enable each application to maintain its own Kit SDK and dependencies, isolated from other applications.

**Critical Need**: 
- Apps with custom `.kit` configurations currently break global cache
- No way to use different Kit versions per app
- Dependency conflicts between apps
- Cannot track custom Kit branches per app

**Approach**: Extend (not rewrite) packman using existing capabilities with orchestration changes in build system.

---

## Current Architecture Problems

### Problem 1: Global Dependencies

```
_build/linux-x86_64/release/
├── kit/                    # SHARED by all apps
├── exts/                   # SHARED extensions
└── apps/                   # App directories
    ├── app1/
    ├── app2/
    └── app3/
```

**Issues**:
- App1's custom Kit config affects App2
- All apps must use same Kit version
- Cache invalidation affects all apps
- No dependency isolation

### Problem 2: Configuration Conflicts

**Scenario**:
1. App A modifies Kit SDK config in `.kit` file
2. Packman caches this modified version
3. App B expects standard Kit SDK
4. App B gets App A's modified version from cache
5. **App B breaks**

### Problem 3: Version Lock-In

**Current**: All apps share `_build/kit/`
**Cannot do**:
- App A on Kit 106.0
- App B on Kit 105.5 stable
- App C on experimental branch

### Problem 4: Custom Branches

**Use Case**: Development team wants to:
- Track custom Kit branch for App A
- Use stable Kit for App B
- Test beta Kit for App C

**Current System**: Impossible (global Kit only)

---

## Target Architecture

### Per-App Dependencies

```
source/apps/my.app/
├── my.app.kit
├── .project-meta.toml
├── dependencies/               # NEW: Per-app dependency config
│   └── kit-deps.toml          # Kit SDK version, custom deps
└── _kit/                       # NEW: App-specific Kit SDK
    ├── kit/                    # Kit SDK for this app only
    │   ├── kit                 # Kit executable
    │   ├── kernel/
    │   └── ...
    ├── exts/                   # Extensions for this app
    │   └── ...
    └── cache/                  # App-specific packman cache
```

### Benefits

✅ **Isolation**: Each app has its own Kit SDK  
✅ **Version Freedom**: Different Kit versions per app  
✅ **No Conflicts**: Custom configs don't affect other apps  
✅ **Custom Branches**: Track experimental Kit per app  
✅ **Proper Caching**: Cache is app-specific  
✅ **Independent Development**: Changes in App A don't break App B

---

## Implementation Approach

### Strategy: Extension-Based (No Packman Core Changes)

**Use Existing Packman Features**:
1. `packman pull --path <custom-path>` - Install to specific location
2. `PM_PACKAGES_ROOT` env var - Override package root
3. `PM_MODULE_DIR` env var - Override cache location
4. Packman already supports all needed capabilities

**Our Changes** (orchestration only):
1. `repo.toml` / app config - Specify per-app dependencies
2. `repoman.py` - Pass app-specific paths to packman
3. `premake5.lua` - Use app-specific SDK paths
4. `launch.py` - Find app-specific Kit executable

---

## Detailed Design

### 1. Configuration Structure

**App-Level Config**: `source/apps/my.app/dependencies/kit-deps.toml`

```toml
[kit_sdk]
# Kit SDK version for this app
version = "106.0"

# Optional: Custom Kit branch/build
# branch = "experimental-feature-x"
# build_id = "12345"

# Optional: Custom packman server
# server = "https://custom-packman.company.com"

[dependencies]
# App-specific dependencies
# These override global dependencies for this app

[dependencies.custom_ext]
package = "my.custom.extension"
version = "1.2.3"

[cache]
# Cache strategy for this app
# "isolated" = app-specific cache (default)
# "shared" = use global cache (backward compat)
strategy = "isolated"
```

**Global Fallback**: If `dependencies/kit-deps.toml` doesn't exist, use global dependencies (backward compatible).

---

### 2. Build System Changes

**File**: `tools/repoman/repoman.py`

**Changes Needed**:

```python
def get_app_dependencies_path(app_path: Path) -> Optional[Path]:
    """Get app-specific dependencies directory if it exists."""
    deps_dir = app_path / "dependencies"
    if deps_dir.exists() and (deps_dir / "kit-deps.toml").exists():
        return deps_dir
    return None

def get_app_kit_path(app_path: Path) -> Path:
    """Get app-specific Kit SDK path."""
    return app_path / "_kit"

def pull_app_dependencies(app_path: Path):
    """Pull dependencies for specific app using packman."""
    deps_config = get_app_dependencies_path(app_path)
    if not deps_config:
        # Use global dependencies (backward compat)
        return pull_global_dependencies()
    
    # Read app-specific config
    config = load_toml(deps_config / "kit-deps.toml")
    kit_path = get_app_kit_path(app_path)
    
    # Set environment for app-specific install
    env = os.environ.copy()
    env['PM_PACKAGES_ROOT'] = str(kit_path)
    env['PM_MODULE_DIR'] = str(kit_path / 'cache')
    
    # Pull using packman with custom path
    packmanapi.pull(
        package=f"kit-sdk-{config['kit_sdk']['version']}",
        path=str(kit_path / 'kit'),
        env=env
    )
    
    # Pull other dependencies
    for dep_name, dep_config in config.get('dependencies', {}).items():
        packmanapi.pull(
            package=dep_config['package'],
            version=dep_config['version'],
            path=str(kit_path / 'exts'),
            env=env
        )
```

---

### 3. Premake Changes

**File**: `premake5.lua`

**Changes Needed**:

```lua
-- Function to find app-specific Kit SDK
function findAppKitSdk(appPath)
    local appKitPath = path.join(appPath, "_kit/kit")
    if os.isdir(appKitPath) then
        return appKitPath
    end
    -- Fallback to global Kit SDK
    return path.join(BUILD_DIR, "kit")
end

-- When configuring app build
for _, app in ipairs(apps) do
    local appPath = path.join(SOURCE_DIR, "apps", app)
    local kitSdkPath = findAppKitSdk(appPath)
    
    project(app)
        -- Use app-specific Kit SDK
        includedirs { path.join(kitSdkPath, "include") }
        libdirs { path.join(kitSdkPath, "lib") }
end
```

---

### 4. Launch System Changes

**File**: `tools/repoman/launch.py`

**Changes Needed**:

```python
def find_app_kit_executable(app_path: Path) -> Path:
    """Find Kit executable for app (app-specific or global)."""
    # Check for app-specific Kit
    app_kit = app_path / "_kit" / "kit" / "kit"
    if app_kit.exists():
        return app_kit
    
    # Fallback to global Kit
    global_kit = Path("_build") / PLATFORM / CONFIG / "kit" / "kit"
    if global_kit.exists():
        return global_kit
    
    raise FileNotFoundError("Kit executable not found")

def launch_app(app_name: str, args: list):
    """Launch app with correct Kit SDK."""
    app_path = Path("source/apps") / app_name
    kit_exe = find_app_kit_executable(app_path)
    
    # Set environment for app-specific extensions
    env = os.environ.copy()
    if (app_path / "_kit").exists():
        env['CARB_APP_PATH'] = str(app_path / "_kit")
    
    # Launch Kit with app's .kit file
    subprocess.run([str(kit_exe), str(app_path / f"{app_name}.kit")] + args, env=env)
```

---

### 5. Migration Strategy

**Backward Compatibility**:
1. Apps without `dependencies/` directory use global Kit (current behavior)
2. Apps with `dependencies/kit-deps.toml` use per-app Kit
3. No breaking changes for existing apps

**Migration Path**:

```bash
# 1. Create per-app dependencies config
mkdir -p source/apps/my.app/dependencies
cat > source/apps/my.app/dependencies/kit-deps.toml << EOF
[kit_sdk]
version = "106.0"

[cache]
strategy = "isolated"
EOF

# 2. Build app (pulls to app-specific location)
./repo.sh build --app my.app

# 3. App now has own Kit SDK
ls source/apps/my.app/_kit/
```

---

## CLI Changes

### New Build Flag

```bash
# Build app with per-app dependencies
./repo.sh build --app my.app --use-app-deps

# Build all apps with per-app deps (where configured)
./repo.sh build --use-app-deps

# Force global dependencies (override config)
./repo.sh build --app my.app --use-global-deps
```

### New Template Option

```bash
# Create app with per-app dependencies enabled
./repo.sh template new kit_base_editor \
  --name my.app \
  --per-app-deps

# Generates app with dependencies/ directory pre-configured
```

---

## Implementation Plan

### Phase 6.1: Foundation (90 min)

**Tasks**:
1. Design `kit-deps.toml` schema
2. Add config parsing to repoman.py
3. Implement app dependency detection
4. Add environment variable setup

**Deliverable**: Can detect and parse per-app deps config

---

### Phase 6.2: Packman Integration (60 min)

**Tasks**:
1. Modify packman calls to use app-specific paths
2. Set `PM_PACKAGES_ROOT` and `PM_MODULE_DIR`
3. Implement per-app pull logic
4. Add fallback to global deps

**Deliverable**: Packman installs to app-specific paths

---

### Phase 6.3: Build System (45 min)

**Tasks**:
1. Update premake5.lua for app-specific paths
2. Modify build scripts to use app Kit SDK
3. Update path resolution
4. Test build with per-app deps

**Deliverable**: Apps build with their own Kit SDK

---

### Phase 6.4: Launch System (30 min)

**Tasks**:
1. Update launch.py to find app-specific Kit
2. Set correct environment variables
3. Handle both per-app and global modes
4. Test launching apps

**Deliverable**: Apps launch with their own Kit SDK

---

### Phase 6.5: Testing (60 min)

**Tasks**:
1. Test per-app deps creation
2. Test build with per-app deps
3. Test launch with per-app deps
4. Test backward compatibility (global deps)
5. Test multiple apps with different Kit versions
6. Test cache isolation

**Deliverable**: Comprehensive test suite

---

### Phase 6.6: Documentation (45 min)

**Tasks**:
1. User guide for per-app dependencies
2. Migration guide
3. Configuration reference
4. Troubleshooting
5. Best practices

**Deliverable**: Complete documentation

---

## Testing Strategy

### Test Cases

**Test 1: Per-App Creation**
- Create app with `--per-app-deps`
- Verify `dependencies/` directory created
- Verify `kit-deps.toml` exists

**Test 2: Isolated Build**
- Configure App A with Kit 106.0
- Configure App B with Kit 105.5
- Build both
- Verify each has correct Kit version

**Test 3: Cache Isolation**
- Modify App A's `.kit` file
- Build App A
- Build App B
- Verify App B uses its own cache (not affected)

**Test 4: Backward Compatibility**
- Build app without `dependencies/`
- Verify uses global Kit SDK
- Verify no errors

**Test 5: Launch Isolation**
- Launch App A (per-app deps)
- Launch App B (per-app deps)
- Verify each uses own Kit SDK

**Test 6: Migration**
- Start with global deps app
- Add `dependencies/kit-deps.toml`
- Rebuild
- Verify switches to per-app deps

---

## Risks & Mitigations

### Risk 1: Disk Space

**Problem**: Each app downloads its own Kit SDK (~1-2 GB)

**Mitigation**:
- Make per-app deps opt-in
- Allow shared cache for common dependencies
- Document disk requirements

### Risk 2: Build Time

**Problem**: Initial build downloads Kit SDK per app

**Mitigation**:
- Cache downloads (packman already does this)
- Parallel downloads for multiple apps
- Share cache for identical versions

### Risk 3: Complexity

**Problem**: More complex than global deps

**Mitigation**:
- Clear documentation
- Good error messages
- Helper commands for setup
- Backward compatibility (can ignore)

### Risk 4: Packman Limitations

**Problem**: Packman might not support all needed features

**Mitigation**:
- Use only documented packman features
- Test extensively before committing
- Have fallback plan (enhance packman if needed)

---

## Success Criteria

✅ Apps can specify their own Kit SDK version  
✅ Apps can use custom Kit branches  
✅ Configuration changes in one app don't affect others  
✅ Cache is properly isolated per app  
✅ Backward compatible (existing apps work unchanged)  
✅ All tests pass  
✅ Performance acceptable  
✅ Well documented

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 6.1 Foundation | 90 min | Config parsing |
| 6.2 Packman Integration | 60 min | Per-app installs |
| 6.3 Build System | 45 min | Build with per-app SDK |
| 6.4 Launch System | 30 min | Launch with per-app SDK |
| 6.5 Testing | 60 min | Test suite |
| 6.6 Documentation | 45 min | User docs |
| **Total** | **330 min** | **~5.5 hours** |

---

## Next Steps

1. Review this design
2. Prototype packman integration (test capabilities)
3. Implement Phase 6.1-6.4 sequentially
4. Test thoroughly (Phase 6.5)
5. Document (Phase 6.6)

---

**Status**: Design complete, awaiting implementation decision  
**Estimated Effort**: 5-6 hours  
**Complexity**: High (but achievable with current approach)  
**Risk**: Medium (depends on packman capabilities)

**Recommendation**: Prototype packman integration first to validate approach, then proceed with full implementation.

