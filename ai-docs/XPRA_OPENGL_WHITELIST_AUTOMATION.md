# Xpra OpenGL Whitelist - Automated Setup

## Overview

This document describes the **automated Xpra OpenGL whitelist system** that ensures Kit applications can use OpenGL rendering when launched with Xpra preview mode.

**Status:** ✅ **FULLY AUTOMATED** - No user intervention required

---

## Problem Statement

### Original Issue

Xpra was **disabling OpenGL** for the `llvmpipe` software renderer, causing Kit applications to hang during startup:

```bash
$ xpra info :100 | grep opengl
display.opengl.enable=False
display.opengl.message=driver found in greylist
display.opengl.renderer=llvmpipe (LLVM 15.0.7, 256 bits)
```

### Root Cause

Xpra maintains three lists for GPU driver management:
1. **WHITELIST** - Known good drivers (always enabled)
2. **GREYLIST** - Potentially problematic drivers (disabled by default)
3. **BLOCKLIST** - Known bad drivers (always disabled)

**Problems:**
1. `llvmpipe` (Mesa software renderer) is in the GREYLIST
2. Even if whitelisted, a secondary check re-disables greylisted drivers
3. No built-in configuration option to override this behavior

### Impact

- ❌ Kit applications hang on startup with Xpra
- ❌ No GPU/OpenGL acceleration available
- ❌ Applications never render windows
- ❌ Users see blank Xpra desktop indefinitely

---

## Solution

### Automated System

The playground now includes an **automated setup system** that:

1. ✅ **Detects** if Xpra is installed
2. ✅ **Checks** if patches are already applied
3. ✅ **Applies** patches if needed
4. ✅ **Handles** permissions (sudo or direct write access)
5. ✅ **Validates** successful patching
6. ✅ **Is idempotent** (safe to run multiple times)
7. ✅ **Runs automatically** on every `make playground` startup

### Components

#### 1. Setup Script: `tools/setup_xpra_opengl.sh`

**Location:** `/home/jkh/Src/kit-app-template/tools/setup_xpra_opengl.sh`

**Features:**
- Automatic detection of Xpra installation
- Idempotent patching (checks if already applied)
- Automatic backup creation (`.backup` files)
- Python bytecode cache clearing
- Colored output for visibility
- Graceful failure handling

**What it patches:**

**File 1: `/usr/lib/python3/dist-packages/xpra/opengl/drivers.py`**
```python
# Before:
WHITELIST: GL_MATCH_LIST = {
}

# After:
WHITELIST: GL_MATCH_LIST = {
    "renderer": ("llvmpipe",),
}
```

**File 2: `/usr/lib/python3/dist-packages/xpra/opengl/check.py`** (Line 505)
```python
# Before:
if safe and match_list(props, GREYLIST, "greylist"):
    props["enable"] = False

# After:
if safe and match_list(props, GREYLIST, "greylist") and not match_list(props, WHITELIST, "whitelist"):
    props["enable"] = False
```

#### 2. Makefile Integration

**Target:** `playground-setup-xpra`

**Dependency Chain:**
```makefile
playground: playground-stop → playground-setup-xpra → playground-start
```

**Logic:**
1. Check if `xpra` command exists
2. Check if we have write permissions to Xpra Python files
3. Run script directly if we have write access
4. Use `sudo` if passwordless sudo is available
5. Skip gracefully if neither condition is met

**Code:**
```makefile
.PHONY: playground-setup-xpra
playground-setup-xpra:
	@if command -v xpra >/dev/null 2>&1; then \
		if [ -w /usr/lib/python3/dist-packages/xpra/opengl/drivers.py ] 2>/dev/null; then \
			./tools/setup_xpra_opengl.sh; \
		elif sudo -n true 2>/dev/null; then \
			sudo ./tools/setup_xpra_opengl.sh; \
		else \
			echo "$(YELLOW)[Xpra OpenGL] Skipping setup - requires sudo or file permissions$(NC)"; \
		fi \
	fi
```

---

## User Experience

### First Run (Patches Not Applied)

