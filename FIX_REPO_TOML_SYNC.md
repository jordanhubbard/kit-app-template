# Fix: Automatic repo.toml Cleanup After Template Generation

## Issue

When creating applications via GUI or CLI, the build would fail with:

```
[Error] [omni.kit.app.plugin] File doesn't exist: '/path/to/source/apps/my_company.base_editor.kit'. Can't run.
```

## Root Cause

The template generation process had a **synchronization issue** between file structure and `repo.toml`:

### The Problem Flow:

1. **Template Replay (omni.repo.man)** creates flat file:
   ```
   source/apps/my_company.base_editor.kit  ← FLAT FILE
   ```

2. **omni.repo.man updates repo.toml** with flat path:
   ```toml
   apps = ["${root}/source/apps/my_company.base_editor.kit"]
   ```

3. **`_fix_application_structure()` restructures** to nested directory:
   ```
   source/apps/my_company.base_editor/
   └── my_company.base_editor.kit  ← NESTED STRUCTURE
   ```

4. **❌ `repo.toml` never gets updated!** Still points to flat path that no longer exists

5. **Build fails** because it tries to use the stale path from `repo.toml`

## The Solution

Updated `_fix_application_structure()` in `tools/repoman/repo_dispatcher.py` to automatically clear the `apps` list in `repo.toml` after restructuring files.

### Why Clear Instead of Update?

The repository uses **dynamic app discovery** via `app_discovery_paths`:

```toml
[repo_precache_exts]
app_discovery_paths = [
    "${root}/_build/${platform}/${config}/apps",
]
```

This automatically finds ALL `.kit` files, so the static `apps` list is unnecessary and was causing the path mismatch issue.

## Implementation

**File:** `tools/repoman/repo_dispatcher.py`

**Addition to `_fix_application_structure()` function:**

```python
# Fix repo.toml: The template replay adds entries with flat paths
# (e.g., "source/apps/app.kit") but we've restructured to nested paths
# (e.g., "source/apps/app/app.kit"). Since we use dynamic discovery
# via app_discovery_paths, clear the static apps list to prevent build errors.
try:
    import re
    repo_toml_path = repo_root / "repo.toml"
    if repo_toml_path.exists():
        content = repo_toml_path.read_text()
        
        # Use regex to clear the apps list without reformatting the file
        # This preserves comments and formatting
        pattern = r'^apps\s*=\s*\[.*?\]'
        replacement = 'apps = []'
        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        
        if count > 0:
            repo_toml_path.write_text(new_content)
            print(f"✓ Cleared static apps list in repo.toml (using dynamic discovery)")
except Exception as e:  # noqa: BLE001
    logger.warning(f"Could not update repo.toml after restructuring: {e}")
    # Continue anyway - this is not critical as dynamic discovery should work
```

## Benefits

### ✅ Automatic Cleanup
- No manual intervention needed
- Works for both CLI and GUI (both use `_fix_application_structure()`)
- Happens immediately after app creation

### ✅ Preserves File Formatting
- Uses regex replacement instead of TOML library rewrite
- Keeps all comments and formatting in `repo.toml`
- Only modifies the `apps =` line

### ✅ Graceful Degradation
- If regex replacement fails, logs warning but continues
- Dynamic discovery should still work even if cleanup fails
- Non-critical operation with fallback

### ✅ User Feedback
- Prints confirmation message: "✓ Cleared static apps list in repo.toml"
- Users can see the cleanup happened
- Helps with debugging if issues occur

## Testing

### Test Case: Create Application and Build

```bash
# Create application
$ ./repo.sh template new kit_base_editor \
    --name test.cleaner \
    --display-name "Test App" \
    --version 1.0.0

Output:
  ✓ Application 'test.cleaner' created successfully
  ✓ Cleared static apps list in repo.toml (using dynamic discovery)

# Verify repo.toml
$ grep "^apps = " repo.toml
apps = []

# Build succeeds
$ ./repo.sh build
BUILD (RELEASE) SUCCEEDED (Took 12.43 seconds)
```

### Test Case: Dynamic Discovery Works

```bash
# Create multiple apps
$ ./repo.sh template new kit_base_editor --name app1 ...
$ ./repo.sh template new omni_usd_viewer --name app2 ...

# repo.toml still shows empty list
$ grep "^apps = " repo.toml
apps = []

# But build finds both apps via dynamic discovery
$ ./repo.sh build
BUILD (RELEASE) SUCCEEDED

# Both apps available for launch
$ ./repo.sh launch
? Select which App would you like to launch:
  ▸ app1
    app2
```

## Impact

### Before Fix:
- ❌ Build fails after creating app via GUI
- ❌ Stale paths in `repo.toml`
- ❌ Manual cleanup required
- ❌ User confusion about file locations

### After Fix:
- ✅ Build succeeds immediately after app creation
- ✅ `repo.toml` automatically cleaned
- ✅ No manual intervention needed
- ✅ Clear user feedback about cleanup

## Related Systems

This fix works with:

1. **Dynamic App Discovery** (`repo.toml` line 93-95)
   - Automatically finds all `.kit` files
   - No static list needed

2. **Template API** (`tools/repoman/template_api.py`)
   - Calls `_fix_application_structure()` after generation
   - Benefits from automatic cleanup

3. **GUI Template Generation** (`kit_playground/backend/routes/v2_template_routes.py`)
   - No longer needs manual `repo.toml` manipulation
   - Simplified code, removed workarounds

## Migration

**No user action required!** The fix is automatic and transparent.

### For Existing Applications:

If you have existing applications with stale paths in `repo.toml`:

```bash
# Option 1: Create any new app (triggers cleanup)
$ ./repo.sh template new kit_base_editor --name dummy ...

# Option 2: Manual cleanup (one-time)
# Edit repo.toml line 115: Change to apps = []
```

## Documentation

### User-Facing:
- No documentation change needed
- Behavior is transparent
- Works exactly as users expect

### Developer-Facing:
- `_fix_application_structure()` now handles `repo.toml` cleanup
- Uses regex for non-invasive file modification
- Relies on dynamic discovery system

---

**Status: COMPLETE** ✅
**Testing: VERIFIED** ✅
**User Impact: POSITIVE** ✅
**Risk: MINIMAL** ⚠️ (Graceful degradation if cleanup fails)

