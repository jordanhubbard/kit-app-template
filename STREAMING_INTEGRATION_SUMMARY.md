# Streaming Integration Feature Branch

## Overview
This branch (`feature/streaming-integration`) adds comprehensive Kit App Streaming (WebRTC) support to the Kit App Template, enabling browser-based streaming of Kit applications.

## Base
- **Branched from**: Kit App Template 108.1 (commit `aaf8172b`)
- **Target**: `main` branch for upstream integration

## Feature Commits (6 total)

### 1. `bffbf0a` - feat: add Makefile build system for cross-platform workflows
**Why**: Provides `make` targets for building the UI, streaming client, and managing dependencies.

**Key additions**:
- `Makefile` with targets: `playground-build`, `streaming-client-build`, `streaming-client-dev`
- Cross-platform build automation for the entire stack
- Streaming client build integrated into main UI build process

**Files**:
- `Makefile` (new, 776 lines)

---

### 2. `c3aa193` - feat: add Kit App Streaming utilities for WebRTC detection and configuration
**Why**: Core library for detecting streaming capabilities and configuring applications.

**Key additions**:
- `tools/repoman/streaming_utils.py` - Utilities for:
  - Detecting if an application supports streaming
  - Parsing Kit extension configurations
  - Identifying streaming-enabled layers
- Used by backend to determine launch mode

**Files**:
- `tools/repoman/streaming_utils.py` (new, 285 lines)

---

### 3. `df47d9e` - feat: add NVIDIA web-viewer-sample as submodule and create loader page
**Why**: Integrates NVIDIA's official WebRTC client for browser-based streaming.

**Key additions**:
- Git submodule at `kit_playground/ui/public/ov-web-client` pointing to https://github.com/NVIDIA-Omniverse/web-viewer-sample
- `ov-web-client-loader.html` - Dynamic configuration page that:
  - Accepts `?server=host:port` URL parameter
  - Constructs WebRTC client config on-the-fly
  - Redirects to built client with embedded config

**Files**:
- `.gitmodules` (new)
- `kit_playground/ui/public/ov-web-client` (submodule)
- `kit_playground/ui/public/ov-web-client-loader.html` (new)

---

### 4. `47a6dc7` - feat: add streaming launch policy and WebRTC integration to backend routes
**Why**: Implements the 3-tier launch policy and WebRTC client integration.

**Launch Policy** (in priority order):
1. **Kit App Streaming (WebRTC)**: If template has streaming layer enabled → use WebRTC client
2. **Direct Display**: If `DISPLAY` env var is set → use local X11
3. **Xpra (Remote Desktop)**: Fallback for headless environments → use Xpra streaming

**Key additions**:
- `kit_playground/backend/routes/project_routes.py`:
  - `launch_project()` - Implements 3-tier launch policy
  - WebRTC client URL construction pointing to loader page
  - Working directory set to `~/OmniverseAssets/USD`
  - Client build check with warning if not built
- `kit_playground/backend/routes/template_routes.py`:
  - Layer dependency workarounds for streaming extensions
  - Auto-enables streaming layers for compatible templates

**Files**:
- `kit_playground/backend/routes/project_routes.py` (new, ~1600 lines)
- `kit_playground/backend/routes/template_routes.py` (new, ~600 lines)

---

### 5. `35b971d` - feat: update UI components for Xpra auto-open and streaming client integration
**Why**: Frontend integration for external preview windows and streaming client.

**Key changes**:
- **BuildOutput.tsx**: Auto-opens Xpra/streaming URLs in new browser windows (avoids iframe security issues with self-signed certs)
- **Preview.tsx**: Provides guidance for self-signed SSL certificates, button to open externally
- **panelStore.ts**: Adds `'usd-media'` panel type, enables closing of media library

**Behavior**:
- Xpra: Auto-opens in new window on `xpra_ready` socket event
- Streaming: Auto-opens WebRTC client in new window on `streaming_ready` socket event
- No more embedded iframes (fixes SSL cert warnings)

**Files**:
- `kit_playground/ui/src/components/panels/BuildOutput.tsx` (new, ~500 lines)
- `kit_playground/ui/src/components/panels/Preview.tsx` (new, ~400 lines)
- `kit_playground/ui/src/stores/panelStore.ts` (new, ~400 lines)

---

### 6. `4feb04e` - docs: update README with streaming setup instructions and quick start
**Why**: Complete documentation for developers using streaming features.

**Key sections added**:
- **Quick Start**: Updated to include `--recurse-submodules` and `make streaming-client-build`
- **Kit App Streaming (WebRTC)** section:
  - Architecture overview (Kit streaming server + web client)
  - Setup instructions (building client, launching apps)
  - Troubleshooting (SSL certs, firewall, ports)
  - Technical details (signaling, media streams)
