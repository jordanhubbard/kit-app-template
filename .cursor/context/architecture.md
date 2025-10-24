# Architecture Context for Kit App Template

## Three-Tier Architecture

### 1. CLI Layer (tools/repoman/)
- Command-line interface
- Template engine
- Build and launch system
- Standalone generation
- Per-app dependency management
- Kit App Streaming utilities

### 2. API Layer (kit_playground/backend/)
- REST API endpoints (Flask)
- WebSocket streaming (Flask-SocketIO)
- Job management system
- OpenAPI/Swagger documentation
- Real-time log streaming

### 3. UI Layer (kit_playground/ui/)
- React + TypeScript
- Tailwind CSS styling
- Real-time WebSocket integration
- Job monitoring
- Project management

## Data Flow Patterns

### CLI to API
1. User executes `./repo.sh` command
2. CLI processes and outputs results
3. API can invoke CLI via subprocess
4. Results streamed back via WebSocket

### API to UI
1. UI makes REST API call
2. API returns immediate response + job_id
3. WebSocket streams real-time updates
4. UI updates state reactively

### WebSocket Events
- `job_log` - Real-time log messages
- `job_progress` - Progress updates
- `job_status` - Status changes
- `streaming_ready` - Kit App Streaming ready

## Key Design Patterns

### 1. Backward Compatibility
- All new features are opt-in via flags
- Default behavior never changes
- Existing templates continue to work
- Compatibility tests validate no regression

### 2. Metadata-Driven Extensions
- Template engine adds metadata to playback
- repo_dispatcher detects metadata post-replay
- Extensions (standalone, per-app-deps) applied after template files exist

### 3. Auto-Detection
- Streaming apps detected via .kit file analysis
- Per-app deps detected via dependencies/ directory
- Standalone projects have standalone-specific files

## Integration Points

### CLI ↔ Template System
- template_engine.py generates playback files
- repo_dispatcher.py executes playback via repoman.py
- Post-processing applies extensions

### API ↔ CLI
- subprocess.run() with capture_output
- JSON mode for machine-readable output
- Process group management for clean termination

### UI ↔ API
- axios for HTTP requests
- socket.io-client for WebSocket
- Type-safe TypeScript interfaces
