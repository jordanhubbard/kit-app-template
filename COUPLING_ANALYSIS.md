# CLI-GUI Coupling Analysis

## Executive Summary

The Kit Playground GUI generally follows good separation-of-concerns principles by wrapping CLI functionality via `TemplateAPI` and `subprocess` calls to `repo.sh`. However, there are **three key areas where workarounds and re-implementation** occur:

1. **Post-processing application structure** (`_fix_application_structure`)
2. **Modifying repo.toml static apps list** after template generation
3. **Direct subprocess calls** instead of using TemplateAPI for replay

## Architecture Assessment

### ✅ What's Working Well

#### 1. Template API Abstraction Layer
**Location:** `tools/repoman/template_api.py`

The `TemplateAPI` class provides an excellent abstraction layer:
```python
class TemplateAPI:
    def list_templates(...)    # Used by both CLI and GUI
    def get_template(...)       # Used by both CLI and GUI
    def generate_template(...)  # Used by both CLI and GUI
```

**Evidence of proper wrapping:**
- GUI uses `template_api.list_templates()` instead of re-implementing discovery
- GUI uses `template_api.generate_template()` to create playback files
- Both CLI and GUI share the same `TemplateEngine` underneath

#### 2. Subprocess Delegation for Build/Launch
**Location:** `kit_playground/backend/routes/project_routes.py`

The GUI correctly delegates to `repo.sh` for build and launch operations:
```python
# Build
cmd = ['./repo.sh', 'build', '--config', 'release']
subprocess.run(cmd, cwd=app_dir)

# Launch
cmd = ['./repo.sh', 'launch', '--name', kit_file]
subprocess.Popen(cmd, cwd=app_dir)
```

This is **clean separation** - the GUI doesn't try to re-implement the build system.

### ❌ Problem Areas: Workarounds & Re-implementation

#### Problem 1: Post-Processing Application Structure

**Location:** `kit_playground/backend/routes/v2_template_routes.py:318-342`

After running `repo.sh template replay`, the GUI manually calls `_fix_application_structure()`:

```python
# Post-process: Move files from source/apps to _build/apps
# The replay creates files in source/apps but they need to be
# restructured in _build/apps/{name}/{name}.kit format
_fix_application_structure(repo_root, playback_data)
```

**Why this is a problem:**
1. ✗ **Re-implementing logic** that should be in the template replay system
2. ✗ **Direct dependency** on internal function `_fix_application_structure`
3. ✗ **GUI has to know** about the application directory structure
4. ✗ **Duplication** - both CLI and GUI have to call this function

**Root cause:**
The `omni.repo.man` template replay creates `.kit` files as flat files in `source/apps/`, but the desired structure is `source/apps/{name}/{name}.kit` (directory-based).

**Current flow:**
```
TemplateAPI.generate_template()
    ↓ creates playback file
repo.sh template replay <playback>
    ↓ creates flat structure (source/apps/app.kit)
_fix_application_structure()  ← GUI has to call this
    ↓ restructures to directory (source/apps/app/app.kit)
```

**What it should be:**
```
TemplateAPI.generate_template()
    ↓ creates playback file
repo.sh template replay <playback>
    ↓ creates correct structure automatically (source/apps/app/app.kit)
Done! ✓
```

#### Problem 2: Modifying repo.toml After Template Generation

**Location:** `kit_playground/backend/routes/v2_template_routes.py:345-372`

After template generation, the GUI has to manually clear the static apps list in `repo.toml`:

```python
# Fix repo.toml: The template system adds entries to the static apps list,
# but we use dynamic discovery via app_discovery_paths instead.
# Clear the static apps list to prevent build errors.
import re
repo_toml_path = repo_root / "repo.toml"
content = repo_toml_path.read_text()
pattern = r'^apps\s*=\s*\[.*?\]'
replacement = 'apps = []'
new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
repo_toml_path.write_text(new_content)
```

**Why this is a problem:**
1. ✗ **File manipulation** after CLI completes
2. ✗ **GUI has to know** about repo.toml internals
3. ✗ **Brittle regex** parsing of TOML
4. ✗ **Assumes** dynamic discovery is preferred
5. ✗ **Duplication** - CLI doesn't have this issue (why the discrepancy?)

**Root cause:**
The template replay system (via `omni.repo.man`) adds generated apps to the static `apps = [...]` list in `repo.toml`, but Kit Playground uses dynamic discovery via `app_discovery_paths` instead. This creates a conflict.

**Current flow:**
```
repo.sh template replay
    ↓ adds app to repo.toml: apps = ["my_app.kit"]
GUI regex workaround
    ↓ clears: apps = []
```

