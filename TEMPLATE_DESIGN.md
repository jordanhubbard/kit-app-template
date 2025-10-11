# Template System Design - Create, Build, Launch Flow

**Last Updated**: 2025-10-11
**Version**: 2.0

---

## Table of Contents
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Template Creation Flow](#template-creation-flow)
4. [Build Flow](#build-flow)
5. [Launch Flow](#launch-flow)
6. [Xpra Browser Preview](#xpra-browser-preview)
7. [CLI Commands](#cli-commands)
8. [UI Workflow](#ui-workflow)
9. [Path Resolution](#path-resolution)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Kit App Template system provides a complete workflow for creating, building, and launching NVIDIA Omniverse Kit applications through both CLI and web-based UI.

### Key Principles

1. **Platform-Specific Organization**: All build outputs organized by OS and architecture
2. **Python-Centric Logic**: Cross-platform logic implemented in Python
3. **CLI-First Design**: UI operations map directly to CLI commands
4. **Symlink Strategy**: Build system symlinks source → build directories
5. **REMOTE Support**: All services respect REMOTE=1 for remote development

---

## Directory Structure

### Production Structure (After Build)

```
kit-app-template/
├── source/
│   ├── apps/                              # Application source files
│   │   └── my_app/
│   │       ├── my_app.kit                 # Application configuration
│   │       ├── repo.sh                    # Build/launch wrapper (Linux/Mac)
│   │       ├── repo.bat                   # Build/launch wrapper (Windows)
│   │       ├── .project-meta.toml         # Project metadata
│   │       └── README.md                  # Template documentation
│   └── extensions/                        # Extension source files
│       └── my_app_setup/
│
├── _build/
│   ├── linux-x86_64/                      # Platform-specific builds
│   │   └── release/                       # Configuration (release/debug)
│   │       ├── apps/  → ../../source/apps # Symlink to source (created by build)
│   │       ├── my_app.kit.sh              # Built executable
│   │       ├── exts/                      # Built extensions
│   │       └── kit/                       # Kit runtime
│   ├── linux-aarch64/                     # ARM Linux builds
│   ├── windows-x86_64/                    # Windows builds
│   └── macos-x86_64/                      # macOS builds
│
├── templates/                             # Template definitions
└── tools/                                 # Build and template tools
    └── repoman/
        ├── template_api.py                # Template generation API
        ├── repo_dispatcher.py             # Platform detection
        └── launch.py                      # Launch logic with Xpra
```

### Path Resolution Rules

1. **Apps stored in**: `source/apps/{name}/`
2. **Build creates symlink**: `_build/{platform}-{arch}/{config}/apps` → `source/apps`
3. **Executables built in**: `_build/{platform}-{arch}/{config}/{name}.kit.sh`
4. **Both paths work**: Source and symlinked paths are equivalent

---

## Template Creation Flow

### 1. User Initiates Creation

**Via UI**:
- User selects template from gallery
- Enters project name and details
- Clicks "Create"

**Via CLI**:
```bash
./repo.sh template new kit_base_editor --name my_company.my_app
```

### 2. Template API Generates Playback File

**File**: `tools/repoman/template_api.py`

```python
def generate_template(request: TemplateGenerationRequest) -> TemplateGenerationResult:
    # 1. Render template with user variables
    # 2. Create temporary playback TOML file
    # 3. Return playback file path
```

**Playback File** (`/tmp/tmpXXXXXX.toml`):
```toml
[kit_base_editor]
application_name = "my_company.my_app"
application_display_name = "My App"
version = "1.0.0"
```

### 3. Execute Playback (Template Replay)

**Command**:
```bash
./repo.sh template replay /tmp/tmpXXXXXX.toml
```

**What happens**:
1. `omni.repo.man` reads playback file
2. Renders template files to `source/apps/my_app.kit` (as a FILE)
3. Creates extensions in `source/extensions/`
4. Updates `premake5.lua` and `source/rendered_template_metadata.json`

### 4. Post-Processing (Application Restructuring)

**File**: `tools/repoman/repo_dispatcher.py`

```python
def _fix_application_structure(repo_root: Path, playback_data: Dict[str, Any]):
    # 1. Find .kit FILE in source/apps/
    # 2. Create directory: source/apps/{name}/
    # 3. Move {name}.kit into directory
    # 4. Create wrapper scripts (repo.sh, repo.bat)
    # 5. Create .project-meta.toml
    # 6. Create symlink: _build/{platform}/{config}/apps → source/apps
```

**Result**:
```
source/apps/my_app/
  ├── my_app.kit
  ├── repo.sh
  ├── repo.bat
  ├── .project-meta.toml
  └── README.md
```

### 5. Clean Up

- Clears static apps list in `repo.toml` (uses dynamic discovery)
- Returns project info to UI/caller

**API Response**:
```json
{
  "success": true,
  "outputDir": "_build/linux-x86_64/release/apps",
  "projectInfo": {
    "projectName": "my_app",
    "kitFile": "_build/linux-x86_64/release/apps/my_app/my_app.kit"
  }
}
```

---

## Build Flow

### 1. Build Initiation

**Via UI**:
- User clicks "Build" button
- Backend receives: `POST /api/projects/build`

**Via CLI (from repo root)**:
```bash
./repo.sh build --config release
```

**Via CLI (from app directory)**:
```bash
cd source/apps/my_app
./repo.sh build --config release
```

### 2. Build Process

**What the wrapper does**:
```bash
#!/bin/bash
# Finds repo root
REPO_ROOT=$(find_repo_root)
# Calls main repo.sh
exec "$REPO_ROOT/repo.sh" "$@"
```

**Main build steps**:
1. Fetch dependencies (`repo_build` tool)
2. Run premake5 (generate Makefiles)
3. Create symlink: `_build/{platform}/{config}/apps` → `source/apps`
4. Compile extensions
5. Stage files (copy/link)
6. Generate launcher scripts: `_build/{platform}/{config}/{app}.kit.sh`

### 3. Build Output

**Created files**:
```
_build/linux-x86_64/release/
├── apps/  → symlink to source/apps
├── my_app.kit.sh                    # Main launcher
├── tests-my_app.kit.sh              # Test launcher
├── exts/                            # Built extensions
│   ├── my_app_setup/
│   └── my_app_messaging/
└── kit/                             # Kit runtime
```

### 4. CLI Commands Logged (Backend)

**Backend logs** (`kit_playground/backend/routes/project_routes.py`):
```python
socketio.emit('log', {'message': f'$ cd {cwd}'})
socketio.emit('log', {'message': f'$ ./repo.sh build --config release'})
```

**Console output** (what user sees in UI):
```
Building my_app...
$ cd /path/to/source/apps/my_app
$ ./repo.sh build --config release
>>> Fetching all dependencies...
BUILD (RELEASE) SUCCEEDED (Took 12.3 seconds)
```

---

## Launch Flow

### 1. Launch Options

**Option A: Direct Launch (Local Display)**
```bash
./repo.sh launch --name my_app.kit
```
- Launches on current X11 display
- Window appears on host machine

**Option B: Xpra Launch (Browser Preview)**
```bash
./repo.sh launch --name my_app.kit --xpra
```
- Starts Xpra on display :100 (if not running)
- Sets DISPLAY=:100
- Launches app in Xpra virtual display
- Accessible at: `http://localhost:10000`

**Option C: Remote Xpra Launch**
```bash
REMOTE=1 ./repo.sh launch --name my_app.kit --xpra
```
- Xpra binds to 0.0.0.0:10000 (all interfaces)
- Accessible from remote browsers

### 2. Xpra Startup (if --xpra flag used)

**Check if running**:
```bash
xpra list  # Check for :100
```

**Start if needed**:
```bash
xpra start :100 \
  --bind-tcp=0.0.0.0:10000 \  # or localhost if REMOTE!=1
  --html=on \
  --encodings=rgb,png,jpeg \
  --daemon=yes
```

**Set environment**:
```bash
export DISPLAY=:100
```

### 3. Execute Kit App

**Command**:
```bash
_build/linux-x86_64/release/my_app.kit.sh
```

**With environment**:
- `DISPLAY=:100` (if Xpra mode)
- `LD_LIBRARY_PATH`, `PYTHONPATH` (set by launcher script)

### 4. App Launch Monitoring

**Backend monitoring** (`xpra_manager.py`):
```python
# Launch app
self.app_process = subprocess.Popen(cmd_list, env=env, cwd=cwd)

# Wait and check if crashed
time.sleep(2)
if self.app_process.poll() is not None:
    # Crashed - capture output
    stdout, stderr = self.app_process.communicate()
    logger.error(f"App exited with code {poll_result}")
    logger.error(f"Stderr: {stderr}")
```

---

## Xpra Browser Preview

### Architecture

```
┌─────────────┐
│   Browser   │ http://hostname:10000
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Xpra HTML5 Server  │ :100 on port 10000
│  (Virtual Display)  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Kit Application   │ DISPLAY=:100
│  (my_app.kit.sh)    │
└─────────────────────┘
```

### Port Allocation

- **Display**: `:100, :101, :102, ...`
- **Ports**: `10000, 10001, 10002, ...`
- **Formula**: `port = 10000 + (display - 100)`

### REMOTE Mode Behavior

| Mode | Xpra Binds To | Accessible From |
|------|---------------|-----------------|
| Local (`REMOTE=0`) | `localhost:10000` | Same machine only |
| Remote (`REMOTE=1`) | `0.0.0.0:10000` | Any machine on network |

### Browser Access

**Local mode**:
```
http://localhost:10000
```

**Remote mode**:
```
http://your-hostname:10000
http://10.176.222.115:10000
```

---

## CLI Commands

### Complete Workflow Examples

#### Example 1: Create, Build, Run (Local)

```bash
# 1. Create from template
./repo.sh template new kit_base_editor --name my_company.editor

# 2. Build
./repo.sh build --config release

# 3. Launch locally
./repo.sh launch --name my_company.editor.kit
```

#### Example 2: Create, Build, Run with Xpra

```bash
# 1. Create
./repo.sh template new omni_usd_viewer --name my_company.viewer

# 2. Build
cd source/apps/my_company.viewer
./repo.sh build --config release

# 3. Launch in Xpra for browser preview
cd /path/to/repo
./repo.sh launch --name my_company.viewer.kit --xpra

# Browser opens to: http://localhost:10000
```

#### Example 3: Remote Development with Xpra

```bash
# Set REMOTE mode (all services bind to 0.0.0.0)
export REMOTE=1

# Start Kit Playground
make playground

# Or launch app directly with Xpra
./repo.sh launch --name my_app.kit --xpra
# Browser preview: http://your-hostname:10000
```

#### Example 4: Using App Directory Wrapper

```bash
# Navigate to app
cd source/apps/my_app

# Build from app directory
./repo.sh build --config release

# Launch from app directory
./repo.sh launch --name my_app.kit --xpra
```

---

## UI Workflow

### 1. Template Creation (UI)

**User Actions**:
1. Browse templates in left sidebar
2. Click template → shows details
3. Enter project name
4. Click "Create Project"

**Backend Flow**:
```
POST /api/v2/templates/generate
  ↓
template_api.generate_template()
  ↓
Execute: ./repo.sh template replay /tmp/xxx.toml
  ↓
_fix_application_structure()
  ↓
Create symlink if needed
  ↓
Return project info
```

**UI Updates**:
```
Console logs:
  Creating project: My App
  Template: kit_base_editor
  $ cd /path/to/repo
  $ ./repo.sh template replay /tmp/xxx.toml
  Project created successfully

Editor loads: my_app.kit file
Sidebar refreshes: shows new project
```

### 2. Build (UI)

**User Actions**:
1. Select project from sidebar
2. Click "Build" button (toolbar below editor)

**Backend Flow**:
```
POST /api/projects/build
  ↓
Validate project path
  ↓
Execute: ./repo.sh build --config release
  ↓
Stream output via WebSocket
  ↓
Return success/failure
```

**Console Output**:
```
Building my_app...
$ cd /path/to/source/apps/my_app
$ ./repo.sh build --config release
>>> Fetching all dependencies...
BUILD (RELEASE) SUCCEEDED (Took 12.5 seconds)
Build completed successfully
```

**Status Badge Updates**:
- During build: Blue "Building..." badge
- Success: Green "Built" badge with checkmark
- Failure: Red "Build Failed" badge with error icon

### 3. Launch (UI)

**User Actions**:
1. Check "Browser Preview" checkbox (checked by default)
2. Click "Run" button

**Backend Flow (with Xpra)**:
```
POST /api/projects/run (useXpra: true)
  ↓
Create Xpra session
  ↓
Start Xpra on :100 if needed
  ↓
Execute: ./repo.sh launch --name my_app.kit
  ↓
Set DISPLAY=:100 environment
  ↓
Monitor app process
  ↓
Return preview URL
```

**Console Output**:
```
Using Xpra for browser preview...
Starting Xpra session...
$ cd /path/to/source/apps/my_app
$ DISPLAY=:100 ./repo.sh launch --name my_app.kit
Application launched in Xpra
Preview available at: http://hostname:10000
Opening preview window...
```

**UI Navigation**:
- Automatically switches to "Preview" tab
- Loads Xpra URL in iframe
- Shows preview controls (zoom, refresh, fullscreen)

**Status Badge Updates**:
- During launch: Yellow "Running" badge
- Success: Green "Ran" badge with checkmark
- Failure: Red "Launch Failed" badge with error icon

---

## Path Resolution

### Platform Detection

**Function**: `get_platform_info()` in `repo_dispatcher.py`

```python
system = platform.system().lower()  # 'linux', 'windows', 'darwin'
machine = platform.machine().lower()  # 'x86_64', 'aarch64', 'arm64'

# Normalization
if system == 'darwin': platform_name = 'macos'
if machine in ['amd64', 'x86_64']: arch = 'x86_64'
if machine in ['arm64', 'aarch64']: arch = 'aarch64'

return (platform_name, arch)  # e.g., ('linux', 'x86_64')
```

### Build Directory Resolution

**Function**: `get_platform_build_dir(repo_root, config='release')`

```python
platform_name, arch = get_platform_info()
return repo_root / "_build" / f"{platform_name}-{arch}" / config
# Returns: /path/to/repo/_build/linux-x86_64/release
```

### Symlink Creation

**When**: During `_fix_application_structure()` after template creation

```python
platform_build_dir = get_platform_build_dir(repo_root, 'release')
symlink_path = platform_build_dir / "apps"
symlink_target = repo_root / "source" / "apps"

if not symlink_path.exists():
    symlink_path.symlink_to(symlink_target)
```

**Result**: `_build/linux-x86_64/release/apps` → `source/apps`

---

## Xpra Browser Preview

### Startup Sequence

1. **Check if Xpra Running**:
   ```bash
   xpra list
   ```

2. **Start Xpra (if needed)**:
   ```bash
   # Determine bind address
   BIND_HOST=$([ "$REMOTE" = "1" ] && echo "0.0.0.0" || echo "localhost")

   xpra start :100 \
     --bind-tcp=${BIND_HOST}:10000 \
     --html=on \
     --encodings=rgb,png,jpeg \
     --compression=0 \
     --opengl=yes \
     --speaker=off \
     --microphone=off \
     --daemon=yes
   ```

3. **Set Display Environment**:
   ```bash
   export DISPLAY=:100
   ```

4. **Launch Application**:
   ```bash
   _build/linux-x86_64/release/my_app.kit.sh
   ```

5. **Access in Browser**:
   ```
   http://localhost:10000        # Local mode
   http://hostname:10000         # Remote mode
   ```

### Testing Xpra Independently

**Test X server is working**:
```bash
export DISPLAY=:100
xterm  # Should appear in browser at http://localhost:10000
```

**Test Kit app with Xpra**:
```bash
# Using new --xpra flag
./repo.sh launch --name my_app.kit --xpra

# Or manually
export DISPLAY=:100
_build/linux-x86_64/release/my_app.kit.sh
```

### Xpra Session Management

**Backend** (`xpra_manager.py`):
- Creates sessions with unique IDs: `project_{name}`
- Manages multiple sessions (different display numbers)
- Monitors app processes
- Captures crash output for debugging

**Stop Xpra**:
```bash
xpra stop :100
```

---

## CLI Commands Reference

### Template Operations

```bash
# List available templates
./repo.sh template list

# Create new project
./repo.sh template new <template_name> --name <project_name>

# Replay from playback file
./repo.sh template replay /path/to/playback.toml
```

### Build Operations

```bash
# Build all (from repo root)
./repo.sh build --config release

# Build from app directory
cd source/apps/my_app
./repo.sh build --config release

# Build specific platform (cross-compile)
./repo.sh build --config release --platform windows-x86_64
```

### Launch Operations

```bash
# Launch with app selection menu
./repo.sh launch

# Launch specific app
./repo.sh launch --name my_app.kit

# Launch with Xpra (browser preview)
./repo.sh launch --name my_app.kit --xpra

# Launch with custom Xpra display
./repo.sh launch --name my_app.kit --xpra --xpra-display 101

# Launch with dev bundle enabled
./repo.sh launch --name my_app.kit --dev-bundle

# Remote Xpra launch
REMOTE=1 ./repo.sh launch --name my_app.kit --xpra
```

### Kit Playground Operations

```bash
# Start playground (local mode)
make playground

# Start playground (remote mode - accessible from other machines)
make playground REMOTE=1

# Stop playground
make playground-stop

# Build UI only
make playground-build

# Clean artifacts
make playground-clean
```

---

## Troubleshooting

### Build Issues

**Issue**: Build fails with symlink error
```
ERROR: Link '/path/_build/linux-x86_64/release/apps' cannot be created
```
**Solution**:
```bash
# Remove the real directory and let build create symlink
rm -rf _build/linux-x86_64/release/apps
rm -f _build/generated/prebuild.toml
./repo.sh build --config release
```

**Issue**: "Invalid project path" when building from UI
**Solution**: Symlink doesn't exist yet - run build once to create it, or it should be created automatically during project creation

### Launch Issues

**Issue**: `error: invalid choice: 'my_app.kit'`
**Solution**: Use --name flag
```bash
# Wrong
./repo.sh launch my_app.kit

# Correct
./repo.sh launch --name my_app.kit
```

**Issue**: App launches but no window appears
**Solution**: Check DISPLAY variable
```bash
echo $DISPLAY  # Should be set (e.g., :0, :100)
export DISPLAY=:0  # Or :100 for Xpra
```

**Issue**: App crashes immediately in Xpra
**Solution**: Check app error output (now captured in logs)
```
# Backend logs show:
App exited immediately with code 1
App stderr: [Error] File doesn't exist: /wrong/path/app.kit
```

### Xpra Issues

**Issue**: "Xpra refused to connect" in browser
**Check**:
1. Is Xpra running? `xpra list`
2. Is port accessible? `curl http://localhost:10000`
3. Is app actually running? `ps aux | grep my_app`
4. Check Xpra logs for errors

**Issue**: Xpra shows empty display
**Solution**: App crashed or didn't launch
- Check backend logs for app stderr
- Test with xterm first: `export DISPLAY=:100 && xterm`
- Verify kit file path is correct

### UI Issues

**Issue**: No CLI commands visible in console
**Status**: Under investigation - WebSocket logs may not be connecting properly
**Workaround**: Check backend logs at `/tmp/playground-backend.log`

**Issue**: Proxy errors when building
**Solution**: Restart playground to regenerate setupProxy.js
```bash
make playground-stop
make playground REMOTE=1
```

---

## Environment Variables

| Variable | Values | Purpose | Scope |
|----------|--------|---------|-------|
| `REMOTE` | `0` (default) or `1` | Controls bind address (localhost vs 0.0.0.0) | All services |
| `DISPLAY` | `:0`, `:100`, etc | X11 display for apps | Kit applications |
| `PRODUCTION` | `0` (default) or `1` | Production vs development mode | Kit Playground |

**Examples**:
```bash
# Local development
make playground

# Remote development
REMOTE=1 make playground

# Production mode
PRODUCTION=1 make playground

# Remote production
REMOTE=1 PRODUCTION=1 make playground
```

---

## API Endpoints

### Template Endpoints

- `GET /api/v2/templates` - List all templates
- `POST /api/v2/templates/generate` - Create new project
- `GET /api/v2/templates/{id}/icon` - Get template icon

### Project Endpoints

- `GET /api/projects/discover?path=<path>` - Discover projects
- `POST /api/projects/build` - Build project
- `POST /api/projects/run` - Launch project
- `POST /api/projects/stop` - Stop running project
- `POST /api/projects/delete` - Delete project

### Xpra Endpoints

- `GET /api/xpra/check` - Check if Xpra installed
- `GET /api/xpra/sessions` - List active Xpra sessions

### Configuration Endpoints

- `GET /api/config/paths` - Get default template/project paths

---

## Best Practices

### 1. Always Use Wrappers

**Good**:
```bash
cd source/apps/my_app
./repo.sh build
```

**Avoid**:
```bash
# Don't run from wrong directory
cd /some/other/place
/path/to/repo.sh build  # May have wrong context
```

### 2. Check Build Before Launch

```bash
# Verify executable exists
ls _build/linux-x86_64/release/my_app.kit.sh

# If missing, build first
./repo.sh build --config release
```

### 3. Test Xpra with xterm First

```bash
export DISPLAY=:100
xterm
# Should appear in browser at http://localhost:10000
```

### 4. Use CLI for Debugging

When UI operations fail, reproduce with CLI:
```bash
# Copy command from UI console (it shows the exact command)
$ cd /path/to/app
$ ./repo.sh build --config release

# Run it directly to see full output
```

### 5. Clean Builds When Paths Change

```bash
# After path structure changes
make clean
rm -f _build/generated/prebuild.toml
./repo.sh build --config release
```

---

## Recent Improvements (2025-10-11)

### Path Structure Alignment
- ✅ Apps now use symlinked platform-specific paths
- ✅ Compatible with build system design
- ✅ Multi-platform support (Windows/Linux/Mac/ARM)

### CLI Command Logging
- ✅ All UI operations show exact CLI commands
- ✅ Users can copy-paste to reproduce from terminal
- ✅ Critical for debugging and learning

### Xpra Enhancements
- ✅ Added --xpra flag to repo.sh launch
- ✅ Automatic Xpra startup if not running
- ✅ Error diagnostics (captures crash output)
- ✅ REMOTE variable support

### Cross-Platform Parity
- ✅ dev.bat (Windows) now matches dev.sh (Linux/Mac)
- ✅ REMOTE variable support on all platforms
- ✅ Dynamic port allocation
- ✅ Intelligent proxy routing

### UI Improvements
- ✅ Toolbar moved below editor
- ✅ Browser Preview checked by default
- ✅ Hot-reload notifications (frontend & backend)
- ✅ Project status badges (Build/Launch states)

---

## File Locations Quick Reference

| What | Where |
|------|-------|
| App source | `source/apps/{name}/{name}.kit` |
| App wrapper | `source/apps/{name}/repo.sh` |
| Build symlink | `_build/{platform}-{arch}/{config}/apps` → `source/apps` |
| Executables | `_build/{platform}-{arch}/{config}/{name}.kit.sh` |
| Extensions | `source/extensions/{name}/` |
| Templates | `templates/apps/{template_name}/` |
| Build tools | `tools/repoman/` |
| Backend | `kit_playground/backend/` |
| Frontend | `kit_playground/ui/src/` |

---

## See Also

- `CODE_REVIEW_SUMMARY.md` - Comprehensive code review
- `kit_playground/README.md` - Kit Playground overview
- `XPRA_SETUP.md` - Xpra installation guide
- `repo.toml` - Build system configuration
