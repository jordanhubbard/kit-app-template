# Build Log Streaming Fix

## Issue
Build logs were not appearing in the BuildOutput panel, even though builds were starting successfully. The panel showed "Waiting for job to start..." indefinitely with no log output.

## Root Cause
**WebSocket Event Name Mismatch**

The frontend and backend were using different event names for log streaming:

### Backend (project_routes.py)
```python
socketio.emit('log', {
    'level': 'info',
    'source': 'build',
    'message': f'Building {project_name}...'
})
```
✅ Emits events as `'log'`

### WebSocket Service (websocket.ts)
```typescript
onLogMessage(handler: WebSocketEventHandler<...>): () => void {
  this.socket.on('log', handler);  // ✅ Correct
}

onJobLog(handler: WebSocketEventHandler<...>): () => void {
  this.socket.on('job_log', handler);  // Different event!
}
```

### BuildOutput Component (BEFORE)
```typescript
const { connected } = useWebSocket({
  onJobLog: (data) => {  // ❌ Listening for 'job_log'
    setLogs(prev => [...prev, data.message]);
  },
});
```
❌ Was listening for `'job_log'` events that backend never emits!

## The Fix

Changed `BuildOutput.tsx` to use `onLogMessage` instead of `onJobLog`:

```typescript
const { connected } = useWebSocket({
  onLogMessage: (data) => {  // ✅ Now listening for 'log'
    console.log('[BuildOutput] Received log:', data);
    const logLine = data.message || JSON.stringify(data);
    setLogs(prev => [...prev, logLine]);
  },
});
```

## Event Flow (After Fix)

```
Backend (project_routes.py)
  ↓ socketio.emit('log', {...})

WebSocket Server (Flask-SocketIO)
  ↓ broadcasts to all connected clients

Frontend WebSocket Service (websocket.ts)
  ↓ socket.on('log', handler)

BuildOutput Component
  ↓ onLogMessage={(data) => setLogs(...)}

UI Panel
  ✅ Displays real-time build logs
```

## Files Modified

### `/kit_playground/ui/src/components/panels/BuildOutput.tsx`
- Changed `onJobLog` → `onLogMessage`
- Added debug logging: `console.log('[BuildOutput] Received log:', data)`
- Logs now stream in real-time as build executes

## Testing

1. **Create a project** (e.g., "Kit Base Editor")
2. **Click "Build"** button in editor toolbar
3. ✅ Build Output panel opens
4. ✅ Shows command being executed:
   ```
   Building turbo_beacon_1...
   $ cd /home/jkh/Src/kit-app-template/source/apps/turbo_beacon_1
   $ ./repo.sh build --config release
   ```
5. ✅ Real-time logs stream as build progresses
6. ✅ Build completion status displayed

## Related Events

The backend emits several types of events for different purposes:

| Event Name | Backend Emits | Frontend Handler | Purpose |
|------------|---------------|------------------|---------|
| `log` | ✅ Yes | `onLogMessage()` | General command output (stdout/stderr) |
| `job_log` | ❌ No (unused) | `onJobLog()` | Job-specific logs (not used yet) |
| `job_status` | ✅ Yes | `onJobStatus()` | Job state changes (pending/running/completed) |
| `job_progress` | ✅ Yes | `onJobProgress()` | Progress updates (percentage) |
| `streaming_ready` | ✅ Yes | `onStreamingReady()` | Kit app streaming URLs |

## Why This Happened

The codebase has two different log event types:
- `'log'` - For general command output (what backend actually uses)
- `'job_log'` - For job-specific logs (not implemented yet)

The `BuildOutput` component was incorrectly using `onJobLog` (expecting `'job_log'` events) when it should have been using `onLogMessage` (for `'log'` events that backend actually emits).

## Future Improvements

1. **Standardize Event Names**: Consider using only `'log'` or renaming to be more explicit
2. **Job Status Integration**: Update job status in BuildOutput when receiving `job_status` events
3. **Progress Bar**: Show build progress when backend emits `job_progress` events
4. **Error Highlighting**: Color-code stderr output differently from stdout
5. **ANSI Color Support**: Parse and render ANSI escape codes from build output

## Related Documents

- `ai-docs/CAROUSEL_AND_BUILD_FIXES.md` - Carousel and build endpoint fixes
- `kit_playground/ui/src/services/websocket.ts` - WebSocket service implementation
- `kit_playground/backend/routes/project_routes.py` - Build endpoint and log emission
