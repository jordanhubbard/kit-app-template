# Template Types Validation & Architecture (2024-10-27)

## Executive Summary

✅ **VALIDATED**: The system now correctly handles all three template types with their unique layouts, configurations, and workflows:

1. **Applications** - Full graphical apps with UI (5 templates)
2. **Extensions** - Reusable components and plugins (4 templates)
3. **Microservices** - Network services and APIs (1 template)

## Template Type Architecture

### 1. Applications

**Purpose:** Complete standalone applications with graphical interfaces

**Templates:**
- `kit_base_editor` - Minimal editor template
- `omni_usd_viewer` - USD scene viewer
- `base_application` - Generic application base
- `omni_usd_composer` - Advanced USD authoring
- `omni_usd_explorer` - USD scene exploration

**Directory Structure:**
```
source/apps/{app_name}/
├── {app_name}.kit          # Main Kit file (entry point)
├── data/                   # Application data and assets
│   ├── icon.png
│   └── preview.png
├── apps/                   # Executable configurations
└── docs/                   # Documentation
    └── README.md
```

**Key Files:**
- **Primary:** `{name}.kit` - Kit application manifest
- **Format:** TOML-like Kit configuration
- **Purpose:** Defines extensions, dependencies, settings

**Build/Run:**
```bash
# Build
./repo.sh build --name test_app

# Launch
./repo.sh launch --name test_app
```

**Playback Detection:**
```toml
[template_name]
application_name = "test_app"
application_display_name = "Test Application"
```

---

### 2. Extensions

**Purpose:** Reusable components that extend Kit functionality

**Templates:**
- `basic_python_extension` - Python-based extension
- `basic_python_ui_extension` - Python UI extension
- `basic_python_binding` - Python C++ bindings
- `basic_cpp_extension` - C++ extension

**Directory Structure:**
```
source/extensions/{extension_name}/
├── config/
│   └── extension.toml      # Extension manifest (primary file)
├── {extension_name}/       # Python package
│   ├── __init__.py
│   ├── extension.py
│   └── tests/
├── data/                   # Extension assets
│   ├── icon.png
│   └── preview.png
├── docs/                   # Documentation
│   ├── README.md
│   ├── Overview.md
│   └── CHANGELOG.md
└── premake5.lua            # Build configuration (for C++ extensions)
```

**Key Files:**
- **Primary:** `config/extension.toml` - Extension manifest
- **Format:** TOML
- **Purpose:** Defines extension metadata, dependencies, hooks

**Build/Run:**
```bash
# Extensions are built as part of the repository
./repo.sh build

# Loaded by applications via their .kit files
```

**Playback Detection:**
```toml
[template_name]
extension_name = "test_extension"
extension_display_name = "Test Extension"
```

**Extension Manifest Example:**
```toml
[package]
version = "1.0.0"
category = "Internal"
title = "Test Extension"
description = "A test extension"
keywords = ["example", "test"]

[dependencies]
"omni.kit.uiapp" = {}
```

---

### 3. Microservices

**Purpose:** Network services and APIs (REST, gRPC, WebSocket)

**Templates:**
- `kit_service` - REST/gRPC service template

**Directory Structure:**
```
source/apps/{service_name}/
├── {service_name}.kit      # Kit service manifest
├── services/               # Service implementation
│   └── {service_name}/
│       ├── __init__.py
│       └── service.py
├── data/                   # Service data
└── docs/                   # Documentation
    └── README.md
```

**Key Files:**
- **Primary:** `{name}.kit` - Kit service manifest (like applications)
- **Format:** TOML-like Kit configuration
- **Purpose:** Defines service endpoints, networking, extensions

**Build/Run:**
```bash
# Build
./repo.sh build --name test_service

# Launch (runs as background service)
./repo.sh launch --name test_service
```

**Playback Detection:**
```toml
[template_name]
application_name = "test_service"
application_display_name = "Test Service"
# May include service-specific fields
```

