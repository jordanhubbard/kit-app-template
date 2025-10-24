# Phase 5: Standalone Projects

**Date**: October 24, 2025
**Branch**: phase-3-api-layer
**Status**: 🚀 **STARTING**

---

## Overview

Phase 5 enables creation of **truly standalone projects** that can be built independently outside the repository.

**Current Behavior**: Templates create projects in `source/apps/` that depend on repository structure
**New Behavior**: Templates can create self-contained projects anywhere with `--standalone` flag

**Estimated Time**: 2-3 hours
**Approach**: Test-first, incremental implementation

---

## Objectives

### Primary Goal
Enable users to create standalone projects that:
- ✅ Can be created in any directory
- ✅ Include all necessary build tools
- ✅ Build without access to original repository
- ✅ Are distributable (zip/tar and use elsewhere)

### Use Case

```bash
# Create standalone project
./repo.sh template new kit_base_editor \
  --name my.app \
  --output-dir ~/my-standalone-app \
  --standalone

# User can then:
cd ~/my-standalone-app
./repo.sh build
./repo.sh launch
```

---

## Target Structure

```
~/my-standalone-app/
├── my.app.kit               # Application config
├── README.md                # Documentation
├── .project-meta.toml       # Metadata
├── repo.sh / repo.bat       # Self-contained build scripts
├── tools/                   # Required build tools (copied)
│   ├── packman/
│   └── repoman/
├── premake5.lua             # Build config
├── repo.toml                # Local config (modified for standalone)
├── requirements.txt         # Python dependencies
└── source/
    └── apps/
        └── my.app/          # Application source
```

---

## Implementation Plan

### Phase 5.1: Assessment (~15 min)

**Tasks**:
1. ✅ Review current template generation
2. ✅ Identify dependencies on repository
3. ✅ List files needed for standalone operation
4. ✅ Design standalone structure

**Output**: Design document

---

### Phase 5.2: Standalone Generator (~60 min)

**File**: `tools/repoman/standalone_generator.py`

**Features**:
- Copy application template
- Copy build tools (`tools/packman/`, `tools/repoman/`)
- Copy wrapper scripts (`repo.sh`, `repo.bat`)
- Copy/generate `premake5.lua` (standalone version)
- Copy/modify `repo.toml` (update paths)
- Generate `README.md` with instructions
- Generate `.project-meta.toml` with metadata

**Key Challenges**:
- Path updates (absolute → relative)
- Premake configuration for standalone
- Ensure no hard dependencies on original repo

---

### Phase 5.3: CLI Integration (~30 min)

**File**: `tools/repoman/template_engine.py`

**Changes**:
- Add `--standalone` flag to `template new`
- Add `--output-dir` support
- Call standalone generator when `--standalone` is used
- Update help text

**Backward Compatibility**:
- ✅ Existing behavior unchanged
- ✅ `--standalone` is opt-in
- ✅ Default behavior stays the same

---

### Phase 5.4: Testing (~45 min)

**File**: `tests/standalone/test_standalone_projects.py`

**Tests**:
1. Create standalone project
2. Verify all files present
3. Build in isolated directory
4. Launch application
5. Test project is distributable (copy elsewhere and build)
6. Verify no dependency on original repo

**Success Criteria**:
- All tests pass
- Zero dependencies on parent repo
- Project works after moving to different location

---

### Phase 5.5: Documentation (~30 min)

**Files**:
- Update README.md with standalone workflow
- Add STANDALONE_PROJECTS.md guide
- Update API documentation

---

## Files to Create/Modify

### New Files (3 files)
```
tools/repoman/standalone_generator.py         Standalone generator
tests/standalone/__init__.py                  Test package
tests/standalone/test_standalone_projects.py  Standalone tests
```

### Modified Files (2 files)
```
tools/repoman/template_engine.py              Add --standalone flag
tools/repoman/repo_dispatcher.py              Pass standalone flag
```

### Generated Files (per standalone project)
```
<output-dir>/repo.sh
<output-dir>/repo.bat
<output-dir>/premake5.lua
<output-dir>/repo.toml
<output-dir>/README.md
<output-dir>/.project-meta.toml
<output-dir>/tools/               (copied)
```

---

## Technical Approach

### Standalone vs Repository Mode

| Aspect | Repository Mode | Standalone Mode |
|--------|----------------|-----------------|
| Location | `source/apps/` | Any directory |
| Build tools | Shared in repo | Copied locally |
| Premake | Global | Local, modified |
| Dependencies | Shared `_build/` | Local `_build/` |
| Distribution | Requires repo | Self-contained |

---

### Path Mapping

**Repository paths** (before):
```
/path/to/kit-app-template/
├── tools/packman/
├── tools/repoman/
├── repo.sh
├── premake5.lua
└── source/apps/my.app/
```

**Standalone paths** (after):
```
~/my-standalone-app/
├── tools/packman/          (copied)
├── tools/repoman/          (copied)
├── repo.sh                 (copied, modified)
├── premake5.lua            (generated)
├── repo.toml               (generated)
└── source/apps/my.app/     (copied)
```

---

## Dependencies to Copy

### Essential Files
1. **Build Tools**:
   - `tools/packman/` (entire directory)
   - `tools/repoman/` (entire directory, or subset)

2. **Build Scripts**:
   - `repo.sh`
   - `repo.bat`
   - `build.sh`
   - `build.bat`

3. **Configuration**:
   - `premake5.lua` (modified for standalone)
   - `repo.toml` (modified for standalone)
   - `requirements.txt` (if needed)

### Optional Files
- `.gitignore` (for version control)
- `.editorconfig` (for IDE settings)

---

## Success Criteria

### Functional Requirements
- [ ] `--standalone` flag works
- [ ] Project created in specified directory
- [ ] All build tools included
- [ ] Project builds successfully
- [ ] Project launches successfully
- [ ] No errors about missing files
- [ ] No dependency on original repo

### Quality Requirements
- [ ] Tests pass (100%)
- [ ] Zero regressions
- [ ] Backward compatible
- [ ] Well-documented
- [ ] Code quality maintained

### User Experience
- [ ] Clear usage instructions
- [ ] Good error messages
- [ ] Intuitive workflow
- [ ] Fast execution

---

## Risks & Mitigation

### Risk: Large file copies
**Mitigation**: Copy only essential files, document optional dependencies

### Risk: Path issues
**Mitigation**: Use relative paths, thorough testing

### Risk: Build system complexity
**Mitigation**: Start simple, test incrementally

### Risk: Breaking changes
**Mitigation**: Opt-in with flag, test backward compatibility

---

## Timeline

| Task | Time | Cumulative |
|------|------|------------|
| Assessment & Design | 15 min | 15 min |
| Standalone Generator | 60 min | 75 min |
| CLI Integration | 30 min | 105 min |
| Testing | 45 min | 150 min |
| Documentation | 30 min | 180 min |
| **Total** | **180 min** | **3 hours** |

---

## Next Steps

**Immediate**:
1. Review current template generation code
2. Identify all file dependencies
3. Design standalone generator API

**Then**:
4. Implement standalone generator
5. Add CLI integration
6. Write tests
7. Document feature

Let's begin!
