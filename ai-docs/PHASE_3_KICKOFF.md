# Phase 3: API Layer - REST API Wrapper

**Started**: October 23, 2025
**Branch**: phase-3-api-layer
**Status**: 🚀 **IN PROGRESS**

## Overview

Phase 3 focuses on enhancing the REST API layer to provide complete CLI functionality via HTTP endpoints, enabling:
- Remote execution from web UI
- CI/CD pipeline integration via API
- Job management for long-running operations
- Real-time log streaming via WebSocket

## Current State

### Existing Infrastructure ✅

The kit_playground backend already has:
- ✅ **Flask-based API server** (`kit_playground/backend/web_server.py`)
- ✅ **Template routes** (`routes/template_routes.py`)
  - `/api/templates/list` - List templates
  - `/api/templates/get/<name>` - Get template details
  - `/api/templates/create` - Create from template
- ✅ **TemplateAPI integration** (uses `tools/repoman/template_api.py`)
- ✅ **Project routes** (`routes/project_routes.py`)
- ✅ **Xpra integration** (`xpra_manager.py`)

### What Needs Enhancement

1. **Leverage Phase 2 CLI Flags** ⏳
   - API should use `--json` for machine-readable output
   - API should use `--accept-license` for automation
   - API should use `--quiet` for minimal output

2. **Job Management System** ⏳
   - Long-running operations (build, launch) need job tracking
   - Status polling for async operations
   - Job cancellation support

3. **WebSocket Streaming** ⏳
   - Real-time log output during builds
   - Progress updates for template creation
   - Live feedback to web UI

4. **Comprehensive Testing** ⏳
   - API endpoint tests
   - CLI-API equivalence tests
   - Integration tests

5. **API Documentation** ⏳
   - OpenAPI/Swagger documentation
   - Usage examples
   - Error codes and responses

## Phase 3 Goals

### Primary Objectives

1. ✅ **Complete API Coverage**
   - Every CLI command accessible via API
   - Consistent request/response format
   - Proper error handling

2. ✅ **Job Management**
   - Queue long-running operations
   - Track job status
   - Cancel jobs
   - Retrieve job results

3. ✅ **Real-Time Streaming**
   - WebSocket support for logs
   - Progress updates
   - Live feedback

4. ✅ **Testing**
   - API endpoint tests
   - CLI-API equivalence
   - Integration tests

5. ✅ **Documentation**
   - OpenAPI spec
   - Usage examples
   - API reference

## Architecture

### API Endpoints

#### Existing (to enhance)
```
GET  /api/templates/list          - List all templates
GET  /api/templates/get/<name>    - Get template details
POST /api/templates/create        - Create from template
```

#### To Add
```
POST /api/build                   - Build application
POST /api/launch                  - Launch application
GET  /api/jobs/<job_id>          - Get job status
DELETE /api/jobs/<job_id>        - Cancel job
WS   /api/stream/<job_id>        - Stream logs via WebSocket
```

### Job Management Flow

```
1. Client: POST /api/templates/create
2. Server: Creates job, returns job_id
3. Server: Executes CLI command async
4. Client: GET /api/jobs/<job_id> (polling)
   OR
   Client: WS /api/stream/<job_id> (streaming)
5. Server: Returns status/output
```

### Components

```
kit_playground/backend/
├── web_server.py                 # Main Flask app
├── routes/
│   ├── template_routes.py        # Template endpoints (enhance)
│   ├── build_routes.py           # Build endpoints (new)
│   ├── job_routes.py             # Job management (new)
│   └── websocket_routes.py       # WebSocket streaming (new)
├── source/
│   ├── job_manager.py            # Job queue/tracking (new)
│   ├── command_executor.py       # CLI command wrapper (new)
│   └── log_streamer.py           # WebSocket log streaming (new)
└── tests/
    └── api/
        ├── test_template_api.py  # Template endpoint tests (new)
        ├── test_job_api.py       # Job management tests (new)
        └── test_cli_api_equivalence.py  # Equivalence tests (new)
```

## Implementation Plan

### Week 1: Core API & Testing

