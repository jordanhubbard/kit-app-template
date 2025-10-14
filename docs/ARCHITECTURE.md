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
            │   repo_dispatcher.py   │
            │   (Enhanced Router)    │
            ├────────────────────────┤
            │ - Command routing      │
            │ - Template preprocessing│
            │ - Delegates to repoman │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Template Engine      │
            │   (template_engine.py) │
            ├────────────────────────┤
            │ - TOML-driven config   │
            │ - Template discovery   │
            │ - Variable interpolation│
            │ - Playback generation  │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   repoman.py           │
            │   (Core Build System)  │
            ├────────────────────────┤
            │ - Template replay      │
            │ - Build execution      │
            │ - Launch management    │
            └────────────────────────┘
```

## Components

### 1. CLI Interface (Primary, Monolithic)

**Location:** `tools/repoman/`

**Key Files:**
- `repo_dispatcher.py` - OS-independent command router with enhanced template support
- `template_engine.py` - TOML-driven template discovery and generation engine
- `repoman.py` - Core build system (template replay, build, launch)

**Characteristics:**
- **Standalone operation** - Works without any background services
- **Direct execution** - Commands run, complete, and exit immediately
- **No hanging** - All operations are synchronous and deterministic
- **Cross-platform** - Works on Linux, Windows, and macOS
- **Data-driven** - Templates defined via TOML configuration files

**Example Usage:**
```bash
# These work immediately with no web server:
./repo.sh template list
./repo.sh template new kit_base_editor --name my_company.my_app
./repo.sh template docs kit_base_editor
./repo.sh build --config release
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

### 3. Template System (Data-Driven Architecture)

**Location:** `tools/repoman/template_engine.py` + `templates/`

**Purpose:** Provides TOML-driven template discovery, configuration, and generation.

**Key Components:**

#### Template Discovery
- Templates organized hierarchically: `templates/{type}/{category}/{name}/template.toml`
- Types: `applications`, `extensions`, `microservices`, `components`
- Registry-driven discovery via `templates/template_registry.toml`
- Pattern-based discovery: `applications/*/template.toml`, `extensions/*/*/template.toml`

#### Template Configuration
- **template.toml** - Main template definition file
- **template_registry.toml** - Global template catalog and relationships
- **config/*.toml** - Shared configuration bases (base.toml, nvidia.toml)
- Variable interpolation with `{{variable_name}}` syntax
- Configuration inheritance via `extends` field

#### Template Generation Workflow
1. **Discovery** - Find all templates via registry patterns
2. **Configuration** - Load template.toml + merge inherited configs
3. **Validation** - Check required fields and variables
4. **Playback Generation** - Create .kit-template-playback.toml file
5. **Replay** - Execute playback via repoman.py
6. **Post-processing** - Restructure to `_build/apps/{name}/` directory

#### Application Structure (Post-Generation)
```
_build/apps/{app_name}/
├── {app_name}.kit           # Main application configuration
├── .project-meta.toml       # Project metadata
├── README.md                # Documentation
├── repo.sh                  # Wrapper script (finds repo root)
└── repo.bat                 # Windows wrapper script
```

**Architecture Benefits:**
- **Data-driven** - Templates are pure configuration, not code
- **Self-documenting** - Metadata and docs embedded in TOML
- **Extensible** - Add templates without modifying engine code
- **Versionable** - Templates tracked in git with full history
- **Testable** - Validation built into template system

## How They Work Together

### CLI-Only Workflow (Template Generation)

```
User runs: ./repo.sh template new kit_base_editor --name my_company.my_app
       ↓
repo.sh bootstraps environment → repo_dispatcher.py
       ↓
repo_dispatcher.py parses arguments and routes to template engine
       ↓
template_engine.py:
  1. Discovers template via template_registry.toml
  2. Loads templates/applications/kit_base_editor/template.toml
  3. Merges inherited configurations (extends: base_application)
  4. Interpolates variables: {{application_name}} → my_company.my_app
  5. Generates .kit-template-playback.toml
       ↓
repoman.py replays playback:
  - Creates files in source/apps/
  - Copies template content
       ↓
repo_dispatcher.py post-processing:
  - Moves from source/apps/ to _build/apps/{name}/
  - Creates {name}.kit, README.md, .project-meta.toml
  - Generates wrapper scripts (repo.sh, repo.bat)
  - Creates symlink _build/apps/{name}.kit → {name}/{name}.kit
       ↓
Command completes and exits
```

**Duration:** Seconds (synchronous, completes immediately)
**Dependencies:** Python 3.8+, TOML library (auto-installed)
**Output:** Self-contained application directory in `_build/apps/{name}/`

### Playground Workflow (Client-Server)

```
User runs: ./repo.sh playground
       ↓
repo.sh checks for npm, installs dependencies if needed
       ↓
Launches React dev server (Vite) on default port
       ↓
Browser opens UI at http://localhost:5173
       ↓
User interacts with visual interface
       ↓
UI makes direct API calls (future: will use Flask backend)
       ↓
Currently: UI demonstrates template browser/editor concept
       ↓
Server keeps running until stopped (Ctrl+C)
```

**Duration:** Runs continuously until stopped
**Dependencies:** Node.js (v18+), npm
**Note:** Playground integration with template_engine.py is planned

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

### Decision 3: TOML-Driven Template System

**Rationale:**
- **Data over code** - Templates are pure configuration, easy to author and validate
- **Self-documenting** - Metadata, docs, and config in one file (template.toml)
- **Version controlled** - Templates tracked alongside code, full git history
- **Hierarchical organization** - Clear structure: type/category/name
- **Extensible** - Add new templates without touching engine code
- **Playback-based** - Separation between template definition and execution
- **Variable interpolation** - `{{variable_name}}` syntax for customization
- **Configuration inheritance** - DRY via `extends` field

**Trade-off:** Requires learning TOML format and template conventions

### Decision 4: _build/apps Directory Structure

**Rationale:**
- **Self-contained apps** - Each app is a standalone directory with all needed files
- **Workspace isolation** - Build artifacts separated from source code
- **Multi-project support** - Multiple apps can coexist in one repository
- **Portable** - Apps include wrapper scripts to find repo root from any location
- **Metadata tracking** - `.project-meta.toml` records template, version, creation time
- **Symlinks for compatibility** - `{name}.kit` symlinks support existing workflows

**Trade-off:** Different structure than previous source/apps approach

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

## Template System Details

### Template Discovery Process

1. **Load Registry** - Read `templates/template_registry.toml`
2. **Apply Patterns** - Match discovery patterns against filesystem:
   - `applications/*/template.toml`
   - `extensions/*/*/template.toml`
   - `microservices/*/template.toml`
   - `components/*/*/template.toml`
3. **Parse Metadata** - Extract type, category, name from each template.toml
4. **Build Index** - Create searchable catalog with metadata

### Variable Interpolation

Templates support variable substitution using `{{variable_name}}` syntax:

**Example template.toml:**
```toml
[variables]
application_name = "my_company.my_app"
application_display_name = "My Application"

