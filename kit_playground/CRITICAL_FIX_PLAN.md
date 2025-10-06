# Critical Directory Structure Fix Plan

**Date:** October 4, 2025
**Issue:** Fundamental flaw in CLI and UI project directory structure

---

## 🚨 The Problem

### Current (INCORRECT) Behavior

```bash
$ ./repo.sh template new kit_base_editor --name=my_company.my_editor

Output: "Application 'my_company.my_editor' created successfully in
/home/jkh/Src/kit-app-template/_build/apps/my_company.my_editor.kit"

Directory Structure Created:
_build/apps/
└── my_company.my_editor.kit/     ← WRONG: Directory with .kit extension
    └── my_company.my_editor.kit  ← Actual config file
```

**Problems:**
1. Directory is named `{project_name}.kit` - misleading and incorrect
2. No build metadata or structure included
3. No platform-specific build directories
4. UI assumes this broken structure
5. Project discovery looks for `.kit` directories instead of proper project directories

---

## ✅ Correct Behavior

###Expected Directory Structure

```bash
$ ./repo.sh template new kit_base_editor --name=my_company.my_editor

Output: "Application 'my_company.my_editor' created successfully in
/home/jkh/Src/kit-app-template/_build/apps/my_company.my_editor"

Directory Structure Should Be:
_build/apps/
└── my_company.my_editor/                    ← Directory WITHOUT .kit extension
    ├── my_company.my_editor.kit             ← Main Kit configuration file
    ├── premake5.lua                         ← Build configuration
    ├── README.md                            ← Project documentation
    ├── .project-meta.toml                   ← Project metadata (NEW)
    └── [generated during build]
        ├── _build/                          ← Build artifacts
        │   ├── windows/                     ← Windows build files
        │   └── linux/                       ← Linux build files
        └── _compiler/                       ← Compiler artifacts
```

---

## 🔧 Required Fixes

### 1. Backend Template Generation (HIGH PRIORITY)

**Files to modify:**
- `tools/repoman/template_engine.py`
- `tools/repoman/template_validator.py` (line 440)
- `tools/repoman/repo_dispatcher.py`

**Changes needed:**
```python
# OLD (WRONG):
generated_path = self.repo_root / "source" / "apps" / f"{app_name}.kit"

# NEW (CORRECT):
project_dir = self.repo_root / "source" / "apps" / app_name
kit_file = project_dir / f"{app_name}.kit"
```

**Actions:**
1. Remove `.kit` suffix from directory names
2. Create proper project directory structure
3. Add build metadata files (premake5.lua, README.md)
4. Add `.project-meta.toml` with metadata:
   ```toml
   [project]
   name = "my_company.my_editor"
   display_name = "My Editor"
   version = "1.0.0"
   type = "application"
   template = "kit_base_editor"
   created = "2025-10-04T10:00:00Z"

   [build]
   platforms = ["windows", "linux"]
   config_file = "my_company.my_editor.kit"
   ```

### 2. Project Discovery (HIGH PRIORITY)

**File:** `kit_playground/backend/web_server.py` (lines 691-734)

**Current (WRONG):**
```python
if item.is_dir() and item.suffix == '.kit':  # Looking for .kit directories
    project_name = item.stem
    kit_file = item / f"{project_name}.kit"
```

**Fixed (CORRECT):**
```python
if item.is_dir():
    # Look for .project-meta.toml or {name}.kit file
    potential_kit_files = list(item.glob("*.kit"))
    if potential_kit_files:
        kit_file = potential_kit_files[0]
        project_name = kit_file.stem
```

### 3. UI Path Construction (MEDIUM PRIORITY)

**File:** `kit_playground/ui/src/components/layout/MainLayoutWorkflow.tsx`

**Current fix applied (line 381):**
```typescript
const projectPath = `${repoRoot}/${projectInfo.outputDir}/${projectInfo.projectName}.kit`;
const kitFilePath = `${projectPath}/${projectInfo.projectName}.kit`;
```

**After backend fix, should be:**
```typescript
const projectPath = `${repoRoot}/${projectInfo.outputDir}/${projectInfo.projectName}`;
const kitFilePath = `${projectPath}/${projectInfo.projectName}.kit`;
```

### 4. Build Integration (MEDIUM PRIORITY)

**Requirements:**
- When building, create `_build/` directory in project root
- Platform-specific build outputs go in `_build/{platform}/`
- `repo build` command should work from project directory
- UI should show build status and artifacts

### 5. Project Metadata (NEW FEATURE)