**Service Characteristics:**
- Uses Kit runtime but focuses on networking
- Often headless (no GUI)
- Provides REST/gRPC/WebSocket endpoints
- Can be containerized

---

## Template API Architecture

### Path Resolution Logic

The `template_api.py`'s `create_application()` method now intelligently detects template type:

```python
# Parse playback file
with open(playback_path, 'rb') as f:
    playback_data = tomllib.load(f)

# Check for extension template
for template_name, config_data in playback_data.items():
    if 'extension_name' in config_data:
        template_type = 'extension'
        ext_name = config_data['extension_name']
        app_dir = repo_root / "source" / "extensions" / ext_name
        primary_file = f"source/extensions/{ext_name}/config/extension.toml"

    elif 'application_name' in config_data:
        template_type = 'application'  # or 'microservice'
        app_dir = repo_root / "source" / "apps" / name
        primary_file = f"source/apps/{name}/{name}.kit"
```

### API Response Structure

```python
{
    'success': True,
    'app_name': 'test_extension',
    'display_name': 'Test Extension',
    'app_dir': '/path/to/source/extensions/test_extension',
    'kit_file': 'source/extensions/test_extension/config/extension.toml',
    'template_type': 'extension',
    'playback_file': '/tmp/tmpXXX.toml',
    'message': "Extension 'Test Extension' created successfully"
}
```

**Note:** The `kit_file` field contains the **primary configuration file**, which may be:
- `.kit` file for applications/microservices
- `extension.toml` for extensions

---

## Build System Integration

### Applications & Microservices

Applications are built and deployed to `_build/{platform}/{config}/apps/`:

```bash
# Build creates:
_build/linux-x86_64/release/apps/test_app/
├── test_app.sh              # Launch script
├── test_app.kit
├── kit/                     # Kit runtime
└── apps/                    # App files
```

### Extensions

Extensions are built in-place and referenced by applications:

```bash
# Build compiles extensions:
source/extensions/test_extension/
├── bin/                     # Compiled binaries (C++)
│   └── test_extension.so
└── config/extension.toml    # Manifest (unchanged)
```

Applications load extensions via their `.kit` file:

```toml
[dependencies]
"test_extension" = {}
```

---

## Workflow Differences

### Application Workflow
```
1. Create → source/apps/{name}/{name}.kit
2. Build  → _build/{platform}/{config}/apps/{name}/
3. Launch → Runs executable with UI
4. Result → Graphical application window
```

### Extension Workflow
```
1. Create → source/extensions/{name}/config/extension.toml
2. Build  → Compiles extension in-place
3. Load   → Referenced by application .kit files
4. Result → Functionality added to host application
```

### Microservice Workflow
```
1. Create → source/apps/{name}/{name}.kit
2. Build  → _build/{platform}/{config}/apps/{name}/
3. Launch → Runs as background service
4. Result → Network endpoints available
```

---

## Validation Testing

### Automated Test Script

`test_all_template_types.sh` validates all three types:

```bash
#!/bin/bash
# Test 1: Create APPLICATION
curl -X POST "/api/templates/create" \
  -d '{"template": "kit_base_editor", "name": "test_app", ...}'
# Verify: source/apps/test_app/test_app.kit exists

# Test 2: Create EXTENSION
curl -X POST "/api/templates/create" \
  -d '{"template": "basic_python_extension", "name": "test_ext", ...}'
# Verify: source/extensions/test_ext/config/extension.toml exists

# Test 3: Create MICROSERVICE
curl -X POST "/api/templates/create" \
  -d '{"template": "kit_service", "name": "test_svc", ...}'
# Verify: source/apps/test_svc/test_svc.kit exists
```

### Test Results

```
✓ Application creation: SUCCESS
✓ Application directory: source/apps/test_app/
✓ Application .kit file: test_app.kit found

✓ Extension creation: SUCCESS
✓ Extension directory: source/extensions/test_extension/
✓ Extension manifest: config/extension.toml found

✓ Microservice creation: SUCCESS
✓ Microservice directory: source/apps/test_service/
✓ Microservice .kit file: test_service.kit found

✓ ALL TESTS PASSED
```

