# Kit App Template - User Guide

Welcome to the Kit App Template User Guide. This guide will teach you how to create, build, and launch NVIDIA Omniverse applications using both the visual **Kit Playground** interface and the command-line tools.

## Table of Contents

- [Getting Started](#getting-started)
- [Example 1: Creating Your First Application](#example-1-creating-your-first-application)
- [Example 2: Building Your Application](#example-2-building-your-application)
- [Example 3: Launching Your Application](#example-3-launching-your-application)
- [Example 4: Editing Configuration Files](#example-4-editing-configuration-files)
- [Example 5: Working with Extensions](#example-5-working-with-extensions)
- [Example 6: Creating Standalone Projects](#example-6-creating-standalone-projects)
- [Advanced Workflows](#advanced-workflows)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

The Kit App Template provides two ways to work with Omniverse applications:

1. **Kit Playground (UI)** - A visual development environment with real-time feedback
2. **Command Line (CLI)** - Direct terminal access for automation and scripting

### Prerequisites

Before you begin, ensure you have:
- **Operating System**: Windows 10/11 or Linux (Ubuntu 22.04+)
- **GPU**: NVIDIA RTX-capable GPU (RTX 3070 or better recommended)
- **Driver**: NVIDIA driver version 537.58 or newer
- **Python**: Version 3.8 or newer
- **Git**: With Git LFS enabled

### Initial Setup

**Clone the repository:**
```bash
git clone <repository-url>
cd kit-app-template
```

**Run the setup (automatically installs dependencies):**
```bash
# Linux/Mac
./repo.sh

# Windows
repo.bat
```

This command will:
- Download the Omniverse Kit SDK
- Install required Python packages
- Set up the development environment

---

## Example 1: Creating Your First Application

Let's create a simple 3D editor application called `my_editor`.

### Using Kit Playground (UI)

1. **Start Kit Playground:**
   ```bash
   cd kit_playground
   ./dev.sh  # Linux/Mac
   # OR
   dev.bat   # Windows
   ```

2. **Open your browser** to `http://localhost:3000`

3. **Browse templates** in the left sidebar
   - Click "Applications" to expand the applications category
   - You'll see template options like "Kit Base Editor"

4. **Select a template**
   - Click on "Kit Base Editor" card
   - A detail panel opens with template information

5. **Create your project**
   - Click "Create Project" button
   - The form auto-fills with a generated name (e.g., `happy_falcon_1`)
   - Change the **Project Name** to `my_editor`
   - Change the **Display Name** to `My Editor`
   - Click **"Create Project"** button

6. **Wait for creation**
   - A progress panel shows the creation process
   - Output logs stream in real-time at the bottom
   - Green checkmark appears when complete

**Result:** Your application is created at `source/apps/my_editor/`

### Using Command Line (CLI)

```bash
# Create application from template
./repo.sh template new \
  --template kit_base_editor \
  --name my_editor \
  --display-name "My Editor" \
  --version 1.0.0
```

**Result:** Your application is created at `source/apps/my_editor/`

### What Was Created?

Your new application includes:
```
source/apps/my_editor/
├── my_editor.kit          # Main configuration file
├── config/                # Application settings
├── data/                  # Icons and assets
├── docs/                  # Documentation
└── README.md              # Project-specific readme
```

The `.kit` file is the heart of your application - it defines:
- Window settings (title, size)
- Extensions to load
- UI layout
- Application behavior

---

## Example 2: Building Your Application

Building compiles your application and resolves all dependencies.

### Using Kit Playground (UI)

1. **Open the editor panel** (if you just created the project, it's already open)
   - The editor shows your `my_editor.kit` file

2. **Click the "Build" button** (blue button above the editor)

3. **Watch the build progress** in the Build Output panel
   - Build commands appear in green
   - Dependency downloads stream in real-time
   - Compilation progress updates continuously
   - "BUILD (RELEASE) SUCCEEDED" indicates success

4. **When complete:**
   - A blue "Launch" button appears
   - Build artifacts are in `_build/linux-x86_64/release/` (or `windows-x86_64` on Windows)

**Build time:** First build may take 5-10 minutes as dependencies download

### Using Command Line (CLI)

**Navigate to your project:**
```bash
cd source/apps/my_editor
```

**Build the application:**
```bash
# Build release configuration (optimized)
./repo.sh build --config release

# OR build debug configuration (with debugging symbols)
./repo.sh build --config debug
```

**Monitor build progress:**
- Dependency resolution and download
- Extension compilation
- Asset packaging
- Final linking

**Result:** Build artifacts are in `_build/linux-x86_64/release/` (or `windows-x86_64/release` on Windows)

### Understanding Build Output

The build process:
1. **Resolves dependencies** - Downloads required Omniverse extensions
2. **Configures extensions** - Sets up Python environments
3. **Compiles code** - Builds C++ extensions if present
4. **Packages assets** - Copies icons, data files, and resources
5. **Creates executable** - Generates the final application binary

---

## Example 3: Launching Your Application

Once built, you can launch your application.

### Using Kit Playground (UI)

1. **After a successful build**, click the **"Launch"** button (blue, appears in Build Output panel)

2. **Monitor the launch process**
   - A new "Launch Output" panel opens
   - Application startup logs stream in real-time
   - Window initialization messages appear

3. **Application window opens** in a new display
   - Your application runs with the configured UI
   - Check console for any runtime warnings or errors

**Note:** Launch integration with windowed display is still in development. Currently opens logs for monitoring.

### Using Command Line (CLI)

**From your project directory:**
```bash
cd source/apps/my_editor

# Launch the built application
./repo.sh launch --config release

# OR launch with additional logging
./repo.sh launch --config release --verbose
```

**Your application starts** with:
- The configured window title ("My Editor")
- Extensions loaded as specified in the `.kit` file
- UI panels and menus as defined

**To stop the application:**
- Close the window, or
- Press `Ctrl+C` in the terminal

### Launch Options

**Common flags:**
```bash
# Launch in debug mode with full logging
./repo.sh launch --config debug --verbose

# Launch with a specific window size
./repo.sh launch --config release --width 1920 --height 1080

# Launch and immediately load a USD file
./repo.sh launch --config release --open /path/to/scene.usd
```

---

## Example 4: Editing Configuration Files

The `.kit` file controls your application's behavior.

### Using Kit Playground (UI)

1. **The editor panel** shows your `.kit` file after project creation
   - If closed, reopen by clicking on your project in the sidebar

2. **Edit the file** directly in the textarea
   - Syntax highlighting helps identify sections
   - Changes are marked with a yellow dot indicator

3. **Save your changes:**
   - Click the green **"Save"** button above the editor
   - The yellow indicator disappears when saved

4. **Discard changes** (if needed):
   - Click the **"Discard"** button
   - Reverts to the last saved version

5. **Rebuild after changes:**
   - Click **"Build"** to apply your modifications
   - Watch the build logs to verify success

### Using Command Line (CLI)

**Open the file in your editor:**
```bash
cd source/apps/my_editor
nano my_editor.kit  # Or use your preferred editor: vim, code, etc.
```

**Example modification - Change window title:**

Find this section:
```toml
[package]
title = "My Editor"
version = "1.0.0"
```

Change to:
```toml
[package]
title = "My Advanced Editor"
version = "1.1.0"
```

**Save and rebuild:**
```bash
./repo.sh build --config release
```

### Common Configuration Changes

#### Add an Extension

Add this to the `[dependencies]` section:
```toml
[dependencies]
"omni.kit.viewport.window" = {}    # Adds 3D viewport
"omni.kit.property.window" = {}    # Adds property editor
```

#### Change Window Settings

Modify the `[settings]` section:
```toml
[settings.app.window]
title = "My Custom Title"
width = 1920
height = 1080
```

#### Enable Features

```toml
[settings.exts."omni.kit.window.console"]
enabled = true  # Shows console window at startup
```

**After any changes:** Rebuild your application to apply them.

---

## Example 5: Working with Extensions

Extensions add functionality to your application. Let's create and add a custom extension.

### Creating an Extension (CLI)

```bash
# From repository root
./repo.sh template new \
  --template basic_python_extension \
  --name my_custom_tool \
  --display-name "My Custom Tool" \
  --version 1.0.0
```

**Result:** Extension created at `source/extensions/my.custom.tool/`

Extension structure:
```
source/extensions/my.custom.tool/
├── config/
│   └── extension.toml      # Extension metadata
├── docs/                   # Extension documentation
├── my/
│   └── custom/
│       └── tool/
│           ├── __init__.py # Extension entry point
│           └── ui.py       # UI components
└── README.md
```

### Adding Extension to Your Application

#### Using Kit Playground (UI)

1. **Open your application's `.kit` file** in the editor

2. **Add the extension** to the `[dependencies]` section:
   ```toml
   [dependencies]
   "my.custom.tool" = {}
   ```

3. **Click "Save"** then **"Build"**

4. **Launch** to see your extension loaded

#### Using Command Line (CLI)

1. **Edit the `.kit` file:**
   ```bash
   cd source/apps/my_editor
   nano my_editor.kit
   ```

2. **Add the extension:**
   ```toml
   [dependencies]
   "my.custom.tool" = {}
   ```

3. **Save, build, and launch:**
   ```bash
   ./repo.sh build --config release
   ./repo.sh launch --config release
   ```

### Developing the Extension

**Edit extension code:**
```bash
cd source/extensions/my.custom.tool/my/custom/tool
nano ui.py  # Or use your preferred editor
```

**Example - Add a simple UI window:**
```python
import omni.ui as ui

class MyCustomToolWindow:
    def __init__(self):
        self._window = ui.Window("My Custom Tool", width=300, height=200)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Hello from my custom tool!")
                ui.Button("Click Me", clicked_fn=self._on_click)

    def _on_click(self):
        print("Button clicked!")
```

**Hot reload:** Many changes can be seen without restarting:
- Edit your Python code
- Save the file
- The extension automatically reloads in the running application

---

## Example 6: Creating Standalone Projects

Standalone projects are self-contained and can be distributed independently.

### Using Kit Playground (UI)

1. **Create a new project** from a template (as in Example 1)

2. **In the project creation form:**
   - Check the **"Create as standalone project"** checkbox
   - Choose an **output directory** outside the repository

3. **Click "Create Project"**

4. **Result:** A complete, standalone repository is created with:
   - Its own `repo.sh` / `repo.bat` scripts
   - Independent dependency management
   - Full source code and build system

### Using Command Line (CLI)

```bash
# Create standalone project in a specific directory
./repo.sh template new \
  --template kit_base_editor \
  --name my_standalone_app \
  --display-name "My Standalone App" \
  --version 1.0.0 \
  --standalone \
  --output-dir /path/to/my_standalone_app
```

### Working with Standalone Projects

**Navigate to the standalone project:**
```bash
cd /path/to/my_standalone_app
```

**Build and launch** (same commands as before):
```bash
# Build
./repo.sh build --config release

# Launch
./repo.sh launch --config release
```

**Distribute your project:**
- Zip the entire directory
- Share with others - they only need to run `./repo.sh` to get started
- No parent repository needed

---

## Advanced Workflows

### Per-Application Dependencies

Control extension versions per application instead of globally:

**Enable per-app dependencies:**
```bash
./repo.sh template new \
  --template kit_base_editor \
  --name my_app \
  --per-app-deps
```

**Benefits:**
- Each application has isolated dependencies
- Prevents version conflicts
- Easier to maintain multiple projects

**In the `.kit` file:**
```toml
[dependencies]
# Pin specific versions
"omni.kit.window.viewport" = { version = "2.3.1" }
"omni.kit.property.window" = { version = "1.5.0" }
```

### Building Multiple Applications

**Build all applications in the repository:**
```bash
./repo.sh build --all --config release
```

**Build specific applications:**
```bash
./repo.sh build --app my_editor --app my_viewer --config release
```

### Managing Application Registry

**List all discovered applications:**
```bash
./repo.sh list
```

**Register an application manually:**
```bash
./repo.sh register --path source/apps/my_editor
```

**Unregister an application:**
```bash
./repo.sh unregister --name my_editor
```

### Package and Distribution

**Package your application for distribution:**
```bash
cd source/apps/my_editor
./repo.sh package --config release
```

This creates a distributable package in `_packages/` containing:
- Application executable
- Required extensions
- Assets and data
- Runtime dependencies

---

## Troubleshooting

### Build Failures

**Problem:** Build fails with dependency errors

**Solution (UI):**
1. Check the Build Output logs for specific error messages
2. Look for "Failed to download" or "Dependency conflict"  messages
3. Try clicking "Retry" after fixing network issues

**Solution (CLI):**
```bash
# Clear the build cache
rm -rf _build

# Clean dependencies
./repo.sh tools clean

# Rebuild
./repo.sh build --config release
```

### Launch Issues

**Problem:** Application won't start

**Solution:**
1. Verify the build completed successfully
2. Check for error messages in launch logs
3. Try debug mode for more verbose output:
   ```bash
   ./repo.sh launch --config debug --verbose
   ```

### Kit Playground Issues

**Problem:** Playground UI won't load

**Solution:**
```bash
# Stop all services
cd kit_playground
./dev.sh stop

# Clear caches
rm -rf ui/node_modules/.vite

# Restart
./dev.sh
```

**Problem:** Build output not streaming

**Solution:**
- Refresh the browser page (Ctrl+Shift+R)
- Check browser console for WebSocket errors
- Verify backend is running: `curl http://localhost:5000/api/health`

### Extension Development

**Problem:** Extension changes not appearing

**Solution (Hot Reload):**
1. Make sure you saved the file
2. In the running application, open the console (`)
3. Type: `omni.kit.app.get_app().reload_extension("my.custom.tool")`

**Solution (Full Rebuild):**
```bash
./repo.sh build --config release
./repo.sh launch --config release
```

### Performance Issues

**Problem:** Application runs slowly

**Solutions:**
- Build in release mode (not debug)
- Disable unnecessary extensions
- Reduce viewport resolution
- Update GPU drivers

---

## UI Panel Guide

### Kit Playground Interface

When you open Kit Playground (`http://localhost:3000`), you'll see:

**Left Sidebar - Template Browser:**
- Browse available templates by category
- Search for specific templates
- View template details

**Center Area - Panels:**
- **Editor Panel:** Edit `.kit` configuration files
  - Save/Discard/Build buttons above editor
  - Syntax highlighting for TOML format
  - Unsaved changes indicator

- **Build Output Panel:** Real-time build logs
  - Shows commands being executed
  - Dependency download progress
  - Build success/failure status
  - Launch button appears after successful build

- **Output Panel (Bottom):** Global command output
  - All terminal commands logged here
  - Filter by log level
  - Collapsible and resizable

**Panel Navigation:**
- **Carousel System:** Panels scroll left/right when screen fills
- **Green Navigation Arrows:** Click to show hidden panels
- **Close Button (X):** Close individual panels
- **Active Panel:** Highlighted in NVIDIA green

---

## CLI Command Reference

### Template Commands

```bash
# List available templates
./repo.sh template list

# Create from template
./repo.sh template new --template <name> --name <app_name>

# Template with options
./repo.sh template new \
  --template kit_base_editor \
  --name my_app \
  --display-name "My Application" \
  --version 1.0.0 \
  --per-app-deps \
  --standalone \
  --output-dir /path/to/output
```

### Build Commands

```bash
# Build current application
./repo.sh build --config release

# Build with parallel jobs
./repo.sh build --config release -j8

# Build all applications
./repo.sh build --all --config release

# Clean build
./repo.sh build --config release --clean
```

### Launch Commands

```bash
# Launch application
./repo.sh launch --config release

# Launch with options
./repo.sh launch --config release --verbose --portable
```

### Management Commands

```bash
# List applications
./repo.sh list

# Register application
./repo.sh register --path source/apps/my_app

# Unregister application
./repo.sh unregister --name my_app

# Update dependencies
./repo.sh tools update
```

---

## Next Steps

Now that you understand the basics:

1. **Explore Templates** - Try different application templates
2. **Customize Your App** - Modify `.kit` files to add features
3. **Create Extensions** - Build reusable functionality
4. **Read Advanced Docs** - Check the `/docs` folder for deep dives
5. **Join the Community** - Share your creations and get help

**Additional Resources:**
- [Kit SDK Documentation](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template/latest/)
- [OpenUSD Documentation](https://openusd.org/release/index.html)
- [Omniverse Developer Center](https://developer.nvidia.com/omniverse)

---

**Happy Building! 🚀**
