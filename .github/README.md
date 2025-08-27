# Kit Template - Project Structure

## Repository Layout

```
kit-app-template/
├── kit-template              # Main CLI executable
├── requirements.txt          # Python dependencies (jinja2, pyyaml, jsonschema)
├── templates/
│   ├── registry.yaml         # Template definitions and metadata
│   ├── apps/                 # Application templates
│   │   ├── kit_base_editor/
│   │   ├── usd_composer/
│   │   ├── usd_explorer/
│   │   ├── usd_viewer/
│   │   ├── kit_service/
│   │   └── streaming_configs/
│   └── extensions/           # Extension templates  
│       ├── basic_python/
│       ├── python_ui/
│       ├── basic_cpp/
│       ├── basic_python_binding/
│       └── setup extensions/
├── examples/                 # Sample configurations
│   ├── my_editor_config.yaml
│   ├── my_extension_config.yaml
│   └── batch_generation.json
└── README.md                 # Main documentation
```

## Generated Output Structure

When you run the tool, it creates applications and extensions in this structure:

```
source/                       # Generated output directory
├── apps/                     # Generated applications
│   └── your.app.name/
│       ├── your_app.kit      # Main kit file
│       └── README.md         # Generated documentation
└── extensions/               # Generated extensions
    └── your.extension.name/
        ├── config/
        │   └── extension.toml
        ├── your_module/
        │   ├── __init__.py
        │   ├── extension.py
        │   └── tests/
        ├── data/
        │   ├── icon.png
        │   └── preview.png
        ├── docs/
        └── premake5.lua
```

## Template System Architecture

### Core Components

1. **`kit-template`** - Main CLI tool (Python script)
   - Template engine using Jinja2
   - Schema validation using jsonschema  
   - Multiple operation modes (interactive, batch, API)

2. **`templates/registry.yaml`** - Template metadata
   - Template definitions and descriptions
   - Variable schemas and validation rules
   - Dependencies and relationships

3. **Template directories** - Actual template content
   - Jinja2 templates with `{{ variable }}` substitution
   - Directory names can be templated (e.g., `{{python_module_path}}`)
   - Binary files copied as-is, text files processed

### Template Variables

Templates use consistent variable naming:

**Applications:**
- `application_name` - Namespace identifier (e.g., "acme.my_app")  
- `application_display_name` - Human-readable name
- `version` - Semantic version

**Extensions:**
- `extension_name` - Namespace identifier (e.g., "acme.my_extension")
- `extension_display_name` - Human-readable name  
- `version` - Semantic version

**Computed Variables:**
- `python_module_path` - Auto-generated from extension_name (dots → slashes)
- `*_kebab` - Kebab-case versions of variables

## Usage Patterns

### Development Workflow
```bash
# 1. Explore templates
./kit-template list --category app

# 2. Check schema  
./kit-template schema kit_base_editor

# 3. Create config file
cat > my_app.yaml << EOF
application_name: "acme.my_editor"
application_display_name: "Acme Editor"  
version: "1.0.0"
EOF

# 4. Validate config
./kit-template validate kit_base_editor -c my_app.yaml

# 5. Generate template
./kit-template generate kit_base_editor -c my_app.yaml
```

### CI/CD Integration
The tool is designed for automation:
- Non-interactive by default
- Returns proper exit codes
- JSON output available for parsing
- Minimal dependencies for container usage

### AI/Programmatic Usage
Perfect for code generation tools:
- Schema introspection available
- Batch processing support  
- Validation before generation
- Consistent error handling

## Extending the System

### Adding New Templates

1. **Create template directory:**
   ```bash
   mkdir -p templates/apps/my_new_template
   ```

2. **Add template files with Jinja2 syntax:**
   ```bash
   # templates/apps/my_new_template/app.kit
   [package]
   title = "{{ application_display_name }}"
   version = "{{ version }}"
   ```

3. **Update registry.yaml:**
   ```yaml
   my_new_template:
     name: "My New Template"
     description: "What this template creates"
     category: "app"
     template_path: "apps/my_new_template"  
     variables:
       - name: "application_name"
         type: "string"
         required: true
   ```

### Variable Validation

Supported validation rules:
- `required: true/false` - Whether variable must be provided
- `pattern: "regex"` - Regular expression validation
- `choices: [...]` - Must be one of listed values  
- `type: string/number/boolean/choice` - Type validation
- `default: value` - Default value if not provided

## Design Principles

1. **Data-driven** - Templates are data, not code
2. **Validation first** - Catch errors before generation  
3. **Automation friendly** - Non-interactive by default
4. **Simple dependencies** - Minimal external requirements
5. **Consistent output** - Predictable directory structures
6. **Extensible** - Easy to add new templates

This architecture provides a clean, maintainable foundation for template-based Kit application and extension generation.