```bash
$ make playground
Stopping all playground and application processes...
✓ All playground and application processes stopped
[Xpra OpenGL] Patching drivers.py to whitelist llvmpipe...
[Xpra OpenGL]   Created backup: /usr/lib/python3/dist-packages/xpra/opengl/drivers.py.backup
[Xpra OpenGL] ✓ drivers.py patched successfully
[Xpra OpenGL] Patching check.py to fix whitelist bypass...
[Xpra OpenGL]   Created backup: /usr/lib/python3/dist-packages/xpra/opengl/check.py.backup
[Xpra OpenGL] ✓ check.py patched successfully
[Xpra OpenGL] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Xpra OpenGL] ✅ Xpra OpenGL setup complete!
[Xpra OpenGL]    llvmpipe software renderer is now whitelisted
[Xpra OpenGL]    OpenGL will be enabled in Xpra sessions
[Xpra OpenGL] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Kit Playground...
...
```

### Subsequent Runs (Patches Already Applied)

```bash
$ make playground
Stopping all playground and application processes...
✓ All playground and application processes stopped
[Xpra OpenGL] ✓ llvmpipe already whitelisted in drivers.py
[Xpra OpenGL] ✓ check.py already has whitelist bypass fix
[Xpra OpenGL] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Xpra OpenGL] ✅ Xpra OpenGL setup complete!
[Xpra OpenGL]    llvmpipe software renderer is now whitelisted
[Xpra OpenGL]    OpenGL will be enabled in Xpra sessions
[Xpra OpenGL] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Kit Playground...
...
```

### Without Xpra Installed

```bash
$ make playground
Stopping all playground and application processes...
✓ All playground and application processes stopped
[Xpra OpenGL] Xpra not installed, skipping OpenGL setup
Starting Kit Playground...
...
```

### Without Sufficient Permissions

```bash
$ make playground
Stopping all playground and application processes...
✓ All playground and application processes stopped
[Xpra OpenGL] Skipping setup - requires sudo or file permissions
Starting Kit Playground...
...
```

---

## Verification

### Manual Verification

After the automated setup runs, verify OpenGL is enabled:

```bash
# Start a test Xpra session
$ XPRA_OPENGL=1 XPRA_OPENGL_ALLOW_GREYLISTED=1 \
  xpra start :110 --bind-tcp=0.0.0.0:10010 --html=on --opengl=yes --daemon=yes

# Check OpenGL status
$ xpra info :110 | grep -E "opengl.enable|opengl.renderer|opengl.message"
display.opengl.renderer=llvmpipe (LLVM 15.0.7, 256 bits)
# NO display.opengl.enable=False (means it's enabled!)
# NO display.opengl.message=driver found in greylist (no longer disabled!)

# Clean up
$ xpra stop :110
```

### End-to-End Test

1. Start the playground:
   ```bash
   make playground
   ```

2. Create a Kit application in the UI

3. Build the application

4. Click "Launch" → Application launches with Xpra

5. Xpra window opens at `http://<hostname>:10000`

6. Kit application renders successfully (may take 30-60 seconds to initialize)

---

## Technical Details

### Why Two Patches Are Needed

**Patch 1: Whitelist llvmpipe**
- Adds `llvmpipe` to the WHITELIST in `drivers.py`
- This marks the driver as "known good"
- However, this alone is not sufficient...

**Patch 2: Fix greylist bypass logic**
- The `check.py` file has a **bug** in its greylist handling
- Even if a driver is whitelisted, a secondary check re-disables it if it's also greylisted
- Original logic: `if greylisted → disable`
- Fixed logic: `if greylisted AND NOT whitelisted → disable`

### Why Software Rendering?

The system uses **Mesa llvmpipe** (software rendering) because:

1. **No physical GPU** available in the environment
2. **Remote access** - GPU forwarding is complex
3. **Simplicity** - Software rendering works everywhere
4. **Compatibility** - No driver installation required

**Performance:**
- ⚠️ CPU-based rendering (slower)
- ⚠️ No GPU acceleration
- ✅ Good enough for development/testing
- ✅ Works reliably

For production, use Kit App Streaming (WebRTC) which has better GPU support.

---

## Backup and Rollback

### Backup Files

The setup script automatically creates backups on first run:

- `/usr/lib/python3/dist-packages/xpra/opengl/drivers.py.backup`
- `/usr/lib/python3/dist-packages/xpra/opengl/check.py.backup`

### Manual Rollback

If you need to revert the patches:

```bash
# Restore original files
sudo cp /usr/lib/python3/dist-packages/xpra/opengl/drivers.py.backup \
        /usr/lib/python3/dist-packages/xpra/opengl/drivers.py

sudo cp /usr/lib/python3/dist-packages/xpra/opengl/check.py.backup \
        /usr/lib/python3/dist-packages/xpra/opengl/check.py

# Clear Python bytecode cache
sudo rm -f /usr/lib/python3/dist-packages/xpra/opengl/__pycache__/*.pyc

# Restart any Xpra sessions
xpra stop-all
```

