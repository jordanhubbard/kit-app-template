# Kit App Template Architecture Diagrams

**Version**: 2.0 (All 6 Phases Complete)
**Last Updated**: October 24, 2025

This document contains comprehensive Mermaid diagrams illustrating the architecture and workflows of the enhanced Kit App Template system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Template Creation Flow](#template-creation-flow)
3. [CLI Architecture](#cli-architecture)
4. [API Architecture](#api-architecture)
5. [Job Management](#job-management)
6. [Per-App Dependencies](#per-app-dependencies)
7. [Standalone Projects](#standalone-projects)
8. [Phase Evolution](#phase-evolution)

---

## System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI[CLI - repo.sh]
        API[REST API - Flask]
        UI[Web UI - React]
        Scripts[Scripts - curl/Python]
    end

    subgraph "Core Components"
        Dispatcher[repo_dispatcher.py]
        Engine[template_engine.py]
        TemplateAPI[template_api.py]
        Repoman[repoman.py]
        Launch[launch.py]
    end

    subgraph "Phase 5 & 6 Features"
        Standalone[standalone_generator.py]
        AppDeps[app_dependencies.py]
    end

    subgraph "Phase 3b/4 Features"
        JobMgr[job_manager.py]
        WebSocket[websocket_routes.py]
        Docs[docs_routes.py - OpenAPI]
    end

    subgraph "Infrastructure"
        Packman[Packman - Dependencies]
        Premake[Premake5 - Build System]
        KitSDK[Kit SDK]
        Templates[Template Definitions - TOML]
    end

    CLI --> Dispatcher
    API --> TemplateAPI
    UI --> API
    Scripts --> API

    Dispatcher --> Engine
    TemplateAPI --> Engine
    Engine --> Repoman
    Dispatcher --> Repoman
    Dispatcher --> Launch

    Engine -.->|metadata| Standalone
    Engine -.->|metadata| AppDeps
    Dispatcher -->|post-process| Standalone
    Dispatcher -->|post-process| AppDeps

    API --> JobMgr
    API --> WebSocket
    API --> Docs

    Repoman --> Packman
    Repoman --> Premake
    Launch --> KitSDK
    Engine --> Templates

    AppDeps -.->|per-app| KitSDK
```

### Component Layers

```mermaid
graph TD
    subgraph "Presentation Layer"
        A1[CLI Interface]
        A2[REST API]
        A3[Web UI]
    end

    subgraph "Application Layer"
        B1[Command Routing]
        B2[Template Engine]
        B3[Job Manager]
    end

    subgraph "Business Logic Layer"
        C1[Template Processing]
        C2[Build Orchestration]
        C3[Dependency Management]
        C4[Launch Management]
    end

    subgraph "Infrastructure Layer"
        D1[Packman]
        D2[Premake5]
        D3[Kit SDK]
        D4[File System]
    end

    A1 --> B1
    A2 --> B2
    A2 --> B3
    A3 --> A2

    B1 --> C1
    B2 --> C1
    B3 --> C2

    C1 --> C2
    C2 --> C3
    C2 --> C4

    C3 --> D1
    C2 --> D2
    C4 --> D3
    C1 --> D4
```

---

## Template Creation Flow

### Standard Template Creation

```mermaid
sequenceDiagram
    participant User
    participant CLI as repo.sh
    participant Dispatcher as repo_dispatcher
    participant Engine as template_engine
    participant Repoman as repoman.py
    participant FS as File System

    User->>CLI: ./repo.sh template new kit_base_editor --name my.app
    CLI->>Dispatcher: Parse arguments
    Dispatcher->>Engine: Generate template(kit_base_editor, my.app)
    Engine->>Engine: Load template.toml
    Engine->>Engine: Process parameters
    Engine->>Engine: Generate playback.toml
    Engine->>Dispatcher: Return playback_file path
    Dispatcher->>Repoman: template replay playback.toml
    Repoman->>FS: Create source/apps/my.app.kit
    Repoman->>Dispatcher: Success
    Dispatcher->>Dispatcher: Fix application structure
    Dispatcher->>FS: Move to source/apps/my.app/my.app.kit
    Dispatcher->>User: ✓ Application created
```

### Template Creation with JSON Mode

```mermaid
sequenceDiagram
    participant User
    participant CLI as repo.sh
    participant Dispatcher as repo_dispatcher
    participant Engine as template_engine
    participant Repoman as repoman.py

    User->>CLI: ./repo.sh template new ... --json
    CLI->>Dispatcher: Parse args (--json detected)
    Dispatcher->>Dispatcher: Enable quiet mode
    Dispatcher->>Engine: Generate with --json flag
    Engine->>Engine: Process template
    Engine->>Engine: Generate JSON output
    Engine-->>Dispatcher: JSON to stdout
    Note over Dispatcher: Parse JSON, extract playback_file
    Dispatcher->>Repoman: template replay (quiet)
    Repoman->>Repoman: Create files (output suppressed)
    Repoman-->>Dispatcher: Success
    Dispatcher->>Dispatcher: Post-process (quiet)
    Dispatcher-->>User: Pure JSON output to stdout
```

---

## CLI Architecture

### Command Flow

```mermaid
flowchart TB
    Start([User Command]) --> Parse[Parse Arguments]
    Parse --> Route{Command Type}

    Route -->|template| TemplateCmd{Sub-Command}
    Route -->|build| BuildCmd[Build Command]
    Route -->|launch| LaunchCmd[Launch Command]

    TemplateCmd -->|list| ListTemplates[List Templates]
    TemplateCmd -->|docs| ShowDocs[Show Documentation]
    TemplateCmd -->|new| NewTemplate[Create from Template]

    NewTemplate --> CheckFlags{Flags Present?}

    CheckFlags -->|--json| JSONMode[JSON Output Mode]
    CheckFlags -->|--verbose| VerboseMode[Verbose Output]
    CheckFlags -->|--quiet| QuietMode[Minimal Output]
    CheckFlags -->|--standalone| StandaloneMode[Standalone Project]
    CheckFlags -->|--per-app-deps| PerAppMode[Per-App Dependencies]
    CheckFlags -->|none| NormalMode[Normal Output]

    JSONMode --> CallEngine[Call template_engine]
    VerboseMode --> CallEngine
    QuietMode --> CallEngine
    NormalMode --> CallEngine

    CallEngine --> Engine[template_engine.py]
    Engine --> GeneratePlayback[Generate Playback]
    GeneratePlayback --> Replay[Template Replay]
    Replay --> PostProcess[Post-Processing]

    StandaloneMode --> PostProcess
    PerAppMode --> PostProcess

    PostProcess --> End([Complete])
```

### Flag Processing

```mermaid
graph LR
    subgraph "Input Flags"
        F1[--json]
        F2[--verbose]
        F3[--quiet]
        F4[--accept-license]
        F5[--standalone]
        F6[--per-app-deps]
    end

    subgraph "Processing"
        P1[repo_dispatcher]
        P2[template_engine]
    end

    subgraph "Output Mode"
        O1[JSON to stdout]
        O2[Verbose to stderr]
        O3[Minimal output]
        O4[Normal output]
    end

    subgraph "Metadata"
        M1[_standalone_project]
        M2[_per_app_deps]
    end

    F1 --> P1
    F2 --> P1
    F3 --> P1
    F1 --> P2
    F2 --> P2
    F3 --> P2

    P2 --> O1
    P2 --> O2
    P2 --> O3
    P2 --> O4

    F5 --> P2 --> M1
    F6 --> P2 --> M2

    F4 --> P1
```

---

## API Architecture

### REST API Structure

```mermaid
graph TB
    subgraph "Client"
        Browser[Web Browser]
        Script[curl/Python Script]
        UI[React UI]
    end

    subgraph "Flask Application"
        Flask[Flask Web Server]

        subgraph "Routes"
            TemplateRoutes[template_routes.py]
            JobRoutes[job_routes.py]
            WebSocketRoutes[websocket_routes.py]
            DocsRoutes[docs_routes.py]
        end

        subgraph "Core Logic"
            TemplateAPI[template_api.py]
            JobManager[job_manager.py]
            SocketIO[Socket.IO]
        end
    end

    subgraph "Backend"
        Engine[template_engine.py]
        Repoman[repoman.py]
    end

    Browser --> Flask
    Script --> Flask
    UI --> Flask

    Flask --> TemplateRoutes
    Flask --> JobRoutes
    Flask --> WebSocketRoutes
    Flask --> DocsRoutes

    TemplateRoutes --> TemplateAPI
    JobRoutes --> JobManager
    WebSocketRoutes --> SocketIO

    TemplateAPI --> Engine
    JobManager --> Repoman

    SocketIO -.->|real-time| Browser
    SocketIO -.->|real-time| UI
```

### API Endpoint Organization

```mermaid
graph LR
    subgraph "Template Management"
        T1[GET /api/templates/list]
        T2[GET /api/templates/get/name]
        T3[POST /api/templates/create]
    end

    subgraph "Job Management"
        J1[GET /api/jobs]
        J2[GET /api/jobs/id]
        J3[POST /api/jobs/id/cancel]
        J4[DELETE /api/jobs/id]
        J5[GET /api/jobs/stats]
    end

    subgraph "Documentation"
        D1[GET /api/docs]
        D2[GET /api/docs]
    end

    subgraph "WebSocket Events"
        W1[job_log]
        W2[job_progress]
        W3[job_status]
    end

    API[Flask App] --> T1
    API --> T2
    API --> T3
    API --> J1
    API --> J2
    API --> J3
    API --> J4
    API --> J5
    API --> D1
    API --> D2

    SocketIO[Socket.IO] -.-> W1
    SocketIO -.-> W2
    SocketIO -.-> W3
```

---

## Job Management

### Job Lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending: Job Submitted
    pending --> running: Start Execution
    running --> completed: Success
    running --> failed: Error
    pending --> cancelled: User Cancels
    running --> cancelled: User Cancels
    completed --> [*]
    failed --> [*]
    cancelled --> [*]

    note right of pending
        Job created
        Waiting for execution
    end note

    note right of running
        Task executing
        Progress updates
        Log streaming
    end note

    note right of completed
        Task successful
        Logs available
        Can be deleted
    end note
```

### Job Management Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as Flask API
    participant JobMgr as JobManager
    participant Worker as Background Worker
    participant WS as WebSocket

    Client->>API: POST /api/templates/create
    API->>JobMgr: submit_job(task, type, args)
    JobMgr->>JobMgr: Create Job (pending)
    JobMgr-->>API: Return job_id
    API-->>Client: {"job_id": "abc123", ...}

    JobMgr->>Worker: Start background task
    Worker->>Worker: Update status (running)
    Worker->>WS: Emit job_status
    WS-->>Client: Status update

    loop Task Execution
        Worker->>Worker: Execute step
        Worker->>WS: Emit job_log
        WS-->>Client: Log message
        Worker->>WS: Emit job_progress
        WS-->>Client: Progress %
    end

    Worker->>Worker: Complete task
    Worker->>WS: Emit job_status (completed)
    WS-->>Client: Completion notification

    Client->>API: GET /api/jobs/abc123
    API->>JobMgr: get_job(abc123)
    JobMgr-->>API: Job details
    API-->>Client: Complete job info + logs
```

---

## Per-App Dependencies

### Detection and Initialization

```mermaid
flowchart TB
    Start([Template Creation]) --> Flag{--per-app-deps?}

    Flag -->|No| GlobalDeps[Use Global Dependencies]
    Flag -->|Yes| AddMetadata[Add metadata to playback]

    AddMetadata --> Replay[Template Replay]
    Replay --> Created[App Created in source/apps/]

    Created --> DetectMeta{Metadata Present?}
    DetectMeta -->|Yes| InitDeps[Initialize Per-App Deps]
    DetectMeta -->|No| Done1[Complete]

    InitDeps --> CreateDir[Create dependencies/ dir]
    CreateDir --> CreateToml[Create kit-deps.toml]
    CreateToml --> SetConfig[Set default config]
    SetConfig --> Done2[Complete with Per-App Deps]

    GlobalDeps --> Done1
```

### Launch with Per-App Dependencies

```mermaid
sequenceDiagram
    participant User
    participant Launch as launch.py
    participant AppDeps as app_dependencies.py
    participant Kit as Kit SDK

    User->>Launch: ./repo.sh launch my.app
    Launch->>Launch: Get app path
    Launch->>AppDeps: should_use_per_app_deps(app_path)

    alt Has Per-App Dependencies
        AppDeps-->>Launch: True
        Launch->>AppDeps: get_app_kit_path(app_path)
        AppDeps-->>Launch: source/apps/my.app/_kit
        Launch->>Launch: Set environment variables
        Note over Launch: CARB_APP_PATH=.../my.app/_kit/kit<br/>PATH=.../my.app/_kit/kit/kit:$PATH
        Launch->>Kit: Launch with app-specific Kit
    else No Per-App Dependencies
        AppDeps-->>Launch: False
        Launch->>Kit: Launch with global Kit
    end

    Kit-->>User: Application Running
```

### Directory Structure

```mermaid
graph TD
    subgraph "Global Dependencies (Default)"
        G1[_build/]
        G2[_build/linux-x86_64/release/]
        G3[_build/linux-x86_64/release/kit/]
        G1 --> G2
        G2 --> G3
    end

    subgraph "Per-App Dependencies"
        A1[source/apps/my.app/]
        A2[source/apps/my.app/dependencies/]
        A3[source/apps/my.app/dependencies/kit-deps.toml]
        A4[source/apps/my.app/_kit/]
        A5[source/apps/my.app/_kit/kit/]
        A1 --> A2
        A2 --> A3
        A1 --> A4
        A4 --> A5
    end

    App[Application] -.->|uses| G3
    App -.->|OR uses| A5
```

---

## Standalone Projects

### Generation Flow

```mermaid
flowchart TB
    Start([User Command --standalone]) --> Engine[template_engine.py]
    Engine --> AddMeta[Add _standalone_project metadata]
    AddMeta --> SavePlayback[Save to playback.toml]

    SavePlayback --> Dispatcher[repo_dispatcher.py]
    Dispatcher --> Replay[Template Replay]
    Replay --> AppCreated[App created in source/apps/]

    AppCreated --> DetectStandalone{Standalone metadata?}
    DetectStandalone -->|Yes| StandaloneGen[standalone_generator.py]
    DetectStandalone -->|No| Done1[Complete]

    StandaloneGen --> CopyApp[Copy application files]
    CopyApp --> CopyTools[Copy build tools]
    CopyTools --> CopyDeps[Copy templates, packman]
    CopyDeps --> ModifyScripts[Modify repo.sh/bat for standalone]
    ModifyScripts --> CreateReadme[Generate README]
    CreateReadme --> Done2[Standalone Project Complete]
```

### Standalone Project Structure

```mermaid
graph TD
    Root[Standalone Project Root]

    Root --> R1[repo.sh - modified]
    Root --> R2[repo.bat - modified]
    Root --> R3[README.md - generated]

    Root --> Source[source/]
    Source --> Apps[apps/]
    Apps --> MyApp[my.app/]
    MyApp --> Kit[my.app.kit]

    Root --> Tools[tools/]
    Tools --> Packman[packman/]
    Tools --> Repoman[repoman/ - subset]

    Root --> Templates[templates/]
    Templates --> App Templates[applications/]
    AppTemplates --> KitBase[kit_base_editor/]

    Root --> BuildDir[_build/ - created on first build]
```

---

## Phase Evolution

### System Growth Across Phases

```mermaid
timeline
    title Enhancement Phases Timeline
    section Phase 1
        Compatibility Testing : 29 baseline tests
                              : All templates validated
                              : Build and launch verified
    section Phase 2
        CLI Enhancement : --json, --verbose, --quiet
                        : --accept-license, --batch-mode
                        : 26 CLI tests
                        : Zero breaking changes
    section Phase 3
        API Foundation : REST API endpoints
                       : Template CRUD
                       : 20 API tests
                       : CLI-API equivalence
    section Phase 3b/4
        Backend Ready : Job management (18 tests)
                      : WebSocket streaming
                      : OpenAPI docs (6 tests)
                      : 44 total API tests
    section Phase 5
        Standalone Projects : Self-contained generation
                            : Portable applications
                            : 4 integration tests
    section Phase 6
        Per-App Dependencies : Isolated Kit SDK
                             : Version isolation
                             : 23 unit/integration tests
                             : 120+ total tests
```

### Feature Dependencies

```mermaid
graph TB
    P1[Phase 1:<br/>Compatibility Testing]
    P2[Phase 2:<br/>CLI Enhancement]
    P3[Phase 3:<br/>API Foundation]
    P3b[Phase 3b/4:<br/>Backend Ready]
    P5[Phase 5:<br/>Standalone Projects]
    P6[Phase 6:<br/>Per-App Dependencies]

    P1 --> P2
    P2 --> P3
    P3 --> P3b
    P2 --> P5
    P2 --> P6

    P1 -.->|baseline for| P2
    P1 -.->|baseline for| P3
    P1 -.->|baseline for| P5
    P1 -.->|baseline for| P6

    P2 -.->|flags used by| P5
    P2 -.->|flags used by| P6
    P3 -.->|infrastructure for| P3b
```

### Component Addition Timeline

```mermaid
gantt
    title Component Development Timeline
    dateFormat YYYY-MM-DD
    section Testing
    Compatibility Tests       :done, 2025-10-01, 2d
    section CLI
    CLI Flags & JSON Mode    :done, 2025-10-03, 2d
    section API
    REST API Foundation      :done, 2025-10-05, 1d
    Job Management          :done, 2025-10-06, 2d
    WebSocket & Docs        :done, 2025-10-08, 1d
    section Projects
    Standalone Generator    :done, 2025-10-09, 2d
    Per-App Dependencies    :done, 2025-10-11, 3d
    section Enhancement
    JSON Mode Improvements  :done, 2025-10-24, 1d
```

---

## Legend

### Node Types

- **Rectangle**: Process or Component
- **Diamond**: Decision Point
- **Cylinder**: Data Storage
- **Rounded Rectangle**: External System
- **Parallelogram**: Input/Output
- **Circle**: Start/End Point

### Line Types

- **Solid Line** (→): Direct flow or dependency
- **Dotted Line** (⋯→): Optional or conditional flow
- **Dashed Line** (--→): Metadata or configuration

### Colors (when rendered)

- **Blue**: User-facing components
- **Green**: Core processing
- **Yellow**: Infrastructure
- **Purple**: New features (Phase 5/6)
- **Orange**: API/Backend (Phase 3/4)

---

## Viewing Diagrams

These diagrams use **Mermaid** syntax and can be viewed in:

1. **GitHub**: Natively supports Mermaid diagrams
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Mermaid Live Editor**: https://mermaid.live/
4. **Documentation Sites**: Most modern static site generators support Mermaid

---

## Additional Resources

- **Architecture Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **CLI Guide**: [README.md](README.md)
- **API Usage**: [API_USAGE.md](API_USAGE.md)
- **CLI Workflow Diagram**: [CLI_WORKFLOW_DIAGRAM.md](CLI_WORKFLOW_DIAGRAM.md)

---

**For interactive diagram editing, visit**: https://mermaid.live/
