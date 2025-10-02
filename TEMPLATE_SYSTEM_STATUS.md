# Template System Status and Requirements

## Current State Analysis

### What Works ✅

1. **CLI with Full Arguments**
   ```bash
   ./repo.sh template new kit_base_editor --name=my_company.my_app --display-name="My App" --version=1.0.0
   ```
   - Works for simple templates without dependent extensions
   - Arguments are properly passed to template_engine.py
   - Generates playback file and creates template

2. **Template Discovery**
   ```bash
   ./repo.sh template list
   ./repo.sh template list --type=application
   ./repo.sh template docs kit_base_editor
   ```
   - All discovery commands work correctly
   - Templates loaded from template.toml files
   - Metadata and documentation displayed properly

3. **Python Dependency Auto-Installation**
   - `repo.sh` and `repo.bat` automatically check and install toml library
   - Works on first run on fresh systems

### What Needs Fixing 🔧

#### 1. **Templates with Required Extensions (FIXED ✅)**

**Issue:** Templates like `omni_usd_composer` that define setup extensions failed with error:
```
Error: Failed to generate template 'omni_usd_composer': 'list' object has no attribute 'get'
```

**Status: FIXED**
- Updated `_generate_playback()` to handle all TOML extension formats
- Now supports nested arrays: `[[extensions.setup]]`
- Automatically generates extension names based on app name
- Tested successfully with `omni_usd_composer`

#### 2. **License Acceptance (IMPLEMENTED ✅)**

**Status: IMPLEMENTED**
- Created `tools/repoman/license_manager.py` module
- Stores acceptance in `~/.omni/kit-app-template/license_accepted.json`
- Prompts user on first template generation
- Integrated into template_engine.py
- Does not prompt for `list` or `docs` commands
- Includes timestamp and version tracking

**CLI Usage:**
```bash
# Check acceptance status
./tools/packman/python.sh tools/repoman/license_manager.py --check

# Force re-acceptance
./tools/packman/python.sh tools/repoman/license_manager.py --force

# Show acceptance info
./tools/packman/python.sh tools/repoman/license_manager.py --info
```

**TODO:** Integrate into Kit Playground GUI

#### 3. **Application Layers Support**

**Old Behavior:**
```
? Do you want to add application layers? Yes
? Browse layers with arrow keys ↑↓: 1 layer selected
Creating selected ApplicationLayerTemplate.
Application Template -> omni_default_streaming
```

**Current Status:**
- Template engine has `add_layers` field in playback
- Defaults to "No"
- No CLI argument to specify layers
- No automatic layer discovery/application

**Fix Required:**
- Add `--add-layers` CLI argument
- Add `--layers=layer1,layer2` to specify which layers
- Parse layer templates from template registry
- Generate playback for selected layers

#### 4. **Interactive Fallback**

**Current Behavior:**
- Running `./repo.sh template new` (no args) falls back to old interactive repoman
- Fails in non-interactive environments with EOFError

**Desired Behavior:**
- Show usage help when insufficient arguments provided
- Guide user to provide required arguments
- Or: implement new interactive prompts (questionary library)

**Fix Required:**
- Add help message when template name is missing
- Either remove interactive mode or reimplement with modern prompts

#### 5. **Extension Configuration**

**Old Behavior:**
When a template requires setup extensions, it prompted:
```
Setup Extension -> omni_usd_composer_setup
Configuring extension template: Omni USD Composer Setup
? Enter name of extension [name-spaced, lowercase, alphanumeric]: my_company.my_usd_composer_setup_extension
? Enter extension_display_name: My USD Composer Setup Extension
? Enter version: 0.1.0
```

**Current Status:**
- Template engine auto-generates extension names based on app name
- Example: app `my_company.my_composer` → extension `my_company.my_composer_setup`
- No way to customize extension names via CLI

**Fix Required:**
- Add CLI arguments for extension configuration:
  ```bash
  --ext-setup-name=my_company.my_setup
  --ext-setup-display-name="My Setup"
  ```
- Or use sensible auto-generation (current approach is reasonable)

### Summary Table

| Feature | Old System | New System | Status |
|---------|-----------|------------|--------|
| Simple template creation (CLI) | ✅ Interactive | ✅ CLI args | ✅ Works |
| Templates with extensions | ✅ Interactive prompts | ✅ Auto-generated | ✅ FIXED |
| License acceptance | ✅ First-run prompt | ✅ First-run prompt | ✅ IMPLEMENTED |
| Application layers | ✅ Interactive selection | ❌ Not implemented | 🔧 Needs implementation |
| Template discovery | ✅ Works | ✅ Works | ✅ Works |
| GUI integration | ❌ N/A | ⚠️ Partial (Kit Playground) | 🔧 Needs license integration |
| Non-interactive mode | ❌ Requires TTY | ✅ CLI args | ✅ Works |

## Recommended Implementation Order

1. ✅ ~~**Fix extension parsing bug**~~ (COMPLETED - USD Composer and other templates work)
2. ✅ ~~**Implement license acceptance**~~ (COMPLETED - prompts on first template creation)
3. **Add application layers support** (NEXT - important for streaming deployments)
4. **Improve error messages** (NICE TO HAVE for better UX)
5. **GUI license integration** (Kit Playground needs license prompt)

## Testing Checklist

Current status:
- [x] `./repo.sh template new omni_usd_composer --name=... --display-name=... --version=...` works
- [x] Setup extensions are automatically created with proper names
- [x] License prompt appears on first template creation
- [x] License is not prompted on subsequent runs
- [x] `template list` and `template docs` work without license prompt
- [ ] `--add-layers --layers=omni_default_streaming` creates streaming variants (NOT IMPLEMENTED)
- [ ] GUI can create templates with license prompt
- [x] All template types work: application, extension, microservice
