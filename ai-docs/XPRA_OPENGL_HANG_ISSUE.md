# Xpra OpenGL Hang Issue (2024-10-27)

## Issue Summary

Kit applications launched with Xpra preview hang during startup and never display a window, even though:
- ✅ Application process is running
- ✅ Xpra server is running
- ✅ DISPLAY is correctly set (:100)
- ❌ No window appears in Xpra

## Root Cause

**OpenGL is disabled in Xpra despite being requested with `--opengl=yes`**

```bash
$ xpra info :100 | grep opengl.enable
display.opengl.enable=False
display.opengl.message=driver found in greylist
display.opengl.renderer=llvmpipe (LLVM 15.0.7, 256 bits)
```

### Why This Happens

1. Xpra was started with `--opengl=yes`
2. Xpra detected the GPU driver but found it in the "greylist"
3. Greylisted drivers are considered unreliable/unsafe
4. Xpra disabled OpenGL for safety
5. Falls back to CPU-based software rendering (`llvmpipe`)
6. Kit applications require GPU/OpenGL to initialize
7. Kit hangs waiting for GPU that's not available

## Symptoms

### User Experience
- Xpra window opens and shows desktop
- "Application is starting..." message in UI
- No application window ever appears
- Blank Xpra desktop forever

### Technical Indicators
```bash
# Process running but hung
$ ps aux | grep kit | grep happy_nebula
jkh  1110011  4.5  0.3 3743320 280484 ?  S  16:19  0:06  kit happy_nebula_1.kit

# Process state: S (Interruptible Sleep)
$ ps -p 1110011 -o state
S

# No windows registered with Xpra
$ xpra info :100 | grep state.windows
state.windows=0

# Log stuck at extension pulling
$ tail -1 ~/.nvidia-omniverse/logs/Kit/happy_nebula_1/1.0/kit*.log
[9,673ms] [Info] Pulling extension: `omni.kit.viewport.menubar.settings-107.0.4`
# ^ Last log entry, no progression

# Log file not being updated
$ stat ~/.nvidia-omniverse/logs/Kit/happy_nebula_1/1.0/kit*.log | grep Modify
Modify: 2025-10-27 16:19:38.936476246 +0000
# ^ Minutes/hours old
```

## Why Kit Hangs

Kit applications initialize in this order:
1. ✅ Start process
2. ✅ Initialize extensions
3. ✅ Pull dependencies from registry
4. ⏸️ **Initialize OpenGL context** ← HANGS HERE
5. ❌ Create window (never reached)
6. ❌ Show UI (never reached)

When OpenGL is unavailable, Kit gets stuck in step 4 trying to initialize the graphics subsystem.

## Solutions

### Option 1: Whitelist GPU Driver in Xpra

**Add driver to Xpra's whitelist:**

```bash
# Find current driver
xpra info :100 | grep opengl.renderer
# Output: llvmpipe (LLVM 15.0.7, 256 bits)

# Edit Xpra config to whitelist it
# /etc/xpra/conf.d/60_opengl.conf or ~/.xpra/xpra.conf
opengl-driver-whitelist=llvmpipe,mesa,nvidia

# Restart Xpra
xpra stop :100
xpra start :100 --bind-tcp=0.0.0.0:10000 --html=on --opengl=yes
```

### Option 2: Force Software Rendering in Kit

**Launch Kit with software renderer:**

```bash
# Option A: Disable renderer entirely (headless)
./repo.sh launch --name app.kit --no-window

# Option B: Software rendering mode
LIBGL_ALWAYS_SOFTWARE=1 ./repo.sh launch --name app.kit --xpra

# Option C: Kit config flag
./repo.sh launch --name app.kit --xpra -- --/renderer/enabled=false
```

### Option 3: Use Kit App Streaming Instead of Xpra

**Kit App Streaming (WebRTC) handles GPU better:**

Advantages:
- Built-in GPU handling
- Better performance
- Hardware acceleration support
- Designed for Kit applications

Disadvantages:
- Requires streaming extensions
- More complex setup
- Not available in all SDK configurations

**Switch to streaming:**
```python
# In project_routes.py
use_xpra = False
is_streaming_app = True
```

### Option 4: Use Direct Display (If Available)

**If user has local DISPLAY:**

```bash
# Check if DISPLAY is available
$ echo $DISPLAY
:0

# Launch directly (no Xpra)
./repo.sh launch --name app.kit
```

## Recommended Fix for Kit Playground

### Short-term: Detect and Warn

Add OpenGL validation before launch:

```python
# In project_routes.py - run_project endpoint

def check_xpra_opengl(display):
    """Check if Xpra has OpenGL enabled."""
    result = subprocess.run(
        ['xpra', 'info', f':{display}'],
        capture_output=True,
        text=True
    )
    
    for line in result.stdout.split('\n'):
        if 'display.opengl.enable=' in line:
            enabled = 'True' in line
            if not enabled:
                return False, "OpenGL disabled in Xpra (driver greylisted)"
    
    return True, "OpenGL enabled"

# Before launching Kit
opengl_ok, message = check_xpra_opengl(xpra_display)
if not opengl_ok:
    logger.warning(f"Xpra OpenGL issue: {message}")
    socketio.emit('log', {
        'level': 'warning',
        'source': 'runtime',
        'message': f'⚠️ {message} - Application may not display'
    })
```

### Long-term: Smart Launch Mode Selection

```python
def select_launch_mode(app_info):
    """
    Smart decision tree for launch mode:
    1. If streaming app → Use Kit App Streaming
    2. If no DISPLAY and Xpra unavailable → Error
    3. If DISPLAY available → Direct launch (best performance)
    4. If remote + Xpra available → Xpra with OpenGL check
    """
    
    if app_info.get('streaming'):
        return 'streaming'
    
    has_display = os.environ.get('DISPLAY')
    if has_display and not is_remote_client():
        return 'direct'
    
    if xpra_available():
        opengl_ok, _ = check_xpra_opengl()
        if opengl_ok:
            return 'xpra'
        else:
            return 'xpra_sw'  # Software rendering
    
    return 'error'
```

## Detection Script

```bash
#!/bin/bash
# check_xpra_opengl.sh

DISPLAY_NUM=${1:-100}

echo "Checking Xpra OpenGL on display :$DISPLAY_NUM"
echo "=============================================="

# Check if Xpra is running
if ! xpra info :$DISPLAY_NUM >/dev/null 2>&1; then
    echo "❌ Xpra not running on :$DISPLAY_NUM"
    exit 1
fi

# Check OpenGL status
OPENGL_ENABLED=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "display.opengl.enable=" | cut -d= -f2)
OPENGL_MESSAGE=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "display.opengl.message=" | cut -d= -f2)
OPENGL_RENDERER=$(xpra info :$DISPLAY_NUM 2>/dev/null | grep "display.opengl.renderer=" | cut -d= -f2)

echo "OpenGL Enabled: $OPENGL_ENABLED"
echo "OpenGL Message: $OPENGL_MESSAGE"
echo "OpenGL Renderer: $OPENGL_RENDERER"

if [ "$OPENGL_ENABLED" = "False" ]; then
    echo ""
    echo "❌ OpenGL is DISABLED"
    echo "⚠️  Kit applications will hang during startup"
    echo ""
    echo "Reason: $OPENGL_MESSAGE"
    echo ""
    echo "Solutions:"
    echo "  1. Whitelist the GPU driver in Xpra config"
    echo "  2. Use software rendering (LIBGL_ALWAYS_SOFTWARE=1)"
    echo "  3. Use Kit App Streaming instead of Xpra"
    exit 1
else
    echo ""
    echo "✅ OpenGL is enabled"
    echo "✅ Kit applications should work"
    exit 0
fi
```

## Testing

### Test 1: Verify OpenGL Status
```bash
$ xpra info :100 | grep -E "opengl.enable|opengl.message|opengl.renderer"
display.opengl.enable=True   # Should be True
display.opengl.renderer=NVIDIA GeForce RTX 3090  # Real GPU, not llvmpipe
```

### Test 2: Verify Window Creation
```bash
# Launch test app
$ DISPLAY=:100 glxgears &

# Check window count
$ xpra info :100 | grep state.windows
state.windows=1  # Should be > 0
```

### Test 3: Verify Kit Launch
```bash
# Launch Kit app with timeout
$ timeout 30s xpra info :100 --wait-for windows

# If timeout expires → Hung
# If returns quickly → Window created
```

## Related Issues

- **Xpra Driver Greylist:** `/etc/xpra/conf.d/60_opengl.conf`
- **Mesa Software Rendering:** `LIBGL_ALWAYS_SOFTWARE` environment variable
- **Kit OpenGL Requirements:** Kit SDK requires OpenGL 4.5+
- **Remote GPU Access:** VirtualGL, TurboVNC as alternatives

## References

- Xpra OpenGL Configuration: https://github.com/Xpra-org/xpra/wiki/OpenGL
- Kit SDK GPU Requirements: [Kit SDK Documentation]
- Mesa llvmpipe: Software OpenGL rasterizer (CPU-based)

## Commit

This issue needs to be fixed in the next iteration of the playground.

**Priority:** High
**Impact:** Xpra preview mode is unusable for Kit applications
**Workaround:** Use Kit App Streaming or direct display