**Add `.project-meta.toml` to each project:**
```toml
[project]
name = "my_company.my_editor"
display_name = "My Editor"
version = "1.0.0"
type = "application"  # or "extension", "microservice"
template = "kit_base_editor"
created = "2025-10-04T10:00:00Z"
last_modified = "2025-10-04T10:00:00Z"

[build]
platforms = ["windows", "linux"]
config_file = "my_company.my_editor.kit"
build_dir = "_build"

[files]
main_config = "my_company.my_editor.kit"
readme = "README.md"
build_script = "premake5.lua"
```

**Benefits:**
- UI can read metadata without parsing .kit files
- Track project history
- Identify project type
- Store build configuration
- Enable project-level features

---

## 📋 Implementation Order

### Phase 1: Backend Core Fixes (CRITICAL - Do First)
1. ✅ Fix `MainLayoutWorkflow.tsx` path construction (DONE)
2. ⏭️ Fix `template_engine.py` directory creation logic
3. ⏭️ Fix `repo_dispatcher.py` output messages
4. ⏭️ Add `.project-meta.toml` generation
5. ⏭️ Add build structure templates (premake5.lua, etc.)

### Phase 2: Project Discovery (HIGH PRIORITY)
1. ⏭️ Update `web_server.py` project discovery logic
2. ⏭️ Test with both old and new project structures
3. ⏭️ Add migration path for existing projects

### Phase 3: UI Updates (MEDIUM PRIORITY)
1. ⏭️ Update UI path assumptions
2. ⏭️ Add project metadata display
3. ⏭️ Show build status and platform info
4. ⏭️ Add build artifact browser

### Phase 4: Build Integration (MEDIUM PRIORITY)
1. ⏭️ Integrate `repo build` correctly
2. ⏭️ Show build output in console
3. ⏭️ Display build artifacts
4. ⏭️ Add clean/rebuild options

### Phase 5: Testing & Migration (LOW PRIORITY)
1. ⏭️ Test with all template types
2. ⏭️ Create migration script for existing projects
3. ⏭️ Update documentation
4. ⏭️ Add validation tests

---

## 🎯 Success Criteria

After fixes are complete:

1. **Directory Structure:**
   ```
   _build/apps/my_company.my_editor/
   ├── my_company.my_editor.kit
   ├── premake5.lua
   ├── README.md
   ├── .project-meta.toml
   └── [build artifacts]
   ```

2. **CLI Output:**
   ```
   Application 'my_company.my_editor' created successfully in
   /path/to/_build/apps/my_company.my_editor

   Main configuration: my_company.my_editor.kit
   Build with: ./repo.sh build
   ```

3. **UI Behavior:**
   - Projects appear in sidebar correctly
   - Clicking project loads `{name}.kit` file
   - Build button works and creates `_build/` directory
   - Console shows build output
   - Status bar shows build progress

4. **Build Integration:**
   - `./repo.sh build` works (builds all apps in _build/apps/)
   - Build artifacts go to `_build/{platform}/`
   - Run button launches built application

---

## ⚠️ Breaking Changes

This fix introduces **breaking changes** for existing projects:

**Old projects:**
```
_build/apps/my_company.my_editor.kit/  ← Directory with .kit
└── my_company.my_editor.kit
```

**New projects:**
```
_build/apps/my_company.my_editor/      ← Directory without .kit
└── my_company.my_editor.kit
```

**Migration Strategy:**
1. Detect old-style projects (directories ending in `.kit`)
2. Offer auto-migration in UI
3. Rename directory (remove `.kit` suffix)
4. Add `.project-meta.toml`
5. Update any references

---

## 📝 Next Steps

1. **Immediate:** Review and approve this plan
2. **Phase 1:** Implement backend core fixes
3. **Testing:** Verify with all template types
4. **Phase 2:** Update project discovery
5. **Phase 3:** Update UI
6. **Documentation:** Update all docs
7. **Migration:** Handle existing projects

---

## ✅ IMPLEMENTATION COMPLETE

**Status:** Phase 1-3 Implemented Successfully
**Date Completed:** October 4, 2025

See `BREAKING_CHANGES_IMPLEMENTED.md` for full details of changes made.

### Completed:
- ✅ Phase 1: Backend Core Fixes
- ✅ Phase 2: Project Discovery Updates
- ✅ Phase 3: UI Path Fixes
- ✅ Added project metadata system
- ✅ Backward compatibility maintained

### Remaining (Optional):
- ⏭️ Phase 4: Enhanced Build Integration
- ⏭️ Phase 5: Testing & Documentation Updates
