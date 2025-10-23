# Kit App Template - Systematic Enhancement Plan

## Executive Summary

This document provides a methodical, test-driven plan to enhance the kit-app-template system while **preserving backward compatibility** and existing CLI behavior. The plan follows a layer-by-layer approach with testing checkpoints at each stage.

### Core Principles

1. **Preserve Existing CLI Behavior** - No breaking changes to documented workflows
2. **Test-First Development** - Write compatibility tests before making changes
3. **Layer-by-Layer Enhancement** - Add features incrementally with validation
4. **Backward Compatibility** - New flags and features, not modified existing ones
5. **Checkpoint Validation** - Test, audit, validate at each stage before proceeding

## Current State Analysis

### What Works ✅

- **CLI Template System**: TOML-driven template discovery and generation (`template_engine.py`)
- **Kit Playground**: Flask backend + React frontend with visual template browser
- **Test Infrastructure**: Unit tests (security, xpra) + integration tests (icons, builds)
- **Documentation**: Comprehensive README, architecture docs, testing guides
- **Makefile**: Build automation for common tasks

### Known Issues ⚠️

1. **No Compatibility Tests**: Cannot validate that existing CLI workflows still work
2. **Interactive Mode Concerns**: Changes may have broken interactive template creation
3. **Undocumented Regressions**: Unknown if all templates build/launch correctly
4. **CLI vs API Divergence**: No API wrapper to expose CLI functionality non-interactively
5. **Missing Test Coverage**: Build/launch workflows for all templates not tested

## Phase 1: Foundation - Compatibility Testing

### Objective
Create comprehensive compatibility tests that validate existing CLI workflows work correctly. These tests serve as the baseline for all future changes.

### Tasks

#### 1.1 Create Compatibility Test Suite
**File**: `tests/compatibility/test_cli_workflows.py`

```python
# Test all existing CLI commands work as documented
class TestCLICompatibility:
    def test_template_list_works(self):
        """Verify ./repo.sh template list"""

    def test_template_docs_works(self):
        """Verify ./repo.sh template docs <name>"""

    def test_template_new_noninteractive(self):
        """Verify ./repo.sh template new <name> --name ... --display-name ..."""

    def test_build_command_works(self):
        """Verify ./repo.sh build"""

    def test_launch_command_works(self):
        """Verify ./repo.sh launch"""
```

#### 1.2 Create Template Generation Tests
**File**: `tests/compatibility/test_template_generation.py`

Test that ALL documented templates can be created:
- Applications: `kit_base_editor`, `omni_usd_viewer`, `omni_usd_explorer`, `omni_usd_composer`
- Extensions: `basic_python_extension`, `basic_python_ui_extension`, `basic_cpp_extension`, `basic_python_binding`
- Microservices: `kit_service`

#### 1.3 Create Build/Launch Tests
**File**: `tests/compatibility/test_template_builds.py` (enhance existing)

Test that generated templates can:
- Build successfully (`./repo.sh build --config release`)
- Launch with --no-window flag
- Exit cleanly
- Produce expected output structure

### Deliverables

- [ ] Compatibility test suite covering all CLI commands
- [ ] Template generation tests for all documented templates
- [ ] Build/launch tests with --no-window validation
- [ ] Test execution script: `make test-compatibility`
- [ ] Baseline test results documented (current passing/failing state)

### Success Criteria

