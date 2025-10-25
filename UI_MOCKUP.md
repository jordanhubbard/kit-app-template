# Kit App Template Playground - UI Mockup
## Visual Reference for Progressive Disclosure Design

---

## 🎨 Full Layout View

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎮 Kit App Template Playground                               [📊 Jobs] [📖 Docs] [⚙️ Settings] │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌─────────────┬──────────────────────┬─────────────────────┬─────────────────────────┐ │
│  │             │                      │                     │                         │ │
│  │  PANEL 1    │  PANEL 2            │  PANEL 3           │  PANEL 4               │ │
│  │  Templates  │  Details            │  Configuration     │  Build & Launch        │ │
│  │  (280px)    │  (400px)            │  (500px)           │  (flexible)            │ │
│  │             │                      │                     │                         │ │
│  │  Always     │  Opens on           │  Opens on          │  Opens on              │ │
│  │  Visible    │  Template Click     │  [Create] Click    │  [Build] Click         │ │
│  │             │                      │                     │                         │ │
│  └─────────────┴──────────────────────┴─────────────────────┴─────────────────────────┘ │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Panel 1: Template Browser (Always Visible)

```
┌────────────────────────────┐
│ 🔍 Search templates...     │ <- Search bar
├────────────────────────────┤
│ [Applications] [Exts] [Svc]│ <- Category tabs
│                            │
│ Sort: [Recent ▼]           │ <- Sort dropdown
├────────────────────────────┤
│                            │
│ ┌──────────────────────┐   │ <- Template cards
│ │ 🎮 Kit Base Editor   │   │   (visual, clickable)
│ │ ╔═══════════════════╗│   │
│ │ ║   [Preview Img]   ║│   │
│ │ ╚═══════════════════╝│   │
│ │ USD-based 3D editor │   │
│ │ #editor #usd #3d    │   │
│ │ [Quick Create →]    │   │ <- Quick action
│ └──────────────────────┘   │
│                            │
│ ┌──────────────────────┐   │
│ │ 🔧 USD Viewer        │   │
│ │ ╔═══════════════════╗│   │
│ │ ║   [Preview Img]   ║│   │
│ │ ╚═══════════════════╝│   │
│ │ View USD files       │   │
│ │ #viewer #usd         │   │
│ │ [Quick Create →]    │   │
│ └──────────────────────┘   │
│                            │
│ ┌──────────────────────┐   │
│ │ 🚀 USD Explorer      │   │
│ │ ╔═══════════════════╗│   │
│ │ ║   [Preview Img]   ║│   │
│ │ ╚═══════════════════╝│   │
│ │ Navigate 3D scenes   │   │
│ │ #explorer #3d #nav   │   │
│ │ [Quick Create →]    │   │
│ └──────────────────────┘   │
│                            │
│ [Scroll for more...]       │
└────────────────────────────┘
```

### Alternative View: "My Projects" Tab

```
┌────────────────────────────┐
│ [Templates] [My Projects]  │ <- Tab switcher
├────────────────────────────┤
│ 🔍 Filter projects...      │
├────────────────────────────┤
│                            │
│ ┌──────────────────────┐   │
│ │ 📦 my_editor_app     │   │
│ │ ✓ Built              │   │ <- Status badge
│ │ Modified: 2h ago     │   │
│ │ Type: Application    │   │
│ │ [Open →]            │   │
│ └──────────────────────┘   │
│                            │
│ ┌──────────────────────┐   │
│ │ 📦 test_streaming    │   │
│ │ 🔴 Running           │   │ <- Live indicator
│ │ Modified: 5m ago     │   │
│ │ Type: Application    │   │
│ │ [Open →]            │   │
│ └──────────────────────┘   │
│                            │
│ ┌──────────────────────┐   │
│ │ 📦 custom_extension  │   │
│ │ ⚠️ Build Failed      │   │
│ │ Modified: 1d ago     │   │
│ │ Type: Extension      │   │
│ │ [Open →]            │   │
│ └──────────────────────┘   │
│                            │
└────────────────────────────┘
```

---

## 🎯 Panel 2: Template Details (Opens on Click)

