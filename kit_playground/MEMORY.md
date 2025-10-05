# Kit Playground UI Architecture - Mind Map

**Created:** October 4, 2025
**Purpose:** Complete state documentation for UI improvements and refactoring

---

## 🎯 Overview

Kit Playground is a **web-based visual development environment** for NVIDIA Omniverse Kit SDK with a React frontend and Flask backend, following a **progressive disclosure workflow** design pattern.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KIT PLAYGROUND                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────┐         ┌──────────────────────┐       │
│  │   REACT FRONTEND   │◄───────►│   FLASK BACKEND      │       │
│  │   (Port 3000)      │  REST   │   (Port 8200)        │       │
│  │   + Socket.IO      │  API    │   + Socket.IO        │       │
│  └────────────────────┘         └──────────────────────┘       │
│           │                              │                       │
│           │                              │                       │
│  ┌────────▼────────┐           ┌────────▼──────────┐           │
│  │  Redux Store    │           │  Template API     │           │
│  │  - templates    │           │  - Unified API    │           │
│  │  - ui           │           │  - Generation     │           │
│  │  - project      │           │  - Discovery      │           │
│  └─────────────────┘           └───────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

### Frontend Stack
```
React 18.2.0
├── TypeScript 5.0
├── Material-UI v5 (MUI)
│   ├── Emotion (CSS-in-JS)
│   └── Icons (@mui/icons-material)
├── Redux Toolkit 1.9.5
│   └── React-Redux 8.0.5
├── Monaco Editor 0.44.0
│   └── @monaco-editor/react 4.6.0
├── React Router DOM 6.11.0
├── Socket.IO Client 4.6.0
├── Axios 1.8.2
└── Additional
    ├── react-split-pane (layout)
    ├── smol-toml (TOML parsing)
    └── uuid (ID generation)
```

### Backend Stack
```
Python 3.8+
├── Flask (REST API)
├── Flask-CORS
├── Flask-SocketIO (WebSocket)
└── Integration
    ├── Template API (tools/repoman)
    ├── PlaygroundApp (core logic)
    └── XpraManager (display server)
```

### Build & Development
```
├── React Scripts 5.0.1
├── npm/Node.js 16+
└── Webpack (bundled with react-scripts)
```

---

## 🎨 UI Component Architecture

### Component Hierarchy Tree

