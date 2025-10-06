# Wrapper Integration for Unix-Friendly CLI & UI Workflow

## Overview

The Kit App Template now has a unified, Unix-friendly workflow where both CLI and UI operations work seamlessly from any directory within an app.

## What Was Implemented

### 1. **Wrapper Scripts** (`repo.sh` and `repo.bat`)

Each created application now includes wrapper scripts that automatically find the repository root:

**Location**: `_build/apps/<app_name>/repo.sh` (and `repo.bat` for Windows)

**Features**:
- Walks up the directory tree to find repo root (looking for `repo.sh` + `repo.toml`)
- Passes all arguments through to the main `repo.sh`
- Works from anywhere inside the app directory
- Cross-platform (Linux/macOS/Windows)

### 2. **CLI Workflow**

#### Before (Broken):
```bash
$ ./repo.sh template new kit_base_editor --name=myapp --version=1.0.0
✓ Application 'myapp' created in _build/apps/myapp
Build with: ./repo.sh build

$ cd _build/apps/myapp
$ ./repo.sh build
# ERROR: ./repo.sh: No such file or directory
```

#### After (Fixed):
```bash
$ ./repo.sh template new kit_base_editor --name=myapp --version=1.0.0
✓ Application 'myapp' created successfully in
  /path/to/_build/apps/myapp

Main configuration: myapp.kit

To build (from repository root):
  cd /path/to/kit-app-template && ./repo.sh build --config release

Or build from app directory:
  cd /path/to/_build/apps/myapp && ./repo.sh build --config release

$ cd _build/apps/myapp
$ ./repo.sh build --config release
# SUCCESS: Wrapper finds repo root and builds!
```

### 3. **UI Integration**

The backend now mirrors the CLI workflow:

#### Build Endpoint (`/api/projects/build`)
```python
# Before: Always ran from repo root
subprocess.run([repo_root / 'repo.sh', 'build'], cwd=repo_root)

# After: Uses app-specific wrapper
if wrapper_script.exists():
    subprocess.run(['./repo.sh', 'build'], cwd=app_dir)
```

#### Run/Launch Endpoint (`/api/projects/run`)
```python
# Before: Always ran from repo root
subprocess.Popen([repo_root / 'repo.sh', 'launch', kit_file], cwd=repo_root)

# After: Uses app-specific wrapper
if wrapper_script.exists():
    subprocess.Popen(['./repo.sh', 'launch', kit_file], cwd=app_dir)
```

**Benefits**:
- UI operations match CLI behavior exactly
- Project context is preserved (working directory is app directory)
- Easier to debug (logs show correct working directory)
- Fallback to repo root for older projects without wrappers

## Files Modified

### 1. Template Creation Scripts
- `tools/repoman/repo_dispatcher.py` - Main script that creates apps
- `kit_playground/backend/source/apps/tools/repoman/repo_dispatcher.py` - Backend copy

**Changes**:
- Creates `repo.sh` wrapper (executable bash script)
- Creates `repo.bat` wrapper (Windows batch file)
- Updates success message with clear instructions

### 2. Backend API
- `kit_playground/backend/web_server.py`

**Changes**:
- `build_project()` - Uses wrapper from app dir if available
- `run_project()` - Uses wrapper from app dir if available
- Both functions receive `projectPath` from UI
- Graceful fallback for older projects

### 3. UI (No changes needed!)
- Already sends `projectPath` with build/run requests
- Works seamlessly with the new backend behavior

## How It Works

### Wrapper Script Logic

```bash
#!/bin/bash
# Find repository root by looking for repo.sh and repo.toml
find_repo_root() {
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/repo.sh" ] && [ -f "$dir/repo.toml" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "Error: Could not find repository root" >&2
    return 1
}

REPO_ROOT=$(find_repo_root)
# Call the main repo.sh with all arguments
exec "$REPO_ROOT/repo.sh" "$@"
```

### Backend Flow

```
User clicks "Build" on project in UI
    ↓
UI sends: { projectPath: "_build/apps/myapp", projectName: "myapp" }
    ↓
Backend receives request
    ↓
Backend checks: Does _build/apps/myapp/repo.sh exist?
    ↓
YES: cd _build/apps/myapp && ./repo.sh build --config release
    ↓
Wrapper finds repo root and calls main repo.sh
    ↓
Build succeeds!
```

## Testing

### CLI Test
```bash
# Create app
./repo.sh template new kit_base_editor --name=test.app --version=1.0.0

# Navigate to app
cd _build/apps/test.app

# Verify wrapper exists
ls -l repo.sh repo.bat

# Test build from app dir
./repo.sh build --config release

# Test from subdirectory
mkdir -p subdir && cd subdir
../repo.sh build  # Also works!
```

### UI Test
1. Create new project in UI
2. Select project in sidebar
3. Click "Build" icon → Backend uses wrapper
4. Click "Run" icon → Backend uses wrapper
5. Check console logs for "Using wrapper from: ..." messages

## Backward Compatibility

✅ **Older projects without wrappers still work**
- Backend checks if wrapper exists
- Falls back to repo root execution if not found
- No breaking changes

## Benefits

### For Users
- ✅ Consistent CLI and UI behavior
- ✅ Can run commands from app directory
- ✅ Clear, copy-pasteable instructions
- ✅ Works on all platforms (Linux/macOS/Windows)

### For Developers
- ✅ Easier debugging (correct working directory)
- ✅ Better logging (shows actual execution context)
- ✅ Matches Unix tool conventions (like `git`)
- ✅ Automation-friendly (scripts can cd to app dir)

## Future Enhancements

Potential improvements:
- Make main `repo.sh` also search upward for repo root
- Add `--app` flag to main `repo.sh` to target specific app
- Support relative paths in wrapper scripts
- Add wrapper script tests

## Documentation Updates

Updated files:
- `kit_playground/CRITICAL_FIX_PLAN.md`
- `kit_playground/BREAKING_CHANGES_IMPLEMENTED.md`
- `kit_playground/IMPLEMENTATION_SUMMARY.md`

All instances of incorrect `--path` flag removed.