```
┌─────────────────────────────────────┐
│ ← Back to Templates                 │ <- Navigation
├─────────────────────────────────────┤
│                                     │
│  🎮 Kit Base Editor                 │ <- Large title
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║                               ║  │
│  ║    [Large Preview Image]      ║  │ <- Hero image
│  ║                               ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  A complete USD-based 3D editor     │
│  built on NVIDIA Omniverse Kit.     │ <- Description
│  Perfect for creating, viewing,     │
│  and editing Universal Scene        │
│  Description (USD) files.           │
│                                     │
│  📊 Created 47 times this month     │ <- Stats
│  ⭐ Popular template                │
│                                     │
│  Tags: #editor #usd #3d #starter    │ <- Tags
│                                     │
│  ┌─────────────────────────────┐   │
│  │ [🚀 Create Application]     │   │ <- Primary action
│  └─────────────────────────────┘   │
│                                     │
│  [📖 View Docs] [📋 Copy Config]   │ <- Secondary actions
│                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                     │
│  📋 What's Included:                │ <- Feature list
│  ✓ USD stage management             │
│  ✓ 3D viewport with RTX rendering   │
│  ✓ Asset browser                    │
│  ✓ Transform tools                  │
│  ✓ Material editor                  │
│                                     │
│  🔧 Requirements:                   │
│  • Kit SDK 106.0 or newer           │
│  • Python 3.10+                     │
│  • GPU with RTX support             │
│                                     │
└─────────────────────────────────────┘
```

### After Clicking "Create Application"

```
┌─────────────────────────────────────┐
│ ← Back to Details                   │
├─────────────────────────────────────┤
│                                     │
│  Create Kit Base Editor App         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Project Name *              │   │
│  │ my_editor_app               │   │ <- Auto-generated
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Display Name                │   │
│  │ My Editor App               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Output Directory            │   │
│  │ source/apps/                │   │ <- Smart default
│  └─────────────────────────────┘   │
│                                     │
│  Advanced Options [▼]              │ <- Collapsible
│  ┌─────────────────────────────┐   │
│  │ ☑ Enable Kit App Streaming  │   │
│  │ ☐ Per-App Dependencies      │   │
│  │ ☐ Create as Standalone      │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ [✨ Create Application]      │   │ <- Animated button
│  └─────────────────────────────┘   │
│                                     │
│  [Cancel]                           │
│                                     │
└─────────────────────────────────────┘
```

---

## ⚙️ Panel 3: Configuration/Progress (Opens on Create)

### During Creation

