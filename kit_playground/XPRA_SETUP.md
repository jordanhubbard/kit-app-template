# Xpra Integration for Kit Playground

This document explains how to set up Xpra to enable remote X11 display of Omniverse Kit applications in the web browser.

## What is Xpra?

Xpra is a "screen for X" that allows you to run X11 programs on a remote host and display them in a web browser using HTML5. This is perfect for displaying Omniverse Kit applications that use X11/OpenGL.

## Installation

### Ubuntu/Debian (Linux)
```bash
# Add Xpra repository
sudo wget -O "/usr/share/keyrings/xpra.asc" https://xpra.org/xpra.asc
cd /etc/apt/sources.list.d
sudo wget https://xpra.org/repos/jammy/xpra.sources

# Install Xpra
sudo apt update
sudo apt install -y xpra xpra-html5

# Verify installation
xpra --version
```

### Windows
```powershell
# Download and install from https://xpra.org/dists/windows/
# Or use winget:
winget install Xpra
```

## How Xpra Works with Kit Playground

1. **Xpra Server**: Runs on the host machine, creates a virtual X11 display
2. **Kit Application**: Launches and connects to the Xpra virtual display
3. **Xpra HTML5 Client**: Served to the browser, connects to Xpra server via WebSocket
4. **User**: Sees the Kit application rendered in their browser

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Browser (Client)                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Kit Playground UI (React)                               │ │
│ │   ├─ Templates Tab                                      │ │
│ │   ├─ Code Tab                                           │ │
│ │   └─ Preview Tab (Xpra HTML5 Client)                   │ │
│ └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket (ws://host:10000)
                         │
┌────────────────────────▼────────────────────────────────────┐
│ Host Machine (Server)                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Flask Web Server (port 8082)                            │ │
│ │   ├─ Serves React UI                                    │ │
│ │   ├─ REST API for templates                             │ │
│ │   └─ Manages Xpra processes                             │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Xpra Server (port 10000)                                │ │
│ │   ├─ Virtual X11 Display (:100)                         │ │
│ │   ├─ WebSocket server for HTML5 client                  │ │
│ │   └─ Forwards X11 events                                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Kit Application                                          │ │
│ │   DISPLAY=:100 kit-app                                   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Integration Steps

### 1. Start Xpra Server (automatically managed by Flask)

When a user clicks "Run" on a template, the Flask server will:

```python
import subprocess
import os

def start_xpra_session(display_number=100):
    """Start an Xpra server on a virtual display."""
    # Start Xpra in daemon mode with HTML5 support
    cmd = [
        'xpra', 'start',
        f':{display_number}',
        '--bind-tcp=0.0.0.0:10000',  # Listen on all interfaces
        '--html=on',                  # Enable HTML5 client
        '--no-daemon',                # Run in foreground (we'll manage it)
        '--start-child=xterm',        # Optional: start a test app
    ]

    process = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    return process

def launch_kit_app(app_path, display_number=100):
    """Launch a Kit application on the Xpra display."""
    env = os.environ.copy()
    env['DISPLAY'] = f':{display_number}'

    cmd = [app_path]
    process = subprocess.Popen(cmd, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    return process
```

### 2. Embed Xpra HTML5 Client in Preview Tab

The Xpra HTML5 client files are typically located at:
- `/usr/share/xpra/www/` (Linux)
- `C:\Program Files\Xpra\share\xpra\www\` (Windows)

We'll serve these files and embed them in an iframe:

```tsx
<iframe
  src="http://localhost:10000"
  style={{ width: '100%', height: '100%', border: 'none' }}
  title="Xpra Display"
/>
```

### 3. Session Management

Each running application gets its own Xpra session:
- Display :100 for first app
- Display :101 for second app
- etc.

The Flask server tracks which sessions are active and cleans them up when done.

## Configuration

### Recommended Xpra Settings

For Kit applications (which use OpenGL), use these Xpra options:

```bash
xpra start :100 \
  --bind-tcp=0.0.0.0:10000 \
  --html=on \
  --encodings=rgb,png,jpeg \
  --compression=0 \
  --opengl=yes \
  --speaker=off \
  --microphone=off
```

### Security Considerations

For production use:
1. Enable Xpra authentication: `--auth=password:file=/path/to/password`
2. Use SSL/TLS: `--ssl-cert=/path/to/cert.pem`
3. Restrict bind address: `--bind-tcp=127.0.0.1:10000` (then use nginx proxy)

## Troubleshooting

### Xpra not found
```bash
which xpra  # Should show /usr/bin/xpra
```

### Display issues
```bash
# Check if display is available
xpra list
xpra info :100
```

### Connection refused
```bash
# Check if Xpra is listening
netstat -tlnp | grep 10000
```

### Performance issues
- Reduce encoding quality
- Use h264 encoding if available: `--encoding=h264`
- Adjust compression: `--compression=0` (for LAN) or `--compression=9` (for WAN)

## Alternative: VirtualGL + TurboVNC

For better OpenGL performance, consider:
1. VirtualGL: Renders OpenGL on GPU, sends pixels to VNC
2. TurboVNC: High-performance VNC server
3. noVNC: HTML5 VNC client

This stack may provide better performance for Omniverse Kit applications.

## References

- Xpra Official Docs: https://xpra.org/
- Xpra HTML5 Client: https://github.com/Xpra-org/xpra-html5
- VirtualGL: https://www.virtualgl.org/
