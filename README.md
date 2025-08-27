# Kat Manager - Modern Template System for Omniverse Kit

A clean, data-driven template system for creating Omniverse Kit applications and extensions. Kat (Kit Application Template) Manager features cross-platform support with automatic virtual environment management and self-contained operation.

## Features

- 🌍 **Cross-platform**: Works on Windows, Linux, and macOS
- 🐍 **Self-contained**: Automatic Python virtual environment management
- 🚀 **Non-interactive**: Perfect for automation and AI code generation
- 📝 **Data-driven**: Templates defined in clean YAML format
- 🔍 **Schema validation**: Catch configuration errors before generation
- 🔧 **Multiple modes**: Interactive, batch, and programmatic usage
- 📦 **Environment isolation**: All dependencies and generated content in managed venv
- 🧹 **Clean deployment**: Easy cleanup and selective deployment

## Quick Start

### Windows
```powershell
kat-manager list
kat-manager generate kit_base_editor --var application_name=acme.my_editor --var application_display_name="My Editor" --var version=1.0.0
```

### Linux/macOS  
```bash
./kat-manager.sh list
./kat-manager.sh generate kit_base_editor --var application_name=acme.my_editor --var application_display_name="My Editor" --var version=1.0.0
```

The system automatically:
1. Creates a Python virtual environment (`_kat_venv/`) if needed
2. Installs dependencies in the isolated environment  
3. Generates templates within the managed environment
4. Keeps everything self-contained and easily cleanable

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

## Core Commands

### Template Operations
```bash
# Windows
kat-manager list                                    # List available templates
kat-manager schema kit_base_editor                  # Show template requirements
kat-manager generate kit_base_editor -c config.yaml # Generate from config file
kat-manager validate kit_base_editor -c config.yaml # Validate configuration

# Linux/macOS
./kat-manager.sh list
./kat-manager.sh schema kit_base_editor  
./kat-manager.sh generate kit_base_editor -c config.yaml
./kat-manager.sh validate kit_base_editor -c config.yaml
```

### Environment Management
```bash
# Windows
kat-manager status                                  # Show environment status
kat-manager deploy my_app C:\Projects\             # Deploy app to external location
kat-manager clean                                   # Remove venv and all generated content

# Linux/macOS  
./kat-manager.sh status
./kat-manager.sh deploy my_app /home/user/projects/
./kat-manager.sh clean
```

## Configuration Files

### Application Template (YAML)
```yaml
# my_editor.yaml
application_name: "acme.content_editor"
application_display_name: "Acme Content Editor"
version: "2.1.0"
```

### Extension Template (YAML)
```yaml  
# my_extension.yaml
extension_name: "acme.workflow_tools"
extension_display_name: "Acme Workflow Tools"
version: "1.5.0"
```

### Batch Configuration (JSON)
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

## Usage Examples

### Interactive Mode
```bash
# Windows
kat-manager generate kit_base_editor --interactive

# Linux/macOS
./kat-manager.sh generate kit_base_editor --interactive
```

### Command Line Variables
```bash
# Windows
kat-manager generate basic_python_extension ^
  --var extension_name=acme.my_tools ^
  --var extension_display_name="Acme Tools" ^
  --var version=1.2.3

# Linux/macOS
./kat-manager.sh generate basic_python_extension \
  --var extension_name=acme.my_tools \
  --var extension_display_name="Acme Tools" \
  --var version=1.2.3
```

### Deploy Generated Applications
```bash
# Generate and deploy in one workflow
kat-manager generate kit_base_editor -c my_config.yaml
kat-manager deploy acme.my_editor C:\MyProjects\

# Linux/macOS
./kat-manager.sh generate kit_base_editor -c my_config.yaml  
./kat-manager.sh deploy acme.my_editor /home/user/projects/
```

## Environment Structure

```
kit-app-template/
├── kat-manager.bat             # Windows entrypoint
├── kat-manager.sh              # Linux/macOS entrypoint
├── kat_env_manager.py          # Environment management logic
├── kat-manager                 # Core template engine
├── requirements.txt            # Python dependencies
├── templates/
│   ├── registry.yaml           # Template definitions
│   ├── apps/                   # Application templates
│   └── extensions/             # Extension templates
├── examples/                   # Sample configurations
└── _kat_venv/                  # Managed virtual environment
    ├── source/                 # Generated templates
    ├── deployed/               # Deployed template tracking
    └── [Python venv files]
```