---

## Troubleshooting

### Issue: Patches not being applied

**Symptoms:**
```
[Xpra OpenGL] Skipping setup - requires sudo or file permissions
```

**Solutions:**

**Option 1: Run with sudo (recommended)**
```bash
# Run once manually with sudo to apply patches
sudo ./tools/setup_xpra_opengl.sh

# Then start playground normally
make playground
```

**Option 2: Configure passwordless sudo for the script**
```bash
# Add to /etc/sudoers.d/xpra-setup (use visudo!)
yourusername ALL=(ALL) NOPASSWD: /path/to/kit-app-template/tools/setup_xpra_opengl.sh
```

**Option 3: Change file permissions (not recommended)**
```bash
# Only if you trust the script completely
sudo chown -R $USER /usr/lib/python3/dist-packages/xpra/opengl/
```

### Issue: Xpra still shows "driver found in greylist"

**Check Python bytecode cache:**
```bash
# Clear all Xpra OpenGL cache
sudo rm -rf /usr/lib/python3/dist-packages/xpra/opengl/__pycache__/

# Restart Xpra session
xpra stop-all
```

**Verify patches were actually applied:**
```bash
# Check drivers.py
grep -A 2 "^WHITELIST" /usr/lib/python3/dist-packages/xpra/opengl/drivers.py

# Should show:
# WHITELIST: GL_MATCH_LIST = {
#     "renderer": ("llvmpipe",),
# }

# Check check.py
grep -A 2 "match_list(props, GREYLIST" /usr/lib/python3/dist-packages/xpra/opengl/check.py

# Should show:
# if safe and match_list(props, GREYLIST, "greylist") and not match_list(props, WHITELIST, "whitelist"):
```

### Issue: Kit application still hangs with Xpra

**Verify OpenGL is actually enabled:**
```bash
# Start Xpra
xpra start :111 --bind-tcp=0.0.0.0:10011 --html=on --opengl=yes --daemon=yes

# Check status after it starts (wait 3 seconds)
sleep 3
xpra info :111 | grep "display.opengl"

# Look for:
# - opengl.renderer should be "llvmpipe"
# - opengl.safe should be "True"
# - NO opengl.enable=False
# - NO opengl.message=driver found in greylist
```

**If OpenGL is still disabled**, check Xpra logs:
```bash
tail -100 ~/.xpra/:111/server.log | grep -i opengl
```

---

## Future Improvements

### Potential Enhancements

1. **Auto-detect GPU drivers**
   - If real GPU is available, whitelist it instead
   - Detect NVIDIA, AMD, Intel drivers
   - Use hardware acceleration when possible

2. **Configuration file support**
   - Create `~/.xpra/xpra.conf` with whitelist
   - Less invasive than patching system files
   - Per-user configuration

3. **Xpra version detection**
   - Different Xpra versions may have different file structures
   - Adapt patching logic based on version
   - Support multiple Xpra installation paths

4. **Health check**
   - Test Xpra OpenGL on startup
   - Warn if OpenGL is not working
   - Provide actionable troubleshooting steps

---

## Related Documentation

- **Main Issue:** `ai-docs/XPRA_OPENGL_HANG_ISSUE.md`
- **Xpra Setup:** `docs/XPRA_SETUP.md`
- **Launch Decision Tree:** `ai-docs/SMART_LAUNCH_DECISION_TREE.md`
- **Port Registry:** `kit_playground/backend/source/port_registry.py`

---

## Commit History

**Initial Implementation:**
- Created automated setup script
- Integrated into Makefile
- Added comprehensive documentation
- Tested idempotency and error handling

**Benefits:**
- ✅ Zero user intervention required
- ✅ Runs on every playground startup
- ✅ Handles permissions gracefully
- ✅ Provides clear feedback
- ✅ Safe to run multiple times
- ✅ Creates automatic backups

---

## Summary

The Xpra OpenGL whitelist system is now **fully automated** and seamlessly integrated into the playground startup process. Users don't need to know it exists - it just works! 🎉

**Key Points:**
1. Runs automatically with `make playground`
2. Detects and applies patches if needed
3. Idempotent and safe
4. Handles permissions intelligently
5. Provides clear, colored output
6. Creates automatic backups
7. Enables OpenGL for Kit applications in Xpra

**Result:** Kit applications can now successfully launch and render using Xpra preview mode with software-based OpenGL rendering!