**What it should be:**
Option A: Template replay shouldn't modify `repo.toml` when dynamic discovery is enabled
Option B: Template replay should support a `--no-register` flag
Option C: GUI should use the static apps list instead of dynamic discovery

#### Problem 3: Direct Subprocess Call to repo.sh replay

**Location:** `kit_playground/backend/routes/v2_template_routes.py:226-273`

The GUI bypasses `TemplateAPI` and directly calls `subprocess.run()` for replay:

```python
replay_cmd = [
    str(repo_root / 'repo.sh'),
    'template',
    'replay',
    result.playback_file  # Positional argument
]
replay_result = subprocess.run(replay_cmd, cwd=str(repo_root), ...)
```

**Why this is a problem:**
1. ✗ **Bypassing the abstraction layer** - `TemplateAPI.generate_template()` already exists
2. ✗ **GUI constructs command-line args** instead of using API
3. ✗ **Duplicates** what CLI does
4. ✗ **Harder to test** - subprocess calls are harder to mock than API calls

**Root cause:**
`TemplateAPI.generate_template()` only creates the playback file - it doesn't execute it. The GUI has to manually run `repo.sh template replay`.

**Current flow:**
```python
result = template_api.generate_template(req)  # Creates playback file
# Now GUI manually runs replay
subprocess.run(['repo.sh', 'template', 'replay', result.playback_file])
```

**What it should be:**
```python
result = template_api.generate_template(req, execute=True)  # Creates AND executes
# Done! ✓
```

Or:
```python
result = template_api.generate_template(req)
template_api.execute_playback(result.playback_file)  # New API method
```

## Recommendations

### High Priority: Fix in Repoman (Backward Compatible)

These changes should be made to `omni.repo.man` or the template system to eliminate GUI workarounds:

#### 1. Make Template Replay Create Correct Directory Structure

**File:** `omni.repo.man` template replay logic

**Change:** When replaying application templates, create the directory structure automatically:
- Current: Creates `source/apps/app.kit` (flat file)
- Desired: Creates `source/apps/app/app.kit` (directory structure)

**Backward compatibility:** Check if a "modern" flag is set in the playback file, or detect based on template metadata.

**Implementation approach:**
```python
# In omni.repo.man replay logic
if template_type == 'application':
    # Create directory structure instead of flat file
    app_dir = source_dir / "apps" / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    kit_file = app_dir / f"{app_name}.kit"
    # Copy template content to kit_file
```

**Benefits:**
- ✓ Eliminates `_fix_application_structure()` workaround
- ✓ GUI doesn't need to know about directory structure
- ✓ CLI and GUI behave identically
- ✓ Cleaner separation of concerns

#### 2. Add --no-register Flag to Template Replay

**File:** `tools/repoman/repoman.py` (or wherever replay is implemented)

**Change:** Add a flag to skip modifying `repo.toml`:
```bash
./repo.sh template replay playback.toml --no-register
```

**When --no-register is used:**
- Don't add app to `apps = [...]` in repo.toml
- Don't modify premake files
- Just create the application files

**Backward compatibility:** Default behavior unchanged (still registers). Only affects GUI when flag is used.

**Benefits:**
- ✓ Eliminates repo.toml regex workaround
- ✓ GUI can opt-out of static registration
- ✓ Cleaner separation - GUI doesn't modify TOML files

#### 3. Extend TemplateAPI to Execute Playback

**File:** `tools/repoman/template_api.py`

**Change:** Add execution support to TemplateAPI:
```python
class TemplateAPI:
    def generate_template(self, request, execute=False):
        """Generate template and optionally execute playback."""
        playback = self.engine.generate_template(...)
        playback_file = self.engine.save_playback_file(playback)

        if execute:
            self.execute_playback(playback_file)

        return TemplateGenerationResult(...)

    def execute_playback(self, playback_file: str,
                        no_register: bool = False) -> bool:
        """Execute a playback file."""
        cmd = [self._get_repo_cmd(), 'template', 'replay', playback_file]
        if no_register:
            cmd.append('--no-register')
        result = subprocess.run(cmd, ...)
        return result.returncode == 0
```

**Benefits:**
- ✓ GUI uses API instead of subprocess
- ✓ Cleaner abstraction
- ✓ Easier to test
- ✓ Can handle --no-register flag internally

### Medium Priority: Improve API Design

#### 4. Unified Template Creation Workflow

Instead of:
```python
# Current: GUI has to do 3 steps
result = template_api.generate_template(req)  # 1. Create playback
subprocess.run(['repo.sh', 'template', 'replay', ...])  # 2. Execute
_fix_application_structure(repo_root, playback_data)  # 3. Fix structure
```

