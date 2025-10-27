# README Quick Start Section Update

**This file contains updated content for the README.md Quick Start section.**

## 🚀 Quick Start

Get up and running in minutes! This guide shows you the fastest path to creating your first Omniverse Kit application.

> **📚 Full Documentation:**
> - **[User Guide](docs/USER_GUIDE.md)** - Complete workflows with CLI and UI examples
> - **[Kit Playground Guide](docs/KIT_PLAYGROUND_GUIDE.md)** - Detailed visual development guide
> - **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet

### Choose Your Development Style

You can use either:
- **🎨 Kit Playground** (Visual GUI) - Browser-based development with real-time feedback
- **⌨️ Command Line** (CLI) - Traditional developer workflow

Both methods produce identical results and can be used interchangeably.

---

### 🎨 Option A: Visual Development with Kit Playground (Recommended)

The fastest way to get started with a visual, browser-based interface:

**1. Clone and Setup:**
```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
cd kit-app-template
./repo.sh  # Downloads SDK and dependencies (first run takes ~5 minutes)
```

**2. Launch Kit Playground:**
```bash
cd kit_playground
./dev.sh  # Linux/Mac
# OR
dev.bat   # Windows
```

This starts:
- Backend API on `http://localhost:5000`
- Frontend UI on `http://localhost:3000` (opens automatically in browser)

**3. Create Your First Application:**

In the browser at `http://localhost:3000`:

1. Click **"Templates"** in the left sidebar
2. Click **"Applications"** to expand
3. Click the **"Kit Base Editor"** card
4. Click **"Create Project"** button
5. Edit fields (or use auto-generated defaults):
   - **Project Name:** `my_first_editor` (lowercase, underscores)
   - **Display Name:** `My First Editor`
   - **Version:** `1.0.0`
6. Click **"Create Project"** (green button)
7. Watch the creation logs stream in real-time
8. **Editor panel opens** automatically with your `.kit` file

**4. Build Your Application:**

1. In the Editor panel, click the **"Build"** button (blue, above editor)
2. **Build Output panel** shows real-time progress:
   - Dependency downloads
   - Compilation steps
   - Build status
3. Wait for **"BUILD (RELEASE) SUCCEEDED"** message (~5-10 minutes first time)
4. **"Launch" button** appears automatically

**5. Launch Your Application:**

1. Click the **"Launch"** button (blue)
2. Watch launch logs stream
3. Your application window opens with the configured UI

**6. Edit and Iterate:**

1. Edit the `.kit` file in the Editor panel
2. Add extensions, change settings, customize UI
3. Click **"Save"** then **"Build"** to apply changes
4. Launch to see your modifications

✅ **You now have a working Omniverse Kit application!**

> 📖 **Learn More:** [Kit Playground Guide](docs/KIT_PLAYGROUND_GUIDE.md) for detailed UI workflows

---

### ⌨️ Option B: Command Line Development

For developers who prefer terminal workflows:

**1. Clone and Setup:**
```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
cd kit-app-template
./repo.sh  # Linux/Mac - Downloads SDK and dependencies
# OR
repo.bat   # Windows
```

**2. Create an Application:**

```bash
# Create from template
./repo.sh template new \
  --template kit_base_editor \
  --name my_first_editor \
  --display-name "My First Editor" \
  --version 1.0.0

# Navigate to your new project
cd source/apps/my_first_editor
```

**3. Build Your Application:**

```bash
# Build in release configuration (optimized)
./repo.sh build --config release

# First build takes ~5-10 minutes as dependencies download
# Subsequent builds are much faster (incremental)
```

**4. Launch Your Application:**

```bash
# Launch the built application
./repo.sh launch --config release

# Your application window opens
# Check the terminal for startup logs
```

**5. Edit and Iterate:**

```bash
# Edit the configuration file
nano my_first_editor.kit  # Or use your preferred editor

# Add extensions, change settings, etc.
# Then rebuild:
./repo.sh build --config release

# And launch:
./repo.sh launch --config release
```

✅ **You now have a working Omniverse Kit application!**

> 📖 **Learn More:** [User Guide](docs/USER_GUIDE.md) for detailed CLI workflows and examples

---

### 📝 What Gets Created?

Both methods create the same project structure:

```
source/apps/my_first_editor/
├── my_first_editor.kit    # Main configuration (TOML format)
├── config/                # Additional settings
│   └── *.toml
├── data/                  # Icons and assets
│   └── icon.png
├── docs/                  # Project documentation
│   └── README.md
└── README.md              # Project overview
```

