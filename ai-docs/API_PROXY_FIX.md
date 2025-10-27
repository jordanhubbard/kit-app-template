# API Proxy Configuration Fix

## Issue
The frontend was making API calls to the wrong server, causing **404 Not Found** errors:

```
POST http://jordanh-dev.hrd.nvidia.com:3000/api/projects/build
404 (Not Found)
```

**Frontend (Vite)**: Port 3000
**Backend (Flask)**: Port 5000

The frontend was trying to call `/api/*` endpoints on its own server (port 3000) instead of proxying to the backend (port 5000).

## Root Cause

### Missing Vite Proxy Configuration
The `vite.config.ts` had **no proxy configuration**, so all `/api/*` and `/socket.io/*` requests were being sent to the Vite dev server (port 3000) instead of the backend (port 5000).

### Hardcoded Full URLs
Both the API service and WebSocket service were configured with full URLs:

```typescript
// api.ts
const API_BASE_URL = 'http://localhost:5000/api';  // ❌ Bypasses proxy

// websocket.ts
const WS_BASE_URL = 'http://localhost:5000';  // ❌ Bypasses proxy
```

This prevented the Vite proxy from intercepting and forwarding requests.

## The Fix

### 1. Added Vite Proxy Configuration

**File**: `kit_playground/ui/vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    // ... other config ...

    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true,  // Enable WebSocket proxying
      },
    },
  },
  // ...
})
```

### 2. Changed API Service to Use Relative Paths

**File**: `kit_playground/ui/src/services/api.ts`

```typescript
// BEFORE
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// AFTER
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
```

Now API calls use relative paths (e.g., `/api/projects/build`), which Vite proxies to `http://localhost:5000/api/projects/build`.

### 3. Changed WebSocket Service to Use Current Origin

**File**: `kit_playground/ui/src/services/websocket.ts`

```typescript
// BEFORE
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'http://localhost:5000';
this.socket = io(WS_BASE_URL, { ... });

// AFTER
const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || '';
this.socket = io(WS_BASE_URL, {
  path: '/socket.io',  // Explicitly set for proxy
  transports: ['websocket', 'polling'],
  // ...
});
```

Socket.io-client connects to the current origin (port 3000), and Vite proxies `/socket.io/*` to the backend (port 5000).

## Request Flow (After Fix)

### API Requests
```
Browser
  ↓ fetch('/api/projects/build')

Vite Dev Server (port 3000)
  ↓ proxy → http://localhost:5000/api/projects/build

Flask Backend (port 5000)
  ↓ processes request

Response
  ↓ proxy back through Vite

Browser receives response
```

### WebSocket Connection
```
Browser
  ↓ io('', {path: '/socket.io'})

Vite Dev Server (port 3000)
  ↓ proxy → ws://localhost:5000/socket.io

Flask-SocketIO Backend (port 5000)
  ↓ WebSocket handshake

Real-time bidirectional connection established
```

## Testing

### Test API Proxy
```bash
# Call API through frontend port (should proxy to backend)
curl http://localhost:3000/api/health

# Should return backend health check:
{
  "service": "kit-playground",
  "status": "healthy",
  "timestamp": "2025-10-27T02:15:44.061517"
}
```

### Test in Browser
1. **Hard refresh** browser (Ctrl+Shift+R)
2. Open DevTools → Network tab
3. Create a project
4. Click **"Build"** button
5. ✅ Check Network tab shows:
   ```
   POST /api/projects/build
   Status: 200 OK
   Request URL: http://jordanh-dev.hrd.nvidia.com:3000/api/projects/build
   ```
   (Vite transparently proxies to port 5000)

### Test WebSocket
1. Open DevTools → Network tab → WS filter
2. Look for WebSocket connection
3. ✅ Should show:
   ```
   ws://jordanh-dev.hrd.nvidia.com:3000/socket.io/?...
   Status: 101 Switching Protocols
   ```
   (Vite proxies to backend WebSocket)

## API Endpoint Audit

All backend endpoints are now accessible through the frontend at `http://localhost:3000/api/*`:

### Template Routes
| Endpoint | Method | Frontend Usage | Status |
|----------|--------|---------------|--------|
| `/api/templates` | GET | `apiService.getTemplates()` | ✅ Works |
| `/api/templates/<id>` | GET | `apiService.getTemplateDetails(id)` | ✅ Works |
| `/api/templates/create` | POST | `apiService.createFromTemplate()` | ✅ Works |
| `/api/v2/templates` | GET | `apiService.getTemplatesV2()` | ✅ Works |
| `/api/v2/templates/<id>/icon` | GET | Template icons | ✅ Works |
| `/api/v2/templates/<id>/docs` | GET | Template docs | ✅ Works |

### Project Routes
| Endpoint | Method | Frontend Usage | Status |
|----------|--------|---------------|--------|
| `/api/projects/build` | POST | `useJob.ts → fetch()` | ✅ Works (now!) |
| `/api/projects/run` | POST | Build panel | ✅ Works |
| `/api/projects/discover` | GET | Project discovery | ✅ Works |
| `/api/projects/stop` | POST | Stop running app | ✅ Works |
| `/api/projects/delete` | POST | Delete project | ✅ Works |

### Filesystem Routes
| Endpoint | Method | Frontend Usage | Status |
|----------|--------|---------------|--------|
| `/api/filesystem/read` | GET | `apiService.readFile()` | ✅ Works |
| `/api/filesystem/write` | POST | `apiService.saveFile()` | ✅ Works (newly added) |
| `/api/filesystem/list` | GET | `apiService.listDirectory()` | ✅ Works |
| `/api/filesystem/mkdir` | POST | Directory creation | ✅ Works |

### WebSocket Events
| Event | Direction | Frontend Handler | Status |
|-------|-----------|------------------|--------|
| `connect` | Backend → Frontend | Connection handler | ✅ Works |
| `disconnect` | Backend → Frontend | Disconnect handler | ✅ Works |
| `log` | Backend → Frontend | `onLogMessage()` | ✅ Works (fixed!) |
| `job_status` | Backend → Frontend | `onJobStatus()` | ✅ Works |
| `job_progress` | Backend → Frontend | `onJobProgress()` | ✅ Works |
| `streaming_ready` | Backend → Frontend | `onStreamingReady()` | ✅ Works |

## Production Considerations

In production, you may want to:

1. **Set environment variables** for absolute URLs:
   ```bash
   export VITE_API_BASE_URL="https://api.example.com/api"
   export VITE_WS_BASE_URL="https://api.example.com"
   ```

2. **Use a reverse proxy** (nginx/Apache) instead of Vite proxy:
   ```nginx
   location /api {
       proxy_pass http://backend:5000;
   }

   location /socket.io {
       proxy_pass http://backend:5000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

3. **Enable CORS** on the backend if serving from different domains

## Related Files Modified

- `kit_playground/ui/vite.config.ts` - Added proxy configuration
- `kit_playground/ui/src/services/api.ts` - Changed to relative paths
- `kit_playground/ui/src/services/websocket.ts` - Changed to current origin
- `kit_playground/ui/src/hooks/useJob.ts` - Already using relative paths (no change needed)

## Related Documents

- `ai-docs/BUILD_LOG_STREAMING_FIX.md` - WebSocket log streaming
- `ai-docs/FILE_SAVE_FIX.md` - File save endpoint
- `ai-docs/CAROUSEL_AND_BUILD_FIXES.md` - Build button fixes