```
┌──────────────────────────────────────┐
│ Creating Application...              │
├──────────────────────────────────────┤
│                                      │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░  65%          │ <- Progress bar
│                                      │
│  Current Step:                       │
│  ✓ Creating directory structure      │
│  ✓ Generating .kit file              │
│  ▶ Copying template files...         │ <- Current
│  ○ Initializing dependencies         │
│  ○ Setting up build config           │
│                                      │
│  📝 Log Output:                      │
│  ┌────────────────────────────────┐ │
│  │ Creating apps/my_editor_app/   │ │ <- Scrollable log
│  │ Generating my_editor_app.kit   │ │
│  │ Copying templates/kit_base/... │ │
│  │ ...                            │ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

### After Success

```
┌──────────────────────────────────────┐
│ ✅ Application Created!              │ <- Success header
├──────────────────────────────────────┤
│                                      │
│  🎉 Congratulations!                 │ <- Celebration
│                                      │
│  Your application is ready to build. │
│                                      │
│  📦 my_editor_app                    │
│  📁 source/apps/my_editor_app/       │
│  📄 my_editor_app.kit                │
│  🎬 Created just now                 │
│                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                      │
│  What's Next?                        │
│                                      │
│  ┌────────────────────────────────┐ │
│  │ [🏗️ Build Application]         │ │ <- Primary action
│  └────────────────────────────────┘ │
│                                      │
│  [✏️ Edit .kit File]                │ <- Secondary
│  [📖 View Documentation]             │
│  [🗑️ Delete Project]                │
│                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                      │
│  💡 Tip: Build your app to test it! │
│                                      │
└──────────────────────────────────────┘
```

---

## 🏗️ Panel 4: Build Output (Opens on Build)

### During Build

```
┌─────────────────────────────────────────────┐
│ Building my_editor_app...                   │
├─────────────────────────────────────────────┤
│                                             │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  78%                 │
│  Compiling extensions... (2/5)              │
│                                             │
│  📊 Build Info:                             │
│  Started: 10:45:32 AM                       │
│  Elapsed: 1m 23s                            │
│  Target: _build/linux-x86_64/release/       │
│                                             │
│  📝 Build Log: [Filter: All ▼]             │
│  ┌─────────────────────────────────────┐   │
│  │ [INFO] Starting build process...    │   │ <- Colored logs
│  │ [INFO] Found 5 extensions to build  │   │
│  │ [WARN] Extension omni.kit.test...   │   │ <- ANSI colors
│  │ [INFO] Compiling C++ bindings...    │   │
│  │ [INFO] ✓ my_editor_app.basic       │   │
│  │ [INFO] ▶ my_editor_app.core        │   │ <- In progress
│  │ [INFO]   Linking libraries...       │   │
│  │ ...                                 │   │
│  │ [AUTO-SCROLL]                       │   │ <- Auto-scroll indicator
│  └─────────────────────────────────────┘   │
│                                             │
│  [⏸️ Pause Auto-Scroll] [❌ Cancel Build]  │
│                                             │
└─────────────────────────────────────────────┘
```

### Build Complete

```
┌─────────────────────────────────────────────┐
│ ✅ Build Successful!                        │
├─────────────────────────────────────────────┤
│                                             │
│  🎉 Your application is ready to launch!   │
│                                             │
│  📊 Build Summary:                          │
│  ✓ 5 extensions compiled                    │
│  ✓ 0 warnings                               │
│  ✓ 0 errors                                 │
│  ⏱️ Build time: 2m 15s                     │
│  📦 Size: 145 MB                            │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                             │
│  Launch Options:                            │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ [🚀 Launch Application]               │ │ <- Direct launch
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ [🌐 Launch with Streaming]            │ │ <- Streaming
│  └───────────────────────────────────────┘ │
│                                             │
│  [📖 View Build Log] [🔧 Rebuild]          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🌐 Panel 5: Live Preview (Opens on Launch)

### Streaming Application

```
┌───────────────────────────────────────────────────────┐
│ 🔴 LIVE - my_editor_app                              │ <- Live indicator
├───────────────────────────────────────────────────────┤
│                                                       │
│  🌐 Streaming URL:                                    │
│  ┌─────────────────────────────────────────────────┐ │
│  │ https://localhost:47995                          │ │ <- Copy button
│  │ [📋 Copy] [🔗 Open in New Tab]                  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ╔═══════════════════════════════════════════════╗  │
│  ║                                               ║  │
│  ║                                               ║  │
│  ║         [Live Application Preview]            ║  │ <- iframe
│  ║                                               ║  │
│  ║         (Interactive WebRTC Stream)           ║  │
│  ║                                               ║  │
│  ║                                               ║  │
│  ║                                               ║  │
│  ╚═══════════════════════════════════════════════╝  │
│                                                       │
│  📊 Session Info:                                     │
│  • Status: Connected                                  │
│  • Latency: 45ms                                      │
│  • FPS: 60                                            │
│  • Resolution: 1920x1080                              │
│                                                       │
│  [⏹️ Stop Application] [🔄 Restart] [📖 Logs]       │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Direct Launch (No Streaming)

```
┌───────────────────────────────────────────────────────┐
│ ✅ Application Launched                              │
├───────────────────────────────────────────────────────┤
│                                                       │
│  🚀 my_editor_app is running locally                 │
│                                                       │
│  The application should appear on your display.       │
│  If you don't see it, check the logs below.          │
│                                                       │
│  📊 Process Info:                                     │
│  • PID: 12345                                         │
│  • Started: 10:47:15 AM                               │
│  • Display: :0                                        │
│  • Memory: 1.2 GB                                     │
│                                                       │
│  📝 Application Log: [Filter: All ▼]                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │ [INFO] Kit App starting...                       │ │
│  │ [INFO] Loading extensions...                     │ │
│  │ [INFO] ✓ USD stage initialized                  │ │
│  │ [INFO] ✓ Viewport created                       │ │
│  │ [INFO] Application ready!                        │ │
│  │ ...                                              │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  [⏹️ Stop Application] [🔄 Restart] [📝 Full Log]   │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 🎨 Visual Details

