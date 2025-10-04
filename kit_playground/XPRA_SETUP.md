# Xpra Integration for Kit Playground

This document explains how to set up Xpra to enable remote X11 display of Omniverse Kit applications in the web browser.

## What is Xpra?

Xpra is a "screen for X" that allows you to run X11 programs on a remote host and display them in a web browser using HTML5. This is perfect for displaying Omniverse Kit applications that use X11/OpenGL.

## Installation

### Quick Install (Recommended)

**All Platforms:**
```bash
make install-xpra
```

This automatically detects your OS and installs Xpra with all dependencies.

### Manual Installation

#### Ubuntu/Debian (Linux)
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

#### Fedora/RHEL/CentOS
```bash
sudo dnf install xpra xpra-html5
# or
sudo yum install xpra xpra-html5
```

#### Arch Linux
```bash
sudo pacman -S xpra
```

#### macOS
```bash
brew install xpra
# or download from https://xpra.org/dists/MacOS/
```

#### Windows
```powershell
# Download and install from https://xpra.org/dists/windows/
# Or use winget:
winget install Xpra
```

## How Xpra Works with Kit Playground

1. **Xpra Server**: Automatically started when you run a Kit application
2. **Kit Application**: Launches and connects to the Xpra virtual display
3. **Xpra HTML5 Client**: Embedded in Preview pane, connects via WebSocket
4. **User**: Sees the Kit application rendered directly in the browser

**Fully Automated:** When you click "Run" on a Kit application in the Playground, the backend automatically:
- Creates an Xpra session
- Launches the app on a virtual display
- Provides the Xpra HTML5 client URL to the frontend
- Displays the app in the Preview tab

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

## API Integration

The Xpra integration is fully automatic. Here's how it works internally:

### 1. Backend API Endpoints

#### Check Xpra Installation
```bash
GET /api/xpra/check
Response: { "installed": true, "version": "5.0", "installCommand": "make install-xpra" }
```

#### Create Xpra Session
```bash
POST /api/xpra/sessions
Body: { "sessionId": "my-session" }
Response: { "success": true, "sessionId": "my-session", "displayNumber": 100, "port": 10000, "url": "http://localhost:10000" }
```

#### Launch App in Session
```bash
POST /api/xpra/sessions/my-session/launch
Body: { "command": "/path/to/kit-app" }
Response: { "success": true, "url": "http://localhost:10000" }
```

#### Stop Session
```bash
DELETE /api/xpra/sessions/my-session
Response: { "success": true }
```

### 2. Automatic Session Management

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

The Flask backend automatically manages Xpra sessions:

```python
# XpraManager handles all sessions
xpra_manager = XpraManager()

# Create session when app runs
session = xpra_manager.create_session("session_id")

# Launch app
session.launch_app("/path/to/kit-app")

# Get URL for frontend
url = xpra_manager.get_session_url("session_id")
# Returns: http://localhost:10000

# Cleanup when done
xpra_manager.stop_session("session_id")
```

### 3. Frontend Integration

The PreviewPane component automatically detects Xpra mode:

```tsx
<PreviewPane
  url="http://localhost:10000"
  mode="xpra"
  templateId={selectedTemplate}
/>
```

This embeds the Xpra HTML5 client (served by Xpra itself) in an iframe with full clipboard, keyboard, and mouse support.

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