```
App (root)
├── Provider (Redux store)
├── ThemeProvider (MUI dark theme)
├── CssBaseline
├── Router (BrowserRouter)
└── AppContent
    └── MainLayoutWorkflow ⭐ PRIMARY LAYOUT
        ├── WorkflowBreadcrumbs
        │   ├── Navigation controls (back/forward/home)
        │   ├── Current step indicator
        │   └── Selected item display
        │
        ├── WorkflowSidebar
        │   ├── Templates Section
        │   │   ├── Path selector
        │   │   ├── Category tree (Applications/Extensions/Services)
        │   │   ├── Template nodes (clickable)
        │   │   └── Refresh button
        │   ├── Projects Section
        │   │   ├── Path selector
        │   │   ├── Project list (with status icons)
        │   │   ├── Project nodes (clickable)
        │   │   └── Refresh button
        │   └── DirectoryBrowserDialog
        │
        ├── SlidingPanelLayout (main content area)
        │   ├── Browse Panel (step='browse')
        │   │   └── TemplateGallery
        │   │       ├── Search & Filters
        │   │       │   ├── Search bar
        │   │       │   ├── Category dropdown
        │   │       │   ├── Type dropdown
        │   │       │   └── Sort options
        │   │       ├── Tabs (All/Applications/Extensions/Microservices)
        │   │       ├── Template Cards Grid
        │   │       │   ├── Thumbnail
        │   │       │   ├── Type badge
        │   │       │   ├── Favorite star
        │   │       │   ├── Connector info
        │   │       │   ├── Description
        │   │       │   ├── Stats
        │   │       │   └── "Create Project" button
        │   │       ├── TemplateDetailPanel (side panel)
        │   │       │   ├── Detailed info
        │   │       │   ├── Documentation
        │   │       │   └── Actions
        │   │       └── CreateProjectDialog
        │   │           ├── Project name input
        │   │           ├── Display name input
        │   │           ├── Version input
        │   │           ├── Output directory selector
        │   │           └── CLI command preview
        │   │
        │   ├── Edit Panel (step='edit')
        │   │   ├── Toolbar
        │   │   │   ├── Save button
        │   │   │   ├── Build button
        │   │   │   ├── Run button
        │   │   │   ├── Stop button
        │   │   │   └── Status text
        │   │   ├── CodeEditor (Monaco)
        │   │   │   ├── Editor toolbar
        │   │   │   │   ├── File info
        │   │   │   │   ├── Language chip
        │   │   │   │   ├── Modified indicator
        │   │   │   │   ├── Undo/Redo
        │   │   │   │   ├── Format
        │   │   │   │   ├── Search
        │   │   │   │   └── Save
        │   │   │   ├── Monaco instance
        │   │   │   │   ├── Custom "kit-dark" theme
        │   │   │   │   ├── Syntax highlighting
        │   │   │   │   ├── Error markers
        │   │   │   │   ├── Bracket matching
        │   │   │   │   └── Auto-completion
        │   │   │   └── Status footer
        │   │   │       ├── Line/Column position
        │   │   │       └── Line count
        │   │   └── FileExplorer (bottom pane)
        │   │       ├── Directory tree
        │   │       └── File browser
        │   │
        │   └── Preview Panel (step='preview')
        │       └── [Coming soon - Xpra integration]
        │
        ├── Console (bottom, fixed height: 200px)
        │   ├── Header
        │   │   ├── Tabs (All/Build/Runtime/System)
        │   │   ├── Error/Warning badges
        │   │   └── Actions (Filter/Clear/Download/Collapse)
        │   ├── Search bar
        │   ├── Log output area
        │   │   ├── Timestamp
        │   │   ├── Source badge
        │   │   ├── Level indicator
        │   │   └── Message
        │   ├── Auto-scroll indicator
        │   └── Filter menu
        │       └── Level toggles (Error/Warning/Info/Success/Debug)
        │
        └── StatusBar (bottom, height: 24px)
            ├── Project name
            ├── Build status
            ├── Error/Warning counts
            ├── System resources (CPU/Memory)
            ├── Connection status
            └── SDK version
```

---

## 🔄 State Management (Redux)

### Store Structure

```typescript
RootState
├── templates: TemplatesState
│   ├── templates: Record<string, Template>
│   ├── loading: boolean
│   ├── error: string | null
│   └── selectedTemplate: string | null
│
├── ui: UIState
│   ├── sidebarVisible: boolean
│   ├── theme: 'dark' | 'light'
│   ├── activeView: 'gallery' | 'editor' | 'connections' | 'preview'
│   ├── consoleHeight: number
│   └── splitPaneSize: number
│
└── project: ProjectState
    ├── currentProject: Project | null
    │   ├── id: string
    │   ├── name: string
    │   ├── templates: string[]
    │   ├── connections: Connection[]
    │   ├── configuration: Record<string, any>
    │   ├── outputPath: string
    │   ├── hotReload?: boolean
    │   └── runningTemplates?: string[]
    ├── isBuilding: boolean
    ├── isRunning: boolean
    ├── buildOutput: string[]
    └── error: string | null
```

### Redux Slices & Actions

#### templatesSlice
```typescript
Actions:
├── loadTemplates (async thunk)
├── selectTemplate(templateId: string)
└── clearSelection()

State Updates:
└── Templates loaded from /api/templates
```

#### uiSlice
```typescript
Actions:
├── toggleSidebar()
├── setSidebarVisible(visible: boolean)
├── setTheme(theme: 'dark' | 'light')
├── setActiveView(view: string)
├── setConsoleHeight(height: number)
└── setSplitPaneSize(size: number)
```

#### projectSlice
```typescript
Actions:
├── createProject({ name, outputPath })
├── loadProject(project: Project)
├── addTemplate(templateId: string)
├── removeTemplate(templateId: string)
├── setOutputPath(path: string)
├── setBuildStatus(isBuilding: boolean)
├── setRunStatus(isRunning: boolean)
├── addBuildOutput(line: string)
├── clearBuildOutput()
└── setError(error: string | null)
```

