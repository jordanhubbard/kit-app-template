# Kit App Template - Architecture Overview

## Design Philosophy

The kit-app-template follows a **monolithic CLI with optional visual frontend** architecture. This design ensures that:

1. **CLI commands work standalone** - No background services or web servers required
2. **Kit Playground is optional** - Provides a browser-based UI for those who prefer visual tools
3. **No interference** - CLI and Playground are independent and can be used separately or together

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kit App Template System                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
┌───────────────────────┐         ┌───────────────────────────┐
│   CLI Interface       │         │  Kit Playground (Optional)│
│   (Monolithic)        │         │  (Web-based Visual UI)    │
├───────────────────────┤         ├───────────────────────────┤
│ - ./repo.sh           │         │ - Flask Web Server        │
│ - ./repo.bat          │         │ - React Frontend          │
│ - Standalone          │         │ - Port 8888 (default)     │
│ - No dependencies     │         │ - Requires Node.js        │
│   on web server       │         │ - Browser-based UI        │
└───────────┬───────────┘         └───────────┬───────────────┘
            │                                 │
            │                                 │
            └────────────┬────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Unified Template API │
            │   (template_api.py)    │
            ├────────────────────────┤
            │ - Shared backend code  │
            │ - License management   │
            │ - Template discovery   │
            │ - Template generation  │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Template Engine      │
            │   (template_engine.py) │
            ├────────────────────────┤
            │ - TOML configuration   │
            │ - Variable interpolation│
            │ - File generation      │
            │ - Playback system      │
            └────────────────────────┘
```

## Components

### 1. CLI Interface (Primary, Monolithic)

**Location:** `tools/repoman/`

**Key Files:**
- `repo_dispatcher.py` - OS-independent command router
- `repoman.py` - Core CLI functionality
- `template_engine.py` - Template processing engine

**Characteristics:**
- **Standalone operation** - Works without any background services
- **Direct execution** - Commands run, complete, and exit immediately
- **No hanging** - All operations are synchronous and deterministic
- **Cross-platform** - Works on Linux, Windows, and macOS

**Example Usage:**
```bash
# These work immediately with no web server:
./repo.sh template list
./repo.sh template new kit_base_editor --name my.app
./repo.sh build
./repo.sh launch
```

### 2. Kit Playground (Optional, Web-based)

**Location:** `kit_playground/`

**Key Files:**
- `playground.py` - Main entry point
- `backend/web_server.py` - Flask REST API server
- `core/playground_app.py` - Core application logic
- `ui/` - React-based frontend

**Characteristics:**
- **Optional tool** - Not required for CLI functionality
- **Web server** - Runs Flask on port 8888 (configurable)
- **Blocking execution** - Server runs until stopped (Ctrl+C)
- **Visual interface** - Browser-based UI for template browsing and editing
- **Requires Node.js** - For building the React frontend

**Example Usage:**
```bash
# Starts a web server that runs until you stop it:
make playground

# In another terminal, CLI still works:
./repo.sh template list
```

### 3. Unified Template API (Shared Backend)

**Location:** `tools/repoman/template_api.py`

**Purpose:** Provides a common interface for template operations used by both CLI and Playground.

**Key Features:**
- **No dependencies** - Works standalone without web server
- **Shared code** - CLI and Playground use the same backend logic
- **Consistent behavior** - Same results whether using CLI or UI

**Architecture Benefits:**
- **DRY principle** - Single source of truth for template logic
- **Easy testing** - Can test backend without UI
- **Flexible usage** - Can be imported directly by Python scripts

## How They Work Together

### CLI-Only Workflow (Monolithic)

```
User runs: ./repo.sh template new kit_base_editor
       ↓
repo_dispatcher.py routes command
       ↓
template_engine.py generates playback file
       ↓
repoman.py replays playback to create files
       ↓
Command completes and exits
```

**Duration:** Seconds (synchronous, completes immediately)
**Dependencies:** None (just Python and TOML library)

### Playground Workflow (Client-Server)

```
User runs: make playground
       ↓
Flask web server starts on port 8888
       ↓
Browser opens UI
       ↓
User interacts with visual interface
       ↓
UI sends REST API requests to Flask
       ↓
Flask calls template_api.py methods
       ↓
template_api.py uses template_engine.py
       ↓
Results returned to UI
       ↓
Server keeps running until stopped (Ctrl+C)
```

**Duration:** Runs continuously until stopped
**Dependencies:** Node.js, npm, Flask, React frontend

### Combined Workflow

Both can be used simultaneously without interference:

```
Terminal 1:                Terminal 2:
make playground            ./repo.sh template list
(server runs)              (executes immediately)
                          ./repo.sh template new ...
                          (creates template)