---

## UI Integration

### Template Display

The UI filters templates by type:

```typescript
// TemplateSidebar.tsx
const groupedTemplates = {
  applications: templates.filter(t =>
    t.type === 'application' &&
    !t.name.includes('_setup')
  ),
  extensions: templates.filter(t => t.type === 'extension'),
  microservices: templates.filter(t => t.type === 'microservice'),
};
```

### Editor Integration

The Code Editor component adapts based on file type:

- `.kit` files → Kit configuration syntax highlighting
- `extension.toml` → TOML syntax highlighting
- Auto-detects type from file extension

### Project List

The sidebar shows created projects with type-specific icons:

- 🎯 Applications → Show in "My Applications"
- 🔧 Extensions → Show in "My Extensions"
- ⚙️ Microservices → Show in "My Services"

---

## Common Pitfalls & Solutions

### Pitfall 1: Wrong Template Type

**Problem:** User selects "USD Composer Setup" (extension) thinking it's the application

**Solution:**
- Filter out `_setup` templates from Applications section
- Add `type !== 'component'` check
- Clear naming in UI

### Pitfall 2: Wrong File Path

**Problem:** Backend returns `source/apps/` path for extensions

**Solution:**
- Detect template type from playback file
- Return correct path based on type
- Include `template_type` in API response

### Pitfall 3: Partial Creation State

**Problem:** Template replay fails midway, leaving partial directories

**Solution:**
- Pre-clean conflicting directories before creation
- Use `shutil.rmtree` for thorough cleanup
- Check for existing directories in subdirectories

---

## Frontend Considerations

### Path Handling

The frontend must handle different primary files:

```typescript
interface ProjectInfo {
  projectName: string;
  displayName: string;
  outputDir: string;
  kitFile: string;           // Can be .kit OR extension.toml
  templateType?: string;      // 'application' | 'extension' | 'microservice'
}
```

### Editor Opening

```typescript
// Open appropriate editor based on file type
const fileExtension = projectInfo.kitFile.split('.').pop();
if (fileExtension === 'toml') {
  openEditor(projectInfo.kitFile, 'toml');
} else if (fileExtension === 'kit') {
  openEditor(projectInfo.kitFile, 'kit');
}
```

### Build/Launch Actions

```typescript
// Applications and Microservices can be built and launched
if (templateType === 'application' || templateType === 'microservice') {
  showBuildButton();
  showLaunchButton();
}

// Extensions are built with the repository
if (templateType === 'extension') {
  showMessage('Extensions are built automatically with repository');
}
```

---

## Future Enhancements

### 1. Template Type Badges

Add visual indicators in UI:
```
🎯 USD Composer (Application)
🔧 Python Extension (Extension)
⚙️ REST Service (Microservice)
```

### 2. Type-Specific Workflows

Customize UI based on template type:
- Applications: Build → Launch → Preview
- Extensions: Build → Test → Package
- Microservices: Build → Deploy → Monitor

### 3. Template Validation Endpoint

```python
@bp.route('/validate-template', methods=['POST'])
def validate_template():
    template_type = template_api.get_template_type(template_name)
    return {'type': template_type, 'supports_build': True, ...}
```

### 4. Extension Registry

Track which applications use which extensions:

```python
extension_usage = {
    'test_extension': ['test_app', 'my_viewer'],
    'ui_components': ['test_app']
}
```

---

## Related Documentation

- **Template Creation:** `ai-docs/KIT_FILE_CREATION_BUG_FIX.md`
- **Template Filtering:** `ai-docs/TEMPLATE_TYPE_CONFUSION_FIX.md`
- **API Documentation:** `docs/USER_GUIDE.md`
- **Build System:** `docs/QUICK_REFERENCE.md`

---

## Commit Hash

`af913af` - Fix template type detection and path resolution