- All tests run without errors (even if some fail - we're establishing baseline)
- Test results clearly show what currently works vs. what's broken
- Tests are fast enough for regular execution (< 2 minutes for quick suite)
- CI integration ready (can run in GitHub Actions / GitLab CI)

---

## Phase 2: CLI Enhancement - Non-Interactive Support

### Objective
Add non-interactive flags to CLI without breaking existing behavior. Enable automation and scripting.

### Current CLI Behavior (To Preserve)

**Interactive Mode** (no args - currently works):
```bash
./repo.sh template new
# Prompts for: template type, name, display name, version, etc.
```

**Non-Interactive Mode** (with args - currently works):
```bash
./repo.sh template new kit_base_editor --name my.app --display-name "My App" --version 1.0.0
```

### Enhancements Needed

#### 2.1 Add `--accept-license` Flag
**File**: `tools/repoman/template_engine.py`

Allows automation to bypass license prompt:
```bash
./repo.sh template new kit_base_editor --name my.app --accept-license
```

**Implementation**:
- Add `--accept-license` argument to template_engine.py
- Skip interactive license prompt if flag present
- Preserve existing interactive behavior when flag absent

#### 2.2 Add `--batch-mode` Flag
**File**: `tools/repoman/repo_dispatcher.py`

Enables fully non-interactive operation with sensible defaults:
```bash
./repo.sh template new kit_base_editor --name my.app --batch-mode
# Uses default version, display name, company name
```

**Implementation**:
- Add `--batch-mode` argument parser
- Provide defaults for all optional fields
- Exit with error if required fields missing (don't prompt)

#### 2.3 Add JSON Output Mode
**File**: `tools/repoman/template_engine.py`

Enables machine-readable output for CI/CD:
```bash
./repo.sh template new kit_base_editor --name my.app --json
# Outputs: {"status": "success", "path": "/path/to/app", ...}
```

**Implementation**:
- Add `--json` flag
- Suppress all print() statements when --json enabled
- Output structured JSON to stdout
- Errors go to stderr as JSON

#### 2.4 Add Verbose and Quiet Modes
```bash
./repo.sh template new kit_base_editor --name my.app --verbose  # Detailed output
./repo.sh template new kit_base_editor --name my.app --quiet    # Minimal output
```

### Testing Requirements

For each new flag, add tests:
- `tests/cli/test_noninteractive_flags.py`
- Verify flag works correctly
- Verify backward compatibility (existing commands still work)
- Verify error handling

### Deliverables

- [ ] `--accept-license` flag implemented and tested
- [ ] `--batch-mode` flag implemented and tested
- [ ] `--json` output mode implemented and tested
- [ ] `--verbose` and `--quiet` modes implemented and tested
- [ ] Documentation updated (README.md, CLI help text)
- [ ] All compatibility tests still pass

### Success Criteria

- CLI can be scripted without any interactive prompts
- Existing interactive mode still works
- All changes are additive (no breaking changes)
- CI/CD pipelines can use CLI non-interactively

---

## Phase 3: API Layer - REST API Wrapper

### Objective
Create a REST API that wraps all CLI functionality, enabling remote execution and web UI integration.

### Architecture

**Backend API Server**:
- Flask-based REST API (already exists in `kit_playground/backend/web_server.py`)
- Wraps CLI commands via subprocess
- Returns structured JSON responses
- Real-time WebSocket streaming for logs

**API Endpoints** (enhance existing):
```
POST   /api/template/create     - Create template from config
GET    /api/template/list       - List all templates
GET    /api/template/docs/{id}  - Get template documentation
POST   /api/build               - Build application
POST   /api/launch              - Launch application (--no-window + Xpra)
GET    /api/status/{job_id}     - Get job status
DELETE /api/stop/{job_id}       - Stop running job
```

### Implementation Tasks

#### 3.1 API Route Definitions
**File**: `kit_playground/backend/routes/cli_api_routes.py` (new)

Create routes that map 1:1 to CLI commands:

```python
@app.route('/api/template/create', methods=['POST'])
def create_template():
    """
    Accepts JSON body:
    {
        "template_name": "kit_base_editor",
        "name": "my.app",
        "display_name": "My App",
        "version": "1.0.0",
        "accept_license": true
    }

    Returns:
    {
        "job_id": "uuid",
        "status": "running|completed|failed",
        "output": "path/to/app"
    }
    """
    # Call CLI: ./repo.sh template new --json --accept-license ...
    # Stream output via WebSocket
    # Return structured response
```

#### 3.2 Job Management System
**File**: `kit_playground/backend/source/job_manager.py` (new)

Manage long-running CLI operations:
- Queue jobs (create, build, launch)
- Track job status
- Stream logs via WebSocket
- Handle job cancellation

#### 3.3 Command Logging System
**File**: `kit_playground/backend/source/command_logger.py` (enhance)

Log all CLI commands with:
- Timestamp
- Command executed
- Arguments
- Return code
- Output (stdout/stderr)
- Execution time

### Testing Requirements

#### 3.3.1 API Endpoint Tests
**File**: `tests/api/test_cli_api_endpoints.py` (new)

Test each endpoint:
- Request/response format
- Error handling
- Authentication (if added)
- Rate limiting

#### 3.3.2 CLI-API Equivalence Tests
**File**: `tests/api/test_cli_api_equivalence.py` (enhance existing)

Verify API calls produce same results as direct CLI execution:
```python
def test_template_create_equivalence():
    # Create via CLI
    cli_result = run_cli("./repo.sh template new kit_base_editor --name test1 --json")

    # Create via API
    api_result = requests.post("/api/template/create", json={...})

    # Assert same output
    assert cli_result["path"] == api_result["path"]
```

### Deliverables

- [ ] REST API routes for all CLI commands
- [ ] Job management system for long-running operations
- [ ] WebSocket streaming for real-time logs
- [ ] API documentation (OpenAPI/Swagger)
- [ ] API tests covering all endpoints
- [ ] CLI-API equivalence tests

### Success Criteria

- Every CLI operation can be performed via API
- API responses match CLI output (JSON mode)
- Real-time logging works via WebSocket
- API can be called from remote machines
- All tests pass

---

## Phase 4: Web UI Enhancement - Kit Playground

### Objective
Validate and enhance the Kit Playground web UI to provide full visual development experience.

### Current State
- React frontend (`kit_playground/ui/`)
- Flask backend (`kit_playground/backend/`)
- Template browser and editor
- Live preview pane

### Enhancement Tasks

#### 4.1 Template Gallery Validation
**File**: `kit_playground/ui/src/components/gallery/TemplateGallery.tsx`

Verify:
- All templates appear in gallery
- Icons display correctly (already tested in `test_template_icons.py`)
- Search and filter work
- Template metadata displays

#### 4.2 Project Creation Flow
**File**: `kit_playground/ui/src/components/dialogs/CreateProjectDialog.tsx`

Enhance:
- Form validation (name format, version format)
- Real-time feedback
- Progress indicators
- Error handling

#### 4.3 Build Integration
**File**: `kit_playground/ui/src/components/layout/MainLayout.tsx`

Enhance:
- Build button triggers API call
- Real-time log streaming
- Build status indicators
- Error highlighting

#### 4.4 Launch Integration (Xpra)
**File**: `kit_playground/backend/xpra_manager.py`

Enhance:
- Launch app with --no-window
- Start Xpra session
- Embed Xpra HTML5 client in UI
- Handle session cleanup

### Testing Requirements

#### 4.4.1 Frontend Component Tests
**File**: `kit_playground/ui/src/components/__tests__/` (new directory)

Use Jest + React Testing Library:
- Template gallery rendering
- Create dialog validation
- Build/launch button interactions

#### 4.4.2 E2E UI Tests
**File**: `tests/e2e/test_playground_workflows.py` (new)

Use Playwright or Selenium:
- Full template creation workflow
- Build + launch workflow
- Error handling

### Deliverables

- [ ] Template gallery fully functional
- [ ] Project creation wizard validated
- [ ] Build integration with real-time logs
- [ ] Launch integration with Xpra embedding
- [ ] Frontend component tests
- [ ] E2E tests for critical workflows

### Success Criteria

- UI provides complete visual alternative to CLI
- All features work without command line
- Real-time feedback for all operations
- Error messages are clear and actionable

---

## Phase 5: Standalone Projects

### Objective
Enable creation of self-contained projects that can be built independently outside the repository.

### Current Behavior
Templates are created in `source/apps/` and built in `_build/`, but they depend on repository structure.

### Enhancement: True Standalone Projects

**Usage**:
```bash
./repo.sh template new kit_base_editor \
  --name my.app \
  --output-dir ~/my-standalone-app \
  --standalone
```

**Generated Structure**:
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
├── repo.toml                # Local config
└── requirements.txt         # Python dependencies
```

### Implementation Tasks

#### 5.1 Standalone Template Generator
**File**: `tools/repoman/standalone_generator.py` (new)

Copy required files:
- Build tools (`tools/packman/`, `tools/repoman/`)
- Configuration files (`premake5.lua`, `repo.toml`)
- Dependencies (`requirements.txt`)
- Wrapper scripts (`repo.sh`, `repo.bat`)

Modify files for standalone operation:
- Update paths in repo.toml
- Create isolated premake5.lua
- Update wrapper scripts to work standalone

#### 5.2 Standalone Testing
**File**: `tests/standalone/test_standalone_projects.py` (new)

Test:
- Standalone project creation
- Build in isolated directory
- Launch independent of original repo
- No dependency on repository

### Deliverables

- [ ] `--standalone` flag implementation
- [ ] Standalone project generator
- [ ] Standalone project tests
- [ ] Documentation for standalone workflow

### Success Criteria

- Standalone projects can be created in any directory
- Projects build without access to original repository
- Projects are distributable (zip/tar and extract elsewhere)
- All dependencies included or documented

---

## Phase 6: Per-Application Kit Dependencies

### Objective
Store Kit SDK and dependencies per-application instead of globally.

### Current Behavior
```
_build/
├── linux-x86_64/release/
│   ├── kit/                 # Global Kit SDK (shared by all apps)
│   ├── exts/                # Global extensions
│   └── apps/                # Application directories
```

### Enhanced Behavior
```
source/apps/my_company.my_app/
├── my_company.my_app.kit
├── .project-meta.toml
├── _kit/                    # App-specific Kit SDK
│   ├── kit/
│   └── exts/
└── dependencies/
    └── kit-sdk.toml         # App-specific dependencies
```

### Implementation Tasks

#### 6.1 Per-App Dependency Management
**File**: `tools/repoman/app_dependencies.py` (new)

- Parse app-specific dependency files
- Download Kit SDK per-application
- Install extensions per-application
- Isolate build artifacts

#### 6.2 Update Build System
**File**: `premake5.lua`, `tools/repoman/repoman.py`

- Support per-app Kit SDK paths
- Update launch commands to use app-specific SDK
- Handle dependency conflicts

### Benefits

- Apps can use different Kit SDK versions
- True application isolation
- Easier distribution (bundle SDK with app)
- Multiple apps with incompatible dependencies

### Deliverables

- [ ] Per-app dependency management system
- [ ] Build system updates
- [ ] Migration guide for existing apps
- [ ] Tests for multi-version scenarios

### Success Criteria

- Apps can specify their own Kit SDK version
- Multiple apps with different SDK versions coexist
- Build times don't significantly increase

---

## Testing Strategy

### Test Pyramid

```
     E2E Tests (Slow)                    [~1 hour]
    /                \
   /  Integration Tests \                [~10 min]
  /        (Medium)       \
 /                         \
/    Unit Tests (Fast)      \           [~1 min]
\                           /
 \                         /
  \ Compatibility Tests   /              [~2 min]
   \     (Baseline)      /
    -------------------
```

### Test Execution Targets

```makefile
# Quick feedback loop (development)
make test-quick              # Unit + compatibility tests (< 3 min)

# Pre-commit validation
make test-compatibility      # Ensure no regressions
make test-unit               # Fast unit tests

# Pull request validation
make test-integration        # Integration tests (no slow builds)

# Nightly / release validation
make test-all                # Everything including full builds
```

### Coverage Requirements

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All templates tested
- **Compatibility Tests**: All documented CLI workflows
- **E2E Tests**: Critical user journeys (create, build, launch)

---

## Audit and Validation Process

### After Each Phase

1. **Run All Tests**
   ```bash
   make test-all
   ```

2. **Manual Verification**
   - Run through Quick Start guide
   - Test both CLI and UI workflows
   - Verify documentation accuracy

3. **Code Review Checklist**
   - [ ] Backward compatibility preserved
   - [ ] New tests added for new features
   - [ ] Documentation updated
   - [ ] No deprecated patterns introduced
   - [ ] Error messages are clear

4. **Performance Validation**
   - Build times not significantly increased
   - CLI response time < 1 second for list/docs
   - API response time < 200ms for lightweight endpoints

5. **Security Audit**
   - Run security tests: `pytest tests/unit/test_security_validators.py`
   - Check for command injection vulnerabilities
   - Validate path traversal protection

### Sign-off Criteria

Each phase requires:
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Audit checklist completed
- [ ] Performance validated
- [ ] Security validated

---

## Rollback Strategy

### If Phase Introduces Regressions

1. **Immediate**: Revert commits in phase
2. **Analyze**: Review test failures and user reports
3. **Fix**: Address issues in feature branch
4. **Re-validate**: Run full test suite
5. **Re-merge**: Only after all tests pass

### Git Strategy

```bash
# Each phase is a feature branch
git checkout -b phase-1-compatibility-testing
# Work, commit, test
git checkout -b phase-2-cli-enhancement
# Work, commit, test
# etc.

# Only merge to main after complete validation
git checkout main
git merge --no-ff phase-1-compatibility-testing
```

---

## Timeline and Milestones

### Phase 1: Foundation (Week 1-2)
- **Week 1**: Create compatibility test suite
- **Week 2**: Establish baseline, document current state

### Phase 2: CLI Enhancement (Week 3-4)
- **Week 3**: Implement non-interactive flags
- **Week 4**: Testing and documentation

### Phase 3: API Layer (Week 5-7)
- **Week 5-6**: API implementation and job management
- **Week 7**: Testing and CLI-API equivalence validation

### Phase 4: Web UI (Week 8-10)
- **Week 8-9**: UI validation and enhancement
- **Week 10**: E2E testing

### Phase 5: Standalone Projects (Week 11-12)
- **Week 11**: Implementation
- **Week 12**: Testing and documentation

### Phase 6: Per-App Dependencies (Week 13-15)
- **Week 13-14**: Implementation and build system updates
- **Week 15**: Testing and migration guide

---

## Success Metrics

### Quantitative

- **Test Coverage**: > 80% for core modules
- **Test Execution Time**: < 3 minutes for quick suite
- **Build Time**: No more than 10% increase
- **API Response Time**: < 200ms for lightweight endpoints
- **Zero Breaking Changes**: All existing docs/examples still work

### Qualitative

- **Ease of Use**: New users can create first app in < 5 minutes
- **Automation**: Full CI/CD pipeline without interactive prompts
- **Visual Experience**: Playground provides complete alternative to CLI
- **Documentation**: Clear, accurate, with examples

---

## Risk Mitigation

### High-Risk Areas

1. **Breaking Existing CLI**: Mitigated by compatibility tests first
2. **Build System Regressions**: Mitigated by comprehensive build tests
3. **Performance Degradation**: Mitigated by benchmarking at each phase
4. **Security Vulnerabilities**: Mitigated by existing security tests + audits

### Contingency Plans

- **Phase fails validation**: Roll back, analyze, fix in isolation
- **Timeline slips**: Reduce scope of non-critical phases
- **Resource constraints**: Focus on Phases 1-3 (foundation + automation)

---

## Appendices

### A. Current CLI Command Reference

```bash
# Template system
./repo.sh template list [--type=TYPE]
./repo.sh template docs TEMPLATE_NAME
./repo.sh template new TEMPLATE_NAME [--name NAME] [--display-name NAME] [--version VER]

# Build and launch
./repo.sh build [--config=release|debug] [--clean]
./repo.sh launch [--name APP_NAME]

# Playground
./repo.sh playground
```

### B. Test Organization

```
tests/
├── compatibility/           # Phase 1 - Baseline tests
│   ├── test_cli_workflows.py
│   ├── test_template_generation.py
│   └── test_template_builds.py
├── cli/                     # Phase 2 - CLI enhancement tests
│   ├── test_noninteractive_flags.py
│   └── test_json_output.py
├── api/                     # Phase 3 - API tests
│   ├── test_cli_api_endpoints.py
│   └── test_cli_api_equivalence.py
├── ui/                      # Phase 4 - UI tests
│   ├── test_template_gallery.py
│   └── test_build_integration.py
├── standalone/              # Phase 5 - Standalone tests
│   └── test_standalone_projects.py
├── unit/                    # Fast unit tests
└── integration/             # Integration tests
```

### C. API Endpoint Specification

```yaml
openapi: 3.0.0
info:
  title: Kit Playground API
  version: 1.0.0

paths:
  /api/template/list:
    get:
      summary: List all templates
      responses:
        200:
          description: List of templates
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Template'

  /api/template/create:
    post:
      summary: Create template
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTemplateRequest'
      responses:
        200:
          description: Template created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateTemplateResponse'

components:
  schemas:
    Template:
      type: object
      properties:
        name: { type: string }
        type: { type: string }
        category: { type: string }
        description: { type: string }

    CreateTemplateRequest:
      type: object
      required: [template_name, name]
      properties:
        template_name: { type: string }
        name: { type: string }
        display_name: { type: string }
        version: { type: string }
        accept_license: { type: boolean }

    CreateTemplateResponse:
      type: object
      properties:
        job_id: { type: string }
        status: { type: string, enum: [running, completed, failed] }
        output: { type: string }
        error: { type: string }
```

---

## Conclusion

This plan provides a systematic, test-driven approach to enhancing the kit-app-template system while preserving backward compatibility. By following the layer-by-layer methodology with checkpoints at each stage, we minimize risk and ensure quality.

### Key Principles Reinforced

1. ✅ **Test First** - Establish baseline before making changes
2. ✅ **Backward Compatible** - Existing workflows must continue to work
3. ✅ **Incremental** - Small, validated steps rather than big bang
4. ✅ **Auditable** - Clear checkpoints and validation criteria
5. ✅ **Documented** - Each phase produces updated documentation

### Next Steps

1. Review and approve this plan
2. Begin Phase 1: Create compatibility test suite
3. Establish baseline test results
4. Proceed with Phase 2 only after Phase 1 validation

**This plan is a living document and should be updated as implementation progresses and new insights emerge.**
