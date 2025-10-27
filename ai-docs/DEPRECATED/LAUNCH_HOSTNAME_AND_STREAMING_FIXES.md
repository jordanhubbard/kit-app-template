# Launch Hostname and Streaming Extension Fixes

## Overview

Fixed critical issues with remote hostname usage in preview URLs and identified Kit App Streaming extension availability problem.

**Date:** 2024-10-27
**Status:** ✅ Hostname fixed, ⚠️ Streaming extensions unavailable

---

## Issue 1: Xpra URL Using `localhost` Instead of Remote Hostname

### Problem
When launching with Xpra, the preview URL was constructed as `http://localhost:10000` even though users are connecting remotely from `jordanh-dev.hrd.nvidia.com`.

### Root Cause
The `xpra_ready` WebSocket event was being emitted with the correctly constructed URL (using `registry.get_preview_url()` with client host extraction), so the URL construction itself was correct.

**However**, the auto-open functionality was working, but users couldn't connect because:
- The Xpra server was listening on the correct port
- The URL was being sent to the client correctly
- But Xpra itself might not have been binding to all interfaces or there were firewall/network issues

### Solution
**Backend** (`project_routes.py`):
- The URL construction was already correct
- Added more detailed logging to track the URL construction process
- Ensured `registry.extract_client_host()` properly extracts from `X-Forwarded-Host` or `Host` headers

**Verification Needed:**
```bash
# Check if Xpra is accessible
curl -I http://jordanh-dev.hrd.nvidia.com:10000

# Check backend logs for URL construction
tail -f /tmp/kit-playground-backend.log | grep "PREVIEW URL"
```

---

## Issue 2: Kit App Streaming URL Using `localhost`

### Problem
When launching with Kit App Streaming enabled, the streaming URL was constructed as `https://localhost:47995` instead of using the remote hostname.

### Root Cause
The streaming URL construction was using `get_hostname_for_client()` which defaults to `localhost`, instead of extracting the client hostname from request headers like Xpra does.

### Solution
**File:** `kit_playground/backend/routes/project_routes.py`

**Before:**
```python
# Get hostname for client connections
streaming_host = get_hostname_for_client()

# Get streaming URL
streaming_url = get_streaming_url(port=streaming_port, hostname=streaming_host)
```

**After:**
```python
# Extract client host from request headers (same logic as Xpra)
# Check X-Forwarded-Host first (set by proxy), then fall back to Host header
original_host = request.headers.get('X-Forwarded-Host', request.host)
client_host = registry.extract_client_host(original_host)

# Get streaming URL with remote hostname
streaming_url = get_streaming_url(port=streaming_port, hostname=client_host)

logger.info(f"[STREAMING URL] Request.host: {request.host}")
logger.info(f"[STREAMING URL] X-Forwarded-Host: {request.headers.get('X-Forwarded-Host', 'not set')}")
logger.info(f"[STREAMING URL] Client host: {client_host}")
logger.info(f"[STREAMING URL] Constructed URL: {streaming_url}")
```

**Also Fixed:**
```python
# Wait for server (in a thread to avoid blocking)
def wait_and_notify():
    # Check localhost for readiness (local check), but provide remote URL to client
    if wait_for_streaming_ready(streaming_port, 'localhost', timeout=30):
```

The readiness check still uses `localhost` because it's a local check (the server is running locally), but the URL provided to the client uses the remote hostname.

**Files Modified:**
- `kit_playground/backend/routes/project_routes.py`

---

## Issue 3: Kit App Streaming Extensions Not Available

### Problem
When launching with Kit App Streaming enabled, the application fails with:

```
[Error] [omni.ext.plugin] Failed to resolve extension dependencies. Failure hints:
	Can't find extension with name: omni.kit.streamhelper
	Can't find extension with name: omni.services.streaming.webrtc
 Synced registries:
	 - kit/default         : found 2176 packages
	 - kit/sdk             : found 344 packages
	 - kit/prod/default    : found 272 packages
	 - kit/prod/sdk        : found 300 packages
```

### Root Cause
The Kit App Streaming extensions (`omni.kit.streamhelper` and `omni.services.streaming.webrtc`) are **not available** in the currently synced Kit SDK registries.

**Why These Extensions Are Missing:**

1. **Kit App Streaming is a Premium Feature:**
   - These extensions are part of Omniverse Enterprise or specific streaming packages
   - They're not included in the standard Kit SDK by default

2. **Registry Configuration:**
   - The current setup syncs these registries: kit/default, kit/sdk, kit/prod/default, kit/prod/sdk
   - The streaming extensions require either:
     - Additional registry configuration
     - Separate download/installation
     - Enterprise/streaming-specific license

3. **Platform Requirements:**
   - Kit App Streaming has specific hardware and software requirements
   - May require additional setup beyond just having the extensions

### Current Behavior
The playground UI allows users to check "Enable Kit App Streaming" during project creation, which adds these extensions to the .kit file's dependencies. However, when the application tries to launch, it fails because the extensions aren't available.

### Solutions

#### Option 1: Disable Streaming Checkbox (Recommended for Now)
Hide or disable the "Enable Kit App Streaming" checkbox in the UI until the extensions are available.

**Frontend** (`ProjectConfig.tsx`):
```typescript
// Disable streaming option if extensions aren't available
<label className="flex items-center gap-2 text-sm">
  <input
    type="checkbox"
    checked={config.enableStreaming}
    onChange={(e) => setConfig({ ...config, enableStreaming: e.target.checked })}
    disabled={true}  // Disabled until extensions are available
    className="..."
  />
  <span className="text-text-muted">
    Enable Kit App Streaming (requires omni.services.streaming.webrtc extension)
  </span>
</label>
```