Should be:
```python
# Desired: Single API call
result = template_api.create_application(
    template_name='kit_base_editor',
    name='my_app',
    display_name='My App',
    version='1.0.0'
)
# Done! ✓
```

**Implementation:**
```python
class TemplateAPI:
    def create_application(self, template_name: str, name: str,
                          display_name: str, version: str = '0.1.0',
                          **kwargs) -> ApplicationCreationResult:
        """
        High-level API to create a complete application.
        Handles playback generation, execution, and post-processing.
        """
        # 1. Generate playback
        req = TemplateGenerationRequest(...)
        playback_result = self.generate_template(req)

        # 2. Execute playback with modern directory structure
        self.execute_playback(playback_result.playback_file, no_register=True)

        # 3. Return structured result
        return ApplicationCreationResult(
            success=True,
            app_name=name,
            app_dir=self._get_app_dir(name),
            kit_file=self._get_kit_file(name)
        )
```

### Low Priority: Architecture Improvements

#### 5. Consider Moving _fix_application_structure into Repoman

If the directory structure fix can't be done during replay, at least make it part of the official CLI workflow:

```bash
# Current CLI (no fix needed because CLI uses different structure?)
./repo.sh template new kit_base_editor --name my_app

# If fix is needed, make it explicit:
./repo.sh template new kit_base_editor --name my_app --modern-structure
```

This way both CLI and GUI go through the same code path.

#### 6. Document "Modern" vs "Legacy" Template Structure

Create clear documentation about:
- **Legacy structure:** `source/apps/app.kit` (flat file)
- **Modern structure:** `source/apps/app/app.kit` (directory-based)
- **Migration path:** How to convert legacy to modern
- **When to use each:** Maybe legacy is still valid for simple cases?

## Testing Recommendations

### Test 1: GUI Uses Only Public APIs
Audit all GUI code and ensure it only calls:
- ✓ `TemplateAPI` methods
- ✓ `subprocess` calls to `repo.sh` (for build/launch)
- ✗ Direct file manipulation (should be avoided)
- ✗ Importing internal `_private_functions` (like `_fix_application_structure`)

### Test 2: CLI and GUI Produce Identical Results
Create a test that:
1. Uses CLI to create an app: `./repo.sh template new kit_base_editor --name cli_app`
2. Uses GUI API to create an app: `template_api.create_application('kit_base_editor', 'gui_app')`
3. Compares the directory structures - should be **identical**

### Test 3: No File Manipulation After CLI Completes
Monitor filesystem changes:
1. Run CLI command
2. Wait for CLI to exit
3. Assert: GUI doesn't modify any files after CLI exits
4. (Except for logs/cache files)

## Summary of Workarounds

| Workaround | Location | Fix Priority | Solution |
|------------|----------|--------------|----------|
| `_fix_application_structure()` | v2_template_routes.py:342 | **HIGH** | Make replay create correct structure |
| repo.toml regex modification | v2_template_routes.py:345-372 | **HIGH** | Add `--no-register` flag |
| Direct subprocess replay | v2_template_routes.py:226-273 | **MEDIUM** | Extend TemplateAPI |
| Duplicate wrapper script creation | repo_dispatcher.py:188-259 | **LOW** | Keep (this is fine) |

## Conclusion

The Kit Playground generally follows good practices by wrapping the CLI via `TemplateAPI` and subprocess calls. However, there are **three key workarounds** that violate clean separation of concerns:

1. **Post-processing directory structure** after replay completes
2. **Modifying repo.toml** after template generation
3. **Direct subprocess calls** instead of using high-level API

### Recommended Action Plan

**Phase 1: Quick wins (no repoman changes needed)**
- [ ] Create `TemplateAPI.execute_playback()` method
- [ ] Create `TemplateAPI.create_application()` high-level method
- [ ] Remove direct subprocess calls from GUI

**Phase 2: Repoman enhancements (backward compatible)**
- [ ] Add `--no-register` flag to template replay
- [ ] Make replay create directory structure automatically
- [ ] Document modern vs legacy structures

**Phase 3: Cleanup**
- [ ] Remove `_fix_application_structure()` workaround from GUI
- [ ] Remove repo.toml regex workaround from GUI
- [ ] Add tests to ensure CLI and GUI produce identical results

### Backward Compatibility Notes

All proposed changes can be made **backward compatible**:
- New flags (like `--no-register`) are opt-in
- Directory structure can be controlled by playback file metadata
- Existing scripts continue to work unchanged
- GUI migrates to new API over time

The goal is **zero breaking changes** to existing repoman users while enabling cleaner GUI integration.