---

## 🌐 API Architecture

### REST API Endpoints (Flask Backend)

#### Template Management
```
GET    /api/templates
       → List all templates (legacy)

GET    /api/templates/:id/code
       → Get template description/info

POST   /api/templates/:id/update
       → Update template code
       Body: { code: string }

POST   /api/templates/:id/build
       → Build a template

POST   /api/templates/:id/run
       → Run a template

POST   /api/templates/:id/stop
       → Stop running template

POST   /api/templates/:id/deploy
       → Deploy template as standalone
       Body: { outputPath: string }
```

#### Unified Template API (v2)
```
GET    /api/v2/templates
       → List templates (unified API)
       Query: ?type=... &category=...

GET    /api/v2/templates/:id/docs
       → Get template documentation

POST   /api/v2/templates/generate
       → Generate project from template
       Body: TemplateGenerationRequest {
         templateName: string
         name: string
         displayName: string
         version: string
         configFile?: string
         outputDir?: string
         addLayers?: boolean
         layers?: string[]
         acceptLicense?: boolean
         extraParams?: Record<string, any>
       }

GET    /api/v2/license/status
       → Check license acceptance

GET    /api/v2/license/text
       → Get license text

POST   /api/v2/license/accept
       → Accept license
```

#### Project Management
```
POST   /api/projects
       → Create new project
       Body: { name: string, outputPath: string }

POST   /api/projects/build
       → Build project (repo.sh)
       Body: { projectPath: string, projectName: string }

POST   /api/projects/run
       → Run project (repo.sh launch)
       Body: { projectPath: string, projectName: string }

POST   /api/projects/stop
       → Stop running project
       Body: { projectName: string }

GET    /api/projects/discover
       → Discover projects in directory
       Query: ?path=...
```

#### Filesystem Operations
```
GET    /api/filesystem/cwd
       → Get current working directory

GET    /api/filesystem/list
       → List directory contents
       Query: ?path=...

POST   /api/filesystem/mkdir
       → Create directory
       Body: { path: string }

GET    /api/filesystem/read
       → Read file contents
       Query: ?path=...
```

#### Configuration
```
GET    /api/config/paths
       → Get default paths
       Returns: { templatesPath, projectsPath, repoRoot }
```

#### Xpra (Display Server)
```
POST   /api/xpra/sessions
       → Create Xpra session
       Body: { sessionId?: string }

GET    /api/xpra/sessions/:id
       → Get session info

POST   /api/xpra/sessions/:id/launch
       → Launch app in session
       Body: { command: string }

DELETE /api/xpra/sessions/:id
       → Stop Xpra session

GET    /api/xpra/check
       → Check if Xpra is installed
```

#### Health & Misc
```
GET    /api/health
       → Health check

GET    /
GET    /<path>
       → Serve React static files (catch-all)
```

### WebSocket Events (Socket.IO)

#### Client → Server
```
connect
disconnect
```

#### Server → Client
```
connected
  → { status: 'ok' }

log
  → { level, source, message }
  Sources: 'build' | 'runtime' | 'system'
  Levels: 'info' | 'warning' | 'error' | 'success' | 'debug'

build-output
  → { line: string }

runtime-output
  → { line: string }

build-status (custom event)
  → { status, errors, warnings }
```

---

## 🚀 Workflow & User Journey

### Progressive Disclosure Workflow

```
BROWSE → EDIT → PREVIEW
  ↑                 ↓
  └─────────────────┘
     (Navigation)
```

#### Step 1: BROWSE
```
User Actions:
├── View template gallery
├── Search & filter templates
├── Click template card → View details
├── Star favorites
└── Click "Create Project"
    └── Opens CreateProjectDialog
        ├── Enter project name
        ├── Enter display name
        ├── Set version
        ├── (Optional) Custom output directory
        └── Submit → Generates project
            └── Transitions to EDIT step
```

