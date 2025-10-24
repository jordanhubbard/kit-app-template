# Kit App Streaming Implementation Design

## Overview

Support for NVIDIA Kit App Streaming, which enables remote rendering and streaming of Kit applications to web browsers without requiring local GPU resources.

## Current State

### What Exists
- ✅ Xpra support (Mode 2b) - remote X11 display forwarding
- ✅ Direct launch (Mode 2a) - local DISPLAY inheritance
- ✅ Streaming template configs in `templates/apps/streaming_configs/`:
  - `default_stream.kit` - Omniverse Kit App Streaming
  - `nvcf_stream.kit` - NVCF Streaming
  - `gdn_stream.kit` - GDN Streaming
- ✅ Template registry entries for streaming configs

### What's Missing
- ❌ Detection of streaming extensions in .kit files
- ❌ Automatic `--no-window` flag for streaming apps
- ❌ Stdout parsing to extract streaming URL
- ❌ API support for streaming-enabled project creation
- ❌ UI checkbox for "Enable Kit App Streaming"
- ❌ UI checkbox for "Web Preview"
- ❌ URL display/notification in UI

## Three Display Modalities

### Mode 1: Kit App Streaming (NEW - Not Yet Implemented)

**When:** `.kit` file includes `omni.kit.livestream.app` dependency

**Behavior:**
- **Always** pass `--no-window` to the application
- Application prints streaming URL to stdout (format: `Streaming URL: http://...`)
- Backend captures and parses stdout for the URL
- **If "Web Preview" checked:** Wait for URL, open browser tab automatically
- **If "Web Preview" NOT checked:** Display URL in toast/popup for manual connection

**Detection Logic:**
```python
def is_streaming_app(kit_file_path: Path) -> bool:
    """Check if a .kit file uses Kit App Streaming."""
    content = read_toml(kit_file_path)

    # Check dependencies section
    dependencies = content.get('dependencies', {})
    if 'omni.kit.livestream.app' in dependencies:
        return True
    if 'omni.kit.livestream.core' in dependencies:
        return True

    # Check if this is a streaming config (references streaming extension)
    template_name = content.get('package', {}).get('template_name', '')
    if 'streaming' in template_name.lower():
        return True

    return False
```

**Launch Logic:**
```python
def launch_streaming_app(app_path, capture_url=True):
    """Launch streaming app and optionally capture URL."""
    cmd = [str(app_path), '--no-window']

    if capture_url:
        # Capture stdout to get streaming URL
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        streaming_url = None
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Echo to console

            # Parse for streaming URL
            if 'streaming url:' in line.lower() or 'connect to:' in line.lower():
                # Extract URL from line
                streaming_url = extract_url_from_line(line)
                if streaming_url:
                    break

        return process, streaming_url
    else:
        # Just launch without capturing
        subprocess.run(cmd)
```

### Mode 2a: Direct Launch (Existing)

**When:** No streaming extension, "Web Preview" NOT checked

**Behavior:**
- Launch directly with `repo.sh launch`
- Inherits `DISPLAY` from parent process environment
- App connects to user's local X11 display
- No URL needed (runs locally)

**Already implemented** - no changes needed.

### Mode 2b: Xpra Display Server (Existing)

**When:** No streaming extension, "Web Preview" IS checked

**Behavior:**
- Start Xpra on `:100` (port `10000`)
- Set `DISPLAY=:100` for the application
- Launch application with Xpra display
- Wait for both Xpra and app to be ready
- Open browser to `http://localhost:10000` (or `0.0.0.0:10000` if REMOTE=1)

**Already implemented in `launch.py`** - works correctly.

## Implementation Plan

### Phase 1: Backend/CLI Foundation

#### 1.1: Streaming Detection Module (`tools/repoman/streaming_utils.py`)