- Updated all command examples to reflect Makefile usage

**Files**:
- `README.md` (modified, +1046 lines, -60 lines)

---

## Testing Checklist

### Prerequisites
```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd kit-app-template
git checkout feature/streaming-integration

# Install dependencies
make install-deps

# Build streaming client
make streaming-client-build

# Build UI
make playground-build
```

### Test Scenarios

#### 1. **WebRTC Streaming** (Primary feature)
```bash
# Start playground
make playground

# Create an application with streaming enabled:
# - In UI, select a template like "Basic Viewport Template"
# - Enable "Kit App Streaming" layer
# - Click "Create Application"
# - Click "Build"
# - Click "Launch"
# - Verify: Browser opens to WebRTC client
# - Verify: Application renders and is interactive
```

**Expected**:
- Backend emits `streaming_ready` socket event with URL: `/ov-web-client-loader.html?server=host:47995`
- Browser auto-opens to WebRTC client
- Client connects to Kit streaming server on port 47995
- Application renders in browser with full interactivity

#### 2. **Xpra Fallback** (For non-streaming apps without DISPLAY)
```bash
# Unset DISPLAY
unset DISPLAY

# Create a non-streaming application
# - Create app WITHOUT enabling streaming layer
# - Launch

# Expected: Xpra starts and auto-opens in browser
```

#### 3. **Direct Display** (For local development)
```bash
# Set DISPLAY
export DISPLAY=:0

# Create any application
# - Launch

# Expected: Application launches on local X11 display
```

#### 4. **Client Not Built Warning**
```bash
# Remove built client
rm -rf kit_playground/ui/public/ov-web-client/dist

# Try to launch a streaming app

# Expected: Backend logs warning and emits socket event:
# "⚠️  WebRTC client not built. Run: make streaming-client-build"
```

---

## Integration Strategy for Upstream

### Option A: Direct Merge (Recommended)
Since all 6 commits are feature-additive and backwards compatible:

```bash
# From upstream repo:
git remote add jhanna-fork git@github.com:jordanhubbard/kit-app-template.git
git fetch jhanna-fork
git checkout -b feat/webrtc-streaming jhanna-fork/feature/streaming-integration
git rebase main  # Rebase onto current main if desired
# Review, test, then merge to main
```

**Pros**:
- Clean commit history
- Each commit is self-contained and documented
- Bisectable if issues arise
- All changes are backwards compatible (no breaking changes)

**Cons**:
- None (feature is entirely additive)

### Option B: Squash Merge
If upstream prefers a single commit:

```bash
git merge --squash feat/webrtc-streaming
git commit -m "feat: add Kit App Streaming (WebRTC) support

Adds comprehensive WebRTC streaming functionality...
(use full summary from this doc)
"
```

---

## Dependencies

### New Runtime Dependencies
- **NVIDIA web-viewer-sample** (git submodule): Official WebRTC client
- **Node.js/npm**: For building WebRTC client (already required for Kit Playground UI)

### No Changes to Kit SDK Dependencies
- Streaming features use existing Kit SDK extensions
- No new Kit packages required
- Compatible with Kit 108.0+

---

## Backwards Compatibility

✅ **Fully Backwards Compatible**
- All changes are additive (no removals or breaking changes)
- Non-streaming applications work exactly as before
- Makefile is optional (repo.sh still works)
- Streaming client submodule is optional (only needed if using WebRTC)

**Migration Path**: None needed
- Existing projects/workflows unaffected
- Streaming is opt-in at application creation time

---

## Known Limitations

1. **Self-Signed SSL Certificates**: Kit streaming server uses self-signed certs in development
   - **Workaround**: Accept cert warning in browser or configure proper SSL
   - **Documented in**: README "Troubleshooting" section

2. **Firewall**: WebRTC requires ports 47995-47999 open
   - **Documented in**: README "Troubleshooting" section

3. **Browser Compatibility**: WebRTC client requires modern browser (Chrome, Firefox, Edge)
   - **Documented in**: README "Architecture" section

---

## Future Enhancements (Out of Scope)

- [ ] Pre-build streaming client in CI/CD
- [ ] Add streaming client health check API endpoint
- [ ] Persistent WebRTC client configuration
- [ ] Support for custom SSL certificates in Kit streaming server
- [ ] Metrics/telemetry for streaming sessions

---

## Contacts

**Author**: Jordan Hanna (jhanna)  
**Branch**: `feature/streaming-integration`  
**Related Docs**: `README.md`, `MERGE_TO_UPSTREAM_ASSESSMENT.md`