#### Step 2: EDIT
```
User Actions:
├── View generated .kit file in Monaco editor
├── Edit configuration
├── Save changes (Ctrl+S)
├── Browse project files (bottom pane)
├── Click Build → Builds project
│   └── Output streams to Console
└── Click Run → Builds + launches app
    ├── App opens in separate window
    └── Transitions to PREVIEW (if Xpra available)
```

#### Step 3: PREVIEW
```
User Actions:
└── [Coming soon]
    ├── View running app in embedded Xpra session
    └── Stop application
```

### Sidebar Navigation

```
Sidebar (Always Visible):
├── Templates Section
│   ├── Browse templates path
│   ├── Click template → Navigate to BROWSE + select
│   └── Organized by type (Applications/Extensions/Services)
│
└── Projects Section
    ├── Browse projects path
    ├── Click project → Navigate to EDIT + load project
    └── Shows status (✓ ready, ⚙ building, ▶ running, ✗ error)
```

---

## 🎨 Design System

### Theme Configuration

```typescript
Dark Theme (VS Code inspired):
├── Primary: #76b900 (NVIDIA Green)
├── Secondary: #00a86b
├── Background:
│   ├── Default: #1e1e1e
│   └── Paper: #252526
├── Text:
│   ├── Primary: #cccccc
│   └── Secondary: #969696
└── Typography:
    ├── Font: "SF Mono", "Monaco", "Inconsolata", "Fira Code"
    └── Base size: 13px
```

### Monaco Editor Theme

```typescript
Custom "kit-dark" theme:
├── Base: vs-dark
├── Syntax colors:
│   ├── Comments: #6A9955 (italic)
│   ├── Keywords: #569CD6
│   ├── Strings: #CE9178
│   ├── Numbers: #B5CEA8
│   ├── Types: #4EC9B0
│   └── Functions: #DCDCAA
└── Editor colors:
    ├── Background: #1e1e1e
    ├── Foreground: #D4D4D4
    ├── Line highlight: #2A2D2E
    ├── Cursor: #76b900 (NVIDIA Green)
    └── Selection: #264F78
```

### Status Colors

```
Build Status:
├── Idle: #858585 (gray)
├── Building: #4ec9b0 (cyan)
├── Success: #76b900 (green)
└── Error: #f48771 (red)

Log Levels:
├── Error: #f44336 (red)
├── Warning: #ff9800 (orange)
├── Info: #2196f3 (blue)
├── Success: #76b900 (green)
└── Debug: #9e9e9e (gray)
```

---

## 📂 File Organization

### Frontend Structure

```
kit_playground/ui/
├── public/
│   ├── index.html
│   └── manifest.json
│
├── src/
│   ├── index.tsx                    # Entry point
│   ├── App.tsx                      # Root component
│   ├── App.css
│   │
│   ├── components/
│   │   ├── browser/
│   │   │   ├── TemplateBrowser.tsx      # Marketplace template browser
│   │   │   └── TemplateBrowser.css
│   │   │
│   │   ├── connections/
│   │   │   └── ConnectionEditor.tsx     # Visual connection editor
│   │   │
│   │   ├── console/
│   │   │   └── Console.tsx              # Build/runtime log console
│   │   │
│   │   ├── controls/
│   │   │   └── FileExplorer.tsx         # File browser
│   │   │
│   │   ├── dialogs/
│   │   │   ├── CreateProjectDialog.tsx   # New project wizard
│   │   │   └── DirectoryBrowserDialog.tsx # Directory picker
│   │   │
│   │   ├── editor/
│   │   │   └── CodeEditor.tsx           # Monaco editor wrapper
│   │   │
│   │   ├── gallery/
│   │   │   ├── TemplateGallery.tsx      # Local template gallery
│   │   │   └── TemplateDetailPanel.tsx  # Template details side panel
│   │   │
│   │   └── layout/
│   │       ├── MainLayout.tsx           # [Legacy]
│   │       ├── MainLayout.css
│   │       ├── MainLayoutWorkflow.tsx   # ⭐ MAIN LAYOUT (active)
│   │       ├── SlidingPanelLayout.tsx   # Progressive disclosure panels
│   │       ├── StatusBar.tsx            # Bottom status bar
│   │       ├── WorkflowBreadcrumbs.tsx  # Navigation breadcrumbs
│   │       └── WorkflowSidebar.tsx      # Templates & projects sidebar
│   │
│   ├── hooks/
│   │   └── redux.ts                     # Typed Redux hooks
│   │
│   ├── services/
│   │   ├── api.ts                       # API client & endpoints
│   │   └── marketplace.ts               # Marketplace integration (stub)
│   │
│   ├── store/
│   │   ├── index.ts                     # Redux store export
│   │   ├── store.ts                     # Store configuration
│   │   └── slices/
│   │       ├── projectSlice.ts
│   │       ├── templatesSlice.ts
│   │       └── uiSlice.ts
│   │
│   ├── types/
│   │   └── workflow.ts                  # Workflow type definitions
│   │
│   └── react-split-pane.d.ts           # Type definitions
│
├── package.json
├── package-lock.json
├── tsconfig.json
└── build/                               # Production build (generated)
    ├── index.html
    ├── manifest.json
    ├── asset-manifest.json
    └── static/
        ├── css/
        └── js/
```