#### Day 1-2: Setup & Template API Tests
- [ ] Create `tests/api/` directory structure
- [ ] Write tests for `/api/templates/list`
- [ ] Write tests for `/api/templates/create`
- [ ] Enhance `template_routes.py` to use `--json` CLI flag

#### Day 3-4: Job Management Foundation
- [ ] Create `job_manager.py`
- [ ] Implement job queue
- [ ] Add job status tracking
- [ ] Write job management tests

#### Day 5: CLI-API Equivalence
- [ ] Write equivalence tests
- [ ] Verify API matches CLI output
- [ ] Document any differences

### Week 2: Streaming & Documentation

#### Day 1-2: WebSocket Streaming
- [ ] Implement WebSocket support
- [ ] Create log streamer
- [ ] Add progress updates
- [ ] Write streaming tests

#### Day 3-4: Build/Launch Endpoints
- [ ] Add `/api/build` endpoint
- [ ] Add `/api/launch` endpoint
- [ ] Integrate with job management
- [ ] Write tests

#### Day 5: Documentation & Polish
- [ ] Generate OpenAPI spec
- [ ] Write API documentation
- [ ] Create usage examples
- [ ] Run all tests
- [ ] Checkpoint 3 validation

## Test-First Approach

Following Phase 1 & 2 success:

1. **Write tests first** for each endpoint
2. **Run tests** to see current behavior
3. **Implement** to make tests pass
4. **Document** the API
5. **Validate** with integration tests

## Success Criteria

### Must Have
- [ ] All CLI commands accessible via API
- [ ] API tests: 90%+ pass rate
- [ ] CLI-API equivalence validated
- [ ] Job management working
- [ ] Zero regressions (Phase 1 & 2 tests still pass)

### Should Have
- [ ] WebSocket streaming working
- [ ] OpenAPI documentation complete
- [ ] Build/launch endpoints implemented

### Nice to Have
- [ ] Rate limiting
- [ ] Authentication/authorization
- [ ] API versioning

## Initial Discovery

### Existing API Review

**Template Routes** (`routes/template_routes.py`):
- ✅ Uses `TemplateAPI` from Phase 1 work
- ✅ Already has `/list`, `/get`, `/create` endpoints
- ⚠️ Doesn't use Phase 2 `--json` CLI flags
- ⚠️ Direct API calls, not via CLI subprocess

**Current Behavior**:
- API calls Python directly (TemplateAPI)
- Not using CLI subprocess
- Not getting CLI JSON output

**Implications**:
- **Option A**: Continue using TemplateAPI directly (faster, cleaner)
- **Option B**: Wrap CLI with subprocess (matches Phase 2 work)
- **Recommended**: Option A (TemplateAPI), but add CLI equivalence tests

## Phase 3 Strategy

### Hybrid Approach

1. **Keep using TemplateAPI** for template operations
   - Already works well
   - No subprocess overhead
   - Direct Python API

2. **Add CLI subprocess wrapper** for operations that need it
   - Build commands
   - Launch commands
   - Operations that benefit from `--json` output

3. **Add job management** for long-running operations
   - Build (can be slow)
   - Launch (background process)
   - Template creation with large projects

4. **Test equivalence** between API and CLI
   - Ensure API and CLI produce same results
   - Document any differences
   - Validate with integration tests

## Files to Create/Modify

### New Files
```
tests/api/__init__.py
tests/api/conftest.py
tests/api/test_template_api.py
tests/api/test_job_api.py
tests/api/test_cli_api_equivalence.py
kit_playground/backend/source/job_manager.py
kit_playground/backend/source/command_executor.py
kit_playground/backend/routes/job_routes.py
PHASE_3_COMPLETE.md
```

### Modified Files
```
kit_playground/backend/routes/template_routes.py
kit_playground/backend/web_server.py
```

## Next Steps

1. ✅ Create Phase 3 branch
2. ✅ Create kickoff document
3. ⏳ Create `tests/api/` directory
4. ⏳ Write first API tests
5. ⏳ Review existing API implementation
6. ⏳ Enhance with Phase 2 features

---

**Status**: 🚀 **STARTED**
**Next Task**: Create test infrastructure and write first API tests
**Following**: Test-first methodology from Phase 1 & 2
