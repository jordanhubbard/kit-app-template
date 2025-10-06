# API Endpoint Synchronization Audit

## Executive Summary

This document audits all API endpoints called by the frontend UI and verifies they match the backend implementation.

**Date**: 2025-10-06  
**Status**: 🔴 **CRITICAL MISMATCHES FOUND**

---

## Frontend API Calls (from UI code)

### Configuration Endpoints
1. ✅ `GET /api/config/paths` - Get repo and default paths
   - **UI Files**: MainLayoutWorkflow.tsx, CreateProjectDialog.tsx
   - **Backend**: web_server.py (lines 189-206)
   - **Status**: ✅ IMPLEMENTED

### V2 Template Endpoints  
2. ✅ `GET /api/v2/templates` - List all templates with icons
   - **UI Files**: MainLayoutWorkflow.tsx, TemplateGallery.tsx
   - **Backend**: routes/v2_template_routes.py:29
   - **Status**: ✅ IMPLEMENTED (just added)

3. ✅ `POST /api/v2/templates/generate` - Create project from template
   - **UI Files**: CreateProjectDialog.tsx
   - **Backend**: routes/v2_template_routes.py:185
   - **Status**: ✅ IMPLEMENTED (just added)

4. ✅ `GET /api/v2/templates/{id}/icon` - Get template icon image
   - **UI Files**: Rendered by browser from icon URLs
   - **Backend**: routes/v2_template_routes.py:104
   - **Status**: ✅ IMPLEMENTED (just added)

### Project Endpoints
5. ❌ `GET /api/projects/discover?path={path}` - Discover existing projects
   - **UI Files**: MainLayoutWorkflow.tsx:82
   - **Backend**: ❌ **MISSING**
   - **Status**: 🔴 **NOT IMPLEMENTED**

6. ✅ `POST /api/projects/build` - Build a project
   - **UI Files**: MainLayoutWorkflow.tsx:305
   - **Backend**: routes/project_routes.py:40
   - **Status**: ✅ IMPLEMENTED

7. ✅ `POST /api/projects/run` - Run a project
   - **UI Files**: MainLayoutWorkflow.tsx:350
   - **Backend**: routes/project_routes.py:129
   - **Status**: ✅ IMPLEMENTED

8. ❌ `POST /api/projects/stop` - Stop a running project
   - **UI Files**: MainLayoutWorkflow.tsx:387
   - **Backend**: routes/project_routes.py:288 (`/api/projects/stop/<project_name>`)
   - **Status**: 🟡 **MISMATCH** - Backend requires project_name in URL, UI sends in body

### Filesystem Endpoints
9. ✅ `GET /api/filesystem/cwd` - Get current working directory
   - **UI Files**: DirectoryBrowserDialog.tsx:77, FileExplorer.tsx:113
   - **Backend**: routes/filesystem_routes.py:27
   - **Status**: ✅ IMPLEMENTED

10. ✅ `GET /api/filesystem/list?path={path}` - List directory contents
    - **UI Files**: CreateProjectDialog.tsx:84, DirectoryBrowserDialog.tsx:92, FileExplorer.tsx:70
    - **Backend**: routes/filesystem_routes.py:40
    - **Status**: ✅ IMPLEMENTED

11. ✅ `GET /api/filesystem/read?path={path}` - Read file contents
    - **UI Files**: MainLayoutWorkflow.tsx:235, 445
    - **Backend**: routes/filesystem_routes.py:96
    - **Status**: ✅ IMPLEMENTED

12. ✅ `POST /api/filesystem/mkdir` - Create directory
    - **UI Files**: FileExplorer.tsx:158
    - **Backend**: routes/filesystem_routes.py:75
    - **Status**: ✅ IMPLEMENTED

### Xpra/Preview Endpoints
13. ❌ `GET /api/xpra/check` - Check if Xpra is available
    - **UI Files**: PreviewPane.tsx:67
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

