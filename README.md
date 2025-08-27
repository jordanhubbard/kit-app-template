# Kit Template - Modern Template System for Omniverse Kit

A clean, data-driven template system for creating Omniverse Kit applications and extensions. This tool replaces complex interactive workflows with simple, declarative configuration that's perfect for automation, CI/CD, and AI-assisted development.

## Features

- 🚀 **Non-interactive**: Perfect for automation and AI code generation
- 📝 **Data-driven**: Templates defined in clean YAML format
- 🔍 **Schema validation**: Catch configuration errors before generation
- 🔧 **Multiple modes**: Interactive, batch, and programmatic usage
- 📦 **Minimal dependencies**: Just 3 Python packages required
- ✅ **Production ready**: Generates fully functional Kit applications

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. List Available Templates
```bash
./kit-template list
```

### 3. Generate Your First Application
```bash
./kit-template generate kit_base_editor \
  --var application_name=acme.my_editor \
  --var application_display_name="My Editor" \
  --var version=1.0.0
```

## Available Templates

### Applications
- **`kit_base_editor`** - Foundation editor with viewport and property windows
- **`usd_composer`** - Advanced USD authoring application  
- **`usd_explorer`** - USD content viewing and exploration
- **`usd_viewer`** - Lightweight USD viewer
- **`kit_service`** - Headless service application with HTTP APIs

### Extensions
- **`basic_python_extension`** - Simple Python extension
- **`python_ui_extension`** - Python extension with UI components
- **`basic_cpp_extension`** - Native C++ extension
- **`python_binding_extension`** - C++ extension with Python bindings

### Streaming Layers  
- **`omni_default_streaming`** - Default Omniverse streaming
- **`nvcf_streaming`** - NVIDIA Cloud Functions streaming
- **`gdn_streaming`** - GeForce NOW streaming

## Usage Examples

### Command Line Generation
```bash
# Generate an application
./kit-template generate kit_base_editor \
  --var application_name=acme.content_browser \
  --var application_display_name="Acme Content Browser" \
  --var version=2.1.0

# Generate an extension
./kit-template generate basic_python_extension \
  --var extension_name=acme.workflow_tools \
  --var extension_display_name="Acme Workflow Tools" \
  --var version=1.5.0

# Custom output location
./kit-template generate kit_base_editor -c config.yaml --output ./my_projects
```

### Configuration File Usage
Create `my_editor.yaml`:
```yaml
application_name: "acme.content_editor"
application_display_name: "Acme Content Editor"
version: "2.1.0"
```

Then generate:
```bash
./kit-template generate kit_base_editor -c my_editor.yaml
```

### Interactive Mode
```bash
./kit-template generate kit_base_editor --interactive
```

### Batch Configuration
Create `batch_config.json`:
```json
{
  "templates": [
    {
      "id": "kit_base_editor",
      "variables": {
        "application_name": "acme.editor",
        "application_display_name": "Acme Editor",
        "version": "1.0.0"
      }
    },
    {
      "id": "basic_python_extension", 
      "variables": {
        "extension_name": "acme.tools",
        "extension_display_name": "Acme Tools", 
        "version": "1.0.0"
      }
    }
  ]
}
```

## Validation and Schema

### Show Template Schema
```bash
./kit-template schema kit_base_editor
./kit-template schema basic_python_extension --json
```

### Validate Configuration
```bash  
./kit-template validate kit_base_editor -c my_config.yaml
```

## Programmatic Usage

Perfect for CI/CD and AI code generation:

### Python API
```python
import subprocess

def generate_kit_app(name, display_name):
    cmd = ["./kit-template", "generate", "kit_base_editor",
           "--var", f"application_name={name}",
           "--var", f"application_display_name={display_name}",
           "--var", "version=1.0.0"]
    return subprocess.run(cmd, capture_output=True, text=True)

# Usage
success, output, error = generate_kit_app(
    "ai.generated.editor",
    "AI Generated Editor"
)
```

### Shell Scripting
```bash
#!/bin/bash

templates=(
    "kit_base_editor:acme.editor:Acme Editor"
    "basic_python_extension:acme.tools:Acme Tools"
)

for spec in "${templates[@]}"; do
    IFS=':' read -r template name display <<< "$spec"
    ./kit-template generate "$template" \
        --var "application_name=$name" \
        --var "extension_name=$name" \
        --var "application_display_name=$display" \
        --var "extension_display_name=$display" \
        --var "version=1.0.0"
done
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Generate Templates
on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Generate application
      run: |
        ./kit-template generate kit_base_editor \
          --var application_name=ci.test_app \
          --var application_display_name="CI Test App" \
          --var version=1.0.0
```

## Project Structure

```
kit-app-template/
├── kit-template              # Main CLI tool
├── requirements.txt          # Python dependencies
├── templates/
│   ├── registry.yaml        # Template definitions
│   ├── apps/                # Application templates
│   ├── extensions/          # Extension templates
│   └── ...
├── examples/                # Sample configurations
└── README.md
```

## Template Variables

All templates support these common patterns:

### Application Templates
- `application_name` - Namespace identifier (e.g., "acme.my_app")
- `application_display_name` - Human-readable name
- `version` - Semantic version (e.g., "1.0.0")

### Extension Templates  
- `extension_name` - Namespace identifier (e.g., "acme.my_extension")
- `extension_display_name` - Human-readable name
- `version` - Semantic version

All variables are validated with schema checking and pattern matching.

## Building and Running Generated Applications

After generating templates, you can build and run them using standard Kit workflows:

### Build
```bash
# Navigate to generated application directory
cd source/apps/your_app_name/

# Build using Kit SDK tools
# (Specific build commands depend on your Kit SDK setup)
```

### Development
Generated applications include:
- Complete `.kit` configuration files
- Extension scaffolding with proper structure  
- Example code and documentation
- Test frameworks and examples

## Getting Help

```bash
./kit-template --help                    # General help
./kit-template generate --help           # Generate command help
./kit-template list --help               # List command help
./kit-template schema --help             # Schema command help
```

## Template Development

### Adding Custom Templates

1. Create template directory in `templates/apps/` or `templates/extensions/`
2. Add template definition to `templates/registry.yaml`
3. Use `{{ variable_name }}` for template substitution
4. Test with validation tools

**Example registry entry:**
```yaml
my_custom_app:
  name: "My Custom Application"
  description: "Description of the application template"
  category: "app"
  template_path: "apps/my_custom_app"
  variables:
    - name: "application_name"
      type: "string"
      description: "Application identifier"
      required: true
      pattern: "^[a-z0-9_]+\\.[a-z0-9_]+$"
```

### Variable Types
- `string` - Text with optional pattern validation
- `number` - Integer or float values
- `boolean` - true/false values  
- `choice` - Must be one of predefined options

## Contributing

1. Fork the repository
2. Create templates following established patterns
3. Add entries to `templates/registry.yaml`
4. Test with validation tools
5. Submit a pull request

---

**Need help?** Check the examples in the `examples/` directory or run `./kit-template --help` for detailed usage information.