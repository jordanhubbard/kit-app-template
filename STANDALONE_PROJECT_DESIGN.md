# Standalone Project Design

**Date**: October 24, 2025
**Phase**: 5
**Status**: 🎯 **DESIGN**

---

## Overview

Enable creation of self-contained projects that can be built and run independently of the kit-app-template repository.

---

## Current vs Standalone Behavior

### Current Behavior (Repository Mode)

```
kit-app-template/                     ← Repository root
├── repo.sh / repo.bat                ← Main build scripts
├── repo.toml                         ← Global configuration
├── premake5.lua                      ← Global build config
├── tools/                            ← Shared tools
│   ├── packman/                      ← Dependency manager
│   └── repoman/                      ← Build system
└── source/apps/my_app/               ← Application
    ├── my_app.kit
    ├── repo.sh                       ← Wrapper (calls ../../repo.sh)
    └── README.md
```

**Dependencies**:
- App's `repo.sh` finds and calls root `repo.sh`
- Requires repository structure to be present
- Cannot be moved or distributed independently

---

### Standalone Behavior (New)

```
~/my-standalone-app/                  ← Standalone project (anywhere)
├── repo.sh / repo.bat                ← Self-contained scripts (copied)
├── repo.toml                         ← Local configuration (modified)
├── premake5.lua                      ← Local build config (generated)
├── requirements.txt                  ← Python dependencies
├── tools/                            ← Local tools (copied)
│   ├── packman/                      ← Full packman (copied)
│   └── repoman/                      ← Essential repoman files (copied)
├── source/apps/my_app/               ← Application source
│   ├── my_app.kit
│   └── README.md
├── .project-meta.toml                ← Project metadata
└── README.md                         ← Standalone instructions
```

**Independence**:
- All tools included locally
- No dependency on parent repository
- Can be moved, zipped, or distributed
- Builds and runs from its own directory

---

## CLI Usage

### Creating Standalone Project

```bash
# Create standalone project in specified directory
./repo.sh template new kit_base_editor \
  --name my.app \
  --output-dir ~/my-standalone-app \
  --standalone

# Or use default output location
./repo.sh template new kit_base_editor \
  --name my.app \
  --standalone
# Creates: ./my.app/ as standalone project
```

### Building Standalone Project

```bash
cd ~/my-standalone-app
./repo.sh build
./repo.sh launch
```

---

## Implementation Strategy

### Phase 5.1: File Structure

**Files to copy**:
1. **Build tools** (essential):
   - `tools/packman/` (entire directory)
   - `tools/repoman/*.py` (core Python files)
   - `tools/packman/*.sh` and `*.bat` (bootstrap scripts)

2. **Configuration files** (modify):
   - `repo.sh` and `repo.bat` (from root, not app wrapper)
   - `repo.toml` (modify paths for standalone)
   - `premake5.lua` (generate standalone version)
   - `requirements.txt` (copy if exists)

3. **Application files** (as-is):
   - Generated template output (app or extension)
   - `.project-meta.toml` (metadata)
   - `README.md` (from template)

**Files to generate**:
1. **README.md** (standalone-specific instructions)
2. **premake5.lua** (standalone version)
3. **repo.toml** (modified for standalone paths)

---

### Phase 5.2: Path Modifications

**repo.toml changes**:
```toml
# BEFORE (repository mode):
[repo_paths]
root = "."  # Relative to repository root

# AFTER (standalone mode):
[repo_paths]
root = "."  # Now relative to standalone project root
```

**premake5.lua changes**:
```lua
-- BEFORE: Include root workspace
include("../../premake5.lua")  -- Finds repository root

-- AFTER: Standalone workspace
-- Generate self-contained premake config
workspace "MyApp"
    configurations { "debug", "release" }
    -- Include only this project's build config
```

---

### Phase 5.3: Tool Selection