### Legacy Template Endpoints (MainLayout.tsx - Old UI?)
14. ❌ `GET /api/templates` - List templates (old format)
    - **UI Files**: store/slices/templatesSlice.ts:36
    - **Backend**: routes/template_routes.py has `/api/templates/list` instead
    - **Status**: 🟡 **MISMATCH** - Wrong endpoint

15. ❌ `GET /api/templates/{id}/code` - Get template source code
    - **UI Files**: MainLayout.tsx:53, MainLayoutWorkflow.tsx:274
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

16. ❌ `POST /api/templates/{id}/update` - Update template code
    - **UI Files**: MainLayout.tsx:78
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

17. ❌ `POST /api/templates/{id}/build` - Build template
    - **UI Files**: MainLayout.tsx:107
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

18. ❌ `POST /api/templates/{id}/run` - Run template
    - **UI Files**: MainLayout.tsx:121
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

19. ❌ `POST /api/templates/{id}/stop` - Stop running template
    - **UI Files**: (implicit from MainLayout.tsx run/stop toggle)
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

20. ❌ `POST /api/templates/{id}/deploy` - Deploy template
    - **UI Files**: MainLayout.tsx:141
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

21. ❌ `POST /api/templates/{id}/copy` - Copy template
    - **UI Files**: MainLayout.tsx:165
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

22. ❌ `POST /api/templates/auto-connect` - Auto-connect templates
    - **UI Files**: ConnectionEditor.tsx:122
    - **Backend**: ❌ **MISSING**
    - **Status**: 🔴 **NOT IMPLEMENTED**

---

## Backend Routes (Implemented)

### /api/config/* (web_server.py)
- ✅ `GET /api/config/paths`

### /api/v2/templates/* (routes/v2_template_routes.py)
- ✅ `GET /api/v2/templates`
- ✅ `GET /api/v2/templates/{id}/icon`
- ✅ `GET /api/v2/templates/{id}/docs`
- ✅ `POST /api/v2/templates/generate`

### /api/templates/* (routes/template_routes.py)
- ✅ `GET /api/templates/list` (but UI calls `/api/templates`)
- ✅ `GET /api/templates/get/{name}`
- ✅ `POST /api/templates/create`

### /api/projects/* (routes/project_routes.py)
- ✅ `POST /api/projects/build`
- ✅ `POST /api/projects/run`
- ✅ `POST /api/projects/stop/<project_name>` (but UI calls `/api/projects/stop` with body)

### /api/filesystem/* (routes/filesystem_routes.py)
- ✅ `GET /api/filesystem/cwd`
- ✅ `GET /api/filesystem/list`
- ✅ `POST /api/filesystem/mkdir`
- ✅ `GET /api/filesystem/read`

---

## Critical Issues to Fix

### Priority 1: Blocking Issues
1. **Missing `/api/projects/discover`** - UI can't discover existing projects
2. **Mismatch `/api/projects/stop`** - Route signature doesn't match UI call

### Priority 2: Xpra Support
3. **Missing `/api/xpra/check`** - UI can't verify Xpra availability

### Priority 3: Legacy Template Endpoints (if MainLayout.tsx is still used)
4. **Missing multiple `/api/templates/{id}/*` endpoints** - Template editing features won't work

### Priority 4: Template List Endpoint Mismatch
5. **`/api/templates` vs `/api/templates/list`** - Redux store may break

---

## Recommended Actions

1. ✅ **DONE**: Add v2 template routes with icon support
2. **TODO**: Add `/api/projects/discover` endpoint
3. **TODO**: Fix `/api/projects/stop` to accept body parameter
4. **TODO**: Add `/api/xpra/check` endpoint
5. **TODO**: Add route alias `/api/templates` → `/api/templates/list`
6. **TODO**: Investigate if MainLayout.tsx is still used (appears to be old UI)
7. **TODO**: If MainLayout.tsx is active, implement missing template/* endpoints

---

## Notes

- Some UI files (MainLayout.tsx, ConnectionEditor.tsx) may be from an older version of the UI
- MainLayoutWorkflow.tsx appears to be the current active UI
- The v2 API endpoints were just added to support the current UI
- Many old template management endpoints are not implemented in the refactored backend