### Backend Structure

```
kit_playground/
├── backend/
│   ├── __init__.py
│   ├── web_server.py                # ⭐ MAIN SERVER
│   │   └── PlaygroundWebServer class
│   │       ├── Flask app setup
│   │       ├── REST API routes
│   │       ├── WebSocket handlers
│   │       └── Static file serving
│   │
│   ├── xpra_manager.py              # Xpra display server manager
│   └── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── playground_app.py            # Core application logic
│   └── config.py                    # Configuration management
│
├── playground.py                     # CLI entry point
├── playground.sh                     # Linux/macOS launcher
├── playground.bat                    # Windows launcher
├── dev.sh                           # Development mode launcher
└── dev.bat
```

---

## 🔍 Key Features Deep Dive

### 1. Template Gallery

**Purpose:** Visual browsing and selection of Kit templates

**Features:**
- Card-based grid layout
- Thumbnail images with fallback gradients
- Type badges (Application/Extension/Microservice)
- Favorite/star system (localStorage)
- Connector count indicators
- Real-time search & filtering
- Tabs for quick filtering by type
- Detail panel (slide-in from right)

**Data Flow:**
```
Mount → loadTemplates()
  → GET /api/v2/templates
  → Store in templates[] state
  → Filter & display cards
  → Click card → setSelectedTemplate()
  → Show TemplateDetailPanel
  → Click "Create Project" → Open CreateProjectDialog
```

### 2. Code Editor (Monaco)

**Purpose:** Edit .kit configuration files and code

**Features:**
- Monaco editor instance with custom theme
- Language detection (TOML, Python, C++)
- Syntax highlighting
- Error markers with inline messages
- Auto-completion
- Format on save
- Keyboard shortcuts (Ctrl+S, Ctrl+F)
- Line/column indicator
- Undo/Redo
- Search/Replace

**Language Support:**
- TOML (for .kit files) with validation via smol-toml
- Python with PEP 8 checks
- C++
- JavaScript/TypeScript

**Validation:**
- Real-time syntax checking (debounced 500ms)
- Error markers displayed inline
- TOML parsing errors highlighted

**Data Flow:**
```
Project selected → Load .kit file
  → GET /api/filesystem/read?path=...
  → Display in editor
  → User edits → onChange()
  → Validate syntax → Show markers
  → Ctrl+S → handleSave()
  → (Future: POST /api/filesystem/write)
```

### 3. Console (Build Logs)

**Purpose:** Real-time streaming of build, runtime, and system logs

**Features:**
- Tabbed interface (All/Build/Runtime/System)
- Color-coded log levels
- Timestamp for each entry
- Source badges (visual indicators)
- Search/filter logs
- Auto-scroll (with manual override)
- Download logs as .txt
- Clear logs
- Collapsible

**Log Sources:**
- Build: Template/project build output
- Runtime: Application stdout/stderr
- System: Connection status, errors

**Data Flow:**
```
Server emits 'log' event
  → Socket.IO receives
  → addLog() called
  → Append to logs[]
  → Filter by tab/level/search
  → Display in console
  → Auto-scroll to bottom
```