[files]
"{{application_name}}.kit" = "template/app.kit"
```

**Interpolated result:**
```
my_company.my_app.kit created from template/app.kit
```

### Configuration Inheritance

Templates can inherit from base templates using the `extends` field:

**base_application template.toml:**
```toml
[metadata]
type = "application"

[variables]
version = "0.1.0"
author = "My Company"
```

**kit_base_editor template.toml:**
```toml
[template]
extends = "base_application"  # Inherits version, author

[variables]
application_name = "my.editor"  # Adds specific variables
```

### Playback System

The template engine generates a `.kit-template-playback.toml` file that records:
- Files to create
- Content to copy
- Variables to interpolate
- Metadata to track

This playback file is then executed by `repoman.py` for reproducible generation.

## Future Enhancements

Potential architectural improvements while maintaining the monolithic CLI principle:

1. **Plugin system** - Allow custom CLI commands without modifying core
2. **Alternative UIs** - VSCode extension, JetBrains plugin (using template_engine.py)
3. **Cloud integration** - Optional cloud storage while keeping local-first design
4. **Performance optimization** - Cache template metadata to reduce load time
5. **Multiple template sources** - Support git repos, package managers as template sources
6. **Template composition** - Combine multiple templates (e.g., app + streaming + custom UI)
7. **Live preview** - Show what will be generated before committing
8. **Template validation tools** - CLI command to validate template.toml files

All enhancements must preserve the core principle: **CLI works standalone, always.**

## Testing the Architecture

### Verify CLI Independence

```bash
# Test CLI without ever starting playground
./repo.sh template list
./repo.sh template new kit_base_editor --name my_company.test_app
cd _build/apps/my_company.test_app
./repo.sh build --config release
./repo.sh launch
```

All commands should work without errors.

### Verify Playground Independence

```bash
# Start playground
./repo.sh playground

# In another terminal, verify CLI still works
./repo.sh template list
./repo.sh template new kit_base_editor --name another.app
```

Both should work simultaneously.

### Verify Template Engine Directly

```python
# Test template_engine.py directly
from tools.repoman.template_engine import TemplateEngine
from pathlib import Path

engine = TemplateEngine(repo_root=Path.cwd())
templates = engine.discover_templates()
print(f"Found {len(templates)} templates")

# Test template generation
engine.generate_template(
    template_name="kit_base_editor",
    variables={"application_name": "test.app"}
)
```

Should work without any server running.

### Verify Template Structure

```bash
# Check generated application structure
./repo.sh template new kit_base_editor --name test.verify
ls -la _build/apps/test.verify/

# Should show:
# - test.verify.kit (main config)
# - .project-meta.toml (metadata)
# - README.md (documentation)
# - repo.sh (wrapper script)
# - repo.bat (Windows wrapper)
```

### Verify Template Discovery

```bash
# List all templates by type
./repo.sh template list

# Show template documentation
./repo.sh template docs kit_base_editor

# Verify template registry
cat templates/template_registry.toml
```

## Conclusion

The kit-app-template architecture is designed around a **monolithic CLI with optional visual frontend** and a **data-driven template system**. This ensures:

- ✅ CLI commands work instantly without background services
- ✅ Playground provides visual alternative without interfering with CLI
- ✅ TOML-driven templates are self-documenting and version-controlled
- ✅ Template discovery and generation happens via declarative configuration
- ✅ Applications generated in isolated `_build/apps/{name}/` directories
- ✅ Simple deployment and troubleshooting
- ✅ Works in any environment (local, container, CI/CD)
- ✅ Extensible: add templates without modifying engine code

### Key Components Summary

1. **repo.sh/repo.bat** - Cross-platform entry point with environment bootstrapping
2. **repo_dispatcher.py** - Enhanced command router with template preprocessing
3. **template_engine.py** - TOML-driven template discovery, validation, and playback generation
4. **repoman.py** - Core build system that executes playback files
5. **template_registry.toml** - Central registry of all available templates
6. **template.toml** - Individual template definitions with metadata and configuration

This architecture prioritizes **reliability, simplicity, extensibility, and user choice** over architectural complexity.
