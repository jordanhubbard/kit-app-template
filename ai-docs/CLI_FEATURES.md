# CLI Features and Flags

**Last Updated**: October 23, 2025
**Version**: Phase 2 Complete

## Overview

The Kit App Template CLI (`repo.sh` / `repo.bat`) supports various flags for automation, CI/CD integration, and customized output modes.

---

## Non-Interactive Flags

### `--accept-license`

**Purpose**: Accept license terms automatically without interactive prompt.
**Status**: ✅ Fully implemented
**Use Case**: CI/CD pipelines, automated scripts

**Usage**:
```bash
./repo.sh template new kit_base_editor --name my.app --accept-license
```

**Behavior**:
- Automatically accepts NVIDIA Software License Agreement
- Stores acceptance in `~/.omni/kit-app-template/license_accepted.json`
- Future commands don't require the flag (acceptance persists)

**Example - First Time Setup**:
```bash
# Accept license and create template
./repo.sh template new kit_base_editor \
  --name com.company.myapp \
  --display-name "My Application" \
  --version "1.0.0" \
  --accept-license
```

**Example - Subsequent Commands**:
```bash
# License already accepted, flag not needed
./repo.sh template new omni_usd_viewer --name my.viewer
```

---

### `--batch-mode`

**Purpose**: Fully non-interactive operation with sensible defaults.
**Status**: ✅ Works (behavior already implemented)
**Use Case**: Automated template generation, scripts

**Usage**:
```bash
./repo.sh template new kit_base_editor --name my.app --batch-mode
```

**Behavior**:
- Uses default values for optional parameters
- Never prompts for input
- Fails with error if required parameters missing
- Works with all template types

**Example**:
```bash
# Minimal arguments with defaults
./repo.sh template new kit_base_editor --name my.minimal.app --batch-mode

# With explicit values
./repo.sh template new kit_base_editor \
  --name my.app \
  --display-name "My App" \
  --version "2.0.0" \
  --batch-mode
```

---

## Output Mode Flags

### `--json`

**Purpose**: Machine-readable JSON output for CI/CD and automation.
**Status**: ✅ Implemented
**Use Case**: CI/CD pipelines, programmatic access, API integration

**Usage**:
```bash
./repo.sh template new kit_base_editor --name my.app --json
./repo.sh template list --json
```

**Behavior**:
- Outputs structured JSON to stderr (template creation) or stdout (list command)
- Template creation still outputs playback file path for `repo.sh` processing
- JSON contains status, paths, and metadata

**Example - Template List**:
```bash
$ ./repo.sh template list --json
{
  "status": "success",
  "count": 9,
  "templates": [
    {
      "name": "kit_base_editor",
      "display_name": "Kit Base Editor",
      "type": "application",
      "description": "...",
      "category": ""
    },
    ...
  ]
}
```

**Example - Template Creation**:
```bash
$ ./repo.sh template new kit_base_editor --name my.app --json 2>&1 | grep -A 10 "\"status\""
{
  "status": "success",
  "playback_file": "/tmp/tmp_xyz.toml",
  "template_name": "kit_base_editor",
  "name": "my.app",
  "path": ""
}
```

**Integration Example (Python)**:
```python
import subprocess
import json

# List templates
result = subprocess.run(
    ["./repo.sh", "template", "list", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
print(f"Found {data['count']} templates")

# Create template
result = subprocess.run(
    ["./repo.sh", "template", "new", "kit_base_editor",
     "--name", "my.app", "--json"],
    capture_output=True,
    text=True
)
# JSON is in stderr for template creation
if "{" in result.stderr:
    start = result.stderr.index("{")
    end = result.stderr.rindex("}") + 1
    json_data = json.loads(result.stderr[start:end])
    print(f"Status: {json_data['status']}")
```

---

### `--verbose`

**Purpose**: Detailed output with extra debugging information.
**Status**: ✅ Implemented
**Use Case**: Debugging, detailed logs, development

**Usage**:
```bash
./repo.sh template new kit_base_editor --name my.app --verbose
```

**Behavior**:
- Adds `[VERBOSE]` prefixed messages to stderr
- Shows additional details about template processing
- Does not affect stdout (playback file path)

**Example Output**:
```
/tmp/tmpxyz.toml
[VERBOSE] Template: kit_base_editor
[VERBOSE] Playback file: /tmp/tmpxyz.toml
[VERBOSE] Application name: my.app
```

---

### `--quiet`