### 4. Project Creation Dialog

**Purpose:** Wizard for generating projects from templates

**Features:**
- Template info display
- Form fields with validation
  - Project name (lowercase, dots, underscores)
  - Display name (human-readable)
  - Version (semantic versioning)
  - Output directory (optional custom path)
- Real-time validation errors
- Auto-generation of display name
- Directory browser integration
- CLI command preview
- License acceptance flow

**Validation Rules:**
```
Project name: /^[a-z0-9._]+$/
Display name: required, any string
Version: /^\d+\.\d+\.\d+$/
Output dir: required if custom location enabled
```

**Data Flow:**
```
User fills form → Validate
  → Click "Create Project"
  → POST /api/v2/templates/generate
  → Body: TemplateGenerationRequest
  → Backend generates project
  → Returns success + playback file
  → onSuccess() callback
  → Load generated project in editor
  → Transition to EDIT step
```

### 5. Workflow Sidebar

**Purpose:** Persistent navigation for templates and projects

**Features:**
- Dual-section layout (Templates + Projects)
- Collapsible sections
- Path selectors with edit mode
- Directory browser integration
- Refresh buttons
- Tree navigation for categories
- Status indicators for projects
- Chip badges for counts

**Template Section:**
- Browse templates directory
- Organized by type in categories
- Click → Navigate to BROWSE + select template

**Projects Section:**
- Browse projects directory
- Auto-discover .kit projects
- Status icons (✓ ⚙ ▶ ✗)
- Click → Navigate to EDIT + load project

**Data Flow:**
```
Mount → Load default paths
  → GET /api/config/paths
  → Load templates → GET /api/v2/templates
  → Load projects → GET /api/projects/discover?path=...
  → Display in tree structure
  → User clicks node → onSelectNode()
  → Navigate to appropriate step
  → Load selected item
```

### 6. Build & Run System

**Purpose:** Compile and launch Kit applications

**Build Flow:**
```
User clicks Build button
  → setBuildStatus(true)
  → POST /api/projects/build
  → Backend calls repo.sh build
  → Stdout/stderr streamed via Socket.IO
  → emitConsoleLog() displays in Console
  → On completion → setBuildStatus(false)
  → Update status bar
```

**Run Flow:**
```
User clicks Run button
  → setRunStatus(true)
  → handleBuild() first
  → POST /api/projects/run
  → Backend calls repo.sh launch
  → Process started in background
  → App window opens (inherits environment)
  → Status updated
  → Stop button enabled
```

**Stop Flow:**
```
User clicks Stop button
  → POST /api/projects/stop
  → Backend terminates process
  → setRunStatus(false)
  → emitConsoleLog('Stopped')
```

---

## 🔧 Configuration & Setup

### Environment Setup

**Prerequisites:**
- Python 3.8+
- Node.js 16+
- npm
- Git

**Installation:**
```bash
# Option 1: Make
make playground

# Option 2: Scripts
./kit_playground/playground.sh

# Option 3: Manual
cd kit_playground/ui
npm install
npm run build
cd ../backend
python3 web_server.py --port 8200 --open-browser
```

**Development Mode:**
```bash
# Terminal 1: Backend
cd kit_playground/backend
python3 web_server.py --port 8200

# Terminal 2: Frontend (hot reload)
cd kit_playground/ui
npm start
# Opens http://localhost:3000
```

### Server Configuration

**Command-line Options:**
```bash
--port PORT         # Server port (default: 8200)
--host HOST         # Server host (default: localhost)
--open-browser      # Auto-open browser on start
```

**Port Resolution:**
- Attempts specified port
- If occupied, tries port+1 up to 10 attempts
- Logs warning if port changed

### Build Output

**Production Build:**
```
ui/build/
├── index.html
├── manifest.json
├── asset-manifest.json
└── static/
    ├── css/main.*.css
    └── js/main.*.js
```

**Served by Flask:**
- All requests → check for /api/ routes first
- Static files → serve from build/
- SPA routing → serve index.html (catch-all)

---

## 🐛 Known Issues & Limitations