### Card Hover Effect

```
Normal State:
┌──────────────────────┐
│ 🎮 Kit Base Editor   │
│ ╔═══════════════════╗│
│ ║   [Preview Img]   ║│
│ ╚═══════════════════╝│
│ USD-based 3D editor  │
│ #editor #usd #3d     │
│ [Quick Create →]    │
└──────────────────────┘

Hover State:
┌══════════════════════┐ ← Green border
│ 🎮 Kit Base Editor   │ ← Lifted (shadow)
│ ╔═══════════════════╗│
│ ║   [Preview Img]   ║│ ← Slightly larger
│ ╚═══════════════════╝│
│ USD-based 3D editor  │
│ #editor #usd #3d     │
│ [Quick Create →]    │ ← Animated pulse
└══════════════════════┘
```

### Status Badges

```
✓ Built       <- Green background
🔴 Running    <- Red pulsing dot
⚠️ Failed     <- Yellow/orange
⏸️ Paused     <- Gray
🔨 Building   <- Blue with spinner
```

### Progress Indicators

```
Loading:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  70%

Indeterminate:
░░▓▓▓▓░░░░░░░░░░░░░  (animated wave)

Success:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100% ✓

Error:
▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  65% ✗
```

---

## 🎯 Interaction Patterns

### Click Flow: Template → Create → Build → Launch

```
User Action                     UI Response                      Panel State
─────────────────────────────────────────────────────────────────────────────

1. Click template card    →    Panel 2 slides in from right  →  [1][2]
                               Show template details

2. Click [Create]         →    Panel 3 slides in             →  [1][2][3]
                               Show creation form

3. Submit form            →    Panel 3 becomes progress      →  [1][2][3]
                               Show creation progress

4. Creation complete      →    Panel 3 shows success         →  [1][2][3]
                               Confetti animation 🎉

5. Click [Build]          →    Panel 4 slides in             →  [1][2][3][4]
                               Show build output

6. Build complete         →    Panel 4 shows success         →  [1][2][3][4]
                               Launch buttons appear

7. Click [Launch Stream]  →    Panel 5 slides in             →  [1][2][3][4][5]
                               Show streaming preview

8. Close panels           →    Panels slide out right-to-left →  [1]
```

### Keyboard Shortcuts

```
Global:
Cmd/Ctrl + K         → Focus search
Cmd/Ctrl + B         → Toggle sidebar
Cmd/Ctrl + ,         → Open settings
Cmd/Ctrl + /         → Show keyboard shortcuts
Esc                  → Close rightmost panel

Template Actions:
Cmd/Ctrl + N         → New application
Cmd/Ctrl + E         → Edit selected .kit file
Cmd/Ctrl + Shift + B → Build selected project
Cmd/Ctrl + Shift + L → Launch selected project

Editor:
Cmd/Ctrl + S         → Save .kit file
Cmd/Ctrl + Shift + S → Save and build
Cmd/Ctrl + Z         → Undo
Cmd/Ctrl + Shift + Z → Redo
```

---

## 📱 Responsive Behavior

### Desktop (> 1200px)
```
[Panel 1: 280px] [Panel 2: 400px] [Panel 3: 500px] [Panel 4: flexible] [Panel 5: flexible]
```

### Tablet (768px - 1200px)
```
[Panel 1: 240px] [Panel 2: flexible] [Panel 3: flexible]
(Max 3 panels, horizontal scroll for more)
```

### Mobile (< 768px)
```
[Panel 1: Full width]
     ↓
[Panel 2: Full width] (slides up)
     ↓
[Panel 3: Full width] (slides up)
(Vertical stacking, smooth scroll)
```

---

**End of Mockup** 🎨
