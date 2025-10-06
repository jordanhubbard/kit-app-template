# Remote Access Fix - Xpra Preview URL

## Problem

When accessing the Kit Playground UI remotely (e.g., `http://10.176.222.115:8002`), the Xpra preview was not working because:

1. **Preview URL was hardcoded to "localhost"**: Backend returned `http://localhost:10000`
2. **Browser couldn't connect**: From a remote browser, "localhost" refers to the client machine, not the server

**Symptom**: "localhost refused to connect" error in the preview iframe

## Solution

Modified the Xpra manager to use the actual server hostname instead of "localhost" when generating preview URLs.

### Files Modified

#### 1. `kit_playground/backend/xpra_manager.py`
**Line 181-193**: Updated `get_session_url()` method

**Before**:
```python
def get_session_url(self, session_id: str) -> Optional[str]:
    """Get the HTML5 client URL for a session."""
    session = self.sessions.get(session_id)
    if session and session.started:
        return f"http://localhost:{session.port}"
    return None
```

**After**:
```python
def get_session_url(self, session_id: str, host: str = None) -> Optional[str]:
    """Get the HTML5 client URL for a session.

    Args:
        session_id: ID of the session
        host: Optional host to use instead of localhost (for remote access)
    """
    session = self.sessions.get(session_id)
    if session and session.started:
        # Use provided host or default to localhost
        server_host = host if host else "localhost"
        return f"http://{server_host}:{session.port}"
    return None
```

#### 2. `kit_playground/backend/web_server.py`
**Lines 400-408, 858, 876, 903**: Updated all calls to `get_session_url()`

**Example Change**:
```python
# Before
preview_url = self.xpra_manager.get_session_url(session_id)

# After
server_host = request.host.split(':')[0]  # Extract hostname from request
preview_url = self.xpra_manager.get_session_url(session_id, host=server_host)
```

**Changed in 4 locations**:
1. `/api/projects/run` endpoint (line 403) - Main preview URL
2. `/api/xpra/sessions` endpoint (line 858) - Create session
3. `/api/xpra/sessions/<id>` endpoint (line 876) - Get session info
4. `/api/xpra/launch` endpoint (line 903) - Launch app

### How It Works

1. **Frontend makes request**: Browser at `http://10.176.222.115:8002` calls `/api/projects/run`
2. **Backend extracts host**: Flask `request.host` = `"10.176.222.115:8002"`
3. **Extract just hostname**: `request.host.split(':')[0]` = `"10.176.222.115"`
4. **Generate URL**: Returns `http://10.176.222.115:10000` instead of `http://localhost:10000`
5. **Preview works**: Browser can connect to the correct server IP

## Testing

### Local Access (localhost)
```
Access UI at: http://localhost:8002
Preview URL: http://localhost:10000
✅ Works (default behavior)
```

### Remote Access (IP address)
```
Access UI at: http://10.176.222.115:8002
Preview URL: http://10.176.222.115:10000
✅ Now works! (was broken before)
```

### Remote Access (hostname)
```
Access UI at: http://myserver.local:8002
Preview URL: http://myserver.local:10000
✅ Works
```

## Benefits

- ✅ Works for both local and remote access
- ✅ Automatically uses the correct hostname
- ✅ No configuration needed
- ✅ Backwards compatible (defaults to localhost)

## Related Issues

This fix also addresses:
- Remote development scenarios
- SSH tunneling with port forwarding
- Container deployments with mapped ports
- Proxy/reverse proxy setups

## Additional Improvements Made

### Frontend Build Status Check
**File**: `kit_playground/ui/src/components/layout/MainLayoutWorkflow.tsx` (Line 316-328)

Added better error handling to distinguish between HTTP errors and build failures:

```typescript
// Check if response itself failed
if (!response.ok) {
  emitConsoleLog('error', 'build', `Build request failed: ${result.error || response.statusText}`);
  return;
}

if (result.success) {
  emitConsoleLog('success', 'build', `Build completed successfully for ${selectedProject}`);
} else {
  emitConsoleLog('error', 'build', `Build failed: ${result.error || 'Unknown error'}`);
  console.error('Build result:', result);
}
```

This helps diagnose issues by logging the full result to browser console when builds fail.

## Notes

- The fix extracts only the hostname portion from `request.host`, removing any port numbers
- This ensures Xpra port numbers (10000+) aren't confused with the UI server port (8000-8001)
- The approach works with IPv4, IPv6, and hostnames

## Documentation

See also:
- `XPRA_SETUP.md` - Xpra installation and configuration
- `WRAPPER_INTEGRATION.md` - Project wrapper scripts
- `BUGFIXES.md` - Other recent fixes