### Current Issues
1. **Preview Step:** Not yet implemented (placeholder)
2. **Save Functionality:** Editor save doesn't persist to disk
3. **Hot Reload:** Not integrated for running applications
4. **Connection Editor:** Visual connection system incomplete
5. **Xpra Integration:** Basic implementation, needs testing
6. **Project Persistence:** Projects not saved to workspace format
7. **Template Customization:** Limited customization options
8. **Error Handling:** Some error cases not gracefully handled

### Technical Debt
1. **Dual Store Setup:** `store.ts` and `index.ts` both export store (should consolidate)
2. **Legacy Components:** `MainLayout.tsx` still exists but unused (remove)
3. **Mock Data:** `TemplateBrowser.tsx` has mock templates (should use real data)
4. **Marketplace Service:** Stubbed but not implemented
5. **Type Inconsistencies:** Some `any` types should be properly typed
6. **Error Markers:** Monaco error markers could be more sophisticated
7. **WebSocket Reconnection:** No automatic reconnection on disconnect

### Performance Considerations
1. **Template Loading:** All templates loaded at once (consider pagination)
2. **Log Storage:** Unlimited log entries (should cap or virtualize)
3. **Monaco Instance:** One instance per editor (consider reuse)
4. **File Reading:** Large files not chunked
5. **Build Output:** Streams all at once (consider buffering)

---

## 🎯 Improvement Opportunities

### High Priority
1. **Implement Preview Step**
   - Embed Xpra sessions
   - Live application preview
   - Screenshot capture
   - Remote control

2. **Complete Save Functionality**
   - Persist editor changes to disk
   - Auto-save on interval
   - Dirty state indicators
   - File watchers

3. **Enhanced Error Handling**
   - Better error messages
   - Recovery suggestions
   - Retry mechanisms
   - Error boundaries

4. **Project Workspace**
   - Save/load project state
   - Recent projects list
   - Project metadata
   - Multi-project support

### Medium Priority
1. **Visual Connection Editor**
   - Drag-and-drop connections
   - Connection validation
   - Data flow visualization
   - Connector compatibility checks

2. **Template Customization**
   - Template variables UI
   - Layer selection
   - Dependency management
   - Template preview before generation

3. **Enhanced Console**
   - Log export formats (JSON, CSV)
   - Log filtering by regex
   - Syntax highlighting in logs
   - Performance profiling view

4. **Search & Discovery**
   - Global search across projects
   - Tag-based filtering
   - Recent templates
   - Template recommendations

### Low Priority
1. **AI Integration**
   - AI-assisted code generation
   - Template suggestions
   - Error diagnosis
   - Code completion

2. **Collaboration**
   - Share projects
   - Comments/annotations
   - Version control integration
   - Team workspaces

3. **Marketplace**
   - Browse community templates
   - Publish templates
   - Ratings & reviews
   - Template updates

4. **Customization**
   - User preferences
   - Custom themes
   - Keyboard shortcuts
   - Layout configurations

---

## 📊 Data Models

### Template Model
```typescript
interface Template {
  name: string;                    // Internal ID
  display_name: string;            // Human-readable name
  type: 'application' | 'extension' | 'microservice' | 'component';
  category: string;                // e.g., 'editor', 'viewer', 'service'
  description: string;
  version?: string;
  documentation?: string;
  thumbnail?: string;
  icon?: string;
  color_scheme?: {
    primary?: string;
    accent?: string;
  };
  connectors: Connector[];
  metadata?: {
    author?: string;
    tags?: string[];
    license?: string;
  };
}
```

### Connector Model
```typescript
interface Connector {
  name: string;
  type: string;                    // e.g., 'usd_stage', 'websocket'
  direction: 'input' | 'output' | 'bidirectional';
}
```

### Project Model
```typescript
interface Project {
  id: string;
  name: string;
  displayName: string;
  path: string;
  kitFile: string;
  status: 'ready' | 'building' | 'running' | 'error';
  lastModified: number;
  templates: string[];
  connections: Connection[];
  configuration: Record<string, any>;
  outputPath: string;
  hotReload?: boolean;
  runningTemplates?: string[];
}
```

