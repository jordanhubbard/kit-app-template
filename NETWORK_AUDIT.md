# Network Address Audit Results

## Summary

Completed a comprehensive audit of all network addresses, hostnames, and ports in the application. Applied consistent rules for internal vs external communication.

---

## Rules Applied

### Rule 1: Internal Communication
**Use `localhost` for:**
- Health checks (socket connections)
- Service-to-service HTTP requests
- Internal port probing
- Self-hosted API calls

**Rationale**: Internal checks should always use `localhost` because:
- `0.0.0.0` is a bind address, not a connection address
- Services are on the same machine
- Faster and more reliable
- Works regardless of network configuration

### Rule 2: External Communication  
**Use actual IP address for:**
- URLs returned to clients (browsers)
- WebSocket connection URLs
- API endpoint URLs
- Streaming URLs
- Preview URLs

**Rationale**: Clients need real IP addresses to connect from remote machines:
- `0.0.0.0` is meaningless to external clients
- `localhost` only works if client is on same machine
- Actual IP (e.g., `10.176.222.115`) works from anywhere on the network

---

## New Utilities Created

### `kit_playground/backend/utils/network.py`

Centralized network utility functions:

1. **`get_external_ip()`**
   - Detects the actual external IP address
   - Methods: `ip route get`, `hostname -I`, socket connection
   - Fallback: `localhost`

2. **`get_hostname_for_client()`**
   - Returns IP for REMOTE=1, localhost for REMOTE=0
   - **Use for**: URLs sent to browsers/clients

3. **`get_hostname_for_internal()`**
   - Always returns `localhost`
   - **Use for**: Health checks, internal requests

4. **`get_bind_address()`**
   - Returns `0.0.0.0` for REMOTE=1, `localhost` for REMOTE=0
   - **Use for**: Server socket binding
   - **Never send this to clients!**

5. **`format_url()`**
   - Helper to construct URLs with proper hostname

---

## Files Modified

### ✅ `kit_playground/dev.sh`
**Fixed**:
- Line 163: Health check now uses `http://localhost:3000` instead of `http://${FRONTEND_HOST}:3000`
- Already using `API_HOST` (actual IP) for client-facing VITE env vars

**Status**: ✅ Correct

---

### ✅ `kit_playground/backend/routes/project_routes.py`
**Fixed**:
- Line 52-56: Socket health check now uses `'localhost'` instead of `bind_host`
- Line 373-378: Streaming URL now uses `get_hostname_for_client()` instead of `"0.0.0.0"`

**Status**: ✅ Correct

---

### ✅ `kit_playground/backend/routes/xpra_routes.py`
**Fixed**:
- Line 114-122: Socket health check now uses `'localhost'`
- Line 127-138: Internal HTTP request now uses `http://localhost:{port}`
- Line 141-152: URL returned to client now uses `get_hostname_for_client()`

**Status**: ✅ Correct

---

### ✅ `kit_playground/backend/source/port_registry.py`
**Fixed**:
- Simplified `_detect_default_host()` to use `get_hostname_for_client()`
- Line 258-268: Health checks now use `get_hostname_for_internal()` (always localhost)
- No longer returns `"0.0.0.0"` to clients

**Status**: ✅ Correct

---

## Files Already Correct

### ✅ `kit_playground/ui/src/services/api.ts`
- Uses `import.meta.env.VITE_API_BASE_URL` (set by dev.sh with actual IP)
- Fallback: `http://localhost:5000/api`

**Status**: ✅ Correct

---

### ✅ `kit_playground/ui/src/services/websocket.ts`
- Uses `import.meta.env.VITE_WS_BASE_URL` (set by dev.sh with actual IP)
- Fallback: `http://localhost:5000`

**Status**: ✅ Correct

---

### ✅ `kit_playground/backend/web_server.py`
- Takes `--host` parameter (passed from dev.sh)
- Binds to `0.0.0.0` in REMOTE mode, `localhost` in local mode

**Status**: ✅ Correct

---

### ✅ `kit_playground/ui/vite.config.ts`
- Hardcoded `host: '0.0.0.0'` is fine (overridden by CLI `--host` argument from dev.sh)
- CLI arguments take precedence over config file

**Status**: ✅ Correct

---

## Address Matrix

| Use Case | Address Type | Value (LOCAL) | Value (REMOTE) |
|----------|-------------|---------------|----------------|
| Backend bind | Bind address | `localhost` | `0.0.0.0` |
| Frontend bind | Bind address | `localhost` | `0.0.0.0` |
| Health checks | Connection | `localhost` | `localhost` |
| Internal HTTP | Connection | `localhost` | `localhost` |
| Socket probes | Connection | `localhost` | `localhost` |
| Client URLs | Connection | `localhost` | `10.176.222.115` |
| API base URL | Connection | `localhost` | `10.176.222.115` |
| WebSocket URL | Connection | `localhost` | `10.176.222.115` |
| Streaming URL | Connection | `localhost` | `10.176.222.115` |
| Preview URL | Connection | `localhost` | `10.176.222.115` |

---

## Testing Checklist

### Local Mode (`REMOTE=0`)
- [ ] Services start successfully
- [ ] Health checks pass
- [ ] Frontend can connect to backend at `http://localhost:5000`
- [ ] WebSocket connects at `localhost:5000`
- [ ] Preview URLs work at `http://localhost:10000`

### Remote Mode (`REMOTE=1`)
- [ ] Services bind to `0.0.0.0` (all interfaces)
- [ ] Health checks still use `localhost`
- [ ] Frontend receives correct IP in env vars
- [ ] Client URLs contain actual IP (not `0.0.0.0`)
- [ ] Remote browser can connect to all URLs
- [ ] Streaming URLs use actual IP
- [ ] Preview URLs use actual IP

---

## Key Principles

1. **Bind addresses (`0.0.0.0`) are for servers, not clients**
   - Never send `0.0.0.0` in an API response
   - Never use `0.0.0.0` for connection attempts

2. **`localhost` is for internal communication only**
   - Health checks on the same machine
   - Service-to-service calls
   - Not for URLs sent to external clients

3. **Actual IP addresses are for external clients**
   - Browsers connecting from remote machines
   - WebSocket connections from UI
   - Any URL displayed to the user

4. **Centralized utilities prevent inconsistency**
   - Use `network.py` utilities everywhere
   - Don't duplicate IP detection logic
   - Single source of truth for hostname resolution

---

## Future Improvements

1. **Environment Variable**: Consider adding `PUBLIC_IP` env var for explicit control
2. **Docker Support**: Add detection for Docker bridge networks
3. **IPv6 Support**: Add IPv6 address detection
4. **Multi-Interface**: Handle machines with multiple network interfaces
5. **Cloud Metadata**: Detect cloud provider metadata services (AWS, GCP, Azure)

---

## Commit Summary

- Created `kit_playground/backend/utils/network.py`
- Fixed `dev.sh` health check timeout (localhost)
- Fixed `project_routes.py` socket checks and streaming URLs
- Fixed `xpra_routes.py` health checks and client URLs
- Fixed `port_registry.py` hostname detection and health checks
- All services now distinguish internal vs external communication