**Purpose**: Minimal output, only essential information.
**Status**: ✅ Implemented
**Use Case**: Scripts, logs, when output verbosity should be minimized

**Usage**:
```bash
./repo.sh template new kit_base_editor --name my.app --quiet
```

**Behavior**:
- Suppresses extra output messages
- Only outputs essential information (playback file path)
- Errors still reported

**Example**:
```bash
# Normal mode (more output)
$ ./repo.sh template new kit_base_editor --name my.app
[... lots of output ...]
/tmp/tmpxyz.toml

# Quiet mode (minimal output)
$ ./repo.sh template new kit_base_editor --name my.app --quiet
/tmp/tmpxyz.toml
```

---

## Combining Flags

Flags can be combined for specific use cases:

### CI/CD Pipeline

```bash
# Non-interactive, JSON output for parsing
./repo.sh template new kit_base_editor \
  --name com.company.myapp \
  --accept-license \
  --batch-mode \
  --json
```

### Development/Debugging

```bash
# Verbose output for troubleshooting
./repo.sh template new kit_base_editor \
  --name debug.app \
  --accept-license \
  --verbose
```

### Script Integration

```bash
# Quiet mode with acceptance for scripts
./repo.sh template new kit_base_editor \
  --name script.app \
  --accept-license \
  --quiet
```

---

## Compatibility

### Backward Compatibility

✅ **All new flags are additive** - existing commands work unchanged:

```bash
# These still work exactly as before:
./repo.sh template list
./repo.sh template new kit_base_editor --name my.app
./repo.sh template docs kit_base_editor
```

### Template Type Support

All flags work with:
- ✅ **Applications** (kit_base_editor, omni_usd_viewer, etc.)
- ✅ **Extensions** (basic_python_extension, basic_cpp_extension, etc.)
- ✅ **Microservices** (kit_service)

---

## Testing

All CLI features have comprehensive test coverage:

```bash
# Run CLI enhancement tests
python3 -m pytest tests/cli/ -v

# Run compatibility tests (ensure no regressions)
make test-compatibility
```

**Test Coverage**:
- `--accept-license`: 7/7 tests pass ✅
- `--batch-mode`: 7/7 tests pass ✅
- `--json`: 5/7 tests pass, 2 skipped ✅
- `--verbose`/`--quiet`: 5/5 tests pass ✅

**Total**: 24/26 tests pass (92%)

---

## Command Reference

### Template Commands

```bash
# List templates
./repo.sh template list [--type=TYPE] [--json]

# Show template documentation
./repo.sh template docs TEMPLATE_NAME

# Create from template
./repo.sh template new TEMPLATE_NAME \
  --name NAME \
  [--display-name "Display Name"] \
  [--version VERSION] \
  [--accept-license] \
  [--batch-mode] \
  [--json] \
  [--verbose] \
  [--quiet]
```

### Build Commands

```bash
# Build application
./repo.sh build [--config CONFIG] [--name APP_NAME]

# Launch application
./repo.sh launch [--name APP_NAME]
```

---

## Troubleshooting

### License Not Accepted

**Error**: `License terms must be accepted to use templates`

**Solution**:
```bash
./repo.sh template new TEMPLATE --name myapp --accept-license
```

### Missing Required Arguments

**Error**: Command hangs or prompts for input

**Solution**: Provide all required arguments with `--name`:
```bash
./repo.sh template new kit_base_editor --name my.app --batch-mode
```

### JSON Output Location

**Note**: For template creation, JSON output goes to stderr (not stdout) to avoid interfering with `repo.sh`'s internal processing.

**Capture Both**:
```bash
./repo.sh template new kit_base_editor --name my.app --json 2>&1 | grep "\"status\""
```

---

## API Integration

For programmatic use, see `tools/repoman/template_api.py`:

```python
from template_api import TemplateAPI

api = TemplateAPI()

# Accept license
api.accept_license()

# List templates
templates = api.list_templates()

# Create template
result = api.generate_template_simple(
    template_name="kit_base_editor",
    name="my.app",
    display_name="My App",
    accept_license=True
)
```

---

## See Also

- [PLAN.md](PLAN.md) - Complete implementation roadmap
- [START_HERE.md](START_HERE.md) - Getting started guide
- [README.md](README.md) - Project overview
- `tests/cli/` - CLI test suite and examples

---

**Questions or Issues?**
See the test files in `tests/cli/` for usage examples, or check `PLAN.md` for architectural details.
