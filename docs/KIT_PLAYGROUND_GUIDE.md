# Kit Playground - Visual Development Guide

**Kit Playground** is a web-based visual development environment for creating, building, and launching Omniverse applications. This guide covers all features and workflows in detail.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Interface Tour](#interface-tour)
- [Workflows](#workflows)
- [Features](#features)
- [Troubleshooting](#troubleshooting)

---

## Overview

Kit Playground provides a modern, browser-based interface for application development with:

- **Visual Template Browser** - Browse and filter templates with icons
- **Live Code Editor** - Edit `.kit` files with real-time syntax highlighting
- **Streaming Build Output** - Watch builds progress in real-time
- **Panel Management** - Dynamic workspace with multiple simultaneous views
- **Integrated Logs** - All command output in one place

**Access:** `http://localhost:3000` (after starting with `./dev.sh`)

---

## Getting Started

### Starting Kit Playground

**Option 1: Dedicated Script**
```bash
cd kit_playground
./dev.sh          # Linux/Mac
dev.bat           # Windows
```

**Option 2: From Project Root**
```bash
make playground
```

### What Happens on Startup

1. **Backend API starts** on port 5000
   - Discovers templates
   - Scans existing projects
   - Initializes WebSocket server

2. **Frontend UI starts** on port 3000
   - Compiles React application
   - Connects to backend
   - Opens browser automatically

3. **Health Check**
   - Waits for backend readiness
   - Verifies WebSocket connection
   - Displays status messages

**Startup time:** 10-15 seconds

### Stopping Kit Playground

Press `Ctrl+C` in the terminal where you started `./dev.sh`

This will:
- Stop both backend and frontend services
- Clean up temporary files
- Close WebSocket connections

---

## Interface Tour

### Main Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Kit Playground Header                             [v2.0]   │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│  Templates  │     Active Panels (Editor, Build, etc.)      │
│   Sidebar   │     [Scrollable with carousel navigation]    │
│             │                                               │
│   Browse    │     ┌──────────────────────────────────┐    │
│   Search    │     │      Editor Panel                 │    │
│   Filter    │     │  [Save] [Discard] [Build]        │    │
│             │     │                                   │    │
│             │     │  # Configuration file content     │    │
│             │     │  ...                              │    │
│             │     └──────────────────────────────────┘    │
│             │                                               │
├─────────────┴───────────────────────────────────────────────┤
│ Output Panel (Collapsible)                                 │
│ [Filter: All ▼]  [Clear]                        [Collapse] │
│ • 10:23:15  [build]  Building application...               │
│ • 10:23:16  [build]  Fetching dependencies...              │
└─────────────────────────────────────────────────────────────┘
```

### Left Sidebar - Template Browser

**Expandable Sections:**
- **Templates** - Top-level container
  - **All Templates** - View all available templates
  - **Applications** - Full application templates
  - **Extensions** - Extension templates
  - **Services** - Service templates

**Template Card Display:**
- **Icon** - Visual identifier (from template metadata)
- **Name** - Template identifier
- **Description** - Brief description
- **Category Badge** - Type indicator (App, Extension, etc.)

**Search Bar:**
- Type to filter templates by name or description
- Real-time filtering
- Case-insensitive matching

### Center Area - Panel System

**Dynamic Panels** that slide in from left to right:

1. **Template Grid Panel**
   - Shows all templates in a responsive grid
   - Cards adjust to screen size
   - Click a card to view details

2. **Template Detail Panel**
   - Template information and documentation
   - "Create Project" button
   - "Back to Templates" navigation

3. **Project Configuration Panel**
   - Form for project creation
   - Auto-generated default values
   - Validation feedback

4. **Code Editor Panel**
   - Syntax-highlighted `.kit` file editor
   - Save/Discard/Build actions
   - File path display
   - Unsaved changes indicator (yellow dot)

5. **Build Output Panel**
   - Real-time streaming logs
   - Build status indicator
   - Launch button (appears after successful build)
   - Clear logs button

**Panel Navigation:**
- **Carousel System** - Panels automatically scroll when screen is full
- **Navigation Arrows** - Green arrows appear on left/right when panels are hidden
- **Close Button** - X button in top-right of each panel
- **Active Panel** - Highlighted with NVIDIA green accent

### Bottom Panel - Global Output

**Persistent log panel** showing all system activity:

- **Collapsible** - Click to expand/collapse
- **Resizable** - Drag top edge to resize
- **Filterable** - Filter by log level (All, Info, Warning, Error)
- **Auto-scroll** - Automatically scrolls to latest logs
- **Timestamps** - Each log entry has timestamp
- **Color-coded** - Different colors for log levels:
  - 🔵 Blue - Info
  - 🟡 Yellow - Warning
  - 🔴 Red - Error
  - 🟢 Green - Success

---

## Workflows

### Complete Application Development Workflow

**Step-by-step process from template to running application:**

#### 1. Browse Templates

1. **Open Kit Playground** in your browser
2. **Click "Templates"** in the left sidebar
3. **Click "Applications"** to expand
4. **Scan the template cards** - each shows:
   - Icon representing the template
   - Template name
   - Brief description

#### 2. Select Template

1. **Click a template card** (e.g., "Kit Base Editor")
2. **Template Detail panel opens** showing:
   - Detailed description
   - Features list
   - Use cases
   - Getting started guide
3. **Read the documentation** to understand what you're creating

#### 3. Create Project

1. **Click "Create Project"** button
2. **Project Configuration panel opens** with auto-filled fields:
   - **Project Name**: `happy_falcon_1` (randomly generated)
   - **Display Name**: `Happy Falcon` (friendly name)
   - **Version**: `1.0.0`
   - **Options**: Template-specific settings
3. **Customize** (optional):
   - Change project name (alphanumeric and underscores only)
   - Update display name (shown in UI)
   - Toggle options like "Enable Streaming"
4. **Click "Create Project"** (green button)
5. **Watch progress:**
   - Output panel shows commands being executed
   - Template generation logs stream
   - Success message appears when complete
6. **Automatic transition:**
   - Project Config panel closes
   - Template Detail panel closes
   - Editor panel opens with your `.kit` file

#### 4. Review Generated Code

**Editor panel displays** your application's configuration:

```toml
# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material...

[package]
title = "Happy Falcon"
version = "1.0.0"
description = "A Kit-based application"

[dependencies]
# Core Kit extensions
"omni.kit.uiapp" = {}
"omni.kit.renderer.core" = {}
# ... more extensions ...

[settings]
# Application settings
app.window.title = "Happy Falcon"
app.window.width = 1920
app.window.height = 1080
# ... more settings ...
```

**Understanding the file:**
- **[package]** - Application metadata
- **[dependencies]** - Extensions to load
- **[settings]** - Configuration options

#### 5. Edit Configuration (Optional)

**Make changes directly in the editor:**

1. **Click in the textarea** to begin editing
2. **Add an extension:**
   ```toml
   [dependencies]
   "omni.kit.window.console" = {}  # Add console window
   ```
3. **Change window size:**
   ```toml
   [settings.app.window]
   width = 2560
   height = 1440
   ```
4. **Notice the unsaved indicator:**
   - Yellow dot appears next to filename
   - "Unsaved changes" text shows at bottom

#### 6. Save Changes

**Click the green "Save" button** above the editor:
- File writes to disk
- Yellow indicator disappears
- Success message in output panel
- Changes are preserved

**OR discard changes:**
- Click "Discard" button
- File reverts to last saved version
- Yellow indicator disappears

#### 7. Build Application

**Click the blue "Build" button** above the editor:

1. **Build Output panel opens** automatically
2. **Status changes** to "Running" with spinner
3. **Logs stream in real-time:**
   ```
   Building happy_falcon...
   $ cd /home/user/kit-app-template/source/apps/happy_falcon
   $ ./repo.sh build --config release
   >>> Fetching all dependencies.
   [1/35] Downloading omni.kit.uiapp...
   [2/35] Downloading omni.kit.renderer.core...
   ... progress continues ...
   >>> Stage Files Step. Doing file copy and folder linking.
   >>> VS Code setup. Writing: .vscode/settings.json
   +++ Building release +++
   Build arguments: ['make', '__directory=...']
   Running action 'gmake2'...
   Done (171ms).
   BUILD (RELEASE) SUCCEEDED (Took 17.88 seconds)
   ```

4. **Watch for completion:**
   - Green checkmark replaces spinner
   - "BUILD (RELEASE) SUCCEEDED" message
   - **Blue "Launch" button appears**

**Build failures:**
- Red X indicator
- Error messages in logs (in red)
- "Retry" button appears
- Review logs to identify issue

#### 8. Launch Application

**Click the blue "Launch" button:**

1. **Launch Output panel opens** (or reuses Build Output panel)
2. **Application startup logs stream:**
   ```
   Launching happy_falcon...
   $ cd /home/user/kit-app-template/source/apps/happy_falcon
   $ ./repo.sh launch --config release
   [Info] [omni.kit.app] Starting Kit application...
   [Info] [omni.kit.ui] Initializing UI system...
   [Info] [omni.kit.renderer.core] Renderer initialized
   [Info] [omni.kit.window.title] Window created: "Happy Falcon"
   ```

3. **Application window opens** (separate from browser)
4. **Monitor logs** for any runtime errors or warnings

**To stop:**
- Close the application window
- OR click "Cancel" in the Launch Output panel

---

## Features

### Template Browser

**Smart Search:**
- Type to filter instantly
- Searches name AND description
- Results update as you type
- Clear button to reset

**Category Organization:**
- **Applications**: Full Kit applications (editors, viewers, services)
- **Extensions**: Reusable functionality modules
- **Components**: Smaller building blocks

**Template Metadata:**
- **Name**: Technical identifier
- **Display Name**: User-friendly name
- **Description**: What it does
- **Icon**: Visual representation
- **Documentation**: Inline help
- **Features**: Capability list
- **Use Cases**: When to use this template

### Code Editor

**Editing Features:**
- **Syntax Highlighting** for TOML format
- **Monospace Font** for code clarity
- **Line Numbers** (visual reference)
- **Auto-indentation** maintained
- **Large File Support** (1000+ lines)

**File Operations:**
- **Auto-load** - File loads when panel opens
- **Save** - Write changes to disk (Ctrl+S shortcut planned)
- **Discard** - Revert to last saved version
- **Dirty Tracking** - Yellow indicator for unsaved changes

**Integrated Actions:**
- **Build Button** - Trigger build without leaving editor
- **Direct File Path** - See exactly which file you're editing
- **Error Display** - File load errors shown inline

### Build System

**Real-Time Streaming:**
- **PTY-based Output** - True unbuffered streaming
- **Line-by-line Updates** - See progress as it happens
- **Dependency Downloads** - Watch package resolution
- **Compilation Progress** - Track build stages
- **Immediate Feedback** - No delayed buffering

**Build Detection:**
- **Success Detection** - Looks for "BUILD (RELEASE) SUCCEEDED"
- **Failure Detection** - Looks for "BUILD (RELEASE) FAILED"
- **Exit Code Display** - Shows actual return code
- **Status Updates** - Icon changes: spinner → checkmark/X

**Build Controls:**
- **Start** - Begin new build
- **Cancel** - Stop running build (if supported)
- **Retry** - Re-run after failure
- **Clear Logs** - Reset output for clean view

### Launch Integration

**Post-Build Workflow:**
- **Auto-enable Launch** - Button appears after successful build
- **Separate Panel** - Launch logs in dedicated panel
- **Status Tracking** - Monitor application startup
- **Error Capture** - Runtime errors logged

**Launch Controls:**
- **Launch Button** - Start application
- **Cancel** - Attempt to stop (graceful shutdown)
- **Retry** - Restart application
- **Clear Logs** - Reset launch output

### Panel Carousel System

**Dynamic Panel Management:**
- **Automatic Scrolling** - Panels slide left/right when screen fills
- **120% Capacity** - Allows slight overflow before hiding panels
- **Retired Panels** - Hidden panels stored in memory
- **Smooth Animations** - Transitions ease in/out over 300ms

**Navigation Controls:**
- **Left Arrow** - Show previously hidden panels
  - Green button on left edge
  - Only visible when panels are retired
- **Right Arrow** - Hide leftmost panels
  - Green button on right edge
  - Only visible when 3+ panels open
- **Hover Tooltips** - Explain navigation direction

**Panel Behavior:**
- **Replace Mode** - Template panels replace each other
- **Accumulate Mode** - Editor and build panels stack
- **Active Highlight** - Current panel has green accent
- **Close Button** - X to remove individual panels

### Global Output Panel

**Persistent Log Viewer:**
- **Always Visible** - Spans bottom of screen
- **All Commands** - Every shell command logged
- **Stdout + Stderr** - Both output streams captured
- **Real-time Updates** - WebSocket-based streaming

**Panel Controls:**
- **Collapse/Expand** - Click header to toggle
- **Resize** - Drag top edge to adjust height
- **Clear** - Remove all logs
- **Auto-scroll Toggle** - Follow latest output or stay fixed

**Log Filtering:**
- **Level Dropdown** - All, Info, Warning, Error
- **Color Coding** - Visual differentiation
- **Timestamps** - Precise timing information
- **Source Labels** - [build], [create], [launch], etc.

---

## Troubleshooting

### Cannot Access UI

**Problem:** Browser shows "Connection refused" at `localhost:3000`

**Diagnosis:**
```bash
# Check if frontend is running
curl http://localhost:3000
# Check if backend is running
curl http://localhost:5000/api/health
```

**Solutions:**
1. **Restart services:**
   ```bash
   cd kit_playground
   ./dev.sh
   ```

2. **Check port conflicts:**
   ```bash
   # See what's using port 3000
   lsof -i :3000
   # See what's using port 5000
   lsof -i :5000
   ```

3. **Clear caches:**
   ```bash
   rm -rf ui/node_modules/.vite
   ./dev.sh
   ```

### Build Output Not Streaming

**Problem:** Build starts but no output appears

**Diagnosis:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Look for WebSocket connection issues

**Solutions:**

1. **Hard refresh browser:**
   - Chrome/Edge: `Ctrl+Shift+R`
   - Firefox: `Ctrl+Shift+Del` → Clear cache → Refresh

2. **Verify WebSocket:**
   - Check backend logs: `tail -f /tmp/kit-playground-backend.log`
   - Look for "WebSocket client connected"

3. **Restart backend:**
   ```bash
   # In a new terminal
   cd kit_playground
   pkill -f "python.*web_server"
   cd backend
   python3 web_server.py --port 5000 --host 0.0.0.0 > /tmp/kit-playground-backend.log 2>&1 &
   ```

### Editor Not Saving

**Problem:** Click "Save" but changes don't persist

**Diagnosis:**
- Check output panel for error messages
- Look for permission issues
- Verify file path is correct

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la source/apps/your_project/your_project.kit
   ```

2. **Verify you're editing the right file:**
   - Look at the file path shown in editor panel
   - Ensure it matches your project location

3. **Check backend logs:**
   ```bash
   tail -50 /tmp/kit-playground-backend.log | grep -i error
   ```

4. **Manual save as fallback:**
   ```bash
   cd source/apps/your_project
   nano your_project.kit  # Copy content from UI and paste
   ```

### Launch Button Not Appearing

**Problem:** Build succeeds but Launch button doesn't show

**Diagnosis:**
- Check if build actually succeeded
- Look for "BUILD (RELEASE) SUCCEEDED" in logs

**Solutions:**

1. **Verify build success:**
   - Scroll to bottom of Build Output
   - Look for green "BUILD (RELEASE) SUCCEEDED"
   - Check exit code is 0

2. **Refresh the panel:**
   - Close Build Output panel (click X)
   - Click "Build" again
   - Watch for success message

3. **Check build artifacts:**
   ```bash
   ls _build/linux-x86_64/release/  # OR windows-x86_64
   ```
   Should contain build outputs

4. **Manual launch:**
   ```bash
   cd source/apps/your_project
   ./repo.sh launch --config release
   ```

### Panel Navigation Issues

**Problem:** Panels appear out of order or navigation breaks

**Diagnosis:**
- Open browser DevTools Console
- Look for panel management errors

**Solutions:**

1. **Reset panels:**
   - Close all panels (click X on each)
   - Start workflow fresh from Templates

2. **Clear browser storage:**
   - DevTools → Application → Storage → Clear site data
   - Refresh page

3. **Restart Playground:**
   ```bash
   ./dev.sh  # Press Ctrl+C first if running
   ```

### WebSocket Disconnections

**Problem:** "WebSocket already connected" or repeated connection messages

**Symptoms:**
- Multiple connection messages in logs
- Duplicate output
- Stale data

**Solutions:**

1. **Single browser tab:**
   - Close all tabs with Playground
   - Open only ONE new tab
   - Navigate to `http://localhost:3000`

2. **Restart services:**
   ```bash
   cd kit_playground
   ./dev.sh  # Ctrl+C to stop first
   ```

3. **Check for zombie processes:**
   ```bash
   ps aux | grep "web_server\|npm.*dev" | grep -v grep
   # Kill any zombies:
   pkill -f "python.*web_server"
   pkill -f "npm.*dev"
   ```

---

## Performance Tips

### For Faster Builds

1. **Close unnecessary panels** - Reduces UI overhead
2. **Use release builds** - Faster than debug
3. **Disable streaming** if not needed - Less I/O
4. **Build on SSD** - Much faster than HDD

### For Smoother UI

1. **Use Chrome or Edge** - Best WebSocket support
2. **Close DevTools** when not debugging
3. **Limit open panels** to 3-4 simultaneously
4. **Clear logs periodically** - Reduces DOM size

---

## Keyboard Shortcuts

**Current:**
- `Ctrl+C` - Stop services (in terminal)

**Planned:**
- `Ctrl+S` - Save file in editor
- `Ctrl+B` - Build current project
- `Ctrl+L` - Launch built project
- `Ctrl+\`` - Toggle output panel

---

## API Integration

Kit Playground uses a REST API + WebSocket backend.

**REST Endpoints:**
- `GET /api/health` - Service health check
- `GET /api/templates` - List available templates
- `POST /api/templates/create` - Create new project
- `POST /api/projects/build` - Build a project
- `POST /api/projects/launch` - Launch a project
- `GET /api/filesystem/read` - Read file contents
- `POST /api/filesystem/write` - Write file contents

**WebSocket Events:**
- `log` - Command output (stdout/stderr)
- `job_status` - Job state changes
- `job_progress` - Progress updates
- `connected` - Connection established

**For automation**, you can call these APIs directly:
```bash
# Create project via API
curl -X POST http://localhost:5000/api/templates/create \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_base_editor",
    "name": "my_app",
    "displayName": "My App",
    "version": "1.0.0"
  }'
```

---

## Contributing to Playground

**Frontend** (React + TypeScript + Tailwind CSS):
```bash
cd kit_playground/ui
npm install
npm run dev  # Development mode with hot reload
```

**Backend** (Python + Flask + SocketIO):
```bash
cd kit_playground/backend
python3 -m pip install -r requirements.txt
python3 web_server.py --port 5000 --host 0.0.0.0
```

**Tests:**
```bash
# Backend tests
cd kit_playground
pytest tests/

# Frontend tests
cd ui
npm test
```

---

## Next Steps

- **Explore Advanced Features** - Try per-app dependencies
- **Create Custom Templates** - Package your own templates
- **Integrate Tools** - Connect with CI/CD pipelines
- **Share Feedback** - Report issues or suggest features

**Happy Building in Kit Playground! 🎨**