**Key file:** `my_first_editor.kit` controls:
- Window settings (title, size)
- Extensions to load
- UI layout and behavior
- Application configuration

---

### 🔧 Common Next Steps

#### Add an Extension

**Via UI:**
1. Open your `.kit` file in the Editor panel
2. Add to `[dependencies]` section:
   ```toml
   [dependencies]
   "omni.kit.window.console" = {}  # Adds console window
   ```
3. Click "Save" → "Build" → "Launch"

**Via CLI:**
```bash
# Edit the .kit file
nano my_first_editor.kit

# Add extension to [dependencies] section
# Save, then rebuild:
./repo.sh build --config release
./repo.sh launch --config release
```

#### Change Window Settings

Edit your `.kit` file:
```toml
[settings.app.window]
title = "My Custom Title"
width = 2560
height = 1440
```

#### Create a Custom Extension

```bash
# Create extension from template
./repo.sh template new \
  --template basic_python_extension \
  --name my_custom_tool \
  --display-name "My Custom Tool"

# Add to your application's .kit file:
[dependencies]
"my.custom.tool" = {}
```

---

### 🧩 Creating Different Types of Projects

**Applications** (Full standalone applications):
```bash
# 3D Editor
./repo.sh template new --template kit_base_editor --name my_editor

# USD Viewer
./repo.sh template new --template omni_usd_viewer --name my_viewer

# USD Composer
./repo.sh template new --template omni_usd_composer --name my_composer

# Minimal Base
./repo.sh template new --template base_application --name my_app
```

**Extensions** (Reusable components):
```bash
# Python Extension
./repo.sh template new --template basic_python_extension --name my.extension

# Python UI Extension
./repo.sh template new --template basic_python_ui_extension --name my.ui.tool

# C++ Extension (advanced)
./repo.sh template new --template basic_cpp_extension --name my.cpp.module
```

**Services** (Headless microservices):
```bash
# Kit Service
./repo.sh template new --template kit_service --name my_service
```

**Standalone Projects** (Self-contained, distributable):
```bash
./repo.sh template new \
  --template kit_base_editor \
  --name my_standalone_app \
  --standalone \
  --output-dir /path/to/output
```

> 📖 **Learn More:** [User Guide - Example 6](docs/USER_GUIDE.md#example-6-creating-standalone-projects)

---

### 🔍 Troubleshooting Quick Start

**Build Failures:**
```bash
# Clear cache and rebuild
rm -rf _build
./repo.sh tools clean
./repo.sh build --config release
```

**Launch Issues:**
```bash
# Try debug mode for verbose output
./repo.sh launch --config debug --verbose
```

**Kit Playground Won't Start:**
```bash
# Restart services
cd kit_playground
./dev.sh  # Press Ctrl+C to stop first if running

# If issues persist, clear caches:
rm -rf ui/node_modules/.vite
./dev.sh
```

**Still Having Issues?**
- Check [Full Troubleshooting Guide](docs/USER_GUIDE.md#troubleshooting)
- Check [Kit Playground Troubleshooting](docs/KIT_PLAYGROUND_GUIDE.md#troubleshooting)
- Review logs:
  - Backend: `/tmp/kit-playground-backend.log`
  - Frontend: `/tmp/kit-playground-frontend.log`

---

### 📚 Documentation Index

**Start Here:**
- **[User Guide](docs/USER_GUIDE.md)** - Complete workflows with progressive examples
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet

**Visual Development:**
- **[Kit Playground Guide](docs/KIT_PLAYGROUND_GUIDE.md)** - Detailed UI guide
- **[UI Workflows](docs/KIT_PLAYGROUND_GUIDE.md#workflows)** - Step-by-step UI processes

**Technical Details:**
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Template System](docs/TEMPLATE_SYSTEM.md)** - Template structure
- **[API Documentation](docs/API_USAGE.md)** - API reference

**Advanced Topics:**
- **[Per-App Dependencies](ai-docs/PER_APP_DEPENDENCIES.md)** - Isolated dependency management
- **[Standalone Projects](ai-docs/STANDALONE_PROJECTS.md)** - Self-contained applications
- **[Streaming Applications](ai-docs/KIT_APP_STREAMING_DESIGN.md)** - Cloud streaming

---

**Ready to build something amazing? Start with [Example 1 in the User Guide](docs/USER_GUIDE.md#example-1-creating-your-first-application)!** 🚀