### Connection Model
```typescript
interface Connection {
  from: string;                    // Template ID
  fromConnector: string;           // Connector name
  to: string;                      // Template ID
  toConnector: string;             // Connector name
}
```

### Log Entry Model
```typescript
interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'success' | 'debug';
  source: 'build' | 'runtime' | 'system';
  message: string;
}
```

### Workflow State Model
```typescript
type WorkflowStep = 'browse' | 'edit' | 'preview';

interface WorkflowState {
  step: WorkflowStep;
  selectedTemplate: string | null;
  selectedProject: string | null;
  isRunning: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
}

interface WorkflowNode {
  id: string;
  label: string;
  type: 'template' | 'project' | 'category';
  icon?: string;
  children?: WorkflowNode[];
  expanded?: boolean;
}
```

---

## 🔌 Integration Points

### Backend Integration

```
Frontend ←→ Backend Communication:

REST API:
├── Template operations
├── Project CRUD
├── Filesystem access
└── Configuration

WebSocket (Socket.IO):
├── Real-time logs
├── Build progress
├── Runtime output
└── System events

Backend ←→ System:
├── repo.sh (build/launch)
├── Template API (unified)
├── Xpra Manager (display)
└── Filesystem (read/write)
```

### External Systems

```
Kit Playground ←→ External:

Template System:
└── tools/repoman/template_api.py
    ├── TemplateAPI class
    ├── Template discovery
    ├── Generation
    └── License management

Build System:
└── repo.sh
    ├── build command
    ├── launch command
    └── Environment setup

Display Server:
└── Xpra (optional)
    ├── Session management
    ├── App streaming
    └── Web client
```

---

## 📝 Testing Strategy

### Current Testing
- Manual testing only
- `test_backend.sh` script (basic health checks)

### Recommended Testing

**Unit Tests:**
```
Frontend:
├── Redux slices (actions, reducers)
├── API service functions
├── Utility functions
└── Custom hooks

Backend:
├── API route handlers
├── Template API integration
├── Filesystem operations
└── Project management logic
```

**Integration Tests:**
```
├── Template loading flow
├── Project creation flow
├── Build process
├── WebSocket communication
└── File operations
```

**E2E Tests (Future):**
```
├── Complete user workflows
├── Template selection → project creation
├── Edit → build → run
└── Error handling scenarios
```

---

## 🔮 Future Vision

### Short Term (Next Sprint)
- [ ] Fix save functionality
- [ ] Implement basic Xpra preview
- [ ] Add project persistence
- [ ] Improve error handling
- [ ] Add loading states
- [ ] Optimize template loading

### Medium Term (Next Quarter)
- [ ] Complete visual connection editor
- [ ] Enhanced template customization
- [ ] Project workspace management
- [ ] Performance optimizations
- [ ] Comprehensive testing
- [ ] Documentation improvements

### Long Term (6+ Months)
- [ ] AI-powered features
- [ ] Marketplace integration
- [ ] Collaboration tools
- [ ] Cloud deployment
- [ ] Mobile-responsive design
- [ ] Accessibility improvements

---

## 📚 Additional Resources

### Documentation
- [README.md](README.md) - Quick start guide
- [DEV_GUIDE.md](DEV_GUIDE.md) - Development guidelines
- [BUILD.md](BUILD.md) - Build instructions
- [XPRA_SETUP.md](XPRA_SETUP.md) - Xpra configuration

### Related Components
- `tools/repoman/` - Template system
- `templates/` - Template definitions
- `source/apps/` - Generated projects

### External References
- [Material-UI Documentation](https://mui.com/)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO](https://socket.io/)

---

## 🏁 Conclusion

This mind-map provides a comprehensive overview of the Kit Playground UI architecture. Use this as a reference for:

1. **Onboarding:** Understanding the codebase structure
2. **Planning:** Identifying improvement areas
3. **Development:** Navigating the component hierarchy
4. **Debugging:** Tracing data flow and state changes
5. **Refactoring:** Making informed architectural decisions

The progressive disclosure workflow (Browse → Edit → Preview) is the central design pattern, with supporting features built around this core user journey.

---

**Last Updated:** October 4, 2025
**Version:** 1.0
**Status:** Active Development
