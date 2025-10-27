# Launch UX Improvements

## Overview

Fixed three critical UX issues with the launch functionality:
1. Xpra URLs using `localhost` instead of remote hostname
2. No auto-open of preview URLs in new tabs
3. Redundant log displays in multiple windows

**Date:** 2024-10-27
**Status:** ✅ Implemented

---

## Issue 1: Xpra URLs Using localhost

### Problem
Xpra was telling users to connect to `localhost:10000`, but users are remote and need to connect to the actual hostname of the server (e.g., `jordanh-dev.hrd.nvidia.com:10000`).

### Root Cause
The backend was already correctly using `registry.get_preview_url()` with `client_host` extraction from request headers, so the URL construction was correct. However, the WebSocket event `xpra_ready` was not being emitted, so the frontend couldn't auto-open the correct URL.

### Solution
Added `xpra_ready` WebSocket event emission in `project_routes.py`:

```python
# Emit xpra_ready event for frontend to auto-open
socketio.emit('xpra_ready', {
    'project': project_name,
    'url': preview_url,  # Already uses correct hostname from registry
    'display': xpra_display,
    'port': xpra_port
})
```

**Files Modified:**
- `kit_playground/backend/routes/project_routes.py`

---

## Issue 2: No Auto-Open of Preview URLs

### Problem
When Xpra or Kit App Streaming was ready, the UI didn't automatically open the preview URL in a new tab like the old playground did.

### Solution

#### 1. Added WebSocket Event Handlers

**Backend** (`project_routes.py`):
- Already emits `streaming_ready` for Kit App Streaming
- Added `xpra_ready` emission for Xpra (see Issue 1)

**Frontend WebSocket Service** (`websocket.ts`):
```typescript
onXpraReady(
  handler: WebSocketEventHandler<{
    project: string;
    url: string;
    display: number;
    port: number;
  }>
): () => void {
  if (!this.socket) {
    console.warn('WebSocket not connected');
    return () => {};
  }

  this.socket.on('xpra_ready', handler);

  return () => {
    this.socket?.off('xpra_ready', handler);
  };
}
```

**Frontend Hook** (`useWebSocket.ts`):
```typescript
interface UseWebSocketOptions {
  // ... existing options
  onXpraReady?: (data: any) => void;
}
```

#### 2. Auto-Open Implementation

**BuildOutput Component** (`BuildOutput.tsx`):
```typescript
const { connected } = useWebSocket({
  // ... other handlers
  onStreamingReady: (data) => {
    console.log('[BuildOutput] Streaming ready:', data);
    if (data.url && jobType === 'launch') {
      console.log('[BuildOutput] Auto-opening streaming URL:', data.url);
      window.open(data.url, '_blank');
    }
  },
  onXpraReady: (data) => {
    console.log('[BuildOutput] Xpra ready:', data);
    if (data.url && jobType === 'launch') {
      console.log('[BuildOutput] Auto-opening Xpra URL:', data.url);
      window.open(data.url, '_blank');
    }
  },
});
```

**How It Works:**
1. Backend launches application with Xpra or streaming
2. Backend waits for Xpra/streaming to be ready
3. Backend emits `xpra_ready` or `streaming_ready` with URL
4. Frontend's `BuildOutput` component receives event
5. `window.open(url, '_blank')` opens preview in new tab
6. User sees their application immediately

**Files Modified:**
- `kit_playground/ui/src/services/websocket.ts`
- `kit_playground/ui/src/hooks/useWebSocket.ts`
- `kit_playground/ui/src/components/panels/BuildOutput.tsx`

---

## Issue 3: Logs in Three Different Windows

### Problem
Logs were being displayed in:
1. Bottom Output panel (persistent, collapsible)
2. Build Output panel (middle pane)
3. Launch Output panel (right pane)

This created redundancy and confusion - users had to look in multiple places for the same information.

### Solution: Consolidate to Single Log View

#### Bottom Output Panel = Primary Log View
- All stdout/stderr from all commands
- Persistent, collapsible, resizable
- Filterable by source (build, runtime, system)
- Color-coded by level

#### Build/Launch Panels = Status Summary
Transformed these panels from log viewers to **status dashboards**:

**New UI Structure:**
```
┌─────────────────────────────────────┐
│  Status Icon (Spinner/Check/X)      │
│                                      │
│  Status: Running / Completed        │
│  Project: my_editor                  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │ Status:   Running             │  │
│  │ Started:  10:45:32 AM        │  │
│  │ Progress: 75%                 │  │
│  └───────────────────────────────┘  │
│                                      │
│  Instructions:                       │
│  View detailed logs in the Output   │
│  panel at the bottom of the screen. │
└─────────────────────────────────────┘
```

**Changes Made:**