```python
#!/usr/bin/env python3
"""Utilities for Kit App Streaming detection and management."""

import re
from pathlib import Path
from typing import Optional, Tuple
from omni.repo.kit_template.backend import read_toml


def is_streaming_app(kit_file_path: Path) -> bool:
    """
    Detect if a .kit file uses Kit App Streaming.
    
    Checks for:
    - omni.services.streaming.webrtc extension (primary)
    - omni.kit.streamhelper extension
    - omni.kit.livestream.* extensions (legacy)
    - streaming template indicator
    
    Args:
        kit_file_path: Path to .kit file
        
    Returns:
        True if app uses streaming
    """
    if not kit_file_path.exists():
        return False
    
    try:
        content = read_toml(kit_file_path)
        
        # Check dependencies
        dependencies = content.get('dependencies', {})
        streaming_deps = [
            'omni.services.streaming.webrtc',  # Primary WebRTC streaming
            'omni.kit.streamhelper',           # Stream helper utilities
            'omni.kit.livestream.app',         # Legacy livestream
            'omni.kit.livestream.core',        # Legacy livestream
            'omni.kit.livestream.native',      # Legacy livestream
        ]
        
        for dep in streaming_deps:
            if dep in dependencies:
                return True
        
        # Check template name
        template_name = content.get('package', {}).get('template_name', '')
        if 'streaming' in template_name.lower():
            return True
        
        return False
        
    except Exception:
        return False


def get_streaming_url(
    port: int = 47995,
    hostname: str = 'localhost',
    use_https: bool = True
) -> str:
    """
    Construct the streaming URL for a Kit app.
    
    Kit apps host their own HTTPS/WebRTC signaling server on the specified port.
    No stdout parsing needed - the URL is deterministic.
    
    Args:
        port: WebRTC listen port (default 47995)
        hostname: Hostname or IP (default 'localhost', use '0.0.0.0' for remote)
        use_https: Use HTTPS (default True, self-signed cert is normal)
        
    Returns:
        Streaming URL (e.g., 'https://localhost:47995')
    """
    protocol = 'https' if use_https else 'http'
    return f'{protocol}://{hostname}:{port}'


def get_streaming_flags(
    port: int = 47995,
    draw_mouse: bool = False,
    cert_path: Optional[Path] = None,
    key_path: Optional[Path] = None
) -> List[str]:
    """
    Generate command-line flags for Kit App Streaming.
    
    Returns the standard flags needed to enable WebRTC streaming:
    - Enable streaming extensions
    - Set headless/no-window mode
    - Configure WebRTC settings
    - Optional: Custom SSL certificates
    
    Args:
        port: WebRTC listen port (default 47995)
        draw_mouse: Show mouse cursor in stream (default False)
        cert_path: Custom SSL certificate path (optional)
        key_path: Custom SSL private key path (optional)
        
    Returns:
        List of command-line flags
    """
    flags = [
        '--enable', 'omni.services.streaming.webrtc',
        '--enable', 'omni.kit.streamhelper',
        '--allow-root',
        '--no-window',
        f'--/app/window/drawMouse={str(draw_mouse).lower()}',
        '--/renderer/headless=true',
        '--/rtx/webrtc/enable=true',
        f'--/rtx/webrtc/listenPort={port}',
    ]
    
    if cert_path:
        flags.append(f'--/rtx/webrtc/certificatePath={cert_path}')
    
    if key_path:
        flags.append(f'--/rtx/webrtc/privateKeyPath={key_path}')
    
    return flags


def wait_for_streaming_ready(
    port: int = 47995,
    hostname: str = 'localhost',
    timeout: int = 60
) -> bool:
    """
    Wait for Kit streaming server to be ready.
    
    Polls the streaming port until it responds or timeout occurs.
    
    Args:
        port: WebRTC listen port
        hostname: Hostname to check
        timeout: Maximum seconds to wait
        
    Returns:
        True if server is ready, False if timeout
    """
    import socket
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((hostname, port))
            sock.close()
            
            if result == 0:
                # Port is open
                return True
        except Exception:
            pass
        
        time.sleep(0.5)
    
    return False
```

#### 1.2: Modify `launch.py` to Support Streaming

Add streaming detection and automatic flag injection:

```python
def launch_kit(
    app_name,
    target_directory: Path,
    config: dict = {},
    dev_bundle: bool = False,
    extra_args: List[str] = [],
    xpra: bool = False,
    xpra_display: int = 100,
    enable_streaming: bool = False,  # NEW
    streaming_port: int = 47995,     # NEW
    streaming_host: str = 'localhost'  # NEW
):
    """
    Launch a Kit application with optional streaming support.
    
    Args:
        app_name: Name of the .kit file
        target_directory: Build directory
        config: Build configuration
        dev_bundle: Enable developer bundle
        extra_args: Additional command-line arguments
        xpra: Use Xpra display server (Mode 2b)
        xpra_display: Xpra display number
        enable_streaming: Enable WebRTC streaming (Mode 1)
        streaming_port: Port for streaming server (default 47995)
        streaming_host: Hostname for streaming URL construction
        
    Returns:
        Tuple[int, Optional[str]]: (return_code, streaming_url)
    """
    from streaming_utils import (
        is_streaming_app, 
        get_streaming_flags,
        get_streaming_url,
        wait_for_streaming_ready
    )
    
    # ... (existing app selection and per-app deps logic) ...
    
    # Detect if this is a streaming app or streaming is explicitly requested
    app_source_path = repo_root / "source" / "apps" / app_name.replace('.kit', '')
    kit_file = app_source_path / f"{app_name}"
    is_streaming = is_streaming_app(kit_file) or enable_streaming
    
    streaming_url = None
    
    if is_streaming:
        print(f"Launching with Kit App Streaming (WebRTC)")
        print(f"Streaming port: {streaming_port}")
        
        # Add streaming flags to extra_args
        streaming_flags = get_streaming_flags(port=streaming_port)
        extra_args = streaming_flags + extra_args
        
        # Construct streaming URL (deterministic, no parsing needed)
        streaming_url = get_streaming_url(
            port=streaming_port,
            hostname=streaming_host
        )
    
    # ... (existing Xpra and per-app Kit SDK logic) ...
    # Note: Streaming and Xpra are mutually exclusive
    
    # Build command
    app_build_path = Path(omni.repo.man.resolve_tokens(
        str(target_directory) + "/" + app_name + "${shell_ext}"
    ))
    
    if not app_build_path.is_file():
        err_msg = f"\nDesired built Kit App: {app_name} is missing the built entrypoint script: {app_build_path}. Have you built your app via `{_get_repo_cmd()} build`?"
        _quiet_error(err_msg)
    
    kit_cmd = [str(app_build_path)]
    if dev_bundle:
        kit_cmd += ["--enable", "omni.kit.developer.bundle"]
    if extra_args:
        kit_cmd += extra_args
    
    # Launch the app
    if is_streaming:
        # Launch in background and wait for streaming server
        process = subprocess.Popen(
            kit_cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env_vars if env_vars else None,
        )
        
        # Wait for streaming server to be ready
        print(f"Waiting for streaming server on port {streaming_port}...")
        if wait_for_streaming_ready(streaming_port, streaming_host, timeout=30):
            print(f"\n{'='*60}")
            print(f"✓ Streaming ready!")
            print(f"URL: {streaming_url}")
            print(f"{'='*60}")
            print(f"\nNote: Self-signed SSL certificate warning is normal.")
            print(f"Accept the certificate in your browser to continue.\n")
        else:
            print("Warning: Streaming server did not respond within 30 seconds")
            print(f"Try connecting anyway: {streaming_url}")
        
        # Keep process running
        returncode = process.wait()
        return returncode, streaming_url
    else:
        # Normal launch (existing behavior)
        returncode = _run_process(
            kit_cmd,
            exit_on_error=False,
            env=env_vars if env_vars else None,
        )
        return returncode, streaming_url
```

#### 1.3: CLI Support (`repo.sh launch --streaming`)

Add flags to enable streaming:

```bash
# Enable streaming for any app (auto-detects if .kit has streaming extensions)
./repo.sh launch my_app.kit

# Force streaming mode even if not auto-detected
./repo.sh launch my_app.kit --streaming

# Streaming with custom port
./repo.sh launch my_app.kit --streaming --streaming-port 48000

# For remote access
./repo.sh launch my_app.kit --streaming --remote

# The above will print:
# ============================================================
# ✓ Streaming ready!
# URL: https://localhost:47995
# ============================================================
# 
# Note: Self-signed SSL certificate warning is normal.
# Accept the certificate in your browser to continue.
```

### Phase 2: API Support

#### 2.1: Template Creation with Streaming

Modify `/api/templates/create` to accept `enable_streaming` parameter:

```python
@template_bp.route('/create', methods=['POST'])
def create_from_template():
    """Create a new project from a template."""
    data = request.json
    template_name = data.get('template')
    project_name = data.get('name')
    enable_streaming = data.get('enableStreaming', False)  # NEW
    streaming_type = data.get('streamingType', 'default')  # NEW: default, nvcf, gdn

    # ... (existing validation) ...

    # Create base application
    result = template_engine.handle_generate_command(
        template_name,
        args=[...]
    )

    # If streaming enabled, add streaming layer
    if enable_streaming:
        streaming_template_map = {
            'default': 'omni_default_streaming',
            'nvcf': 'nvcf_streaming',
            'gdn': 'omni_gdn_streaming'
        }

        streaming_template = streaming_template_map.get(streaming_type, 'omni_default_streaming')

        # Add streaming .kit file
        # This creates a {project_name}_streaming.kit file
        result_streaming = template_engine.add_streaming_layer(
            base_app=project_name,
            streaming_template=streaming_template
        )

    return jsonify(result)
```

#### 2.2: Launch with Streaming URL Return

Modify job launch to return streaming URL:

```python
@job_bp.route('/launch', methods=['POST'])
def launch_application():
    """Launch an application and return job ID (and streaming URL if applicable)."""
    data = request.json
    app_name = data.get('app_name')
    web_preview = data.get('webPreview', False)  # NEW

    def launch_task():
        from tools.repoman.launch import launch_kit
        from tools.repoman.streaming_utils import is_streaming_app

        # Detect streaming
        kit_file = Path(f"source/apps/{app_name}/{app_name}.kit")
        is_streaming = is_streaming_app(kit_file)

        if is_streaming:
            # Launch with URL capture
            returncode, streaming_url = launch_kit(
                app_name,
                target_directory=...,
                capture_streaming_url=True
            )

            return {
                'returncode': returncode,
                'streaming_url': streaming_url,
                'streaming': True,
                'web_preview': web_preview
            }
        elif web_preview:
            # Use Xpra
            returncode, _ = launch_kit(
                app_name,
                target_directory=...,
                xpra=True
            )

            return {
                'returncode': returncode,
                'xpra_url': 'http://localhost:10000',
                'streaming': False,
                'web_preview': True
            }
        else:
            # Direct launch
            returncode, _ = launch_kit(
                app_name,
                target_directory=...
            )

            return {
                'returncode': returncode,
                'streaming': False,
                'web_preview': False
            }

    job_id = job_manager.create_job(
        "launch_application",
        launch_task
    )

    return jsonify({'job_id': job_id})


@job_bp.route('/jobs/<job_id>/streaming_url', methods=['GET'])
def get_streaming_url(job_id):
    """Get streaming URL for a completed launch job."""
    job = job_manager.get_job(job_id)

    if job and job.get('status') == 'completed':
        result = job.get('result', {})
        return jsonify({
            'streaming_url': result.get('streaming_url'),
            'xpra_url': result.get('xpra_url'),
            'is_streaming': result.get('streaming', False)
        })

    return jsonify({'error': 'Job not found or not completed'}), 404
```

### Phase 3: UI Support

#### 3.1: Create Project Page - Streaming Checkbox

Add to `CreateProjectPage.tsx`:

```typescript
const [enableStreaming, setEnableStreaming] = useState(false);
const [streamingType, setStreamingType] = useState('default');

// In the form:
<div className="form-group">
  <label>
    <input
      type="checkbox"
      checked={enableStreaming}
      onChange={(e) => setEnableStreaming(e.target.checked)}
    />
    Enable Kit App Streaming
  </label>

  {enableStreaming && (
    <select
      value={streamingType}
      onChange={(e) => setStreamingType(e.target.value)}
    >
      <option value="default">Default Streaming</option>
      <option value="nvcf">NVCF Streaming</option>
      <option value="gdn">GDN Streaming</option>
    </select>
  )}
</div>

// When submitting:
const createProject = async () => {
  await api.post('/templates/create', {
    template: selectedTemplate,
    name: projectName,
    enableStreaming: enableStreaming,
    streamingType: streamingType
  });
};
```

#### 3.2: Launch Page - Web Preview Checkbox

Add to launch UI:

```typescript
const [webPreview, setWebPreview] = useState(false);
const [streamingUrl, setStreamingUrl] = useState<string | null>(null);

// In the form:
<div className="form-group">
  <label>
    <input
      type="checkbox"
      checked={webPreview}
      onChange={(e) => setWebPreview(e.target.checked)}
    />
    Web Preview
  </label>
  <span className="help-text">
    {isStreamingApp
      ? "Open streaming session in browser"
      : "Use Xpra for remote preview"}
  </span>
</div>

// When launching:
const launchApp = async () => {
  const response = await api.post('/jobs/launch', {
    app_name: appName,
    webPreview: webPreview
  });

  const jobId = response.data.job_id;

  // Poll for completion
  const pollJob = setInterval(async () => {
    const job = await api.get(`/jobs/${jobId}`);

    if (job.data.status === 'completed') {
      clearInterval(pollJob);

      // Get streaming URL
      const urlResponse = await api.get(`/jobs/${jobId}/streaming_url`);
      const { streaming_url, xpra_url, is_streaming } = urlResponse.data;

      if (webPreview) {
        const url = streaming_url || xpra_url;
        if (url) {
          // Open in new tab
          window.open(url, '_blank');
        }
      } else {
        // Show URL in toast/modal
        if (streaming_url) {
          showToast(`Streaming URL: ${streaming_url}`);
        }
      }
    }
  }, 1000);
};
```

## Testing Strategy

### Unit Tests
- `test_streaming_detection.py` - Test `is_streaming_app()`
- `test_url_extraction.py` - Test `extract_streaming_url()`

### Integration Tests
- Create streaming app via CLI
- Create streaming app via API
- Launch streaming app and verify URL capture
- Launch with web preview and verify browser opens

### Manual Tests
- Create project with streaming enabled
- Build streaming project
- Launch with `--streaming` flag
- Launch via UI with web preview checked
- Verify URL is captured and displayed/opened

## Migration Notes

### Backward Compatibility
- ✅ Existing apps without streaming work unchanged
- ✅ Xpra mode (Mode 2b) continues to work
- ✅ Direct launch (Mode 2a) continues to work
- ✅ New streaming detection is additive only

### Breaking Changes
- None - this is a pure feature addition

## Documentation Requirements

1. `docs/README.md` - Add Kit App Streaming section
2. `docs/API_USAGE.md` - Document streaming endpoints
3. `docs/ARCHITECTURE.md` - Document three display modalities
4. `KIT_APP_STREAMING.md` - Dedicated streaming guide

## Timeline Estimate (Updated)

With the simplified streaming implementation (no stdout parsing, deterministic URLs):

- **Phase 1** (Backend/CLI): 1-2 days ⬇️ (much simpler!)
- **Phase 2** (API): 1 day
- **Phase 3** (UI): 1-2 days  
- **Testing**: 1 day
- **Documentation**: 1 day

**Total**: 5-7 days for complete implementation ⬇️ (was 7-11 days)

**Simplifications:**
- ✅ No stdout parsing needed
- ✅ No complex subprocess handling
- ✅ Deterministic URL construction
- ✅ Simple port availability checking
- ✅ Standard command-line flags

## Answered Questions (From User)

### How Kit App Streaming Works

Kit apps have a **built-in HTTPS/WebRTC signaling server** that can be enabled via command-line flags:

```bash
kit.app \
    --enable omni.services.streaming.webrtc \
    --enable omni.kit.streamhelper \
    --allow-root \
    --no-window \
    --/app/window/drawMouse=false \
    --/renderer/headless=true \
    --/rtx/webrtc/enable=true \
    --/rtx/webrtc/listenPort=47995
```

**Key Points:**
1. **No stdout parsing needed** - URL is deterministic based on port
2. **Default streaming URL**: `https://localhost:47995` (or custom port)
3. **Self-signed cert** is normal (can be overridden)
4. **Extensions required**: `omni.services.streaming.webrtc`, `omni.kit.streamhelper`
5. **Port is configurable**: `--/rtx/webrtc/listenPort=<port>`
6. **Custom certs**: `--/rtx/webrtc/certificatePath=<path>` and `--/rtx/webrtc/privateKeyPath=<path>`

This **greatly simplifies** the implementation!