```

They don't interfere because:
- CLI doesn't use any ports or background services
- Playground server only handles HTTP requests
- Both use the same underlying template engine
- File system operations are atomic

## Key Architectural Decisions

### Decision 1: Monolithic CLI

**Rationale:**
- Simplicity - No daemon management, service discovery, or IPC
- Reliability - No risk of stale server processes or port conflicts
- Performance - No network overhead for local operations
- Portability - Works in any environment (containers, CI/CD, SSH)

**Trade-off:** Each CLI invocation loads Python and libraries fresh (small overhead)

### Decision 2: Optional Web Server

**Rationale:**
- Choice - Users can use CLI or UI based on preference
- Beginner-friendly - Visual interface lowers barrier to entry
- Power users - CLI provides scripting and automation
- No forced complexity - Simple projects don't need UI

**Trade-off:** UI requires additional dependencies (Node.js, npm)

### Decision 3: Shared Template API

**Rationale:**
- Consistency - Same behavior across CLI and UI
- Maintainability - Single codebase for template logic
- Testability - Can test logic independently
- Extensibility - Easy to add new interfaces (CLI plugins, IDE extensions)

**Trade-off:** Must maintain API compatibility across interfaces

## Common Misconceptions

### ❌ "CLI commands hang because they wait for playground"

**Reality:** CLI commands never interact with the playground server. They execute independently and complete immediately. If commands appear to hang, it's due to:
- Long-running build processes (expected)
- License acceptance prompts (interactive)
- Network downloads (SDK, dependencies)
- Shader compilation (first launch)

### ❌ "You need to start playground before using CLI"

**Reality:** CLI works without playground ever being installed or run. Playground is purely optional.

### ❌ "Playground and CLI share state/sessions"

**Reality:** They share the same template definitions and configuration files, but have independent runtime state. The only shared state is the filesystem.

## Troubleshooting

### CLI commands appear to hang

1. **Check for prompts** - Some commands require interactive input (license acceptance)
2. **Check process list** - `ps aux | grep python` to see what's running
3. **Check network** - SDK downloads can take time
4. **Use --verbose** - Most commands support verbose output

### Playground won't start

1. **Check port availability** - Port 8888 might be in use
   ```bash
   lsof -i :8888  # See what's using the port
   ```
2. **Check dependencies** - Playground requires Node.js and npm
   ```bash
   make deps  # Check all dependencies
   ```
3. **Rebuild UI** - If frontend is corrupted
   ```bash
   make playground-clean
   make playground-build
   ```

### Both CLI and playground fail

This indicates an issue with the core template engine:
1. **Check Python version** - Requires Python 3.8+
2. **Check TOML library** - Run `make install-python-deps`
3. **Check file permissions** - Ensure write access to project directory
4. **Check disk space** - Template generation requires free space

## Future Enhancements

Potential architectural improvements while maintaining the monolithic CLI principle:

1. **Plugin system** - Allow custom CLI commands without modifying core
2. **Alternative UIs** - VSCode extension, JetBrains plugin (using template_api.py)
3. **Cloud integration** - Optional cloud storage while keeping local-first design
4. **Performance optimization** - Cache template metadata to reduce load time
5. **Multiple backends** - Support git repos, package managers as template sources

All enhancements must preserve the core principle: **CLI works standalone, always.**

## Testing the Architecture

### Verify CLI Independence

```bash
# Test CLI without ever starting playground
./repo.sh template list
./repo.sh template new kit_base_editor --name test.app --output-dir /tmp/test
cd /tmp/test
./repo.sh build
./repo.sh launch
```

All commands should work without errors.

### Verify Playground Independence

```bash
# Start playground
make playground

# In another terminal, verify CLI still works
./repo.sh template list
./repo.sh template new kit_service --name my.service
```

Both should work simultaneously.

### Verify Shared API

```python
# Test template_api.py directly
from tools.repoman.template_api import TemplateAPI

api = TemplateAPI()
templates = api.list_templates(template_type='application')
print(f"Found {len(templates)} application templates")
```

Should work without any server running.

## Conclusion

The kit-app-template architecture is designed around a **monolithic CLI with optional visual frontend**. This ensures:

- ✅ CLI commands work instantly without background services
- ✅ Playground provides visual alternative without interfering with CLI
- ✅ Shared backend ensures consistent behavior
- ✅ Simple deployment and troubleshooting
- ✅ Works in any environment (local, container, CI/CD)

This architecture prioritizes **reliability, simplicity, and user choice** over architectural complexity.