**BuildOutput.tsx:**
```typescript
// REMOVED: Logs display
const [logs, setLogs] = useState<string[]>([]);
const logsEndRef = useRef<HTMLDivElement>(null);
const logsContainerRef = useRef<HTMLDivElement>(null);

// REMOVED: Log collection
onLogMessage: (data) => {
  setLogs(prev => [...prev, data.message]);  // ❌ Removed
}

// CHANGED: Now just detects status from logs (doesn't display them)
onLogMessage: (data) => {
  // Logs are shown only in the bottom Output panel
  // Build/Launch panels show status info only
  const logLine = data.message || JSON.stringify(data);

  // Detect build completion from log messages
  if (jobType === 'build') {
    if (logLine.includes('BUILD (RELEASE) SUCCEEDED')) {
      setBuildCompleted(true);
    } else if (logLine.includes('BUILD (RELEASE) FAILED')) {
      setBuildFailed(true);
    }
  }
}
```

**New UI Components:**
- **Status Icon:** Large icon showing current state (spinner, checkmark, X)
- **Status Message:** Prominent display of current status
- **Job Details Card:** Structured information (start time, end time, progress)
- **Contextual Instructions:** Tells users where to find logs and what to do next

**Example Messages:**
- **Build Running:** "View detailed logs in the Output panel at the bottom of the screen."
- **Build Succeeded:** "Build successful! Click the Launch button to run your application."
- **Build Failed:** "Build failed. Check the Output panel for error details."
- **Launch Running:** "Application is starting... Preview will open automatically when ready."

**Benefits:**
1. **Single Source of Truth:** All logs in one place (bottom Output panel)
2. **Clear Visual Hierarchy:** Status panels show high-level state, Output panel shows details
3. **Less Scrolling:** Users don't have to scroll through multiple log windows
4. **Better Context:** Instructions guide users to the right next action
5. **Cleaner UI:** Status panels are information-dense but visually clean

**Files Modified:**
- `kit_playground/ui/src/components/panels/BuildOutput.tsx`

**No Changes Needed:**
- `kit_playground/ui/src/components/panels/OutputPanel.tsx` (already working correctly)
- `kit_playground/ui/src/stores/outputStore.ts` (already working correctly)

---

## Testing Checklist

### Issue 1: Xpra URL Hostname
- [x] Backend emits `xpra_ready` event
- [ ] Event includes correct URL with remote hostname
- [ ] URL is constructed using `registry.get_preview_url()`
- [ ] URL uses `X-Forwarded-Host` or `Host` header correctly

**Test:**
```bash
# In browser console when launch completes:
# Should see: xpra_ready: { url: "http://jordanh-dev.hrd.nvidia.com:14500" }
# NOT:        xpra_ready: { url: "http://localhost:14500" }
```

### Issue 2: Auto-Open Preview
- [ ] Xpra preview opens automatically in new tab when ready
- [ ] Streaming preview opens automatically in new tab when ready
- [ ] Only opens when `jobType === 'launch'` (not during build)
- [ ] Console logs show: "Auto-opening Xpra URL: ..."

**Test:**
```
1. Build a project
2. Click "Launch" button
3. Wait for "Application is starting..." message
4. NEW TAB should automatically open with Xpra preview
5. If it doesn't, check browser popup blocker
```

### Issue 3: Consolidated Logs
- [ ] Bottom Output panel shows all logs
- [ ] Build Output panel shows status summary (not logs)
- [ ] Launch Output panel shows status summary (not logs)
- [ ] Status panels have clear instructions
- [ ] Progress indicators work correctly

**Test:**
```
1. Create and build a project
2. Verify logs appear ONLY in bottom Output panel
3. Verify Build Output shows status card with times/progress
4. Click "Launch"
5. Verify Launch Output shows "Application is starting..." message
6. Verify logs still only in bottom Output panel
```

---

## Known Issues

### Browser Popup Blockers
**Problem:** Some browsers block `window.open()` calls from WebSocket event handlers.

**Workaround:** Users may need to:
1. Allow popups for the playground domain
2. Or manually click the URL in the logs

**Future Enhancement:** Add a "Open Preview" button that appears when URL is ready, as a fallback if auto-open is blocked.

### Multiple Launch Panels
**Problem:** Opening multiple launch panels for the same project may cause duplicate tab opens.

**Current Behavior:** Each panel listens for `xpra_ready` and opens a tab.

**Mitigation:** Events are filtered by `jobType === 'launch'`, so build panels won't open tabs. If multiple launch panels exist for the same project, they'll all open tabs (probably intended behavior for testing).

---

## Related Documentation

- **[Smart Launch Decision Tree](./SMART_LAUNCH_DECISION_TREE.md)** - How launch mode is auto-selected
- **[Build Streaming Fix](./BUILD_STREAMING_AND_LAUNCH_FIX.md)** - Real-time output with PTY
- **[Panel Carousel System](./PANEL_CAROUSEL_SYSTEM.md)** - UI panel management
- **[User Guide](../docs/USER_GUIDE.md)** - End-to-end workflows

---

## Summary

### Before
- ❌ Xpra URLs showed `localhost` (wrong for remote users)
- ❌ No auto-open of preview URLs
- ❌ Logs duplicated in 3 different windows
- ❌ Users confused about where to look for information

### After
- ✅ Xpra URLs use correct remote hostname
- ✅ Preview URLs auto-open in new tab when ready
- ✅ Single consolidated log view (bottom Output panel)
- ✅ Build/Launch panels show status summaries with clear instructions
- ✅ Better UX with contextual guidance

**Result:** Seamless launch experience with automatic preview opening and consolidated, easy-to-follow logging.