**What to copy from tools/**:

**packman/** (full directory):
- `bootstrap/` - Required for first-time setup
- `packman` executable
- `python.sh` / `python.bat` - Python bootstrap
- `packmanconf.py` - Configuration

**repoman/** (selective):
Required files:
- `repoman.py` - Main build orchestrator
- `repo_dispatcher.py` - Command dispatcher
- `launch.py` - Application launcher
- `package.py` - Packaging support
- `template_engine.py` - Template operations (if needed)
- `template_api.py` - Template API
- `license_manager.py` - License handling

Optional (skip for minimal):
- `template_validator.py`
- `template_helper.py`
- `repoman_bootstrapper.py`

---

## Implementation: standalone_generator.py

### API Design

```python
class StandaloneGenerator:
    """Generate standalone projects from templates."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def generate_standalone(
        self,
        template_output_dir: Path,  # Where template was generated
        standalone_dir: Path,        # Where to create standalone project
        template_name: str,
        app_name: str
    ) -> Path:
        """
        Convert a template-generated project into a standalone project.

        Args:
            template_output_dir: Directory where template created the app
            standalone_dir: Target directory for standalone project
            template_name: Name of template used
            app_name: Application name

        Returns:
            Path to created standalone project
        """
        # 1. Create standalone directory structure
        # 2. Copy application files
        # 3. Copy build tools
        # 4. Copy/modify configuration files
        # 5. Generate standalone-specific files
        # 6. Create README with instructions
        pass

    def copy_application(self, src: Path, dest: Path):
        """Copy application source files."""
        pass

    def copy_build_tools(self, dest: Path):
        """Copy packman and repoman tools."""
        pass

    def generate_config_files(self, dest: Path, app_name: str):
        """Generate standalone configuration files."""
        pass

    def generate_premake(self, dest: Path, app_name: str):
        """Generate standalone premake5.lua."""
        pass

    def generate_readme(self, dest: Path, template_name: str):
        """Generate standalone README.md with usage instructions."""
        pass
```

---

## Testing Strategy

### Test Cases

**Test 1: Create standalone project**
```python
def test_create_standalone_project():
    """Create standalone project from template."""
    result = subprocess.run([
        "./repo.sh", "template", "new", "kit_base_editor",
        "--name", "test_standalone",
        "--output-dir", "/tmp/test_standalone",
        "--standalone"
    ])
    assert result.returncode == 0
    assert Path("/tmp/test_standalone").exists()
```

**Test 2: Verify file structure**
```python
def test_standalone_structure():
    """Verify all required files are present."""
    project_dir = Path("/tmp/test_standalone")

    # Core files
    assert (project_dir / "repo.sh").exists()
    assert (project_dir / "repo.toml").exists()
    assert (project_dir / "premake5.lua").exists()

    # Tools
    assert (project_dir / "tools/packman").is_dir()
    assert (project_dir / "tools/repoman").is_dir()

    # Application
    assert (project_dir / "source/apps/test_standalone").is_dir()
```

**Test 3: Build standalone project**
```python
def test_build_standalone():
    """Build project in isolation."""
    result = subprocess.run(
        ["./repo.sh", "build"],
        cwd="/tmp/test_standalone"
    )
    assert result.returncode == 0
```

**Test 4: Launch standalone project**
```python
def test_launch_standalone():
    """Launch built application."""
    result = subprocess.run(
        ["./repo.sh", "launch", "--name", "test_standalone.kit"],
        cwd="/tmp/test_standalone",
        timeout=30
    )
    # Verify it starts (may exit quickly in headless)
    assert result.returncode in [0, 2]
```

**Test 5: Verify independence**
```python
def test_standalone_independence():
    """Verify project works without original repository."""
    # Move project to different location
    shutil.move("/tmp/test_standalone", "/tmp/moved_project")

    # Build from new location
    result = subprocess.run(
        ["./repo.sh", "build"],
        cwd="/tmp/moved_project"
    )
    assert result.returncode == 0
```

---

## File Size Estimation

**Approximate sizes**:
- `tools/packman/`: ~5-10 MB
- `tools/repoman/`: ~500 KB
- `premake5.lua`: ~5 KB
- `repo.sh/bat`: ~10 KB
- Application source: ~50-100 KB

**Total standalone project**: ~15-20 MB (before build)

**After build**: ~1-2 GB (includes Kit SDK and dependencies)

---

## Edge Cases & Considerations

### 1. Output Directory Conflicts
**Problem**: Target directory already exists
**Solution**: Add `--force` flag or prompt user

### 2. Relative vs Absolute Paths
**Problem**: Paths in config files
**Solution**: Use relative paths consistently

### 3. Extensions vs Applications
**Problem**: Extensions have different structure
**Solution**: Detect type and adjust accordingly

### 4. Build Dependencies
**Problem**: Kit SDK download location
**Solution**: Use `_build/` in standalone project root

### 5. Template Registry
**Problem**: Standalone project may want to create more apps
**Solution**: Include template registry or document that it's single-app

---

## Success Criteria

✅ **Functional**:
- [ ] Standalone project can be created
- [ ] All required files are included
- [ ] Project builds successfully
- [ ] Project launches successfully
- [ ] Project works after moving to different location
- [ ] No errors about missing files
- [ ] No dependency on original repository

✅ **Quality**:
- [ ] All tests pass
- [ ] Clean error messages
- [ ] Good documentation
- [ ] Reasonable file size

✅ **User Experience**:
- [ ] Intuitive CLI flags
- [ ] Clear instructions in README
- [ ] Easy to share/distribute
- [ ] Works on Windows and Linux

---

## Implementation Checklist

### Phase 5.1: Generator Implementation
- [ ] Create `tools/repoman/standalone_generator.py`
- [ ] Implement `StandaloneGenerator` class
- [ ] Implement file copying logic
- [ ] Implement configuration modification logic
- [ ] Implement premake generation logic
- [ ] Implement README generation logic

### Phase 5.2: CLI Integration
- [ ] Add `--standalone` flag to template_engine.py
- [ ] Add `--output-dir` support (if not present)
- [ ] Update help text
- [ ] Call standalone generator when flag is used

### Phase 5.3: Testing
- [ ] Create `tests/standalone/` directory
- [ ] Write standalone project tests
- [ ] Verify all tests pass
- [ ] Test on Linux (and Windows if available)

### Phase 5.4: Documentation
- [ ] Create STANDALONE_PROJECTS.md guide
- [ ] Update README.md with standalone workflow
- [ ] Generate sample standalone README
- [ ] Document known limitations

---

## Timeline

| Task | Duration | Details |
|------|----------|---------|
| Design | 15 min | ✅ This document |
| Implementation | 60 min | standalone_generator.py + CLI |
| Testing | 45 min | Tests + verification |
| Documentation | 30 min | User guides + samples |
| **Total** | **150 min** | **~2.5 hours** |

---

## Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement `standalone_generator.py`
3. ⏳ Add CLI integration
4. ⏳ Write tests
5. ⏳ Document feature

**Status**: Design complete, ready for implementation!
