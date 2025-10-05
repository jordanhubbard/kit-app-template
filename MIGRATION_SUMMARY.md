# Migration from source/apps to _build/apps

**Date:** October 5, 2025  
**Status:** ✅ Complete

## Overview
Migrated all application output from `source/apps/` to `_build/apps/` to properly organize build artifacts in the `_build` hierarchy.

## Changes Made

### 1. UI Components (TypeScript/React)
- **CreateProjectDialog.tsx**
  - Default output directory: `source/apps` → `_build/apps`
  - Placeholder text updated
  - CLI command preview updated
  
- **MainLayoutWorkflow.tsx**
  - Project path construction updated to use `_build/apps`
  - Comments and fallback messages updated

### 2. Backend API (Python/Flask)
- **web_server.py**
  - Default projects path: `source/apps` → `_build/apps`
  - Project discovery endpoint updated
  - Template generation response updated

### 3. CLI Tools (Python)
- **repo_dispatcher.py**
  - Application structure fix function updated
  - Project directory paths: `source/apps` → `_build/apps`
  - Comments and messages updated

- **template_engine.py**
  - Project structure creation updated
  - Default output directory: `source/apps` → `_build/apps`
  - Directory list updated

- **launch.py**
  - KIT_APP_PATH updated to use `_build/apps`

- **package.py**
  - Help text and references updated

### 4. Documentation
Files updated with bulk find/replace:
- README.md
- TEMPLATE_SYSTEM.md  
- CHANGELOG.md
- repo.toml
- kit_playground/*.md
- readme-assets/additional-docs/*.md

### 5. Infrastructure
- Created `_build/apps/` directory
- Verified `.gitignore` coverage (already ignores `_*/`)

## Migration Impact

### For Users
- **New projects** will automatically be created in `_build/apps/`
- **Existing projects** in `source/apps/` will continue to work but should be manually moved if desired
- Build outputs are now properly segregated in the `_build` directory

### For Developers
- All API endpoints now default to `_build/apps`
- Template generation system automatically creates correct structure
- Project discovery scans `_build/apps` by default

## Testing Checklist
- [ ] Create new project via UI
- [ ] Verify project appears in `_build/apps/{project_name}/`
- [ ] Verify project appears in "My Projects" sidebar
- [ ] Load project in editor
- [ ] Build project
- [ ] Run project

## Backward Compatibility
- The system can still read projects from custom locations
- Users can specify custom output directories via UI or CLI
- No breaking changes for standalone projects


## Post-Migration Fix Applied

After initial migration, discovered that the underlying `omni.repo.man` system still creates files in `source/apps/`. 

**Solution:** Updated `repo_dispatcher.py` post-processing to:
1. Look for newly created `.kit` files in `source/apps/` (where omni.repo.man creates them)
2. Move them to the correct `_build/apps/{project_name}/` directory structure
3. Create proper project metadata and structure

This ensures backward compatibility with the omni.repo.man tool while achieving the desired `_build/` hierarchy.

### Final Verification
```bash
./repo.sh template new kit_base_editor --name=my_company.my_editor --display-name="My Editor" --version=1.0.0
```

Result:
- ✅ Project created in `_build/apps/my_company.my_editor/`
- ✅ Contains `my_company.my_editor.kit`, `README.md`, `.project-meta.toml`
- ✅ No files left in `source/apps/`
- ✅ UI correctly discovers and loads projects from `_build/apps/`

