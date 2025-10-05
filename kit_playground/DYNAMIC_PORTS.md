# Dynamic Port Allocation

## Overview

The Kit Playground now automatically finds and allocates unused ports for both frontend and backend services. This allows the playground to run reliably on any host system, even when the default ports (8200, 3000) are already in use.

## How It Works

### Port Finding Utility

The `find_free_port.py` utility script scans for available ports starting from a specified port number:

```bash
# Find a single free port starting from 8000
python3 find_free_port.py

# Find 2 free ports starting from 8000
python3 find_free_port.py 2 8000
```

### Development Mode (`dev.sh`)

When you start the playground with `make playground` or `./kit_playground/dev.sh`:

1. The script automatically finds 2 available ports (starting from 8000)
2. Backend API is started on the first available port
3. Frontend UI is started on the second available port
4. A dynamic proxy configuration (`setupProxy.js`) is generated to route API calls from frontend to backend
5. The allocated ports are displayed in the startup message

Example output:
```
Finding available ports...
✓ Allocated ports: Backend=8000, Frontend=8001

Starting services:
  • Backend API:  http://0.0.0.0:8000
  • Frontend UI:  http://0.0.0.0:8001 (with hot-reload)
```

### Production Mode (`web_server.py`)

The backend server includes built-in port conflict resolution:

- If the specified port is in use, it automatically tries the next port
- Logs a warning message indicating which port is actually being used
- Can handle up to 10 port conflicts before failing

## Benefits

1. **Reliability**: Works on any system regardless of what ports are already in use
2. **Flexibility**: No need to manually configure ports or stop conflicting services
3. **User-Friendly**: Automatically reports the actual URLs to access the services
4. **CI/CD Friendly**: Multiple instances can run on the same host without conflicts

## Architecture Changes

### Files Modified

1. **`find_free_port.py`** (NEW)
   - Utility to find available network ports
   - Used by both dev and production modes

2. **`dev.sh`**
   - Added dynamic port allocation on startup
   - Generates `setupProxy.js` with correct backend port
   - Cleans up generated proxy config on shutdown
   - Reports allocated ports to user

3. **`ui/package.json`**
   - Removed static `"proxy"` configuration
   - Added `http-proxy-middleware` dependency
   - Proxy now configured dynamically via `setupProxy.js`

4. **`playground.sh`**
   - No changes needed (delegates to `dev.sh`)

### How Proxy Works

The React dev server uses a dynamically generated `setupProxy.js` file that:

1. Is created at startup by `dev.sh` with the actual backend port
2. Routes all `/api/*` requests to the backend server
3. Is automatically cleaned up when the playground stops

## Usage

### Start with Dynamic Ports
```bash
# Remote mode (listens on all interfaces)
make playground REMOTE=1

# Local mode (localhost only)
make playground
```

### Direct Script Usage
```bash
cd kit_playground
./dev.sh              # Local mode
REMOTE=1 ./dev.sh     # Remote mode
```

### Check What Ports Are Used
```bash
# The startup message will show:
#   • Backend API:  http://0.0.0.0:XXXX
#   • Frontend UI:  http://0.0.0.0:YYYY

# Or check the backend logs
tail -f /tmp/playground-backend.log
```

## Troubleshooting

### Port Conflicts

If you see errors about ports being in use:
1. The system will automatically find alternative ports
2. Check the startup message for the actual ports being used
3. Use those URLs to access the services

### Services Not Starting

If services fail to start:
1. Check backend logs: `tail -f /tmp/playground-backend.log`
2. Verify Python and Node.js are installed
3. Ensure no firewall is blocking the allocated ports
4. Try stopping with `make playground-stop` and restarting

### Proxy Not Working

If API calls fail with proxy errors:
1. Verify backend is running: `curl http://localhost:BACKEND_PORT/api/health`
2. Check that `setupProxy.js` was created in `ui/src/`
3. Ensure `http-proxy-middleware` is installed: `cd ui && npm install`
4. Restart the playground to regenerate proxy configuration

## Technical Details

### Port Selection Algorithm

The `find_free_port.py` script:
1. Tries to bind to a port using a TCP socket
2. If successful, the port is free and returned
3. If bind fails (OSError), tries the next port
4. Continues for up to 100 ports before giving up

### Cleanup

The `dev.sh` script includes a cleanup trap that:
1. Kills backend and frontend processes on exit
2. Removes the generated `setupProxy.js` file
3. Ensures clean shutdown on Ctrl+C or script termination

### Future Enhancements

Possible improvements:
- Store allocated ports in a temp file for easier inspection
- Add port range configuration via environment variables
- Support for multiple concurrent playground instances
- Automatic port allocation for Xpra sessions