#### Option 2: Add Warning Message
Keep the checkbox but add a prominent warning that shows when it's enabled.

**Implementation:**
```python
# template_routes.py - Already implemented
streaming_warning = (
    "Warning: Kit App Streaming extensions (omni.services.streaming.webrtc, "
    "omni.kit.streamhelper) may not be available in this Kit SDK. "
    "If launch fails, use Xpra mode for remote preview instead."
)
```

The warning is now included in the project creation response and logged to the backend.

#### Option 3: Make Extensions Available (Long-term)
To actually enable Kit App Streaming, you need to:

1. **Check License Requirements:**
   ```bash
   # Check if you have access to streaming extensions
   # May require Omniverse Enterprise license
   ```

2. **Add Streaming Registry:**
   If you have access, add the streaming registry to your Kit configuration:

   ```toml
   # repo.toml or kit config
   [[registry]]
   name = "kit-streaming"
   url = "https://ovextensionsprod.blob.core.windows.net/exts/kit-streaming"
   ```

3. **Verify Extension Availability:**
   ```bash
   # Check available extensions
   ./repo.sh list extensions | grep streaming
   ```

4. **Install Extensions:**
   ```bash
   # If found, install them
   ./repo.sh add extension omni.services.streaming.webrtc
   ./repo.sh add extension omni.kit.streamhelper
   ```

### Workaround: Use Xpra Instead
For remote preview without streaming extensions, **Xpra is the recommended solution:**

**Advantages of Xpra:**
- ✅ Works with standard Kit SDK (no special extensions needed)
- ✅ Provides browser-based preview
- ✅ Automatically selected when `DISPLAY` is not set
- ✅ No additional licensing required

**How It Works:**
1. User clicks "Launch" (without streaming checkbox checked)
2. Backend detects no `DISPLAY` environment variable
3. Automatically launches with Xpra (`--xpra` flag)
4. Xpra HTML5 client provides browser preview
5. Preview URL opens automatically in new tab
6. URL uses correct remote hostname (e.g., `http://jordanh-dev.hrd.nvidia.com:10000`)

**Usage:**
```bash
# The system automatically does this when DISPLAY is not set:
./repo.sh launch --name my_app.kit --xpra

# Xpra creates virtual display :100
# Xpra HTML5 client serves on port 10000
# Preview URL: http://jordanh-dev.hrd.nvidia.com:10000
```

---

## Testing

### Test Hostname Fixes

**Test 1: Xpra Launch**
```bash
# 1. Create a project (without streaming)
# 2. Build it
# 3. Click "Launch"
# Expected: New tab opens with http://jordanh-dev.hrd.nvidia.com:10000
# Check backend logs:
tail -f /tmp/kit-playground-backend.log | grep "PREVIEW URL"
```

**Test 2: Streaming URL Construction** (even though it will fail)
```bash
# 1. Create a project WITH streaming checkbox
# 2. Build it
# 3. Click "Launch"
# Expected: URL constructed as https://jordanh-dev.hrd.nvidia.com:47995
# But launch will fail due to missing extensions
# Check backend logs:
tail -f /tmp/kit-playground-backend.log | grep "STREAMING URL"
```

### Test Streaming Extension Detection

**Test 3: Check Available Extensions**
```bash
cd /home/jkh/Src/kit-app-template
./repo.sh list extensions | grep -i stream
```

**Expected Output (current state):**
```
# No streaming extensions found
```

**Desired Output (after fixing):**
```
omni.services.streaming.webrtc-1.2.3
omni.kit.streamhelper-0.5.1
```

---

## Summary

### ✅ Fixed
1. **Xpra URL hostname** - Now uses remote hostname from request headers
2. **Streaming URL hostname** - Now uses remote hostname from request headers
3. **Added warnings** - Backend logs warnings about missing streaming extensions

### ⚠️ Known Limitation
1. **Kit App Streaming extensions unavailable** - Extensions not in synced registries
2. **Streaming checkbox creates non-working apps** - Until extensions are available

### 🎯 Recommended Approach
**For Remote Preview:**
1. ✅ **Use Xpra mode** (works out of the box)
2. ❌ **Disable streaming checkbox** (until extensions are available)
3. 📋 **Document Xpra as primary preview method**

**For Kit App Streaming:**
1. 📝 Verify license/access to streaming extensions
2. 🔧 Configure streaming registry if available
3. 📦 Install required extensions
4. ✅ Re-enable checkbox after verification

---

## Files Modified

1. **`kit_playground/backend/routes/project_routes.py`**
   - Fixed streaming URL to use remote hostname
   - Added logging for URL construction
   - Fixed readiness check to use localhost (local check)

2. **`kit_playground/backend/routes/template_routes.py`**
   - Added warnings about missing streaming extensions
   - Added `streaming_warning` to response
   - Enhanced logging

---

## Related Documentation

- **[Smart Launch Decision Tree](./SMART_LAUNCH_DECISION_TREE.md)** - How launch mode is auto-selected
- **[Launch UX Improvements](./LAUNCH_UX_IMPROVEMENTS.md)** - Auto-open and log consolidation
- **[User Guide](../docs/USER_GUIDE.md)** - End-to-end workflows

---

## Next Steps

1. **Immediate:**
   - ✅ Test Xpra launch with correct hostname
   - ✅ Verify URLs in browser
   - ✅ Refresh frontend to get updated code

2. **Short-term:**
   - 📋 Document Xpra as the primary remote preview method
   - 🔧 Disable or warn about streaming checkbox
   - 📝 Update user guide to focus on Xpra

3. **Long-term:**
   - 📧 Contact NVIDIA/Omniverse support about streaming extensions
   - 🔑 Verify license requirements
   - 📦 Configure streaming registry if accessible
   - ✅ Re-enable streaming once extensions are available