## Programmatic Usage

Perfect for CI/CD and AI code generation:

### Python API
```python
import subprocess
import os

def generate_kit_app(name, display_name):
    # Windows
    if os.name == 'nt':
        cmd = ["kat-manager", "generate", "kit_base_editor",
               "--var", f"application_name={name}",
               "--var", f"application_display_name={display_name}",
               "--var", "version=1.0.0"]
    else:
        cmd = ["./kat-manager.sh", "generate", "kit_base_editor",
               "--var", f"application_name={name}",
               "--var", f"application_display_name={display_name}",
               "--var", "version=1.0.0"]
    
    return subprocess.run(cmd, capture_output=True, text=True)

# Usage
result = generate_kit_app("ai.generated.editor", "AI Generated Editor")
if result.returncode == 0:
    print("✅ Template generated successfully!")
    
    # Deploy to external location
    if os.name == 'nt':
        deploy_cmd = ["kat-manager", "deploy", "ai.generated.editor", "C:\\Output\\"]
    else:
        deploy_cmd = ["./kat-manager.sh", "deploy", "ai.generated.editor", "/tmp/output/"]
    subprocess.run(deploy_cmd)
```

### Shell Scripting
```bash
#!/bin/bash

# Cross-platform script detection
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    KAT_CMD="kat-manager"
else
    KAT_CMD="./kat-manager.sh"
fi

# Generate multiple templates
templates=(
    "kit_base_editor:acme.editor:Acme Editor"
    "basic_python_extension:acme.tools:Acme Tools"
)

for spec in "${templates[@]}"; do
    IFS=':' read -r template name display <<< "$spec"
    $KAT_CMD generate "$template" \
        --var "application_name=$name" \
        --var "extension_name=$name" \
        --var "application_display_name=$display" \
        --var "extension_display_name=$display" \
        --var "version=1.0.0"
    
    # Deploy to projects directory
    $KAT_CMD deploy "$name" "../deployed-projects/"
done

# Show status
$KAT_CMD status
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Generate Templates
on: [push]

jobs:
  test-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    - name: Generate application
      run: |
        kat-manager generate kit_base_editor --var application_name=ci.test_app --var application_display_name="CI Test App" --var version=1.0.0
        kat-manager status

  test-linux:
    runs-on: ubuntu-latest  
    steps:
    - uses: actions/checkout@v3
    - name: Generate application
      run: |
        ./kat-manager.sh generate kit_base_editor --var application_name=ci.test_app --var application_display_name="CI Test App" --var version=1.0.0
        ./kat-manager.sh status
```

## Environment Management

### Status and Information
```bash
kat-manager status                    # Show environment status and generated templates
```

### Clean Up
```bash  
kat-manager clean                     # Remove virtual environment and ALL generated content
```

### Deployment
```bash
# Deploy a generated template to external location (preserving it from clean)
kat-manager deploy my_app /path/to/external/location/

# List what can be deployed  
kat-manager list                      # Shows generated templates available for deployment
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

## Troubleshooting

### Environment Issues
```bash
# Check environment status
kat-manager status

# Clean and rebuild environment  
kat-manager clean
kat-manager status  # This will recreate the environment
```

### Template Issues
```bash
# Validate template configuration
kat-manager validate kit_base_editor -c my_config.yaml

# Show template requirements
kat-manager schema kit_base_editor
```

### Cross-Platform Issues
- **Windows**: Use `kat-manager` (batch file)
- **Linux/macOS**: Use `./kat-manager.sh` (shell script)
- **WSL**: Use the Linux version (`./kat-manager.sh`)

## Contributing

1. Fork the repository
2. Create templates following established patterns
3. Add entries to `templates/registry.yaml`
4. Test on both Windows and Linux
5. Submit a pull request

---

**Self-contained, cross-platform, and production-ready.** The Kat Manager system manages its own environment and keeps everything organized for easy development and deployment.