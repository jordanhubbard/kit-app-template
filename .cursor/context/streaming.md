# Kit App Streaming Context

## Overview
Kit App Streaming enables WebRTC streaming of Kit applications for remote browser access.

## Required Extensions
```toml
[dependencies]
"omni.services.streaming.webrtc" = {}
"omni.kit.streamhelper" = {}
```

## CLI Usage
```bash
# Auto-detected streaming
./repo.sh launch my.app.kit --streaming

# Custom port
./repo.sh launch my.app.kit --streaming --streaming-port 48000

# Force streaming (even if not detected)
./repo.sh launch my.app.kit --streaming
```

## API Integration

### Create Streaming App
```bash
POST /api/templates/create
{
  "template": "kit_base_editor",
  "name": "my.streaming.app",
  "enableStreaming": true
}
```

### Launch Streaming App
```bash
POST /api/projects/run
{
  "projectName": "my.streaming.app",
  "streamingPort": 47995
}
```

Response includes:
- `streamingUrl`: Deterministic URL (https://localhost:47995)
- `streaming`: true/false
- `port`: Streaming port

### WebSocket Event
```json
{
  "event": "streaming_ready",
  "data": {
    "project": "my.streaming.app",
    "url": "https://localhost:47995",
    "port": 47995
  }
}
```

## UI Integration

### Create Project Page
- Checkbox: "Enable Kit App Streaming"
- Location: Advanced Options section
- Sends `enableStreaming: true` to API

### HomePage Notification
- Auto-opens browser tab when streaming ready
- Toast notification with URL
- SSL certificate warning
- Auto-dismiss after 10 seconds

## Technical Details

### Deterministic URL
- Format: `https://localhost:{port}`
- Default port: 47995
- Hostname: `localhost` (local) or `0.0.0.0` (remote via REMOTE=1)

### Detection Logic
```python
from tools.repoman.streaming_utils import is_streaming_app

kit_file = Path("source/apps/my.app/my.app.kit")
if is_streaming_app(kit_file):
    # Launch with streaming flags
    pass
```

### Launch Flow
1. Backend detects streaming app
2. Launches with `--streaming` flag via CLI
3. Polls streaming port (30s timeout)
4. Emits `streaming_ready` WebSocket event
5. Returns streaming URL in response

### Self-Signed SSL
- Kit generates self-signed certificate
- Browser shows security warning
- User must accept certificate
- Normal behavior, not an error

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :47995

# Kill the process or use different port
./repo.sh launch my.app.kit --streaming --streaming-port 48000
```

### Server Not Ready
- Wait up to 30 seconds for server startup
- Check process logs for errors
- Ensure no firewall blocking
- Verify extensions in .kit file
